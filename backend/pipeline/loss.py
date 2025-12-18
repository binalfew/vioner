"""
Custom Loss Functions - Phase 4
Implements FocalLoss and class weight balancing for NER training.

Author: Binalfew Kassa Mekonnen
Date: December 2025

Addresses class imbalance in NER:
- O labels dominate (often 80%+ of tokens)
- Rare entity types (MOTIVE, TRIGGER, COORDINATES) get underfit
- FocalLoss down-weights easy examples, focuses on hard ones
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional
import numpy as np
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class FocalLoss(nn.Module):
    """
    Focal Loss for imbalanced classification.

    FL(p_t) = -alpha_t * (1 - p_t)^gamma * log(p_t)

    Where:
    - p_t = probability of correct class
    - gamma = focusing parameter (default 2.0)
    - alpha = class balancing weights

    Benefits for NER:
    - Down-weights easy "O" label predictions
    - Focuses learning on harder entity boundaries
    - Handles rare entity types better

    Reference:
    Lin et al., "Focal Loss for Dense Object Detection", ICCV 2017
    """

    def __init__(
        self,
        num_classes: int,
        gamma: float = 2.0,
        alpha: Optional[torch.Tensor] = None,
        reduction: str = 'mean',
        ignore_index: int = -100,
        label_smoothing: float = 0.0
    ):
        """
        Initialize Focal Loss.

        Args:
            num_classes: Number of classes (BIO labels)
            gamma: Focusing parameter (0 = standard CE, higher = more focus on hard examples)
            alpha: Class weights tensor of shape (num_classes,)
            reduction: 'mean', 'sum', or 'none'
            ignore_index: Label to ignore (typically -100 for padding)
            label_smoothing: Label smoothing factor (0 = no smoothing)
        """
        super().__init__()
        self.num_classes = num_classes
        self.gamma = gamma
        self.alpha = alpha
        self.reduction = reduction
        self.ignore_index = ignore_index
        self.label_smoothing = label_smoothing

        if alpha is not None:
            if isinstance(alpha, (list, np.ndarray)):
                self.alpha = torch.tensor(alpha, dtype=torch.float32)
            self.register_buffer('alpha_buffer', self.alpha)

    def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """
        Compute focal loss.

        Args:
            inputs: Predictions of shape (batch, seq_len, num_classes)
            targets: Ground truth labels of shape (batch, seq_len)

        Returns:
            Scalar loss value
        """
        # Flatten for easier processing
        # inputs: (batch * seq_len, num_classes)
        # targets: (batch * seq_len,)
        inputs = inputs.view(-1, self.num_classes)
        targets = targets.view(-1)

        # Create mask for valid tokens (not ignore_index)
        valid_mask = targets != self.ignore_index

        # Filter to valid tokens only
        inputs = inputs[valid_mask]
        targets = targets[valid_mask]

        if inputs.numel() == 0:
            return torch.tensor(0.0, device=inputs.device, requires_grad=True)

        # Apply label smoothing if configured
        if self.label_smoothing > 0:
            # One-hot encode targets
            targets_one_hot = F.one_hot(targets, self.num_classes).float()
            # Apply smoothing
            targets_smooth = targets_one_hot * (1 - self.label_smoothing) + \
                           self.label_smoothing / self.num_classes
            # Compute log probabilities
            log_probs = F.log_softmax(inputs, dim=-1)
            # Compute cross-entropy with smoothed labels
            ce_loss = -(targets_smooth * log_probs).sum(dim=-1)
            # Get probabilities for focal term
            probs = torch.exp(log_probs)
            p_t = (targets_smooth * probs).sum(dim=-1)
        else:
            # Standard cross-entropy
            ce_loss = F.cross_entropy(inputs, targets, reduction='none')
            # Get probability of correct class
            probs = F.softmax(inputs, dim=-1)
            p_t = probs.gather(1, targets.unsqueeze(1)).squeeze(1)

        # Focal weight: (1 - p_t)^gamma
        focal_weight = (1 - p_t) ** self.gamma

        # Apply alpha weights if provided
        if self.alpha is not None:
            alpha_t = self.alpha_buffer.to(inputs.device).gather(0, targets)
            focal_weight = alpha_t * focal_weight

        # Focal loss
        loss = focal_weight * ce_loss

        # Apply reduction
        if self.reduction == 'mean':
            return loss.mean()
        elif self.reduction == 'sum':
            return loss.sum()
        else:
            return loss


class ClassWeightedCrossEntropy(nn.Module):
    """
    Cross-entropy loss with inverse frequency class weights.

    Automatically computes weights based on training data distribution.
    """

    def __init__(
        self,
        num_classes: int,
        class_weights: Optional[torch.Tensor] = None,
        ignore_index: int = -100,
        label_smoothing: float = 0.0
    ):
        """
        Initialize weighted cross-entropy.

        Args:
            num_classes: Number of classes
            class_weights: Pre-computed class weights (if None, equal weights)
            ignore_index: Label to ignore
            label_smoothing: Smoothing factor
        """
        super().__init__()
        self.num_classes = num_classes
        self.ignore_index = ignore_index
        self.label_smoothing = label_smoothing

        if class_weights is not None:
            self.register_buffer('weight', class_weights)
        else:
            self.register_buffer('weight', torch.ones(num_classes))

    def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """Compute weighted cross-entropy loss."""
        return F.cross_entropy(
            inputs.view(-1, self.num_classes),
            targets.view(-1),
            weight=self.weight.to(inputs.device),
            ignore_index=self.ignore_index,
            label_smoothing=self.label_smoothing
        )


# ============================================================================
# CLASS WEIGHT COMPUTATION
# ============================================================================

def compute_class_weights(
    label_counts: Dict[str, int],
    label2id: Dict[str, int],
    method: str = 'inverse_freq',
    smoothing: float = 0.1,
    max_weight: float = 10.0
) -> torch.Tensor:
    """
    Compute class weights from label distribution.

    Args:
        label_counts: Dictionary mapping label strings to counts
        label2id: Label to ID mapping
        method: Weighting method:
            - 'inverse_freq': w_c = N / (C * n_c)
            - 'inverse_sqrt': w_c = sqrt(N / n_c)
            - 'effective_samples': Uses effective number of samples
        smoothing: Smoothing factor to prevent extreme weights
        max_weight: Maximum allowed weight

    Returns:
        Tensor of class weights, shape (num_classes,)
    """
    num_classes = len(label2id)
    weights = torch.ones(num_classes)

    # Get total samples
    total_samples = sum(label_counts.values())

    if total_samples == 0:
        logger.warning("No samples found, returning equal weights")
        return weights

    for label, label_id in label2id.items():
        count = label_counts.get(label, 0)

        if count == 0:
            # Assign maximum weight to unseen classes
            weights[label_id] = max_weight
            continue

        if method == 'inverse_freq':
            # Inverse frequency: w_c = N / (C * n_c)
            weight = total_samples / (num_classes * count)
        elif method == 'inverse_sqrt':
            # Square root dampening for less aggressive weighting
            weight = np.sqrt(total_samples / count)
        elif method == 'effective_samples':
            # Effective number of samples method (Class-Balanced Loss)
            beta = 0.9999
            effective_num = (1 - beta ** count) / (1 - beta)
            weight = 1.0 / effective_num
        else:
            weight = 1.0

        # Apply smoothing
        weight = smoothing + (1 - smoothing) * weight

        # Clip to max
        weight = min(weight, max_weight)

        weights[label_id] = weight

    # Normalize so mean weight is 1.0
    weights = weights / weights.mean()

    return weights


def compute_class_weights_from_dataset(
    dataset,
    label2id: Dict[str, int],
    method: str = 'inverse_freq'
) -> torch.Tensor:
    """
    Compute class weights by scanning the dataset.

    Args:
        dataset: NERDataset instance
        label2id: Label to ID mapping
        method: Weighting method

    Returns:
        Class weights tensor
    """
    id2label = {v: k for k, v in label2id.items()}
    label_counts = Counter()

    # Count labels across all samples
    for i in range(len(dataset)):
        item = dataset[i]
        labels = item['labels']

        for label_id in labels.tolist():
            if label_id != -100:  # Skip ignored tokens
                label = id2label.get(label_id, 'O')
                label_counts[label] += 1

    logger.info(f"Label distribution: {dict(label_counts.most_common(10))}")

    return compute_class_weights(label_counts, label2id, method=method)


# ============================================================================
# NER-SPECIFIC LOSS HELPERS
# ============================================================================

def get_entity_aware_weights(
    label2id: Dict[str, int],
    o_weight: float = 0.3,
    b_weight: float = 2.0,
    i_weight: float = 1.5
) -> torch.Tensor:
    """
    Create weights that emphasize entity boundaries (B-) over continuations (I-) and O.

    For NER, B- labels are most important for detecting entity starts.

    Args:
        label2id: Label to ID mapping
        o_weight: Weight for O label (typically < 1 to down-weight)
        b_weight: Weight for B- labels (typically > 1)
        i_weight: Weight for I- labels (typically > 1 but < B-)

    Returns:
        Class weights tensor
    """
    num_classes = len(label2id)
    weights = torch.ones(num_classes)

    for label, label_id in label2id.items():
        if label == 'O':
            weights[label_id] = o_weight
        elif label.startswith('B-'):
            weights[label_id] = b_weight
        elif label.startswith('I-'):
            weights[label_id] = i_weight

    return weights


def create_ner_focal_loss(
    label2id: Dict[str, int],
    gamma: float = 2.0,
    label_counts: Optional[Dict[str, int]] = None,
    use_entity_aware_weights: bool = True
) -> FocalLoss:
    """
    Create a FocalLoss configured for NER.

    Args:
        label2id: Label to ID mapping
        gamma: Focusing parameter
        label_counts: Optional label distribution for class weights
        use_entity_aware_weights: Use entity-aware weighting if no counts provided

    Returns:
        Configured FocalLoss instance
    """
    num_classes = len(label2id)

    if label_counts:
        alpha = compute_class_weights(label_counts, label2id, method='inverse_freq')
    elif use_entity_aware_weights:
        alpha = get_entity_aware_weights(label2id)
    else:
        alpha = None

    return FocalLoss(
        num_classes=num_classes,
        gamma=gamma,
        alpha=alpha,
        reduction='mean',
        ignore_index=-100
    )


# ============================================================================
# DEMO / TESTING
# ============================================================================

if __name__ == '__main__':
    # Test focal loss
    print("Testing Focal Loss...")

    num_classes = 17  # Example: 8 entity types * 2 + O
    batch_size = 4
    seq_len = 128

    # Create random inputs
    inputs = torch.randn(batch_size, seq_len, num_classes)
    targets = torch.randint(0, num_classes, (batch_size, seq_len))
    targets[0, :10] = -100  # Some padding

    # Test standard focal loss
    focal_loss = FocalLoss(num_classes=num_classes, gamma=2.0)
    loss = focal_loss(inputs, targets)
    print(f"Focal Loss (gamma=2.0): {loss.item():.4f}")

    # Test with class weights
    weights = torch.rand(num_classes)
    focal_loss_weighted = FocalLoss(num_classes=num_classes, gamma=2.0, alpha=weights)
    loss_weighted = focal_loss_weighted(inputs, targets)
    print(f"Focal Loss (weighted): {loss_weighted.item():.4f}")

    # Test entity-aware weights
    label2id = {'O': 0}
    for i, entity in enumerate(['PERPETRATOR', 'VICTIM', 'EVENT_TYPE', 'WEAPON',
                                 'DATE', 'COUNTRY', 'CITY', 'CASUALTIES']):
        label2id[f'B-{entity}'] = i * 2 + 1
        label2id[f'I-{entity}'] = i * 2 + 2

    entity_weights = get_entity_aware_weights(label2id)
    print(f"\nEntity-aware weights:")
    print(f"  O: {entity_weights[0]:.2f}")
    print(f"  B-PERPETRATOR: {entity_weights[1]:.2f}")
    print(f"  I-PERPETRATOR: {entity_weights[2]:.2f}")

    # Test class weight computation
    label_counts = {
        'O': 100000,
        'B-PERPETRATOR': 5000,
        'I-PERPETRATOR': 3000,
        'B-VICTIM': 4000,
        'I-VICTIM': 2500,
        'B-COUNTRY': 6000,
        'I-COUNTRY': 1000,
        'B-CASUALTIES': 500,
        'I-CASUALTIES': 200,
    }

    computed_weights = compute_class_weights(label_counts, label2id)
    print(f"\nComputed class weights from distribution:")
    for label, label_id in sorted(label2id.items(), key=lambda x: x[1])[:5]:
        print(f"  {label}: {computed_weights[label_id]:.3f}")

    print("\nFocal Loss module OK!")
