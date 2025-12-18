"""System Router - Health checks and system metrics."""

from fastapi import APIRouter, Request
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
import psutil
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class ModelInfo(BaseModel):
    """Model information."""
    model_path: Optional[str]
    model_type: Optional[str]
    num_labels: int
    device: str
    loaded: bool
    loaded_at: Optional[str]

    model_config = {"protected_namespaces": ()}


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    model_loaded: bool
    model_info: Optional[ModelInfo]
    database_enabled: bool
    database_connected: Optional[bool]
    timestamp: datetime
    version: str

    model_config = {"protected_namespaces": ()}


class SystemMetrics(BaseModel):
    """System resource metrics."""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_percent: float
    disk_used_gb: float
    disk_free_gb: float


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    """
    Check system health.

    Returns the health status of the API, model, and database connections.
    """
    settings = request.app.state.settings
    ner_service = request.app.state.ner_service

    # Check NER service
    model_loaded = ner_service is not None and ner_service.is_loaded()
    model_info = None

    if model_loaded:
        loaded_at = getattr(ner_service, 'loaded_at', None)
        if loaded_at and hasattr(loaded_at, 'isoformat'):
            loaded_at = loaded_at.isoformat()
        model_info = ModelInfo(
            model_path=str(ner_service.model_path) if ner_service.model_path else None,
            model_type="bert-base-cased",
            num_labels=len(ner_service.id2label) if hasattr(ner_service, 'id2label') else 0,
            device=str(ner_service.device),
            loaded=True,
            loaded_at=loaded_at
        )

    # Check database connection
    database_connected = None
    if settings.enable_db_storage:
        try:
            from database.connection import check_connection
            database_connected = check_connection()
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            database_connected = False

    status = "healthy" if model_loaded else "degraded"
    if settings.enable_db_storage and database_connected is False:
        status = "degraded"

    return HealthResponse(
        status=status,
        model_loaded=model_loaded,
        model_info=model_info,
        database_enabled=settings.enable_db_storage,
        database_connected=database_connected,
        timestamp=datetime.utcnow(),
        version="1.0.0"
    )


@router.get("/metrics", response_model=SystemMetrics)
async def get_system_metrics():
    """
    Get system resource metrics.

    Returns CPU, memory, and disk usage information.
    """
    # CPU
    cpu_percent = psutil.cpu_percent(interval=0.1)

    # Memory
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    memory_used_mb = memory.used / (1024 * 1024)
    memory_available_mb = memory.available / (1024 * 1024)

    # Disk
    disk = psutil.disk_usage('/')
    disk_percent = disk.percent
    disk_used_gb = disk.used / (1024 * 1024 * 1024)
    disk_free_gb = disk.free / (1024 * 1024 * 1024)

    return SystemMetrics(
        cpu_percent=cpu_percent,
        memory_percent=memory_percent,
        memory_used_mb=round(memory_used_mb, 2),
        memory_available_mb=round(memory_available_mb, 2),
        disk_percent=disk_percent,
        disk_used_gb=round(disk_used_gb, 2),
        disk_free_gb=round(disk_free_gb, 2)
    )


@router.get("/info")
async def get_system_info(request: Request):
    """Get system and application information."""
    settings = request.app.state.settings

    return {
        "application": {
            "name": "VioNER",
            "version": "1.0.0",
            "description": "Violent Event Named Entity Recognition API"
        },
        "configuration": {
            "model_path": settings.model_path,
            "device": settings.device,
            "database_enabled": settings.enable_db_storage,
            "cors_origins": settings.cors_origins
        },
        "endpoints": {
            "training": "/api/training",
            "inference": "/api/inference",
            "events": "/api/events",
            "analytics": "/api/analytics",
            "kb": {
                "actors": "/api/kb/actors",
                "locations": "/api/kb/locations",
                "taxonomies": "/api/kb/taxonomies"
            },
            "system": "/api/system",
            "websocket": "/ws/training"
        },
        "documentation": {
            "openapi": "/docs",
            "redoc": "/redoc"
        }
    }


@router.get("/gpu")
async def get_gpu_info():
    """Get GPU information if available."""
    gpu_info = {
        "available": False,
        "device": "cpu",
        "name": None,
        "memory_total_mb": None,
        "memory_used_mb": None,
        "memory_free_mb": None
    }

    try:
        import torch
        if torch.cuda.is_available():
            gpu_info["available"] = True
            gpu_info["device"] = "cuda"
            gpu_info["name"] = torch.cuda.get_device_name(0)
            gpu_info["memory_total_mb"] = round(torch.cuda.get_device_properties(0).total_memory / (1024 * 1024), 2)
            gpu_info["memory_used_mb"] = round(torch.cuda.memory_allocated(0) / (1024 * 1024), 2)
            gpu_info["memory_free_mb"] = gpu_info["memory_total_mb"] - gpu_info["memory_used_mb"]
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            gpu_info["available"] = True
            gpu_info["device"] = "mps"
            gpu_info["name"] = "Apple Silicon GPU"
    except ImportError:
        pass

    return gpu_info


@router.get("/training/status")
async def get_training_service_status(request: Request):
    """Get training service status."""
    training_service = request.app.state.training_service

    if training_service is None:
        return {
            "available": False,
            "running": False,
            "progress": None
        }

    return {
        "available": True,
        "running": training_service.is_running(),
        "progress": training_service.get_progress()
    }
