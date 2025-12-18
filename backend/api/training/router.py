"""Training API Router - Manages ML training operations."""

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from pathlib import Path
from datetime import datetime
import json
import os
import logging

from services.training import TrainingConfig

router = APIRouter()
logger = logging.getLogger(__name__)


class TrainingConfigRequest(BaseModel):
    """Training configuration request model."""
    model_name: str = Field(default="bert-base-cased", description="Pretrained model name")
    epochs: int = Field(default=10, ge=1, le=100, description="Total epochs")
    batch_size: int = Field(default=4, ge=1, le=128, description="Batch size (default 4 for CPU training)")
    learning_rate: float = Field(default=2e-5, gt=0, description="Learning rate")
    train_file: Optional[str] = Field(default=None, description="Training data file path")
    val_file: Optional[str] = Field(default=None, description="Validation data file path")
    output_dir: Optional[str] = Field(default=None, description="Output directory for checkpoints")
    run_epochs: Optional[int] = Field(default=None, ge=1, description="Run only N epochs this session")
    checkpoint_path: Optional[str] = Field(default=None, description="Checkpoint path for resume")
    extend_epochs: int = Field(default=0, ge=0, description="Extend training by N epochs")


class TrainingResponse(BaseModel):
    """Training operation response."""
    success: bool
    message: str
    status: Optional[str] = None
    session_id: Optional[str] = None
    log_file: Optional[str] = None


def get_default_paths():
    """Get default data paths."""
    # Check if running in Docker (paths are at /app/)
    if Path('/app/data').exists():
        # Docker environment
        return {
            'train_file': '/app/data/processed/train.json',
            'val_file': '/app/data/processed/val.json',
            'output_dir': '/app/models',
        }
    else:
        # Local development paths
        # backend_dir: api/training -> api -> backend
        backend_dir = Path(__file__).parent.parent.parent
        # project_root: backend -> named-entity-recognition
        project_root = backend_dir.parent
        return {
            'train_file': str(project_root / 'data' / 'processed' / 'train.json'),
            'val_file': str(project_root / 'data' / 'processed' / 'val.json'),
            'output_dir': str(backend_dir / 'models'),
        }


@router.get("/status")
async def get_training_status(request: Request):
    """Get current training status and progress."""
    service = request.app.state.training_service
    return service.get_progress()


@router.get("/logs")
async def get_training_logs(request: Request, limit: int = 100):
    """Get training logs."""
    service = request.app.state.training_service
    return {"logs": service.get_logs(limit)}


@router.delete("/logs")
async def clear_training_logs(request: Request):
    """Clear training logs."""
    service = request.app.state.training_service
    service.clear_logs()
    return {"success": True, "message": "Logs cleared"}


@router.get("/logs/files")
async def list_log_files(request: Request):
    """
    List all available training log files.

    Returns list of log files with session_id, path, size, and modified time.
    """
    from services.training import TrainingService
    return {
        "log_files": TrainingService.list_log_files(),
        "current_session": request.app.state.training_service.get_session_id(),
        "current_log_file": request.app.state.training_service.get_log_file_path(),
    }


@router.get("/logs/file/{session_id}")
async def get_log_file(request: Request, session_id: str):
    """
    Get contents of a specific training log file.

    Args:
        session_id: The session ID to get logs for (e.g., bert-base-cased_20251213_143045)
    """
    service = request.app.state.training_service
    contents = service.get_log_file_contents(session_id)

    if contents is None:
        raise HTTPException(status_code=404, detail=f"Log file not found for session: {session_id}")

    return {
        "session_id": session_id,
        "contents": contents,
    }


@router.get("/logs/current")
async def get_current_log_file(request: Request):
    """
    Get contents of the current training session's log file.
    """
    service = request.app.state.training_service
    session_id = service.get_session_id()

    if not session_id:
        return {
            "session_id": None,
            "contents": None,
            "message": "No active training session"
        }

    contents = service.get_log_file_contents()

    return {
        "session_id": session_id,
        "log_file": service.get_log_file_path(),
        "contents": contents,
    }


@router.post("/start", response_model=TrainingResponse)
async def start_training(request: Request, config: TrainingConfigRequest):
    """Start a new training run."""
    service = request.app.state.training_service

    if service.is_running():
        raise HTTPException(status_code=400, detail="Training already in progress")

    # Set default paths if not provided
    defaults = get_default_paths()
    train_file = config.train_file or defaults['train_file']
    val_file = config.val_file or defaults['val_file']
    output_dir = config.output_dir or defaults['output_dir']

    # Validate files exist
    if not Path(train_file).exists():
        raise HTTPException(status_code=400, detail=f"Training file not found: {train_file}")
    if not Path(val_file).exists():
        raise HTTPException(status_code=400, detail=f"Validation file not found: {val_file}")

    training_config = TrainingConfig(
        model_name=config.model_name,
        epochs=config.epochs,
        batch_size=config.batch_size,
        learning_rate=config.learning_rate,
        train_file=train_file,
        val_file=val_file,
        output_dir=output_dir,
        run_epochs=config.run_epochs,
    )

    success = service.start_training(training_config)

    if success:
        return TrainingResponse(
            success=True,
            message="Training started",
            status="running",
            session_id=service.get_session_id(),
            log_file=service.get_log_file_path()
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to start training")


@router.post("/resume", response_model=TrainingResponse)
async def resume_training(request: Request, config: TrainingConfigRequest):
    """Resume training from checkpoint."""
    service = request.app.state.training_service

    if service.is_running():
        raise HTTPException(status_code=400, detail="Training already in progress")

    if not config.checkpoint_path:
        raise HTTPException(status_code=400, detail="Checkpoint path required for resume")

    if not Path(config.checkpoint_path).exists():
        raise HTTPException(status_code=400, detail=f"Checkpoint not found: {config.checkpoint_path}")

    defaults = get_default_paths()

    training_config = TrainingConfig(
        model_name=config.model_name,
        epochs=config.epochs,
        batch_size=config.batch_size,
        learning_rate=config.learning_rate,
        train_file=config.train_file or defaults['train_file'],
        val_file=config.val_file or defaults['val_file'],
        output_dir=config.output_dir or defaults['output_dir'],
        run_epochs=config.run_epochs,
        checkpoint_path=config.checkpoint_path,
        extend_epochs=config.extend_epochs,
    )

    success = service.resume_training(training_config)

    if success:
        return TrainingResponse(
            success=True,
            message="Training resumed",
            status="running",
            session_id=service.get_session_id(),
            log_file=service.get_log_file_path()
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to resume training")


@router.post("/stop", response_model=TrainingResponse)
async def stop_training(request: Request):
    """Stop current training."""
    service = request.app.state.training_service

    if not service.is_running():
        raise HTTPException(status_code=400, detail="No training in progress")

    success = service.stop_training()

    if success:
        return TrainingResponse(
            success=True,
            message="Training stopped",
            status="stopped",
            session_id=service.get_session_id(),
            log_file=service.get_log_file_path()
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to stop training")


@router.get("/models")
async def get_available_models():
    """Get list of available pre-trained models."""
    return {
        "models": [
            {"id": "bert-base-cased", "name": "BERT Base (Cased)", "params": "110M"},
            {"id": "bert-base-uncased", "name": "BERT Base (Uncased)", "params": "110M"},
            {"id": "bert-large-cased", "name": "BERT Large (Cased)", "params": "340M"},
            {"id": "distilbert-base-cased", "name": "DistilBERT (Cased)", "params": "66M"},
            {"id": "distilbert-base-uncased", "name": "DistilBERT (Uncased)", "params": "66M"},
            {"id": "roberta-base", "name": "RoBERTa Base", "params": "125M"},
            {"id": "xlm-roberta-base", "name": "XLM-RoBERTa Base", "params": "270M"},
        ]
    }


@router.get("/defaults")
async def get_default_config():
    """Get default training configuration."""
    defaults = get_default_paths()
    return {
        "model_name": "bert-base-cased",
        "epochs": 10,
        "batch_size": 16,
        "learning_rate": 2e-5,
        **defaults,
        "files_exist": {
            "train": Path(defaults['train_file']).exists(),
            "val": Path(defaults['val_file']).exists(),
        }
    }


# ============================================================
# Model Management Endpoints - Trainings Database Integration
# ============================================================

class TrainingRunResponse(BaseModel):
    """Training run from database."""
    id: int
    session_id: str
    model_name: str
    status: str
    epochs_total: Optional[int]
    epochs_completed: Optional[int]
    best_epoch: Optional[int]
    best_val_loss: Optional[float]
    best_val_accuracy: Optional[float]
    checkpoint_path: Optional[str]
    is_active: bool
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    notes: Optional[str]


class TrainingListResponse(BaseModel):
    """Response for training list with recommendation."""
    trainings: List[TrainingRunResponse]
    recommended_id: Optional[int]
    recommended_reason: Optional[str]
    active_id: Optional[int]


class ActivateModelRequest(BaseModel):
    """Request to activate a model."""
    training_id: int


class SyncResult(BaseModel):
    """Result of syncing models folder."""
    synced: int
    updated: int
    message: str


def get_models_dir() -> Path:
    """Get models directory path."""
    # In Docker, models are at /app/models
    docker_path = Path('/app/models')
    if docker_path.exists():
        return docker_path

    # Locally, models are at backend/models
    return Path(__file__).parent.parent.parent / 'models'


def parse_session_id_timestamp(session_id: str) -> Optional[datetime]:
    """Parse timestamp from session_id like bert-base-cased_20251209_022143."""
    try:
        parts = session_id.rsplit('_', 2)
        if len(parts) >= 3:
            date_str = parts[-2]
            time_str = parts[-1]
            return datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
    except:
        pass
    return None


@router.post("/sync-models", response_model=SyncResult)
async def sync_models_from_folder(request: Request):
    """
    Scan the models folder and sync training runs to the database.
    Creates new entries for untracked models and updates existing ones.
    """
    from database.connection import get_db_context
    from database.models import TrainingDB

    models_dir = get_models_dir()
    if not models_dir.exists():
        raise HTTPException(status_code=404, detail=f"Models directory not found: {models_dir}")

    synced = 0
    updated = 0

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        # Scan each folder in models directory
        for item in models_dir.iterdir():
            if not item.is_dir() or item.name in ['active', '.gitkeep']:
                continue

            config_file = item / 'training_config.json'
            if not config_file.exists():
                continue

            # Read training config
            try:
                with open(config_file) as f:
                    config = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to read {config_file}: {e}")
                continue

            session_id = item.name
            best_folder = item / 'best'

            # Check if already exists in database
            existing = db.query(TrainingDB).filter(TrainingDB.session_id == session_id).first()

            # epoch in config is 0-indexed, so add 1 for display
            epochs_completed = config.get('epoch', 0) + 1
            # best_epoch is already 1-indexed in training.py (saved as epoch + 1)
            best_epoch = config.get('best_epoch')

            if existing:
                # Update existing record
                existing.epochs_total = config.get('total_epochs')
                existing.epochs_completed = epochs_completed
                existing.best_epoch = best_epoch
                existing.best_val_loss = config.get('best_val_loss')
                existing.batch_size = config.get('batch_size')
                existing.learning_rate = config.get('learning_rate')
                existing.status = 'completed' if config.get('is_complete') else 'stopped'
                # Store the root checkpoint directory (not best/ subfolder) for resume capability
                existing.checkpoint_path = str(item) if config_file.exists() else None
                existing.updated_at = datetime.utcnow()
                updated += 1
            else:
                # Create new record
                started_at = parse_session_id_timestamp(session_id) or datetime.utcnow()

                training = TrainingDB(
                    session_id=session_id,
                    model_name=config.get('model_name', 'unknown'),
                    status='completed' if config.get('is_complete') else 'stopped',
                    epochs_total=config.get('total_epochs'),
                    epochs_completed=epochs_completed,
                    batch_size=config.get('batch_size'),
                    learning_rate=config.get('learning_rate'),
                    best_epoch=best_epoch,
                    best_val_loss=config.get('best_val_loss'),
                    # Store the root checkpoint directory (not best/ subfolder) for resume capability
                    checkpoint_path=str(item) if config_file.exists() else None,
                    config_json=config,
                    started_at=started_at,
                    completed_at=started_at if config.get('is_complete') else None,
                    is_active=False
                )
                db.add(training)
                synced += 1

        db.commit()

    return SyncResult(
        synced=synced,
        updated=updated,
        message=f"Synced {synced} new training(s), updated {updated} existing"
    )


@router.get("/runs", response_model=TrainingListResponse)
async def list_training_runs(request: Request):
    """
    List all training runs from database with recommendation for best model.

    The recommendation considers:
    1. Completed trainings are preferred over incomplete ones
    2. Lower validation loss is better
    3. More epochs completed is a tiebreaker
    """
    from database.connection import get_db_context
    from database.models import TrainingDB

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        trainings = db.query(TrainingDB).order_by(TrainingDB.started_at.desc()).all()

        if not trainings:
            return TrainingListResponse(
                trainings=[],
                recommended_id=None,
                recommended_reason=None,
                active_id=None
            )

        # Convert to response models
        training_list = []
        active_id = None
        for t in trainings:
            training_list.append(TrainingRunResponse(
                id=t.id,
                session_id=t.session_id,
                model_name=t.model_name,
                status=t.status,
                epochs_total=t.epochs_total,
                epochs_completed=t.epochs_completed,
                best_epoch=t.best_epoch,
                best_val_loss=float(t.best_val_loss) if t.best_val_loss else None,
                best_val_accuracy=float(t.best_val_accuracy) if t.best_val_accuracy else None,
                checkpoint_path=t.checkpoint_path,
                is_active=t.is_active,
                started_at=t.started_at,
                completed_at=t.completed_at,
                notes=t.notes
            ))
            if t.is_active:
                active_id = t.id

        # Calculate recommendation
        recommended_id, recommended_reason = calculate_recommendation(trainings)

        return TrainingListResponse(
            trainings=training_list,
            recommended_id=recommended_id,
            recommended_reason=recommended_reason,
            active_id=active_id
        )


def calculate_recommendation(trainings) -> tuple:
    """
    Calculate the recommended model based on metrics.

    Priority:
    1. Lowest best_val_loss wins (regardless of completion status)
    2. If val_loss is within 5%, prefer completed over incomplete
    3. If tied, prefer more epochs completed
    """
    if not trainings:
        return None, None

    # Filter trainings with valid loss
    with_loss = [t for t in trainings if t.best_val_loss is not None]

    if not with_loss:
        # No training with valid loss
        if trainings:
            return trainings[0].id, "Only available training (no validation metrics)"
        return None, None

    # Find the absolute best by validation loss
    best_by_loss = min(with_loss, key=lambda t: float(t.best_val_loss))
    best_loss = float(best_by_loss.best_val_loss)

    # Check if there's a completed training within 5% of the best
    completed_within_threshold = [
        t for t in with_loss
        if t.status == 'completed' and float(t.best_val_loss) <= best_loss * 1.05
    ]

    if completed_within_threshold and best_by_loss.status != 'completed':
        # Prefer completed if it's within 5% of the best
        best_completed = min(completed_within_threshold, key=lambda t: float(t.best_val_loss))
        return best_completed.id, f"Completed training with validation loss ({float(best_completed.best_val_loss):.6f})"

    # Otherwise, recommend the one with absolute best validation loss
    status_note = "" if best_by_loss.status == 'completed' else " (training incomplete)"
    return best_by_loss.id, f"Lowest validation loss ({best_loss:.6f}){status_note}"


@router.post("/activate", response_model=TrainingResponse)
async def activate_model(request: Request, body: ActivateModelRequest):
    """
    Activate a specific training model.

    This will:
    1. Deactivate any currently active model
    2. Set the specified training as active
    3. Update the 'active' symlink in the models folder
    """
    from database.connection import get_db_context
    from database.models import TrainingDB

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        # Find the training to activate
        training = db.query(TrainingDB).filter(TrainingDB.id == body.training_id).first()
        if not training:
            raise HTTPException(status_code=404, detail=f"Training not found: {body.training_id}")

        if not training.checkpoint_path or not Path(training.checkpoint_path).exists():
            raise HTTPException(
                status_code=400,
                detail=f"Checkpoint path not found: {training.checkpoint_path}"
            )

        # The checkpoint_path points to root directory, but we need the best/ subfolder for inference
        best_model_path = Path(training.checkpoint_path) / 'best'
        if not best_model_path.exists():
            raise HTTPException(
                status_code=400,
                detail=f"Best model not found: {best_model_path}"
            )

        # Deactivate all other trainings
        db.query(TrainingDB).filter(TrainingDB.is_active == True).update({'is_active': False})

        # Activate the selected training
        training.is_active = True
        db.commit()

        # Update the symlink
        models_dir = get_models_dir()
        active_link = models_dir / 'active'

        try:
            # Remove existing symlink if exists
            if active_link.is_symlink():
                active_link.unlink()
            elif active_link.exists():
                import shutil
                shutil.rmtree(active_link)

            # Create new symlink - point to best/ subfolder for inference
            # Make relative path for symlink
            relative_path = best_model_path.relative_to(models_dir)
            os.symlink(str(relative_path), str(active_link))

            logger.info(f"Activated model: {training.session_id} -> {relative_path}")
        except Exception as e:
            logger.error(f"Failed to update symlink: {e}")
            # Don't fail the request, database is updated

        return TrainingResponse(
            success=True,
            message=f"Activated model: {training.session_id}",
            status="active"
        )


@router.get("/active")
async def get_active_model(request: Request):
    """Get the currently active model."""
    from database.connection import get_db_context
    from database.models import TrainingDB

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        active = db.query(TrainingDB).filter(TrainingDB.is_active == True).first()

        if not active:
            # Check if symlink exists
            models_dir = get_models_dir()
            active_link = models_dir / 'active'

            return {
                "active_training": None,
                "symlink_target": str(os.readlink(active_link)) if active_link.is_symlink() else None,
                "message": "No active model in database. Use /api/training/sync-models to sync and then activate."
            }

        return {
            "active_training": TrainingRunResponse(
                id=active.id,
                session_id=active.session_id,
                model_name=active.model_name,
                status=active.status,
                epochs_total=active.epochs_total,
                epochs_completed=active.epochs_completed,
                best_epoch=active.best_epoch,
                best_val_loss=float(active.best_val_loss) if active.best_val_loss else None,
                best_val_accuracy=float(active.best_val_accuracy) if active.best_val_accuracy else None,
                checkpoint_path=active.checkpoint_path,
                is_active=active.is_active,
                started_at=active.started_at,
                completed_at=active.completed_at,
                notes=active.notes
            ),
            "message": "Active model found"
        }
