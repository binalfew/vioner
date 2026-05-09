"""
ML Training Pipeline - Week 9-10
Fine-tune BERT/RoBERTa models for violent event NER

Author: Binalfew Kassa Mekonnen
Date: December 2025

Enhanced with:
- FocalLoss for handling class imbalance (Phase 4)
- Class weight balancing for rare entity types
- Configurable loss functions
"""

import os
# Disable symlinks in Hugging Face cache (fix for macOS cache issues)
os.environ['HF_HUB_DISABLE_SYMLINKS'] = '1'

import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    get_linear_schedule_with_warmup,
)
from torch.optim.lr_scheduler import ReduceLROnPlateau
from tqdm import tqdm
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import Counter
import logging
from datetime import datetime

# Handle both package import and direct script execution
try:
    from .config import ModelConfig, LabelConfigs
    from .loss import (
        FocalLoss,
        ClassWeightedCrossEntropy,
        compute_class_weights,
        get_entity_aware_weights,
        create_ner_focal_loss
    )
except ImportError:
    from config import ModelConfig, LabelConfigs
    from loss import (
        FocalLoss,
        ClassWeightedCrossEntropy,
        compute_class_weights,
        get_entity_aware_weights,
        create_ner_focal_loss
    )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# DATASET CLASS
# ============================================================================

class NERDataset(Dataset):
    """Dataset for NER training with BIO tags."""

    def __init__(self, data: List[Dict], tokenizer, label2id: Dict, max_length: int = 512):
        """
        Initialize NER dataset.

        Args:
            data: List of events with tokens and labels
            tokenizer: Hugging Face tokenizer
            label2id: Label to ID mapping
            max_length: Maximum sequence length
        """
        self.data = data
        self.tokenizer = tokenizer
        self.label2id = label2id
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        event = self.data[idx]
        tokens = event['tokens']
        labels = event['labels']

        # Tokenize with word-level alignment
        encoding = self.tokenizer(
            tokens,
            is_split_into_words=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        # Align labels with tokenized input
        word_ids = encoding.word_ids(batch_index=0)
        label_ids = []

        previous_word_idx = None
        for word_idx in word_ids:
            if word_idx is None:
                # Special tokens [CLS], [SEP], [PAD]
                label_ids.append(-100)  # Ignore in loss
            elif word_idx != previous_word_idx:
                # First subword of a word → use original label
                label = labels[word_idx] if word_idx < len(labels) else 'O'
                label_ids.append(self.label2id.get(label, 0))
            else:
                # Continuation subword → use same label or -100
                label = labels[word_idx] if word_idx < len(labels) else 'O'
                if label.startswith('B-'):
                    # Convert B- to I- for subwords
                    label = 'I-' + label[2:]
                label_ids.append(self.label2id.get(label, 0))

            previous_word_idx = word_idx

        # Convert to tensors
        item = {
            'input_ids': encoding['input_ids'].squeeze(),
            'attention_mask': encoding['attention_mask'].squeeze(),
            'labels': torch.tensor(label_ids, dtype=torch.long)
        }

        return item


# ============================================================================
# TRAINING CLASS
# ============================================================================

class ViolentEventNER:
    """NER model trainer for violent event extraction."""

    def __init__(self, config: ModelConfig, log_file: str = None):
        """
        Initialize trainer.

        Args:
            config: Model configuration
            log_file: Optional path to write clean log output
        """
        self.config = config
        self.label2id = LabelConfigs.get_label2id()
        self.id2label = LabelConfigs.get_id2label()
        self.log_file = log_file
        self._log_handle = None

        # Set device - handle 'auto' option
        if config.device == 'auto':
            if torch.backends.mps.is_available():
                self.device = torch.device('mps')
                logger.info("✅ Auto-detected Apple Silicon GPU (MPS)")
            elif torch.cuda.is_available():
                self.device = torch.device('cuda')
                logger.info("✅ Auto-detected NVIDIA GPU (CUDA)")
            else:
                self.device = torch.device('cpu')
                logger.info("Using CPU")
        elif config.device == 'mps' and torch.backends.mps.is_available():
            self.device = torch.device('mps')
            logger.info("✅ Using Apple Silicon GPU (MPS)")
        elif config.device == 'cuda' and torch.cuda.is_available():
            self.device = torch.device('cuda')
            logger.info("✅ Using NVIDIA GPU (CUDA)")
        else:
            self.device = torch.device('cpu')
            logger.info("Using CPU")

        # Initialize model and tokenizer
        self.tokenizer = None
        self.model = None
        self.train_dataset = None
        self.val_dataset = None

        # Loss function (initialized after loading data for class weights)
        self.loss_fn = None
        self.class_weights = None

    def _log(self, message: str):
        """Write message to both stdout and log file (if configured)."""
        print(message)
        if self.log_file:
            if self._log_handle is None:
                # Open in append mode
                self._log_handle = open(self.log_file, 'a')
            self._log_handle.write(message + '\n')
            self._log_handle.flush()

    def _close_log(self):
        """Close log file handle."""
        if self._log_handle:
            self._log_handle.close()
            self._log_handle = None

    def load_model(self):
        """Load pre-trained model and tokenizer."""
        logger.info(f"Loading model: {self.config.model_name}")

        # Load tokenizer (works for both local and remote models)
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)

        # Load model with token classification head
        # This automatically adds the classification head with the correct number of labels
        self.model = AutoModelForTokenClassification.from_pretrained(
            self.config.model_name,
            num_labels=self.config.num_labels,
            id2label=self.id2label,
            label2id=self.label2id,
            ignore_mismatched_sizes=True,  # Ignore if base model doesn't have classification head
        )

        self.model.to(self.device)
        logger.info(f"Model loaded with {self.config.num_labels} labels")

    def _load_data_file(self, file_path: str) -> list:
        """Load data from JSONL or JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.endswith('.jsonl'):
                # JSONL format: one JSON object per line
                return [json.loads(line) for line in f if line.strip()]
            else:
                # JSON format: single array
                return json.load(f)

    def load_data(self, train_file: str, val_file: str):
        """Load training and validation data from JSONL or JSON files."""
        logger.info(f"Loading training data from: {train_file}")
        train_data = self._load_data_file(train_file)

        logger.info(f"Loading validation data from: {val_file}")
        val_data = self._load_data_file(val_file)

        # Create datasets
        self.train_dataset = NERDataset(
            train_data,
            self.tokenizer,
            self.label2id,
            self.config.max_length
        )

        self.val_dataset = NERDataset(
            val_data,
            self.tokenizer,
            self.label2id,
            self.config.max_length
        )

        logger.info(f"Train dataset: {len(self.train_dataset)} examples")
        logger.info(f"Validation dataset: {len(self.val_dataset)} examples")

        # Initialize loss function after loading data
        self._init_loss_function()

    def _init_loss_function(self):
        """
        Initialize loss function based on config settings.

        Uses FocalLoss with class weights if enabled, otherwise standard CE.
        """
        use_focal = getattr(self.config, 'use_focal_loss', False)
        use_weights = getattr(self.config, 'use_class_weights', False)
        gamma = getattr(self.config, 'focal_gamma', 2.0)
        label_smoothing = getattr(self.config, 'label_smoothing', 0.0)

        num_classes = len(self.label2id)

        # Compute class weights from training data if enabled
        if use_weights and self.train_dataset is not None:
            self._log("Computing class weights from training data...")
            label_counts = self._compute_label_distribution()

            self.class_weights = compute_class_weights(
                label_counts,
                self.label2id,
                method='inverse_freq'
            ).to(self.device)

            # Log weight statistics
            o_weight = self.class_weights[self.label2id.get('O', 0)].item()
            max_weight = self.class_weights.max().item()
            min_weight = self.class_weights.min().item()
            self._log(f"  O weight: {o_weight:.3f}")
            self._log(f"  Weight range: {min_weight:.3f} - {max_weight:.3f}")
        elif use_weights:
            # Use entity-aware weights as fallback
            self._log("Using entity-aware weights (B- > I- > O)...")
            self.class_weights = get_entity_aware_weights(self.label2id).to(self.device)
        else:
            self.class_weights = None

        # Create loss function
        if use_focal:
            self._log(f"Using FocalLoss (gamma={gamma}, label_smoothing={label_smoothing})")
            self.loss_fn = FocalLoss(
                num_classes=num_classes,
                gamma=gamma,
                alpha=self.class_weights,
                reduction='mean',
                ignore_index=-100,
                label_smoothing=label_smoothing
            )
        elif use_weights and self.class_weights is not None:
            self._log(f"Using weighted CrossEntropyLoss (label_smoothing={label_smoothing})")
            self.loss_fn = ClassWeightedCrossEntropy(
                num_classes=num_classes,
                class_weights=self.class_weights,
                ignore_index=-100,
                label_smoothing=label_smoothing
            )
        else:
            self._log("Using standard CrossEntropyLoss")
            self.loss_fn = None  # Use model's built-in loss

    def _compute_label_distribution(self) -> Dict[str, int]:
        """
        Compute label distribution from training dataset.

        Returns:
            Dictionary mapping label strings to counts
        """
        label_counts = Counter()

        for i in range(len(self.train_dataset)):
            item = self.train_dataset[i]
            labels = item['labels']

            for label_id in labels.tolist():
                if label_id != -100:  # Skip ignored tokens
                    label = self.id2label.get(label_id, 'O')
                    label_counts[label] += 1

        # Log distribution summary
        total = sum(label_counts.values())
        o_count = label_counts.get('O', 0)
        entity_count = total - o_count

        self._log(f"  Total tokens: {total:,}")
        self._log(f"  O tokens: {o_count:,} ({100*o_count/total:.1f}%)")
        self._log(f"  Entity tokens: {entity_count:,} ({100*entity_count/total:.1f}%)")

        # Show top entity types
        entity_labels = [(l, c) for l, c in label_counts.items() if l != 'O']
        entity_labels.sort(key=lambda x: -x[1])
        self._log(f"  Top entity types: {entity_labels[:5]}")

        return dict(label_counts)

    def train(self, run_epochs: int = None) -> Dict:
        """
        Train the model.

        Args:
            run_epochs: Number of epochs to run in this session (None = all)

        Returns:
            Training history
        """
        if self.model is None:
            self.load_model()

        return self._train_from_epoch(start_epoch=0, best_val_loss=float('inf'), run_epochs=run_epochs)

    def _train_from_epoch(self, start_epoch: int = 0, best_val_loss: float = float('inf'),
                          run_epochs: int = None) -> Dict:
        """
        Train the model starting from a specific epoch.

        Args:
            start_epoch: Epoch to start from (0-indexed)
            best_val_loss: Best validation loss so far (for resume)
            run_epochs: Number of epochs to run in this session (None = all remaining)

        Returns:
            Training history
        """
        # Calculate end epoch for this session
        if run_epochs is not None:
            end_epoch = min(start_epoch + run_epochs, self.config.num_epochs)
        else:
            end_epoch = self.config.num_epochs

        # Create data loaders
        train_loader = DataLoader(
            self.train_dataset,
            batch_size=self.config.batch_size,
            shuffle=True,
        )

        val_loader = DataLoader(
            self.val_dataset,
            batch_size=self.config.batch_size,
            shuffle=False,
        )

        # Optimizer
        optimizer = AdamW(
            self.model.parameters(),
            lr=self.config.learning_rate,
            weight_decay=self.config.weight_decay,
        )

        # Learning rate scheduler setup
        lr_scheduler_type = getattr(self.config, 'lr_scheduler', 'linear')
        epochs_this_session = end_epoch - start_epoch
        num_training_steps = len(train_loader) * epochs_this_session

        if lr_scheduler_type == 'reduce_on_plateau':
            # ReduceLROnPlateau - reduces LR when validation loss plateaus
            lr_reduce_factor = getattr(self.config, 'lr_reduce_factor', 0.5)
            lr_reduce_patience = getattr(self.config, 'lr_reduce_patience', 2)
            scheduler = ReduceLROnPlateau(
                optimizer,
                mode='min',
                factor=lr_reduce_factor,
                patience=lr_reduce_patience,
                min_lr=1e-7
            )
            warmup_scheduler = get_linear_schedule_with_warmup(
                optimizer,
                num_warmup_steps=self.config.warmup_steps,
                num_training_steps=num_training_steps,
            )
            use_plateau_scheduler = True
        elif lr_scheduler_type == 'linear':
            scheduler = get_linear_schedule_with_warmup(
                optimizer,
                num_warmup_steps=self.config.warmup_steps,
                num_training_steps=num_training_steps,
            )
            warmup_scheduler = None
            use_plateau_scheduler = False
        else:
            scheduler = None
            warmup_scheduler = None
            use_plateau_scheduler = False

        # Early stopping setup
        use_early_stopping = getattr(self.config, 'use_early_stopping', True)
        early_stopping_patience = getattr(self.config, 'early_stopping_patience', 5)
        early_stopping_threshold = getattr(self.config, 'early_stopping_threshold', 0.001)
        epochs_without_improvement = 0

        # Training history
        history = {
            'train_loss': [],
            'val_loss': [],
            'val_accuracy': [],
            'epochs': [],
            'learning_rates': [],
        }

        best_model_path = None
        stopped_early = False

        if start_epoch == 0:
            self._log("\n" + "=" * 70)
            self._log("TRAINING STARTED")
            self._log("=" * 70)
        else:
            self._log("\n" + "=" * 70)
            self._log(f"CONTINUING TRAINING FROM EPOCH {start_epoch + 1}")
            self._log("=" * 70)

        self._log(f"Model: {self.config.model_name}")
        self._log(f"Device: {self.device}")
        self._log(f"Training samples: {len(self.train_dataset)}")
        self._log(f"Validation samples: {len(self.val_dataset)}")
        self._log(f"Batch size: {self.config.batch_size}")
        self._log(f"This session: Epoch {start_epoch + 1} to {end_epoch} (of {self.config.num_epochs} total)")
        self._log(f"Learning rate: {self.config.learning_rate}")
        self._log(f"LR Scheduler: {lr_scheduler_type}")
        if use_early_stopping:
            self._log(f"Early stopping: patience={early_stopping_patience}, threshold={early_stopping_threshold}")
        self._log("=" * 70)

        # Training loop
        for epoch in range(start_epoch, end_epoch):
            self._log(f"\nEpoch {epoch + 1}/{self.config.num_epochs}")
            self._log("-" * 70)

            # Get current learning rate
            current_lr = optimizer.param_groups[0]['lr']

            # Train (tqdm goes to terminal only, not log file)
            # Use warmup scheduler during training steps if using plateau scheduler
            step_scheduler = warmup_scheduler if use_plateau_scheduler else scheduler
            train_loss = self._train_epoch(train_loader, optimizer, step_scheduler)

            # Validate (tqdm goes to terminal only, not log file)
            val_loss, val_acc = self._validate_epoch(val_loader)

            # Update ReduceLROnPlateau scheduler after validation
            if use_plateau_scheduler and scheduler is not None:
                old_lr = optimizer.param_groups[0]['lr']
                scheduler.step(val_loss)
                new_lr = optimizer.param_groups[0]['lr']
                if new_lr < old_lr:
                    self._log(f"📉 Learning rate reduced: {old_lr:.2e} → {new_lr:.2e}")

            # Record history
            history['train_loss'].append(train_loss)
            history['val_loss'].append(val_loss)
            history['val_accuracy'].append(val_acc)
            history['epochs'].append(epoch + 1)
            history['learning_rates'].append(current_lr)

            # Log metrics (goes to both terminal and log file)
            self._log(f"Train Loss: {train_loss:.4f}")
            self._log(f"Val Loss: {val_loss:.4f}")
            self._log(f"Val Accuracy: {val_acc:.2%}")
            self._log(f"Learning Rate: {current_lr:.2e}")

            # Check for improvement
            improvement = best_val_loss - val_loss
            is_best = improvement > early_stopping_threshold

            if is_best:
                best_val_loss = val_loss
                epochs_without_improvement = 0
            else:
                epochs_without_improvement += 1

            # Always save checkpoint after each epoch (for resume capability)
            best_model_path = self._save_checkpoint(epoch, val_loss, is_best)

            if is_best:
                self._log(f"✅ Best model saved (val_loss: {val_loss:.4f})")
            else:
                self._log(f"💾 Checkpoint saved (epoch {epoch + 1})")
                if use_early_stopping:
                    self._log(f"   No improvement for {epochs_without_improvement}/{early_stopping_patience} epochs")

            # Early stopping check
            if use_early_stopping and epochs_without_improvement >= early_stopping_patience:
                self._log(f"\n⚠️  Early stopping triggered after {epochs_without_improvement} epochs without improvement")
                stopped_early = True
                break

        self._log("\n" + "=" * 70)
        if stopped_early:
            self._log(f"TRAINING STOPPED EARLY (Epoch {epoch + 1}/{self.config.num_epochs})")
            self._log(f"Best model was at epoch {getattr(self, '_best_epoch', 'unknown')}")
        elif end_epoch >= self.config.num_epochs:
            self._log("TRAINING COMPLETE")
        else:
            self._log(f"SESSION COMPLETE (Epoch {end_epoch}/{self.config.num_epochs})")
            self._log(f"To continue: --resume {best_model_path}")
        self._log("=" * 70)
        self._log(f"Best validation loss: {best_val_loss:.4f}")
        self._log(f"Model saved to: {best_model_path}")

        self._close_log()
        return history

    def _train_epoch(self, train_loader, optimizer, scheduler) -> float:
        """Train for one epoch."""
        self.model.train()
        total_loss = 0

        progress_bar = tqdm(train_loader, desc="Training")

        for batch in progress_bar:
            # Move batch to device
            input_ids = batch['input_ids'].to(self.device)
            attention_mask = batch['attention_mask'].to(self.device)
            labels = batch['labels'].to(self.device)

            # Forward pass
            if self.loss_fn is not None:
                # Use custom loss function (FocalLoss or weighted CE)
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=None,  # Don't compute loss in model
                )
                # Compute custom loss
                loss = self.loss_fn(outputs.logits, labels)
            else:
                # Use model's built-in CrossEntropyLoss
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels,
                )
                loss = outputs.loss

            # Backward pass
            loss.backward()

            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(
                self.model.parameters(),
                self.config.max_grad_norm
            )

            # Update weights
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()

            total_loss += loss.item()

            # Update progress bar
            progress_bar.set_postfix({'loss': loss.item()})

        avg_loss = total_loss / len(train_loader)
        return avg_loss

    def _validate_epoch(self, val_loader) -> Tuple[float, float]:
        """Validate for one epoch."""
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0

        with torch.no_grad():
            for batch in tqdm(val_loader, desc="Validating"):
                # Move batch to device
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)

                # Forward pass
                if self.loss_fn is not None:
                    # Use custom loss function
                    outputs = self.model(
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                        labels=None,
                    )
                    loss = self.loss_fn(outputs.logits, labels)
                else:
                    # Use model's built-in loss
                    outputs = self.model(
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                        labels=labels,
                    )
                    loss = outputs.loss

                total_loss += loss.item()

                # Calculate accuracy
                predictions = torch.argmax(outputs.logits, dim=-1)

                # Only count non-padded tokens
                mask = labels != -100
                correct += ((predictions == labels) & mask).sum().item()
                total += mask.sum().item()

        avg_loss = total_loss / len(val_loader)
        accuracy = correct / total if total > 0 else 0

        return avg_loss, accuracy

    def _save_checkpoint(self, epoch: int, val_loss: float, is_best: bool = False) -> str:
        """
        Save model checkpoint with epoch-based folder structure.

        Structure:
            models/bert-base-cased_YYYYMMDD_HHMMSS/
            ├── epoch_01/          # Model after epoch 1
            ├── epoch_02/          # Model after epoch 2
            ├── ...
            ├── best/              # Copy of best model (lowest val_loss)
            └── training_config.json  # Training state for resume
        """
        model_name = self.config.model_name.replace('/', '_')

        # Use consistent directory name for resumable checkpoints
        if not hasattr(self, '_checkpoint_dir') or self._checkpoint_dir is None:
            if self.config.no_timestamp:
                # Use exact output path without timestamp
                self._checkpoint_dir = Path(self.config.output_dir)
            else:
                # Add timestamp to create unique folder
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                self._checkpoint_dir = Path(self.config.output_dir) / f"{model_name}_{timestamp}"

        checkpoint_dir = self._checkpoint_dir
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Create epoch-specific subfolder (1-indexed for readability)
        epoch_folder = checkpoint_dir / f"epoch_{epoch + 1:02d}"
        epoch_folder.mkdir(parents=True, exist_ok=True)

        # Save model to epoch folder
        self.model.save_pretrained(epoch_folder)
        self.tokenizer.save_pretrained(epoch_folder)

        # If this is the best model, also save to best/ folder
        if is_best:
            best_folder = checkpoint_dir / "best"
            best_folder.mkdir(parents=True, exist_ok=True)
            self.model.save_pretrained(best_folder)
            self.tokenizer.save_pretrained(best_folder)

            # Track which epoch is best
            best_epoch = epoch + 1
        else:
            # Load existing best epoch if available
            best_epoch = getattr(self, '_best_epoch', None)

        # Update best epoch tracker
        if is_best:
            self._best_epoch = epoch + 1

        # Save config with training state for resuming (at root level)
        config_dict = {
            'epoch': epoch,
            'val_loss': val_loss,
            'model_name': self.config.model_name,
            'num_labels': self.config.num_labels,
            'total_epochs': self.config.num_epochs,
            'batch_size': self.config.batch_size,
            'learning_rate': self.config.learning_rate,
            'is_complete': (epoch + 1) >= self.config.num_epochs,
            'best_epoch': getattr(self, '_best_epoch', epoch + 1),
            'best_val_loss': val_loss if is_best else getattr(self, '_best_val_loss', val_loss),
        }

        # Track best val loss
        if is_best:
            self._best_val_loss = val_loss

        with open(checkpoint_dir / 'training_config.json', 'w') as f:
            json.dump(config_dict, f, indent=2)

        return str(checkpoint_dir)

    def resume_training(self, checkpoint_path: str, train_file: str, val_file: str,
                        run_epochs: int = None, extend_epochs: int = None) -> Dict:
        """
        Resume training from a checkpoint.

        Args:
            checkpoint_path: Path to checkpoint directory (root level, not epoch folder)
            train_file: Training data file
            val_file: Validation data file
            run_epochs: Number of epochs to run in this session (None = all remaining)
            extend_epochs: Add more epochs to completed training (e.g., 2 adds 2 more)

        Returns:
            Training history
        """
        checkpoint_dir = Path(checkpoint_path)

        # Load saved config
        with open(checkpoint_dir / 'training_config.json', 'r') as f:
            saved_config = json.load(f)

        start_epoch = saved_config['epoch'] + 1  # Resume from next epoch

        # Handle extending training (works for both complete and incomplete)
        if extend_epochs:
            old_total = saved_config['total_epochs']
            new_total = old_total + extend_epochs
            self._log(f"\n📈 Extending training: {old_total} → {new_total} epochs (+{extend_epochs})")
            saved_config['total_epochs'] = new_total
            saved_config['is_complete'] = False
            self.config.num_epochs = new_total
        elif saved_config.get('is_complete', False):
            self._log(f"Training already completed at epoch {saved_config['epoch'] + 1}")
            self._log(f"To add more epochs, use: --extend-epochs N")
            return {}

        self._log(f"\n{'='*70}")
        self._log(f"RESUMING TRAINING FROM EPOCH {start_epoch + 1}")
        self._log(f"{'='*70}")
        self._log(f"Checkpoint: {checkpoint_path}")
        self._log(f"Last completed epoch: {saved_config['epoch'] + 1}")
        self._log(f"Last validation loss: {saved_config['val_loss']:.4f}")
        if 'best_epoch' in saved_config:
            self._log(f"Best epoch so far: {saved_config['best_epoch']} (val_loss: {saved_config.get('best_val_loss', 'N/A')})")
        self._log(f"{'='*70}\n")

        # Set the checkpoint directory for continued saving
        self._checkpoint_dir = checkpoint_dir

        # Restore best epoch tracking
        if 'best_epoch' in saved_config:
            self._best_epoch = saved_config['best_epoch']
            self._best_val_loss = saved_config.get('best_val_loss', saved_config['val_loss'])

        # Find the latest epoch folder to load model from
        last_epoch = saved_config['epoch'] + 1  # 1-indexed
        epoch_folder = checkpoint_dir / f"epoch_{last_epoch:02d}"

        if epoch_folder.exists():
            model_path = epoch_folder
            logger.info(f"Loading model from epoch folder: {model_path}")
        else:
            # Fallback to root dir (for old checkpoint format compatibility)
            model_path = checkpoint_dir
            logger.info(f"Loading model from checkpoint root: {model_path}")

        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForTokenClassification.from_pretrained(model_path)
        self.model.to(self.device)

        # Load data
        self.load_data(train_file, val_file)

        # Continue training from start_epoch with the best val loss seen so far
        best_val_so_far = saved_config.get('best_val_loss', saved_config['val_loss'])
        return self._train_from_epoch(start_epoch, best_val_so_far, run_epochs=run_epochs)

    def predict(self, text: str) -> List[Tuple[str, str]]:
        """
        Predict entities in text.

        Args:
            text: Input text

        Returns:
            List of (token, label) pairs
        """
        self.model.eval()

        # Tokenize
        inputs = self.tokenizer(
            text,
            return_tensors='pt',
            truncation=True,
            max_length=self.config.max_length,
        )

        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Predict
        with torch.no_grad():
            outputs = self.model(**inputs)

        predictions = torch.argmax(outputs.logits, dim=-1)

        # Decode predictions
        tokens = self.tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
        labels = [self.id2label[p.item()] for p in predictions[0]]

        # Filter special tokens
        results = []
        for token, label in zip(tokens, labels):
            if token not in ['[CLS]', '[SEP]', '[PAD]']:
                results.append((token, label))

        return results


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def load_trained_model(model_path: str, device: str = 'mps', epoch: str = 'best') -> ViolentEventNER:
    """
    Load a trained model from disk.

    Args:
        model_path: Path to the checkpoint directory (e.g., models/bert-base-cased_20251208_150218/)
        device: Device to load model on ('mps', 'cuda', or 'cpu')
        epoch: Which epoch to load - 'best', 'latest', or specific number like '3'

    Returns:
        ViolentEventNER trainer with loaded model
    """
    model_dir = Path(model_path)
    logger.info(f"Loading trained model from: {model_path}")

    # Load config from root level
    config_path = model_dir / 'training_config.json'
    if not config_path.exists():
        # Maybe user passed epoch folder directly - try parent
        if model_dir.parent.name != 'models':
            config_path = model_dir.parent / 'training_config.json'

    with open(config_path, 'r') as f:
        saved_config = json.load(f)

    # Determine which model folder to load from
    if epoch == 'best':
        # Load from best/ folder
        actual_model_path = model_dir / 'best'
        if not actual_model_path.exists():
            # Fallback to best epoch folder
            best_epoch = saved_config.get('best_epoch', saved_config['epoch'] + 1)
            actual_model_path = model_dir / f"epoch_{best_epoch:02d}"
        logger.info(f"Loading best model from: {actual_model_path}")
    elif epoch == 'latest':
        # Load from latest epoch folder
        last_epoch = saved_config['epoch'] + 1
        actual_model_path = model_dir / f"epoch_{last_epoch:02d}"
        logger.info(f"Loading latest model (epoch {last_epoch}) from: {actual_model_path}")
    else:
        # Load specific epoch
        epoch_num = int(epoch)
        actual_model_path = model_dir / f"epoch_{epoch_num:02d}"
        logger.info(f"Loading epoch {epoch_num} model from: {actual_model_path}")

    # Fallback to root dir (for old checkpoint format compatibility)
    if not actual_model_path.exists():
        actual_model_path = model_dir
        logger.info(f"Epoch folder not found, falling back to root: {actual_model_path}")

    # Create config
    config = ModelConfig(
        model_name=saved_config['model_name'],
        num_labels=saved_config['num_labels'],
        device=device,
    )

    # Load model
    trainer = ViolentEventNER(config)
    trainer.tokenizer = AutoTokenizer.from_pretrained(actual_model_path)
    trainer.model = AutoModelForTokenClassification.from_pretrained(actual_model_path)
    trainer.model.to(trainer.device)

    logger.info("✅ Model loaded successfully")
    return trainer


# ============================================================================
# MAIN (FOR TESTING)
# ============================================================================

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Train NER model for violent events')
    parser.add_argument('--train', required=True, help='Training data (JSON)')
    parser.add_argument('--val', required=True, help='Validation data (JSON)')
    parser.add_argument('--model', default='bert-base-cased', help='Model name')
    parser.add_argument('--epochs', type=int, default=10, help='Number of epochs')
    parser.add_argument('--batch-size', type=int, default=16, help='Batch size')
    parser.add_argument('--lr', type=float, default=2e-5, help='Learning rate')
    parser.add_argument('--output', default='models', help='Output directory')
    parser.add_argument('--no-timestamp', action='store_true',
                        help='Use exact output path without adding timestamp (e.g., --output models/latest --no-timestamp)')
    parser.add_argument('--resume', type=str, default=None, nargs='?', const='auto',
                        help='Resume training. Use --resume for auto-detect, or --resume PATH for specific checkpoint')
    parser.add_argument('--run-epochs', type=int, default=None,
                        help='Number of epochs to run in this session (default: all remaining)')
    parser.add_argument('--extend-epochs', type=int, default=None,
                        help='Add more epochs to completed training (e.g., --extend-epochs 2 adds 2 more)')
    parser.add_argument('--log-file', type=str, default=None,
                        help='Path to write clean log output (without tqdm progress bars)')

    # Early stopping options
    parser.add_argument('--early-stopping', action='store_true', default=True,
                        help='Enable early stopping (default: True)')
    parser.add_argument('--no-early-stopping', dest='early_stopping', action='store_false',
                        help='Disable early stopping')
    parser.add_argument('--patience', type=int, default=5,
                        help='Early stopping patience (epochs without improvement)')

    # Learning rate scheduler options
    parser.add_argument('--lr-scheduler', type=str, default='reduce_on_plateau',
                        choices=['linear', 'reduce_on_plateau', 'none'],
                        help='Learning rate scheduler type')
    parser.add_argument('--lr-reduce-factor', type=float, default=0.5,
                        help='Factor to reduce LR by when plateau detected')
    parser.add_argument('--lr-reduce-patience', type=int, default=2,
                        help='Epochs to wait before reducing LR')

    args = parser.parse_args()

    # Helper to log messages (before trainer is created)
    def log_message(msg):
        print(msg)
        if args.log_file:
            with open(args.log_file, 'a') as f:
                f.write(msg + '\n')

    # Auto-detect latest checkpoint if --resume is used without a path
    if args.resume == 'auto':
        output_dir = Path(args.output)
        if output_dir.exists():
            # Find all checkpoint directories
            checkpoints = [d for d in output_dir.iterdir()
                          if d.is_dir() and (d / 'training_config.json').exists()]
            if checkpoints:
                # Sort by modification time, get most recent
                latest = max(checkpoints, key=lambda x: x.stat().st_mtime)
                args.resume = str(latest)
                log_message(f"🔍 Auto-detected latest checkpoint: {args.resume}")
            else:
                log_message("⚠️  No checkpoints found in models/. Starting fresh training.")
                args.resume = None
        else:
            log_message("⚠️  Models directory doesn't exist. Starting fresh training.")
            args.resume = None

    # Create config
    config = ModelConfig(
        model_name=args.model,
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        output_dir=args.output,
        no_timestamp=args.no_timestamp,
        # Early stopping
        use_early_stopping=args.early_stopping,
        early_stopping_patience=args.patience,
        # Learning rate scheduler
        lr_scheduler=args.lr_scheduler,
        lr_reduce_factor=args.lr_reduce_factor,
        lr_reduce_patience=args.lr_reduce_patience,
    )

    # Initialize trainer with optional log file
    trainer = ViolentEventNER(config, log_file=args.log_file)

    try:
        if args.resume:
            # Resume training from checkpoint
            trainer._log(f"\n🔄 Resuming training from: {args.resume}")
            history = trainer.resume_training(
                args.resume, args.train, args.val,
                run_epochs=args.run_epochs,
                extend_epochs=args.extend_epochs
            )
        else:
            # Fresh training
            # Load model and tokenizer first (needed for data preprocessing)
            trainer.load_model()

            # Load data
            trainer.load_data(args.train, args.val)

            # Train
            history = trainer.train(run_epochs=args.run_epochs)

        trainer._log("\n✅ Training complete!")
    except KeyboardInterrupt:
        trainer._log("\n\n⚠️  Training interrupted by user (Ctrl+C)")
        trainer._log("Your progress has been saved. To resume, run:")
        trainer._log(f"  --resume {args.output}")
    finally:
        trainer._close_log()
