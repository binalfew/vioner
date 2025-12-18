"""Evaluation Router - API endpoints for model evaluation and analytics."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import asyncio
import logging

from services.evaluation import get_evaluation_service, EvaluationResult

router = APIRouter(prefix="/evaluation", tags=["evaluation"])
logger = logging.getLogger(__name__)

# Cache for evaluation results
_evaluation_cache: Dict[str, dict] = {}
_evaluation_in_progress: Dict[str, bool] = {}


# ============================================================
# Pydantic Models
# ============================================================

class EntityMetricsResponse(BaseModel):
    """Metrics for a single entity type."""
    entity_type: str
    precision: float
    recall: float
    f1: float
    support: int
    predicted: int
    correct: int


class ConfusionEntryResponse(BaseModel):
    """Confusion matrix entry."""
    true_label: str
    predicted_label: str
    count: int
    examples: List[Dict]


class ErrorExampleResponse(BaseModel):
    """Error example."""
    text: str
    true_entities: List[Dict]
    predicted_entities: List[Dict]
    error_type: str
    entity_type: str


class EvaluationResponse(BaseModel):
    """Complete evaluation response."""
    checkpoint_name: str
    epoch: Optional[int]
    total_samples: int
    overall_precision: float
    overall_recall: float
    overall_f1: float
    entity_metrics: List[EntityMetricsResponse]
    confusion_matrix: List[ConfusionEntryResponse]
    error_examples: List[ErrorExampleResponse]
    entity_distribution: Dict[str, int]


class EvaluationRequest(BaseModel):
    """Request to run evaluation."""
    checkpoint_name: str
    epoch: Optional[int] = None
    max_samples: Optional[int] = Field(default=None, description="Limit samples for faster evaluation")


class EvaluationStatusResponse(BaseModel):
    """Status of evaluation."""
    checkpoint_name: str
    status: str  # 'running', 'complete', 'not_started', 'error'
    cached: bool = False
    error: Optional[str] = None


class EvaluationListResponse(BaseModel):
    """List of available evaluations."""
    evaluations: List[Dict]


# ============================================================
# Helper Functions
# ============================================================

def _get_cache_key(checkpoint_name: str, epoch: Optional[int]) -> str:
    """Generate cache key for evaluation."""
    return f"{checkpoint_name}_{epoch or 'best'}"


async def _run_evaluation_async(
    checkpoint_name: str,
    epoch: Optional[int],
    max_samples: Optional[int]
) -> None:
    """Run evaluation in background."""
    cache_key = _get_cache_key(checkpoint_name, epoch)
    _evaluation_in_progress[cache_key] = True

    try:
        service = get_evaluation_service()
        loop = asyncio.get_event_loop()

        # Run evaluation in thread pool
        result = await loop.run_in_executor(
            None,
            service.evaluate,
            checkpoint_name,
            epoch,
            max_samples
        )

        if result:
            _evaluation_cache[cache_key] = result.to_dict()
        else:
            _evaluation_cache[cache_key] = {'error': 'Evaluation failed'}

    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        _evaluation_cache[cache_key] = {'error': str(e)}
    finally:
        _evaluation_in_progress[cache_key] = False


# ============================================================
# Endpoints
# ============================================================

@router.post("/run", response_model=EvaluationStatusResponse)
async def run_evaluation(
    request: EvaluationRequest,
    background_tasks: BackgroundTasks
):
    """
    Start evaluation for a checkpoint.

    This runs evaluation in the background and caches results.
    Poll /status to check when complete, then /results to get data.
    """
    cache_key = _get_cache_key(request.checkpoint_name, request.epoch)

    # Check if already in cache
    if cache_key in _evaluation_cache and 'error' not in _evaluation_cache[cache_key]:
        return EvaluationStatusResponse(
            checkpoint_name=request.checkpoint_name,
            status='complete',
            cached=True
        )

    # Check if already running
    if _evaluation_in_progress.get(cache_key):
        return EvaluationStatusResponse(
            checkpoint_name=request.checkpoint_name,
            status='running'
        )

    # Start background evaluation
    background_tasks.add_task(
        _run_evaluation_async,
        request.checkpoint_name,
        request.epoch,
        request.max_samples
    )

    return EvaluationStatusResponse(
        checkpoint_name=request.checkpoint_name,
        status='running'
    )


@router.get("/status/{checkpoint_name}")
async def get_evaluation_status(
    checkpoint_name: str,
    epoch: Optional[int] = None
) -> EvaluationStatusResponse:
    """Get status of an evaluation."""
    cache_key = _get_cache_key(checkpoint_name, epoch)

    if cache_key in _evaluation_cache:
        cached = _evaluation_cache[cache_key]
        if 'error' in cached:
            return EvaluationStatusResponse(
                checkpoint_name=checkpoint_name,
                status='error',
                error=cached['error']
            )
        return EvaluationStatusResponse(
            checkpoint_name=checkpoint_name,
            status='complete',
            cached=True
        )

    if _evaluation_in_progress.get(cache_key):
        return EvaluationStatusResponse(
            checkpoint_name=checkpoint_name,
            status='running'
        )

    return EvaluationStatusResponse(
        checkpoint_name=checkpoint_name,
        status='not_started'
    )


@router.get("/results/{checkpoint_name}", response_model=EvaluationResponse)
async def get_evaluation_results(
    checkpoint_name: str,
    epoch: Optional[int] = None
):
    """Get cached evaluation results."""
    cache_key = _get_cache_key(checkpoint_name, epoch)

    if cache_key not in _evaluation_cache:
        raise HTTPException(
            404,
            detail="Evaluation not found. Run evaluation first with POST /run"
        )

    cached = _evaluation_cache[cache_key]
    if 'error' in cached:
        raise HTTPException(500, detail=cached['error'])

    return EvaluationResponse(**cached)


@router.get("/list", response_model=EvaluationListResponse)
async def list_evaluations():
    """List all cached evaluations."""
    evaluations = []
    for cache_key, data in _evaluation_cache.items():
        if 'error' not in data:
            evaluations.append({
                'cache_key': cache_key,
                'checkpoint_name': data.get('checkpoint_name'),
                'epoch': data.get('epoch'),
                'overall_f1': data.get('overall_f1'),
                'total_samples': data.get('total_samples')
            })

    return EvaluationListResponse(evaluations=evaluations)


@router.delete("/cache/{checkpoint_name}")
async def clear_evaluation_cache(
    checkpoint_name: str,
    epoch: Optional[int] = None
):
    """Clear cached evaluation for a checkpoint."""
    cache_key = _get_cache_key(checkpoint_name, epoch)

    if cache_key in _evaluation_cache:
        del _evaluation_cache[cache_key]
        return {"message": "Cache cleared", "cache_key": cache_key}

    return {"message": "No cache found", "cache_key": cache_key}


@router.delete("/cache")
async def clear_all_cache():
    """Clear all cached evaluations."""
    count = len(_evaluation_cache)
    _evaluation_cache.clear()
    return {"message": f"Cleared {count} cached evaluations"}


@router.get("/quick/{checkpoint_name}", response_model=EvaluationResponse)
async def quick_evaluation(
    checkpoint_name: str,
    epoch: Optional[int] = None,
    samples: int = 500
):
    """
    Run a quick evaluation on a subset of samples.

    This is synchronous and returns results immediately.
    Good for quick checks without waiting for full evaluation.
    """
    service = get_evaluation_service()

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        service.evaluate,
        checkpoint_name,
        epoch,
        samples
    )

    if not result:
        raise HTTPException(500, detail="Evaluation failed")

    return EvaluationResponse(**result.to_dict())
