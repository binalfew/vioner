"""Extraction history endpoints."""

from fastapi import APIRouter, HTTPException, Query, Request
from datetime import datetime
from typing import Optional, List
import logging

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()


class ExtractionHistoryItem(BaseModel):
    """Single extraction history item."""
    id: int
    request_id: str
    text: str
    entity_count: int
    processing_time_ms: Optional[float]
    model_version: Optional[str]
    user_rating: Optional[int]
    saved_to_events: bool
    event_id: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class ExtractionHistoryDetail(ExtractionHistoryItem):
    """Detailed extraction history with entities."""
    entities: List[dict]
    structured_event: dict
    confidence_scores: dict

    model_config = {"from_attributes": True}


class FeedbackRequest(BaseModel):
    """Request model for updating feedback."""
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating 1-5")
    feedback: Optional[str] = Field(None, max_length=1000)
    corrections: Optional[dict] = None


@router.get("", response_model=List[ExtractionHistoryItem])
async def get_extraction_history(
    request: Request,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """
    Get extraction history.

    Returns a paginated list of past extractions with metadata.
    """
    settings = request.app.state.settings

    if not settings.enable_db_storage:
        raise HTTPException(
            status_code=503,
            detail="Database storage not enabled"
        )

    from database.connection import get_db_context
    from database.repository import EventRepository

    with get_db_context() as db:
        if db is None:
            raise HTTPException(
                status_code=503,
                detail="Database not available"
            )

        repo = EventRepository(db)
        extractions = repo.get_extraction_history(
            limit=limit,
            offset=offset,
            start_date=start_date,
            end_date=end_date
        )

        return [
            ExtractionHistoryItem(
                id=e.id,
                request_id=e.request_id,
                text=e.text[:200] + "..." if len(e.text) > 200 else e.text,
                entity_count=e.entity_count or 0,
                processing_time_ms=e.processing_time_ms,
                model_version=e.model_version,
                user_rating=e.user_rating,
                saved_to_events=e.saved_to_events or False,
                event_id=e.event_id,
                created_at=e.created_at
            )
            for e in extractions
        ]


@router.get("/{extraction_id}", response_model=ExtractionHistoryDetail)
async def get_extraction_detail(request: Request, extraction_id: int):
    """
    Get detailed extraction by ID.

    Returns full extraction details including all entities and structured output.
    """
    settings = request.app.state.settings

    if not settings.enable_db_storage:
        raise HTTPException(status_code=503, detail="Database storage not enabled")

    from database.connection import get_db_context
    from database.repository import EventRepository

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        repo = EventRepository(db)
        extraction = repo.get_extraction_by_id(extraction_id)

        if not extraction:
            raise HTTPException(status_code=404, detail="Extraction not found")

        return ExtractionHistoryDetail(
            id=extraction.id,
            request_id=extraction.request_id,
            text=extraction.text,
            entity_count=extraction.entity_count or 0,
            processing_time_ms=extraction.processing_time_ms,
            model_version=extraction.model_version,
            user_rating=extraction.user_rating,
            saved_to_events=extraction.saved_to_events or False,
            event_id=extraction.event_id,
            created_at=extraction.created_at,
            entities=extraction.entities_json or [],
            structured_event=extraction.structured_event_json or {},
            confidence_scores=extraction.confidence_scores_json or {}
        )


@router.post("/{extraction_id}/feedback")
async def update_feedback(request: Request, extraction_id: int, feedback: FeedbackRequest):
    """
    Update feedback for an extraction.

    Allows users to rate and provide feedback on extraction quality.
    """
    settings = request.app.state.settings

    if not settings.enable_db_storage:
        raise HTTPException(status_code=503, detail="Database storage not enabled")

    from database.connection import get_db_context
    from database.repository import EventRepository

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        repo = EventRepository(db)
        updated = repo.update_extraction_feedback(
            extraction_id=extraction_id,
            rating=feedback.rating,
            feedback=feedback.feedback,
            corrections=feedback.corrections
        )

        if not updated:
            raise HTTPException(status_code=404, detail="Extraction not found")

        return {"message": "Feedback updated successfully", "extraction_id": extraction_id}


@router.delete("/{extraction_id}")
async def delete_extraction(request: Request, extraction_id: int):
    """Delete an extraction from history."""
    settings = request.app.state.settings

    if not settings.enable_db_storage:
        raise HTTPException(status_code=503, detail="Database storage not enabled")

    from database.connection import get_db_context
    from database.models import HistoryDB

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        extraction = db.query(HistoryDB).filter(
            HistoryDB.id == extraction_id
        ).first()

        if not extraction:
            raise HTTPException(status_code=404, detail="Extraction not found")

        db.delete(extraction)

        return {"message": "Extraction deleted", "extraction_id": extraction_id}
