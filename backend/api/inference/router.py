"""Inference Router - Entity extraction endpoints."""

from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional
from datetime import datetime
import time
import uuid
import logging
import torch

logger = logging.getLogger(__name__)

router = APIRouter()


# Request Models
class ExtractionRequest(BaseModel):
    """Request model for single text extraction."""
    text: str = Field(
        ...,
        min_length=10,
        max_length=10000,
        description="Text to extract entities from"
    )
    request_id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique request identifier"
    )
    save_to_db: bool = Field(
        default=False,
        description="Whether to save extraction results to database"
    )

    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Text cannot be empty')
        return v


class BatchExtractionRequest(BaseModel):
    """Request model for batch text extraction."""
    texts: List[str] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of texts to extract entities from"
    )
    request_id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique request identifier"
    )

    @field_validator('texts')
    @classmethod
    def validate_texts(cls, v: List[str]) -> List[str]:
        cleaned = []
        for text in v:
            text = text.strip()
            if text and 10 <= len(text) <= 10000:
                cleaned.append(text)
        if not cleaned:
            raise ValueError('At least one valid text is required')
        return cleaned


# Response Models
class Entity(BaseModel):
    """Individual extracted entity."""
    text: str
    label: str
    start: int
    end: int
    confidence: float


class StructuredEvent(BaseModel):
    """5W1H+WHY structured event representation."""
    who: List[str] = Field(default_factory=list, description="Actors: PERPETRATOR, VICTIM, TARGET, ORGANIZATION, GOVERNMENT")
    what: List[str] = Field(default_factory=list, description="Events: EVENT_TYPE, ACTION, WEAPON, VIOLENCE_TYPE")
    when: List[str] = Field(default_factory=list, description="Temporal: DATE, TIME, DURATION, FREQUENCY")
    where: List[str] = Field(default_factory=list, description="Location: COUNTRY, REGION, CITY, DISTRICT, FACILITY, GEOGRAPHIC, COORDINATES")
    how: List[str] = Field(default_factory=list, description="Impact: CASUALTIES, INJURED, DISPLACEMENT, DAMAGE")
    why: List[str] = Field(default_factory=list, description="Cause: MOTIVE, TRIGGER")


class ExtractionResponse(BaseModel):
    """Response model for single text extraction."""
    request_id: str
    text: str
    entities: List[Entity]
    structured_event: StructuredEvent
    confidence_scores: Dict[str, float]
    processing_time_ms: float
    model_version: str
    timestamp: datetime

    model_config = {"protected_namespaces": ()}


class BatchExtractionResult(BaseModel):
    """Individual result in batch extraction."""
    index: int
    text: str
    entities: Optional[List[Entity]] = None
    structured_event: Optional[StructuredEvent] = None
    confidence_scores: Optional[Dict[str, float]] = None
    error: Optional[str] = None


class BatchExtractionResponse(BaseModel):
    """Response model for batch text extraction."""
    request_id: str
    results: List[BatchExtractionResult]
    total_processed: int
    successful: int
    failed: int
    processing_time_ms: float
    model_version: str
    timestamp: datetime

    model_config = {"protected_namespaces": ()}


def save_extraction_to_history(
    request_id: str,
    text: str,
    entities: list,
    structured_event: dict,
    confidence_scores: dict,
    processing_time_ms: float,
    model_version: str,
    db_context,
    repository_class
):
    """Background task to save extraction to history."""
    try:
        with db_context() as db:
            if db:
                repo = repository_class(db)
                repo.save_extraction(
                    request_id=request_id,
                    text=text,
                    entities=entities,
                    structured_event=structured_event,
                    confidence_scores=confidence_scores,
                    processing_time_ms=processing_time_ms,
                    model_version=model_version
                )
    except Exception as e:
        logger.error(f"Failed to save extraction to history: {e}")


@router.post("", response_model=ExtractionResponse)
async def extract_entities(
    request_data: ExtractionRequest,
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Extract entities from text and return structured 5W1H output.

    Analyzes input text using a BERT-based NER model to extract entities like
    perpetrators, victims, locations, dates, weapons, and casualties.
    """
    ner_service = request.app.state.ner_service
    settings = request.app.state.settings

    if ner_service is None or not ner_service.is_loaded():
        raise HTTPException(
            status_code=503,
            detail="NER service not available. Model may not be loaded."
        )

    start_time = time.time()

    try:
        result = ner_service.extract(request_data.text)
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Extraction failed: {str(e)}"
        )

    processing_time = (time.time() - start_time) * 1000

    entities = [Entity(**e) for e in result['entities']]
    structured_event = StructuredEvent(**result['structured_event'])

    # Get actual model session_id from loaded model path
    from utils.paths import extract_session_id
    model_version = extract_session_id(str(ner_service.model_path)) or "unknown"

    # Save to history in background (non-blocking)
    if settings.enable_db_storage and request_data.save_to_db:
        from database.connection import get_db_context
        from database.repository import EventRepository
        background_tasks.add_task(
            save_extraction_to_history,
            request_id=request_data.request_id,
            text=request_data.text,
            entities=result['entities'],
            structured_event=result['structured_event'],
            confidence_scores=result['confidence_scores'],
            processing_time_ms=round(processing_time, 2),
            model_version=model_version,
            db_context=get_db_context,
            repository_class=EventRepository
        )

    return ExtractionResponse(
        request_id=request_data.request_id,
        text=request_data.text,
        entities=entities,
        structured_event=structured_event,
        confidence_scores=result['confidence_scores'],
        processing_time_ms=round(processing_time, 2),
        model_version=model_version,
        timestamp=datetime.utcnow()
    )


@router.post("/batch", response_model=BatchExtractionResponse)
async def extract_batch(
    request_data: BatchExtractionRequest,
    request: Request
):
    """
    Extract entities from multiple texts in batch.

    Processes up to 100 texts in a single request.
    """
    ner_service = request.app.state.ner_service

    if ner_service is None or not ner_service.is_loaded():
        raise HTTPException(
            status_code=503,
            detail="NER service not available. Model may not be loaded."
        )

    start_time = time.time()
    results = []
    successful = 0
    failed = 0

    for idx, text in enumerate(request_data.texts):
        try:
            result = ner_service.extract(text)

            entities = [Entity(**e) for e in result['entities']]
            structured_event = StructuredEvent(**result['structured_event'])

            results.append(BatchExtractionResult(
                index=idx,
                text=text,
                entities=entities,
                structured_event=structured_event,
                confidence_scores=result['confidence_scores'],
                error=None
            ))
            successful += 1

        except Exception as e:
            logger.error(f"Batch extraction failed for index {idx}: {e}")
            results.append(BatchExtractionResult(
                index=idx,
                text=text,
                entities=None,
                structured_event=None,
                confidence_scores=None,
                error=str(e)
            ))
            failed += 1

    processing_time = (time.time() - start_time) * 1000

    # Get actual model session_id from loaded model path
    from utils.paths import extract_session_id
    model_version = extract_session_id(str(ner_service.model_path)) or "unknown"

    return BatchExtractionResponse(
        request_id=request_data.request_id,
        results=results,
        total_processed=len(request_data.texts),
        successful=successful,
        failed=failed,
        processing_time_ms=round(processing_time, 2),
        model_version=model_version,
        timestamp=datetime.utcnow()
    )


@router.get("/categories")
async def get_categories(request: Request):
    """
    Get the 5W1H category to entity label mapping.
    """
    ner_service = request.app.state.ner_service

    if ner_service is None or not ner_service.is_loaded():
        raise HTTPException(
            status_code=503,
            detail="NER service not available."
        )

    return {
        "categories": ner_service.get_categories(),
        "description": {
            "WHO": "Actors involved (perpetrators, victims, groups)",
            "WHAT": "Event types, actions, and weapons used",
            "WHEN": "Temporal information (dates, times)",
            "WHERE": "Geographic locations (countries, cities)",
            "HOW": "Methods, casualties, and manner of attack"
        }
    }


@router.get("/model/info")
async def get_model_info(request: Request):
    """Get information about the loaded model."""
    ner_service = request.app.state.ner_service

    if ner_service is None:
        return {
            "model_path": None,
            "model_type": None,
            "num_labels": 0,
            "device": "none",
            "loaded": False,
            "loaded_at": None,
            "labels": []
        }

    return {
        "model_path": str(ner_service.model_path),
        "model_type": "bert-base-cased",
        "num_labels": len(ner_service.id2label) if hasattr(ner_service, 'id2label') else 0,
        "device": str(ner_service.device),
        "loaded": ner_service.is_loaded(),
        "loaded_at": getattr(ner_service, 'loaded_at', None),
        "labels": list(ner_service.id2label.values()) if hasattr(ner_service, 'id2label') else []
    }


class ModelSwitchRequest(BaseModel):
    """Request to switch the active model."""
    session_id: str = Field(..., description="Model session identifier (e.g., 'bert-base-cased_20251209_212123')")
    subfolder: str = Field(default='best', description="Subfolder to load ('best', 'epoch_01', etc.)")


@router.post("/model/switch")
async def switch_model(request_data: ModelSwitchRequest, request: Request):
    """
    Switch to a different model for inference.

    This reloads the NER service with a new model checkpoint.
    Note: This operation takes 20-30 seconds as the model needs to be loaded into memory.

    The path is resolved at runtime based on the current environment:
    - Docker: /app/models/{session_id}/{subfolder}
    - Local: ./models/{session_id}/{subfolder}
    """
    from services.ner import NERService
    from utils.paths import resolve_model_path

    # Resolve session_id to full path based on current environment
    model_path = resolve_model_path(request_data.session_id, request_data.subfolder)

    logger.info(f"Resolved model path: {model_path} (session_id={request_data.session_id}, subfolder={request_data.subfolder})")

    # Validate model path exists
    if not model_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Model not found: {request_data.session_id}/{request_data.subfolder}"
        )

    # Check for required model files
    if not (model_path / "config.json").exists():
        raise HTTPException(
            status_code=400,
            detail=f"Invalid model directory: missing config.json"
        )

    try:
        logger.info(f"Switching model to: {request_data.session_id}")

        # Determine device (prefer MPS on Mac, then CUDA, then CPU)
        device = "cpu"
        if hasattr(torch, 'backends') and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device = "mps"
        elif torch.cuda.is_available():
            device = "cuda"

        # Create and load new NER service
        new_service = NERService(str(model_path), device=device)
        new_service.load()

        # Replace the app's NER service
        request.app.state.ner_service = new_service

        logger.info(f"Model switched successfully: {request_data.session_id}")

        return {
            "success": True,
            "message": f"Model switched to {request_data.session_id}",
            "session_id": request_data.session_id,
            "subfolder": request_data.subfolder,
            "device": device,
            "num_labels": len(new_service.id2label)
        }

    except Exception as e:
        logger.error(f"Failed to switch model: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load model: {str(e)}"
        )
