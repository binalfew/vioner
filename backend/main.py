"""
Unified NER System - Main FastAPI Application

This consolidates:
- Week 7-8: Database/Analytics API
- Week 9-10: Training Dashboard API
- Week 11-12: Production Inference API

Author: Binalfew Kassa Mekonnen
Institution: Addis Ababa University
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from config import settings
from database.connection import init_database, check_connection
from services.ner import NERService
from services.training import TrainingService

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown."""
    logger.info("Starting VioNER...")

    # Initialize database
    if settings.enable_db_storage:
        logger.info("Initializing database connection...")
        engine = init_database()
        if engine:
            logger.info("Database connected successfully")
            # Initialize demo user
            from api.auth.router import init_demo_user
            init_demo_user()
        else:
            logger.warning("Database connection failed - continuing without DB")

    # Initialize NER service
    logger.info(f"Loading NER model from: {settings.model_path}")
    ner_service = NERService(
        model_path=str(settings.get_model_path()),
        device=settings.get_device()
    )

    try:
        ner_service.load()
        app.state.ner_service = ner_service
        logger.info("NER model loaded successfully")
    except FileNotFoundError as e:
        logger.warning(f"NER model not found: {e}")
        logger.warning("API will start without inference capability")
        app.state.ner_service = None
    except Exception as e:
        logger.error(f"Failed to load NER model: {e}")
        app.state.ner_service = None

    # Initialize training service
    app.state.training_service = TrainingService()
    logger.info("Training service initialized")

    # Store settings in app state for router access
    app.state.settings = settings

    logger.info("=" * 50)
    logger.info("VioNER started successfully")
    logger.info(f"API: http://{settings.host}:{settings.port}")
    logger.info(f"Docs: http://{settings.host}:{settings.port}/docs")
    logger.info("=" * 50)

    yield

    # Cleanup
    logger.info("Shutting down...")
    if app.state.training_service:
        app.state.training_service.cleanup()


# Create FastAPI application
app = FastAPI(
    title="VioNER",
    description="""
    A comprehensive system for extracting structured information (5W1H) from
    news articles about violent events in Africa.

    ## Features
    - **Training**: Fine-tune BERT models for NER
    - **Inference**: Extract entities from text
    - **Events**: Store and query extracted events
    - **Analytics**: Statistics and trend analysis
    - **Knowledge Base**: Manage actors, locations, taxonomies

    ## 5W1H Entity Types (8 types)
    - **WHO**: ACTOR (perpetrators, organizations, government forces)
    - **WHOM**: VICTIM
    - **WHAT**: ACTION
    - **WHEN**: DATE
    - **WHERE**: REGION, CITY, DISTRICT
    - **HOW**: CASUALTIES

    Note: Event type classification (taxonomy) is handled as a post-NER task.
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc) if settings.debug else "Internal server error",
            "type": type(exc).__name__
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """API information and available endpoints."""
    return {
        "name": "VioNER",
        "version": "1.0.0",
        "description": "Unified API for NER training, inference, and event management",
        "endpoints": {
            "training": "/api/training/*",
            "inference": "/api/inference/*",
            "events": "/api/events/*",
            "analytics": "/api/analytics/*",
            "knowledge_base": "/api/kb/*",
            "history": "/api/history/*",
            "system": "/api/system/*"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }


# Health check endpoint
@app.get("/health")
async def health_check(request: Request):
    """Health check with service status."""
    ner_loaded = (
        request.app.state.ner_service is not None
        and request.app.state.ner_service.is_loaded()
    )
    db_connected = check_connection() if settings.enable_db_storage else None
    training_running = (
        request.app.state.training_service is not None
        and request.app.state.training_service.is_running()
    )

    status = "healthy" if ner_loaded else "degraded"

    return {
        "status": status,
        "services": {
            "ner_model": "loaded" if ner_loaded else "not_loaded",
            "database": "connected" if db_connected else ("disabled" if db_connected is None else "disconnected"),
            "training": "running" if training_running else "idle"
        },
        "config": {
            "model_path": settings.model_path,
            "device": settings.get_device(),
            "db_enabled": settings.enable_db_storage
        }
    }


# Import and register routers
from api.auth.router import router as auth_router
from api.training.router import router as training_router
from api.training.checkpoint import router as checkpoints_router
from api.training.data import router as training_data_router
from api.training.evaluation import router as evaluation_router
from api.inference.router import router as inference_router
from api.events.router import router as events_router
from api.analytics.router import router as analytics_router
from api.kb.actors import router as actors_router
from api.kb.locations import router as locations_router
from api.kb.taxonomies import router as taxonomies_router
from api.system.router import router as system_router
from api.history.router import router as history_router

# Auth endpoints
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])

# Training endpoints
app.include_router(training_router, prefix="/api/training", tags=["Training"])
app.include_router(checkpoints_router, prefix="/api/training/checkpoints", tags=["Checkpoints"])
app.include_router(training_data_router, prefix="/api/training", tags=["Training Data"])
app.include_router(evaluation_router, prefix="/api/training", tags=["Evaluation"])

# Inference endpoints
app.include_router(inference_router, prefix="/api/inference", tags=["Inference"])

# Events endpoints
app.include_router(events_router, prefix="/api/events", tags=["Events"])

# Analytics endpoints
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])

# Knowledge base endpoints
app.include_router(actors_router, prefix="/api/kb/actors", tags=["Knowledge Base - Actors"])
app.include_router(locations_router, prefix="/api/kb/locations", tags=["Knowledge Base - Locations"])
app.include_router(taxonomies_router, prefix="/api/kb/taxonomies", tags=["Knowledge Base - Taxonomies"])

# System endpoints
app.include_router(system_router, prefix="/api/system", tags=["System"])

# History endpoints
app.include_router(history_router, prefix="/api/history", tags=["History"])


# WebSocket for training progress
from api.websocket import router as websocket_router
app.include_router(websocket_router, prefix="/ws/training", tags=["WebSocket"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
