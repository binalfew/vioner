"""Path utilities for model resolution.

This module provides environment-agnostic path resolution for models.
Paths are resolved at runtime based on the current environment (Docker vs local).
"""

from pathlib import Path
import os
import logging

logger = logging.getLogger(__name__)


def get_models_dir() -> Path:
    """
    Get the models directory for the current environment.

    Returns:
        Path to models directory:
        - Docker: /app/models (via MODEL_PATH env var)
        - Local: <backend>/models
    """
    # Check environment variable first (for Docker)
    model_path = os.environ.get('MODEL_PATH', '')
    if model_path:
        # MODEL_PATH points to active model, go up one level for models dir
        return Path(model_path).parent

    # Fallback to relative path for local development
    return Path(__file__).parent.parent / "models"


def resolve_model_path(session_id: str, subfolder: str = 'best') -> Path:
    """
    Resolve a session_id to a full model path.

    Args:
        session_id: Model session identifier (e.g., 'bert-base-cased_20251209_212123')
        subfolder: Subfolder within the checkpoint ('best', 'epoch_01', etc.)

    Returns:
        Full path to the model directory

    Example:
        >>> resolve_model_path('bert-base-cased_20251209_212123', 'best')
        PosixPath('/app/models/bert-base-cased_20251209_212123/best')  # Docker
        PosixPath('/Users/.../backend/models/bert-base-cased_20251209_212123/best')  # Local
    """
    models_dir = get_models_dir()
    return models_dir / session_id / subfolder


def extract_session_id(path: str) -> str:
    """
    Extract session_id from a full path or return as-is if already a session_id.

    Handles various path formats:
    - /app/models/bert-base-cased_xxx/best -> bert-base-cased_xxx
    - /Users/.../models/bert-base-cased_xxx/best -> bert-base-cased_xxx
    - bert-base-cased_xxx -> bert-base-cased_xxx (already a session_id)

    Args:
        path: Full path or session_id

    Returns:
        The session_id (checkpoint name)
    """
    # If it's just a session_id (no slashes or only has /best suffix)
    if '/' not in path:
        return path

    path_parts = path.rstrip('/').split('/')

    # Find the session_id part (starts with 'bert-' typically)
    for i, part in enumerate(path_parts):
        if part.startswith('bert-') or part.startswith('roberta-') or part.startswith('distilbert-'):
            return part

    # Fallback: return the parent of 'best' or 'epoch_xx'
    for i, part in enumerate(path_parts):
        if part == 'best' or part.startswith('epoch_'):
            if i > 0:
                return path_parts[i - 1]

    # Last resort: return the second to last part (assuming /models/session_id/best structure)
    if len(path_parts) >= 2:
        return path_parts[-2] if path_parts[-1] in ['best'] or path_parts[-1].startswith('epoch_') else path_parts[-1]

    return path
