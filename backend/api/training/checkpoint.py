"""Checkpoints Router - API endpoints for checkpoint management."""

from fastapi import APIRouter, HTTPException
from pathlib import Path
import json
import shutil
import os
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class CheckpointInfo(BaseModel):
    """Checkpoint information model."""
    path: str
    name: str
    model_name: str
    current_epoch: int
    total_epochs: int
    best_epoch: int
    best_val_loss: float
    val_loss: float
    is_complete: bool
    batch_size: int
    learning_rate: float
    num_labels: int
    available_epochs: List[int]
    has_best: bool
    size_mb: float
    modified: str


def get_models_dir() -> Path:
    """Get models directory path."""
    # Check environment variable first (for Docker)
    model_path = os.environ.get('MODEL_PATH', '')
    if model_path:
        # MODEL_PATH points to active model, go up one level for models dir
        return Path(model_path).parent

    # Fallback to relative path for local development
    return Path(__file__).parent.parent.parent / "models"


def get_checkpoint_info(checkpoint_path: Path) -> Optional[CheckpointInfo]:
    """Get detailed information about a checkpoint."""
    config_file = checkpoint_path / 'training_config.json'
    if not config_file.exists():
        return None

    try:
        with open(config_file, 'r') as f:
            config = json.load(f)

        # Calculate size
        total_size = sum(f.stat().st_size for f in checkpoint_path.rglob('*') if f.is_file())

        # Get available epochs
        epochs = []
        for d in checkpoint_path.iterdir():
            if d.is_dir() and d.name.startswith('epoch_'):
                try:
                    epoch_num = int(d.name.split('_')[1])
                    epochs.append(epoch_num)
                except:
                    pass
        epochs.sort()

        has_best = (checkpoint_path / 'best').exists()

        return CheckpointInfo(
            path=str(checkpoint_path),
            name=checkpoint_path.name,
            model_name=config.get('model_name', 'unknown'),
            current_epoch=config.get('epoch', 0) + 1,
            total_epochs=config.get('total_epochs', 0),
            best_epoch=config.get('best_epoch', 0),
            best_val_loss=config.get('best_val_loss', 0),
            val_loss=config.get('val_loss', 0),
            is_complete=config.get('is_complete', False),
            batch_size=config.get('batch_size', 0),
            learning_rate=config.get('learning_rate', 0),
            num_labels=config.get('num_labels', 0),
            available_epochs=epochs,
            has_best=has_best,
            size_mb=total_size / (1024 * 1024),
            modified=datetime.fromtimestamp(checkpoint_path.stat().st_mtime).isoformat(),
        )
    except Exception as e:
        print(f"Error reading checkpoint {checkpoint_path}: {e}")
        return None


@router.get("/")
async def list_checkpoints():
    """List all available checkpoints."""
    models_dir = get_models_dir()

    if not models_dir.exists():
        return {"checkpoints": [], "total": 0}

    checkpoints = []
    for d in models_dir.iterdir():
        if d.is_dir() and (d / 'training_config.json').exists():
            info = get_checkpoint_info(d)
            if info:
                checkpoints.append(info)

    # Sort by modification time (newest first)
    checkpoints.sort(key=lambda x: x.modified, reverse=True)

    return {
        "checkpoints": checkpoints,
        "total": len(checkpoints)
    }


@router.get("/best")
async def get_best_checkpoint():
    """Get the best checkpoint (lowest validation loss)."""
    models_dir = get_models_dir()

    if not models_dir.exists():
        return None

    best_checkpoint = None
    best_loss = float('inf')

    for d in models_dir.iterdir():
        if d.is_dir() and (d / 'training_config.json').exists():
            info = get_checkpoint_info(d)
            if info and info.best_val_loss < best_loss:
                best_loss = info.best_val_loss
                best_checkpoint = info

    return best_checkpoint


@router.get("/{checkpoint_name}")
async def get_checkpoint(checkpoint_name: str):
    """Get details of a specific checkpoint."""
    checkpoint_path = get_models_dir() / checkpoint_name

    if not checkpoint_path.exists():
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    info = get_checkpoint_info(checkpoint_path)
    if not info:
        raise HTTPException(status_code=500, detail="Failed to read checkpoint info")

    return info


@router.delete("/{checkpoint_name}")
async def delete_checkpoint(checkpoint_name: str):
    """Delete a checkpoint."""
    checkpoint_path = get_models_dir() / checkpoint_name

    if not checkpoint_path.exists():
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    try:
        shutil.rmtree(checkpoint_path)
        return {"success": True, "message": f"Deleted {checkpoint_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete: {e}")


@router.get("/{checkpoint_name}/epochs")
async def list_checkpoint_epochs(checkpoint_name: str):
    """List available epochs for a checkpoint."""
    checkpoint_path = get_models_dir() / checkpoint_name

    if not checkpoint_path.exists():
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    epochs = []
    has_best = (checkpoint_path / 'best').exists()

    for d in checkpoint_path.iterdir():
        if d.is_dir() and d.name.startswith('epoch_'):
            try:
                epoch_num = int(d.name.split('_')[1])
                epochs.append({
                    "epoch": epoch_num,
                    "path": str(d),
                    "name": d.name
                })
            except:
                pass

    epochs.sort(key=lambda x: x['epoch'])

    return {
        "checkpoint": checkpoint_name,
        "epochs": epochs,
        "has_best": has_best,
        "best_path": str(checkpoint_path / 'best') if has_best else None
    }


@router.post("/cleanup/incomplete")
async def cleanup_incomplete():
    """Delete all incomplete checkpoints."""
    models_dir = get_models_dir()

    if not models_dir.exists():
        return {"deleted": [], "count": 0}

    deleted = []
    for d in models_dir.iterdir():
        if d.is_dir() and (d / 'training_config.json').exists():
            info = get_checkpoint_info(d)
            if info and not info.is_complete:
                try:
                    shutil.rmtree(d)
                    deleted.append(d.name)
                except:
                    pass

    return {"deleted": deleted, "count": len(deleted)}


@router.get("/compare")
async def compare_checkpoints(checkpoint1: str, checkpoint2: str):
    """Compare two checkpoints."""
    cp1_path = Path(checkpoint1)
    cp2_path = Path(checkpoint2)

    if not cp1_path.exists():
        raise HTTPException(status_code=404, detail=f"Checkpoint not found: {checkpoint1}")
    if not cp2_path.exists():
        raise HTTPException(status_code=404, detail=f"Checkpoint not found: {checkpoint2}")

    info1 = get_checkpoint_info(cp1_path)
    info2 = get_checkpoint_info(cp2_path)

    if not info1 or not info2:
        raise HTTPException(status_code=500, detail="Failed to read checkpoint info")

    return {
        "checkpoint1": info1,
        "checkpoint2": info2,
        "differences": {
            "val_loss": info2.best_val_loss - info1.best_val_loss,
            "val_accuracy": 0,
            "epochs": info2.current_epoch - info1.current_epoch,
        },
        "comparison": {
            "better_loss": info1.name if info1.best_val_loss < info2.best_val_loss else info2.name,
            "loss_difference": abs(info1.best_val_loss - info2.best_val_loss),
            "same_model": info1.model_name == info2.model_name,
        }
    }
