"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List
from pathlib import Path
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = Field(default="VioNER")
    debug: bool = Field(default=False)

    # Database
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/violent_events"
    )
    enable_db_storage: bool = Field(default=True)

    # Model (paths relative to backend folder)
    model_path: str = Field(default="./models/active")
    device: str = Field(default="auto")  # auto, cpu, cuda, mps
    max_sequence_length: int = Field(default=512)
    max_batch_size: int = Field(default=100)

    # Training (data is at project root, models inside backend)
    train_data_path: str = Field(default="../data/processed/train.json")
    val_data_path: str = Field(default="../data/processed/val.json")
    models_output_dir: str = Field(default="./models")

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    cors_origins: str = Field(default="http://localhost:3000,http://localhost:5173")

    # WebSocket
    ws_heartbeat_interval: int = Field(default=30)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]

    def get_model_path(self) -> Path:
        """Get resolved model path, checking database for active model first."""
        # Try to get active model from database
        if self.enable_db_storage:
            db_path = self._get_active_model_from_db()
            if db_path:
                return db_path

        # Fallback to configured path
        path = Path(self.model_path)
        if path.is_absolute():
            return path
        # Relative to backend folder (where config.py is)
        return Path(__file__).parent / self.model_path

    def _get_active_model_from_db(self) -> Optional[Path]:
        """Query database for active model checkpoint path."""
        try:
            from database.connection import get_db_context
            from database.models import TrainingDB

            with get_db_context() as db:
                if db is None:
                    return None

                active = db.query(TrainingDB).filter(TrainingDB.is_active == True).first()
                if active and active.checkpoint_path:
                    checkpoint_path = Path(active.checkpoint_path)
                    # Model files are in 'best/' subdirectory, not checkpoint root
                    best_path = checkpoint_path / 'best'
                    if best_path.exists() and (best_path / 'config.json').exists():
                        return best_path
                    # Fallback to checkpoint root if it has config.json
                    if checkpoint_path.exists() and (checkpoint_path / 'config.json').exists():
                        return checkpoint_path
        except Exception:
            pass  # Fall back to configured path
        return None

    def get_device(self) -> str:
        """Get compute device with auto-detection."""
        if self.device != "auto":
            return self.device

        # Auto-detect device
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"
        except ImportError:
            pass

        return "cpu"


# Global settings instance
settings = Settings()
