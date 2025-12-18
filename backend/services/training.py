"""
Training Service
Manages background training processes with real-time progress tracking
"""

import subprocess
import threading
import time
import os
import signal
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum


def get_console_dir() -> Path:
    """Get the console directory for training logs."""
    console_dir = Path(__file__).parent.parent / 'console'
    console_dir.mkdir(parents=True, exist_ok=True)
    return console_dir


class TrainingStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


@dataclass
class TrainingConfig:
    """Training configuration."""
    model_name: str = "bert-base-cased"
    epochs: int = 10
    batch_size: int = 16
    learning_rate: float = 2e-5
    train_file: str = ""
    val_file: str = ""
    output_dir: str = ""
    run_epochs: Optional[int] = None
    checkpoint_path: Optional[str] = None
    extend_epochs: int = 0


@dataclass
class TrainingProgress:
    """Training progress data."""
    status: TrainingStatus = TrainingStatus.IDLE
    current_epoch: int = 0
    total_epochs: int = 0
    current_batch: int = 0
    total_batches: int = 0
    train_loss: float = 0.0
    val_loss: float = 0.0
    val_accuracy: float = 0.0
    best_epoch: int = 0
    best_val_loss: float = float('inf')
    elapsed_time: float = 0.0
    eta: float = 0.0
    samples_per_second: float = 0.0
    model_name: str = ""
    train_samples: int = 0
    val_samples: int = 0
    history: Dict[str, List] = None

    def __post_init__(self):
        if self.history is None:
            self.history = {
                'epochs': [],
                'train_loss': [],
                'val_loss': [],
                'val_accuracy': []
            }

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['status'] = self.status.value
        # Handle infinity for JSON serialization
        if data['best_val_loss'] == float('inf'):
            data['best_val_loss'] = None
        return data


class TrainingService:
    """Service for managing model training."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.process: Optional[subprocess.Popen] = None
        self.progress = TrainingProgress()
        self.logs: List[str] = []
        self.subscribers: List[Callable] = []
        self._stop_flag = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._start_time: float = 0
        # Default to backend directory (where models and pipeline are)
        self._base_dir = base_dir or Path(__file__).parent.parent
        # Log file for persistent logging
        self._log_file: Optional[Path] = None
        self._session_id: Optional[str] = None
        # Pre-resume state for rollback on cancel
        self._pre_resume_config: Optional[Dict] = None
        self._pre_resume_checkpoint_path: Optional[str] = None
        self._is_resume_session: bool = False

    def get_log_file_path(self) -> Optional[str]:
        """Get the current log file path."""
        return str(self._log_file) if self._log_file else None

    def get_session_id(self) -> Optional[str]:
        """Get the current session ID."""
        return self._session_id

    def get_log_file_contents(self, session_id: Optional[str] = None) -> Optional[str]:
        """
        Read contents of a log file.

        Args:
            session_id: Session ID to get logs for. If None, uses current session.

        Returns:
            Log file contents or None if not found.
        """
        if session_id:
            log_file = get_console_dir() / f"training_{session_id}.log"
        else:
            log_file = self._log_file

        if log_file and log_file.exists():
            return log_file.read_text()
        return None

    @staticmethod
    def list_log_files() -> List[Dict]:
        """
        List all available training log files.

        Returns:
            List of dicts with session_id, path, size, and modified time.
        """
        console_dir = get_console_dir()
        logs = []

        for log_file in console_dir.glob("training_*.log"):
            # Extract session ID from filename
            session_id = log_file.stem.replace("training_", "")
            stat = log_file.stat()

            logs.append({
                "session_id": session_id,
                "path": str(log_file),
                "size_kb": round(stat.st_size / 1024, 2),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })

        # Sort by modified time (newest first)
        logs.sort(key=lambda x: x["modified"], reverse=True)
        return logs

    def _generate_session_id(self, model_name: str) -> str:
        """Generate a unique session ID based on model name and timestamp."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        clean_model_name = model_name.replace('/', '_')
        return f"{clean_model_name}_{timestamp}"

    def _write_log_header(self, config: 'TrainingConfig', resume: bool = False):
        """Write header to the log file."""
        if not self._log_file:
            return

        header = f"""
================================================================================
RUN: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
SESSION: {self._session_id}
SOURCE: Web Dashboard API
MODE: {'RESUME' if resume else 'NEW'}
================================================================================
"""
        with open(self._log_file, 'a') as f:
            f.write(header)

    def _write_log_footer(self, success: bool):
        """Write footer to the log file."""
        if not self._log_file:
            return

        status = "SUCCESS" if success else "STOPPED/FAILED"
        footer = f"""
--------------------------------------------------------------------------------
COMPLETED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Exit code: {0 if success else 1} - {status})
--------------------------------------------------------------------------------
"""
        with open(self._log_file, 'a') as f:
            f.write(footer)

    def is_running(self) -> bool:
        """Check if training is currently running."""
        return self.progress.status == TrainingStatus.RUNNING

    def get_progress(self) -> Dict:
        """Get current training progress."""
        return self.progress.to_dict()

    def get_logs(self, limit: int = 100) -> List[str]:
        """Get training logs."""
        return self.logs[-limit:]

    def clear_logs(self):
        """Clear training logs."""
        self.logs = []

    def subscribe(self, callback: Callable):
        """Subscribe to progress updates."""
        self.subscribers.append(callback)

    def unsubscribe(self, callback: Callable):
        """Unsubscribe from progress updates."""
        if callback in self.subscribers:
            self.subscribers.remove(callback)

    def _notify_subscribers(self):
        """Notify all subscribers of progress update."""
        data = self.get_progress()
        for callback in self.subscribers:
            try:
                callback(data)
            except Exception as e:
                print(f"Error notifying subscriber: {e}")

    def start_training(self, config: TrainingConfig) -> bool:
        """Start a new training run."""
        if self.is_running():
            return False

        # Generate session ID and log file path
        self._session_id = self._generate_session_id(config.model_name)
        self._log_file = get_console_dir() / f"training_{self._session_id}.log"

        # Reset state
        self.progress = TrainingProgress(
            status=TrainingStatus.RUNNING,
            total_epochs=config.epochs,
            model_name=config.model_name
        )
        self.logs = []
        self._stop_flag = False
        self._start_time = time.time()
        # Clear resume state (this is a fresh start)
        self._pre_resume_config = None
        self._pre_resume_checkpoint_path = None
        self._is_resume_session = False

        # Write header to log file
        self._write_log_header(config, resume=False)

        # Build command with log file
        cmd = self._build_command(config)
        self._add_log(f"Starting training: {' '.join(cmd)}")
        self._add_log(f"Session ID: {self._session_id}")
        self._add_log(f"Log file: {self._log_file}")
        self._add_log(f"Model: {config.model_name}")
        self._add_log(f"Epochs: {config.epochs}")
        self._add_log(f"Batch Size: {config.batch_size}")
        self._add_log("-" * 50)

        # Start subprocess
        self._run_subprocess(cmd)
        return True

    def resume_training(self, config: TrainingConfig) -> bool:
        """Resume training from checkpoint."""
        if self.is_running():
            return False

        if not config.checkpoint_path:
            self._add_log("Error: No checkpoint path provided")
            return False

        # Save pre-resume state for rollback on cancel
        self._is_resume_session = True
        self._pre_resume_checkpoint_path = config.checkpoint_path
        config_file = Path(config.checkpoint_path) / 'training_config.json'
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    self._pre_resume_config = json.load(f)
                self._add_log(f"Saved pre-resume state for rollback")
            except Exception as e:
                self._add_log(f"Warning: Could not save pre-resume state: {e}")
                self._pre_resume_config = None
        else:
            self._pre_resume_config = None

        # Extract session ID from checkpoint path or generate new one
        checkpoint_name = Path(config.checkpoint_path).name
        if checkpoint_name and '_' in checkpoint_name:
            self._session_id = checkpoint_name
        else:
            self._session_id = self._generate_session_id(config.model_name)

        # Use existing log file or create new one
        self._log_file = get_console_dir() / f"training_{self._session_id}.log"

        # Reset state
        self.progress = TrainingProgress(
            status=TrainingStatus.RUNNING,
            total_epochs=config.epochs,
            model_name=config.model_name
        )
        self.logs = []
        self._stop_flag = False
        self._start_time = time.time()

        # Write header to log file
        self._write_log_header(config, resume=True)

        # Build resume command
        cmd = self._build_command(config, resume=True)
        self._add_log(f"Resuming from: {config.checkpoint_path}")
        self._add_log(f"Session ID: {self._session_id}")
        self._add_log(f"Log file: {self._log_file}")
        self._add_log("-" * 50)

        self._run_subprocess(cmd)
        return True

    def stop_training(self) -> bool:
        """Stop the current training."""
        if not self.is_running():
            return False

        self._stop_flag = True
        self._add_log("Stopping training...")

        if self.process:
            try:
                os.kill(self.process.pid, signal.SIGINT)
                time.sleep(2)
                if self.process.poll() is None:
                    self.process.terminate()
                    time.sleep(1)
                    if self.process.poll() is None:
                        self.process.kill()
            except Exception as e:
                self._add_log(f"Error stopping process: {e}")

        # Restore pre-resume config if this was a resume session
        self._add_log(f"DEBUG: _is_resume_session={self._is_resume_session}, has_pre_config={self._pre_resume_config is not None}, has_checkpoint={self._pre_resume_checkpoint_path is not None}")
        if self._is_resume_session and self._pre_resume_config and self._pre_resume_checkpoint_path:
            self._restore_pre_resume_state()
            self._add_log(f"Progress reset to: {self.progress.current_epoch}/{self.progress.total_epochs}")
        else:
            # For fresh training, reset progress to idle state
            self._add_log("DEBUG: Calling _reset_progress()")
            self._reset_progress()
            self._add_log(f"DEBUG: After reset - epoch={self.progress.current_epoch}, total={self.progress.total_epochs}")

        self.progress.status = TrainingStatus.STOPPED
        self._add_log(f"DEBUG: Final status={self.progress.status}, epoch={self.progress.current_epoch}/{self.progress.total_epochs}")
        self._add_log("Training stopped by user")
        # Notify subscribers with the updated (restored) progress
        self._notify_subscribers()
        # Send another notification after a brief delay to ensure frontend receives it
        def delayed_notify():
            time.sleep(0.5)
            self._notify_subscribers()
        threading.Thread(target=delayed_notify, daemon=True).start()
        return True

    def _reset_progress(self):
        """Reset progress to idle defaults."""
        self.progress = TrainingProgress(
            status=TrainingStatus.IDLE,
            current_epoch=0,
            total_epochs=0,
            current_batch=0,
            total_batches=0,
            train_loss=0.0,
            val_loss=0.0,
            val_accuracy=0.0,
            best_epoch=0,
            best_val_loss=float('inf'),
            model_name='',
        )

    def _restore_pre_resume_state(self):
        """Restore the training_config.json to its pre-resume state."""
        if not self._pre_resume_config or not self._pre_resume_checkpoint_path:
            return

        config_file = Path(self._pre_resume_checkpoint_path) / 'training_config.json'
        try:
            with open(config_file, 'w') as f:
                json.dump(self._pre_resume_config, f, indent=2)

            # Also reset the in-memory progress to match restored state
            restored_epoch = self._pre_resume_config.get('epoch', 0) + 1
            restored_total = self._pre_resume_config.get('total_epochs', 0)
            self.progress.current_epoch = restored_epoch
            self.progress.total_epochs = restored_total
            self.progress.val_loss = self._pre_resume_config.get('val_loss', 0)
            self.progress.best_epoch = self._pre_resume_config.get('best_epoch', 0)
            self.progress.best_val_loss = self._pre_resume_config.get('best_val_loss', float('inf'))

            self._add_log(f"Restored training config to pre-resume state")
            self._add_log(f"  - Epochs: {restored_epoch}/{restored_total}")
            self._add_log(f"  - Status: {'completed' if self._pre_resume_config.get('is_complete') else 'stopped'}")
        except Exception as e:
            self._add_log(f"Warning: Could not restore pre-resume state: {e}")
        finally:
            # Clear the saved state
            self._clear_resume_state()

    def _clear_resume_state(self):
        """Clear the saved resume state without restoring."""
        self._pre_resume_config = None
        self._pre_resume_checkpoint_path = None
        self._is_resume_session = False

    def cleanup(self):
        """Cleanup resources."""
        if self.process:
            self.stop_training()

    def _build_command(self, config: TrainingConfig, resume: bool = False) -> List[str]:
        """Build the training command."""
        # Use pipeline/training.py relative to backend directory
        pipeline_path = Path(__file__).parent.parent / 'pipeline' / 'training.py'

        cmd = [
            'python3',
            str(pipeline_path),
            '--train', config.train_file,
            '--val', config.val_file,
            '--model', config.model_name,
            '--epochs', str(config.epochs),
            '--batch-size', str(config.batch_size),
            '--lr', str(config.learning_rate),
            '--output', config.output_dir,
        ]

        # Add log file for persistent logging (avoids tqdm spam in logs)
        if self._log_file:
            cmd.extend(['--log-file', str(self._log_file)])

        # Note: JSON progress emission not yet implemented in training.py
        # The service uses regex fallback parsing instead

        if resume and config.checkpoint_path:
            cmd.extend(['--resume', config.checkpoint_path])
            if config.extend_epochs > 0:
                cmd.extend(['--extend-epochs', str(config.extend_epochs)])

        if config.run_epochs:
            cmd.extend(['--run-epochs', str(config.run_epochs)])

        return cmd

    def _run_subprocess(self, cmd: List[str]):
        """Run training in a subprocess."""
        env = os.environ.copy()
        env['HF_HUB_DISABLE_SYMLINKS'] = '1'
        env['PYTHONUNBUFFERED'] = '1'
        # Add ml directory to Python path for imports
        ml_dir = str(Path(__file__).parent.parent / 'ml')
        env['PYTHONPATH'] = f"{ml_dir}:{env.get('PYTHONPATH', '')}"

        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=env,
                cwd=str(self._base_dir)
            )

            self._monitor_thread = threading.Thread(
                target=self._monitor_output,
                daemon=True
            )
            self._monitor_thread.start()

        except Exception as e:
            self._add_log(f"Error starting training: {e}")
            self.progress.status = TrainingStatus.FAILED
            self._notify_subscribers()

    def _monitor_output(self):
        """Monitor subprocess output and update progress."""
        try:
            for line in iter(self.process.stdout.readline, ''):
                if self._stop_flag:
                    break

                line = line.strip()
                if not line:
                    continue

                # Check for JSON progress lines (from --emit-progress)
                if line.startswith('PROGRESS_JSON:'):
                    self._parse_json_progress(line[14:])  # Skip 'PROGRESS_JSON:' prefix
                else:
                    # Regular log line - add to in-memory logs
                    self._add_log(line)
                    self._parse_output_line(line)

                # Update timing
                self.progress.elapsed_time = time.time() - self._start_time
                if self.progress.current_epoch > 0:
                    time_per_epoch = self.progress.elapsed_time / self.progress.current_epoch
                    remaining = self.progress.total_epochs - self.progress.current_epoch
                    self.progress.eta = time_per_epoch * remaining

                self._notify_subscribers()

            return_code = self.process.wait()

            if return_code == 0:
                self.progress.status = TrainingStatus.COMPLETED
                self._add_log("Training completed successfully!")
                self._write_log_footer(success=True)
                # Clear resume state on successful completion (no rollback needed)
                self._clear_resume_state()
                self._notify_subscribers()
            elif self._stop_flag:
                # Don't notify here - stop_training() already handled reset and notification
                self._write_log_footer(success=False)
            else:
                self.progress.status = TrainingStatus.FAILED
                self._add_log(f"Training failed with code: {return_code}")
                self._write_log_footer(success=False)
                # On failure, restore pre-resume state if applicable
                if self._is_resume_session and self._pre_resume_config:
                    self._restore_pre_resume_state()
                else:
                    # Reset progress for fresh training failures
                    self._reset_progress()
                    self.progress.status = TrainingStatus.FAILED
                self._notify_subscribers()

        except Exception as e:
            self._add_log(f"Error in monitoring: {e}")
            self.progress.status = TrainingStatus.FAILED
            self._notify_subscribers()

    def _parse_json_progress(self, json_str: str):
        """
        Parse JSON progress from training pipeline.

        Progress types:
        - loading: Model/data loading phase
        - training_start: Initial training info
        - epoch_start: Beginning of an epoch
        - epoch_end: End of epoch with metrics
        - batch: Per-batch progress (train/validate)
        - training_complete: Training finished
        """
        try:
            data = json.loads(json_str)
            progress_type = data.get('type')

            if progress_type == 'loading':
                # Update status to show loading phase
                phase = data.get('phase', 'model')
                message = data.get('message', f'Loading {phase}...')
                self._add_log(message)
                # Keep status as RUNNING but indicate loading phase
                if phase == 'model':
                    self.progress.model_name = data.get('model_name', self.progress.model_name)

            elif progress_type == 'training_start':
                self.progress.total_epochs = data.get('total_epochs', 0)
                self.progress.model_name = data.get('model_name', '')
                self.progress.train_samples = data.get('train_samples', 0)
                self.progress.val_samples = data.get('val_samples', 0)

            elif progress_type == 'epoch_start':
                self.progress.current_epoch = data.get('epoch', 0)
                self.progress.total_epochs = data.get('total_epochs', 0)
                self.progress.current_batch = 0
                self.progress.total_batches = 0

            elif progress_type == 'epoch_end':
                self.progress.current_epoch = data.get('epoch', 0)
                self.progress.train_loss = data.get('train_loss', 0)
                self.progress.val_loss = data.get('val_loss', 0)
                self.progress.val_accuracy = data.get('val_accuracy', 0)
                if data.get('is_best', False):
                    self.progress.best_epoch = data.get('epoch', 0)
                    self.progress.best_val_loss = data.get('best_val_loss', float('inf'))
                # Record history
                epoch = data.get('epoch', 0)
                if epoch not in self.progress.history['epochs']:
                    self.progress.history['epochs'].append(epoch)
                    self.progress.history['train_loss'].append(data.get('train_loss', 0))
                    self.progress.history['val_loss'].append(data.get('val_loss', 0))
                    self.progress.history['val_accuracy'].append(data.get('val_accuracy', 0))

            elif progress_type == 'batch':
                self.progress.current_batch = data.get('batch', 0)
                self.progress.total_batches = data.get('total_batches', 0)
                if data.get('phase') == 'train':
                    self.progress.train_loss = data.get('loss', 0)
                # Calculate samples per second
                if self.progress.elapsed_time > 0 and self.progress.current_batch > 0:
                    batch_size = self.progress.train_samples // self.progress.total_batches if self.progress.total_batches > 0 else 16
                    samples_processed = self.progress.current_batch * batch_size
                    self.progress.samples_per_second = samples_processed / self.progress.elapsed_time

            elif progress_type == 'training_complete':
                self.progress.best_val_loss = data.get('best_val_loss', float('inf'))

        except Exception as e:
            self._add_log(f"Error parsing progress JSON: {e}")

    def _parse_output_line(self, line: str):
        """Parse output line and update progress (fallback for non-JSON lines)."""
        # Epoch
        match = re.search(r'Epoch (\d+)/(\d+)', line)
        if match:
            self.progress.current_epoch = int(match.group(1))
            self.progress.total_epochs = int(match.group(2))

        # Train loss
        match = re.search(r'Train Loss:\s*([\d.]+)', line)
        if match:
            self.progress.train_loss = float(match.group(1))

        # Val loss
        match = re.search(r'Val Loss:\s*([\d.]+)', line)
        if match:
            self.progress.val_loss = float(match.group(1))

        # Val accuracy
        match = re.search(r'Val Accuracy:\s*([\d.]+)%', line)
        if match:
            self.progress.val_accuracy = float(match.group(1)) / 100

        # Best model
        if 'Best model saved' in line:
            match = re.search(r'val_loss:\s*([\d.]+)', line)
            if match:
                self.progress.best_epoch = self.progress.current_epoch
                self.progress.best_val_loss = float(match.group(1))

        # Batch progress
        match = re.search(r'(\d+)/(\d+)\s*\[', line)
        if match:
            self.progress.current_batch = int(match.group(1))
            self.progress.total_batches = int(match.group(2))

        # Training samples
        match = re.search(r'Training samples:\s*(\d+)', line)
        if match:
            self.progress.train_samples = int(match.group(1))

        match = re.search(r'Validation samples:\s*(\d+)', line)
        if match:
            self.progress.val_samples = int(match.group(1))

        # Update history on epoch completion
        if self.progress.train_loss > 0 and self.progress.val_loss > 0:
            epoch = self.progress.current_epoch
            if epoch not in self.progress.history['epochs']:
                self.progress.history['epochs'].append(epoch)
                self.progress.history['train_loss'].append(self.progress.train_loss)
                self.progress.history['val_loss'].append(self.progress.val_loss)
                self.progress.history['val_accuracy'].append(self.progress.val_accuracy)

    def _add_log(self, message: str):
        """Add a log message."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.logs.append(f"[{timestamp}] {message}")
        if len(self.logs) > 1000:
            self.logs = self.logs[-1000:]
