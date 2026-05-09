"""
Evaluation Service - Phase 6
Compute detailed per-entity metrics for NER models with 5W1H category analysis.

Author: Binalfew Kassa Mekonnen
Date: December 2025

Enhanced with:
- 5W1H category metrics (WHO, WHOM, WHAT, WHEN, WHERE, HOW)
- Error analysis report generation
- Domain-specific validation integration
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
from dataclasses import dataclass, asdict, field
from datetime import datetime
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification

logger = logging.getLogger(__name__)


# ============================================================================
# 5W1H CATEGORY MAPPING (8-entity schema optimized for grounding)
# ============================================================================

CATEGORY_5W1H = {
    'WHO': ['ACTOR'],
    'WHOM': ['VICTIM'],
    'WHAT': ['ACTION'],
    'WHEN': ['DATE'],
    'WHERE': ['REGION', 'CITY', 'DISTRICT'],
    'HOW': ['CASUALTIES'],
}

# Reverse mapping: entity type -> category
ENTITY_TO_CATEGORY = {}
for category, entities in CATEGORY_5W1H.items():
    for entity in entities:
        ENTITY_TO_CATEGORY[entity] = category


@dataclass
class EntityMetrics:
    """Metrics for a single entity type."""
    entity_type: str
    precision: float
    recall: float
    f1: float
    support: int  # Number of true entities
    predicted: int  # Number of predicted entities
    correct: int  # Number of correctly predicted entities
    category: str = ""  # 5W1H category


@dataclass
class CategoryMetrics:
    """Metrics for a 5W1H category."""
    category: str  # WHO, WHOM, WHAT, WHEN, WHERE, HOW
    precision: float
    recall: float
    f1: float
    support: int
    predicted: int
    correct: int
    entity_types: List[str] = field(default_factory=list)  # Entity types in this category
    entity_breakdown: Dict[str, Dict] = field(default_factory=dict)  # Per-entity metrics


@dataclass
class ConfusionEntry:
    """Entry in the confusion matrix."""
    true_label: str
    predicted_label: str
    count: int
    examples: List[Dict]  # Sample error texts


@dataclass
class ErrorExample:
    """An example of a prediction error."""
    text: str
    true_entities: List[Dict]
    predicted_entities: List[Dict]
    error_type: str  # 'false_positive', 'false_negative', 'wrong_type'
    entity_type: str


@dataclass
class ErrorAnalysis:
    """Detailed error analysis report."""
    total_errors: int
    false_positives: int
    false_negatives: int
    type_mismatches: int
    common_fp_patterns: List[Dict]  # Common false positive patterns
    common_fn_patterns: List[Dict]  # Common false negative patterns
    category_errors: Dict[str, Dict]  # Errors by 5W1H category
    difficult_examples: List[Dict]  # Examples with multiple errors
    recommendations: List[str]  # Suggested improvements


@dataclass
class EvaluationResult:
    """Complete evaluation result."""
    checkpoint_name: str
    epoch: Optional[int]
    total_samples: int
    overall_precision: float
    overall_recall: float
    overall_f1: float
    entity_metrics: List[EntityMetrics]
    category_metrics: List[CategoryMetrics]  # 5W1H category metrics
    confusion_matrix: List[ConfusionEntry]
    error_examples: List[ErrorExample]
    error_analysis: Optional[ErrorAnalysis]  # Detailed error analysis
    entity_distribution: Dict[str, int]
    timestamp: str = ""

    def to_dict(self) -> dict:
        return {
            'checkpoint_name': self.checkpoint_name,
            'epoch': self.epoch,
            'total_samples': self.total_samples,
            'overall_precision': self.overall_precision,
            'overall_recall': self.overall_recall,
            'overall_f1': self.overall_f1,
            'entity_metrics': [asdict(m) for m in self.entity_metrics],
            'category_metrics': [asdict(c) for c in self.category_metrics],
            'confusion_matrix': [asdict(c) for c in self.confusion_matrix],
            'error_examples': [asdict(e) for e in self.error_examples],
            'error_analysis': asdict(self.error_analysis) if self.error_analysis else None,
            'entity_distribution': self.entity_distribution,
            'timestamp': self.timestamp,
        }

    def get_category_summary(self) -> Dict[str, Dict]:
        """Get summary of metrics by 5W1H category."""
        return {
            cm.category: {
                'precision': cm.precision,
                'recall': cm.recall,
                'f1': cm.f1,
                'support': cm.support,
                'entity_types': cm.entity_types
            }
            for cm in self.category_metrics
        }

    def get_weakest_categories(self, n: int = 3) -> List[str]:
        """Get categories with lowest F1 scores."""
        sorted_cats = sorted(self.category_metrics, key=lambda x: x.f1)
        return [c.category for c in sorted_cats[:n]]

    def get_strongest_categories(self, n: int = 3) -> List[str]:
        """Get categories with highest F1 scores."""
        sorted_cats = sorted(self.category_metrics, key=lambda x: -x.f1)
        return [c.category for c in sorted_cats[:n]]


class EvaluationService:
    """Service for evaluating NER models on validation data."""

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.id2label = None
        self.label2id = None
        self.device = None
        self._loaded_checkpoint = None

    def _get_models_dir(self) -> Path:
        """Get models directory."""
        if Path('/app/models').exists():
            return Path('/app/models')
        return Path(__file__).parent.parent / 'models'

    def _get_data_dir(self) -> Path:
        """Get data directory."""
        if Path('/app/data').exists():
            return Path('/app/data')
        return Path(__file__).parent.parent.parent / 'data'

    def load_model(self, checkpoint_name: str, epoch: Optional[int] = None) -> bool:
        """Load model from checkpoint."""
        models_dir = self._get_models_dir()
        checkpoint_path = models_dir / checkpoint_name

        if not checkpoint_path.exists():
            logger.error(f"Checkpoint not found: {checkpoint_path}")
            return False

        # Determine which epoch to load
        if epoch is not None:
            model_path = checkpoint_path / f"epoch_{epoch:02d}"
        else:
            # Try 'best' first, then 'active'
            best_path = checkpoint_path / "best"
            if best_path.exists():
                model_path = best_path
            else:
                # Find latest epoch
                epochs = sorted([d for d in checkpoint_path.iterdir()
                               if d.is_dir() and d.name.startswith("epoch_")])
                if not epochs:
                    logger.error(f"No epochs found in checkpoint: {checkpoint_path}")
                    return False
                model_path = epochs[-1]

        if not model_path.exists():
            logger.error(f"Model path not found: {model_path}")
            return False

        try:
            logger.info(f"Loading model from: {model_path}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForTokenClassification.from_pretrained(model_path)

            # Get label mappings
            self.id2label = self.model.config.id2label
            self.label2id = self.model.config.label2id

            # Set device
            if torch.cuda.is_available():
                self.device = torch.device("cuda")
            elif torch.backends.mps.is_available():
                self.device = torch.device("mps")
            else:
                self.device = torch.device("cpu")

            self.model.to(self.device)
            self.model.eval()
            self._loaded_checkpoint = (checkpoint_name, epoch)

            logger.info(f"Model loaded successfully on {self.device}")
            return True

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False

    def _predict_tokens(self, tokens: List[str]) -> Tuple[List[str], List[float]]:
        """Predict labels for tokens."""
        # Tokenize with word IDs tracking
        encoding = self.tokenizer(
            tokens,
            is_split_into_words=True,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        )

        word_ids = encoding.word_ids()

        # Run inference
        with torch.no_grad():
            encoding = {k: v.to(self.device) for k, v in encoding.items()}
            outputs = self.model(**encoding)
            predictions = torch.argmax(outputs.logits, dim=-1)[0]
            probabilities = torch.softmax(outputs.logits, dim=-1)[0]

        # Map back to word-level predictions
        predicted_labels = []
        confidences = []
        previous_word_id = None

        for idx, word_id in enumerate(word_ids):
            if word_id is None:
                continue
            if word_id != previous_word_id:
                pred_id = predictions[idx].item()
                label = self.id2label.get(pred_id, "O")
                confidence = probabilities[idx][pred_id].item()
                predicted_labels.append(label)
                confidences.append(confidence)
            previous_word_id = word_id

        return predicted_labels, confidences

    def _extract_entities(self, tokens: List[str], labels: List[str]) -> List[Dict]:
        """Extract entity spans from BIO labels."""
        entities = []
        current_entity = None
        current_tokens = []
        current_start = 0

        char_offset = 0
        for i, (token, label) in enumerate(zip(tokens, labels)):
            if label.startswith("B-"):
                # Save previous entity
                if current_entity:
                    entities.append({
                        'text': ' '.join(current_tokens),
                        'type': current_entity,
                        'start': current_start,
                        'end': char_offset
                    })
                # Start new entity
                current_entity = label[2:]
                current_tokens = [token]
                current_start = char_offset
            elif label.startswith("I-") and current_entity == label[2:]:
                current_tokens.append(token)
            else:
                if current_entity:
                    entities.append({
                        'text': ' '.join(current_tokens),
                        'type': current_entity,
                        'start': current_start,
                        'end': char_offset
                    })
                    current_entity = None
                    current_tokens = []

            char_offset += len(token) + 1

        # Don't forget last entity
        if current_entity:
            entities.append({
                'text': ' '.join(current_tokens),
                'type': current_entity,
                'start': current_start,
                'end': char_offset
            })

        return entities

    def _compute_entity_metrics(
        self,
        true_entities_list: List[List[Dict]],
        pred_entities_list: List[List[Dict]]
    ) -> Tuple[Dict[str, EntityMetrics], float, float, float]:
        """Compute per-entity type metrics."""
        # Count per entity type
        true_counts = defaultdict(int)
        pred_counts = defaultdict(int)
        correct_counts = defaultdict(int)

        for true_entities, pred_entities in zip(true_entities_list, pred_entities_list):
            # Create sets of (text, type) for comparison
            true_set = {(e['text'].lower(), e['type']) for e in true_entities}
            pred_set = {(e['text'].lower(), e['type']) for e in pred_entities}

            for _, etype in true_set:
                true_counts[etype] += 1
            for _, etype in pred_set:
                pred_counts[etype] += 1
            for text, etype in true_set & pred_set:
                correct_counts[etype] += 1

        # Compute metrics per entity type
        all_types = set(true_counts.keys()) | set(pred_counts.keys())
        entity_metrics = {}

        total_correct = 0
        total_true = 0
        total_pred = 0

        for etype in sorted(all_types):
            true_c = true_counts[etype]
            pred_c = pred_counts[etype]
            correct_c = correct_counts[etype]

            precision = correct_c / pred_c if pred_c > 0 else 0.0
            recall = correct_c / true_c if true_c > 0 else 0.0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

            # Get 5W1H category
            category = ENTITY_TO_CATEGORY.get(etype, 'OTHER')

            entity_metrics[etype] = EntityMetrics(
                entity_type=etype,
                precision=round(precision, 4),
                recall=round(recall, 4),
                f1=round(f1, 4),
                support=true_c,
                predicted=pred_c,
                correct=correct_c,
                category=category
            )

            total_correct += correct_c
            total_true += true_c
            total_pred += pred_c

        # Overall metrics (micro-average)
        overall_precision = total_correct / total_pred if total_pred > 0 else 0.0
        overall_recall = total_correct / total_true if total_true > 0 else 0.0
        overall_f1 = 2 * overall_precision * overall_recall / (overall_precision + overall_recall) if (overall_precision + overall_recall) > 0 else 0.0

        return entity_metrics, overall_precision, overall_recall, overall_f1

    def _compute_category_metrics(
        self,
        entity_metrics: Dict[str, EntityMetrics]
    ) -> List[CategoryMetrics]:
        """Compute metrics aggregated by 5W1H category."""
        category_metrics = []

        for category, entity_types in CATEGORY_5W1H.items():
            # Aggregate metrics for this category
            total_support = 0
            total_predicted = 0
            total_correct = 0
            entity_breakdown = {}

            for etype in entity_types:
                if etype in entity_metrics:
                    em = entity_metrics[etype]
                    total_support += em.support
                    total_predicted += em.predicted
                    total_correct += em.correct
                    entity_breakdown[etype] = {
                        'precision': em.precision,
                        'recall': em.recall,
                        'f1': em.f1,
                        'support': em.support
                    }

            # Calculate category-level metrics
            precision = total_correct / total_predicted if total_predicted > 0 else 0.0
            recall = total_correct / total_support if total_support > 0 else 0.0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

            category_metrics.append(CategoryMetrics(
                category=category,
                precision=round(precision, 4),
                recall=round(recall, 4),
                f1=round(f1, 4),
                support=total_support,
                predicted=total_predicted,
                correct=total_correct,
                entity_types=[et for et in entity_types if et in entity_metrics],
                entity_breakdown=entity_breakdown
            ))

        return category_metrics

    def _generate_error_analysis(
        self,
        true_entities_list: List[List[Dict]],
        pred_entities_list: List[List[Dict]],
        texts: List[str],
        entity_metrics: Dict[str, EntityMetrics]
    ) -> ErrorAnalysis:
        """Generate detailed error analysis report."""
        total_fp = 0
        total_fn = 0
        total_type_mismatch = 0

        fp_patterns = defaultdict(int)
        fn_patterns = defaultdict(int)
        category_errors = {cat: {'fp': 0, 'fn': 0, 'total': 0} for cat in CATEGORY_5W1H}
        difficult_examples = []

        for text, true_entities, pred_entities in zip(texts, true_entities_list, pred_entities_list):
            true_dict = {e['text'].lower(): e['type'] for e in true_entities}
            pred_dict = {e['text'].lower(): e['type'] for e in pred_entities}

            sample_errors = 0

            # Check false positives (predicted but not true)
            for entity_text, pred_type in pred_dict.items():
                true_type = true_dict.get(entity_text)
                if true_type is None:
                    total_fp += 1
                    sample_errors += 1
                    fp_patterns[pred_type] += 1
                    cat = ENTITY_TO_CATEGORY.get(pred_type, 'OTHER')
                    if cat in category_errors:
                        category_errors[cat]['fp'] += 1
                        category_errors[cat]['total'] += 1
                elif true_type != pred_type:
                    total_type_mismatch += 1
                    sample_errors += 1

            # Check false negatives (true but not predicted)
            for entity_text, true_type in true_dict.items():
                if entity_text not in pred_dict:
                    total_fn += 1
                    sample_errors += 1
                    fn_patterns[true_type] += 1
                    cat = ENTITY_TO_CATEGORY.get(true_type, 'OTHER')
                    if cat in category_errors:
                        category_errors[cat]['fn'] += 1
                        category_errors[cat]['total'] += 1

            # Track difficult examples (multiple errors)
            if sample_errors >= 3:
                difficult_examples.append({
                    'text': text[:200] + ('...' if len(text) > 200 else ''),
                    'error_count': sample_errors,
                    'true_entities': [{'text': e['text'], 'type': e['type']} for e in true_entities],
                    'pred_entities': [{'text': e['text'], 'type': e['type']} for e in pred_entities]
                })

        # Sort patterns by frequency
        common_fp = [{'entity_type': k, 'count': v} for k, v in sorted(fp_patterns.items(), key=lambda x: -x[1])[:10]]
        common_fn = [{'entity_type': k, 'count': v} for k, v in sorted(fn_patterns.items(), key=lambda x: -x[1])[:10]]

        # Sort difficult examples by error count
        difficult_examples = sorted(difficult_examples, key=lambda x: -x['error_count'])[:20]

        # Generate recommendations
        recommendations = self._generate_recommendations(
            entity_metrics, common_fp, common_fn, category_errors
        )

        return ErrorAnalysis(
            total_errors=total_fp + total_fn + total_type_mismatch,
            false_positives=total_fp,
            false_negatives=total_fn,
            type_mismatches=total_type_mismatch,
            common_fp_patterns=common_fp,
            common_fn_patterns=common_fn,
            category_errors=category_errors,
            difficult_examples=difficult_examples,
            recommendations=recommendations
        )

    def _generate_recommendations(
        self,
        entity_metrics: Dict[str, EntityMetrics],
        common_fp: List[Dict],
        common_fn: List[Dict],
        category_errors: Dict[str, Dict]
    ) -> List[str]:
        """Generate actionable recommendations based on error analysis."""
        recommendations = []

        # Find entity types with lowest F1
        low_f1_types = [
            (et, em.f1) for et, em in entity_metrics.items()
            if em.support >= 10 and em.f1 < 0.5
        ]
        low_f1_types.sort(key=lambda x: x[1])

        if low_f1_types:
            types_str = ', '.join([f"{t[0]} (F1={t[1]:.2f})" for t in low_f1_types[:3]])
            recommendations.append(
                f"Focus on improving: {types_str}. Consider adding more training examples for these entity types."
            )

        # Check for high false positive rates
        high_fp_types = [p['entity_type'] for p in common_fp if p['count'] > 50]
        if high_fp_types:
            recommendations.append(
                f"High false positive rate for: {', '.join(high_fp_types[:3])}. "
                "Consider using higher confidence thresholds or adding negative examples."
            )

        # Check for high false negative rates
        high_fn_types = [p['entity_type'] for p in common_fn if p['count'] > 50]
        if high_fn_types:
            recommendations.append(
                f"High false negative rate for: {', '.join(high_fn_types[:3])}. "
                "Consider lower confidence thresholds or additional data augmentation."
            )

        # Check category performance
        weak_categories = [
            (cat, data) for cat, data in category_errors.items()
            if data['total'] > 100
        ]
        weak_categories.sort(key=lambda x: -x[1]['total'])

        if weak_categories:
            cat_name = weak_categories[0][0]
            cat_errors = weak_categories[0][1]['total']
            recommendations.append(
                f"The '{cat_name}' category has the most errors ({cat_errors}). "
                f"Review entity types: {', '.join(CATEGORY_5W1H.get(cat_name, []))}."
            )

        # General recommendations
        if not recommendations:
            recommendations.append(
                "Model performance is balanced across entity types. "
                "Consider fine-tuning with domain-specific examples."
            )

        return recommendations

    def _build_confusion_matrix(
        self,
        true_entities_list: List[List[Dict]],
        pred_entities_list: List[List[Dict]],
        texts: List[str],
        max_examples: int = 3
    ) -> List[ConfusionEntry]:
        """Build confusion matrix with example errors."""
        confusion = defaultdict(lambda: {'count': 0, 'examples': []})

        for text, true_entities, pred_entities in zip(texts, true_entities_list, pred_entities_list):
            true_map = {e['text'].lower(): e['type'] for e in true_entities}
            pred_map = {e['text'].lower(): e['type'] for e in pred_entities}

            all_texts = set(true_map.keys()) | set(pred_map.keys())

            for entity_text in all_texts:
                true_type = true_map.get(entity_text, 'O')
                pred_type = pred_map.get(entity_text, 'O')

                if true_type != pred_type:
                    key = (true_type, pred_type)
                    confusion[key]['count'] += 1
                    if len(confusion[key]['examples']) < max_examples:
                        confusion[key]['examples'].append({
                            'text': text[:200] + ('...' if len(text) > 200 else ''),
                            'entity': entity_text
                        })

        # Convert to list
        entries = []
        for (true_label, pred_label), data in sorted(confusion.items(), key=lambda x: -x[1]['count']):
            entries.append(ConfusionEntry(
                true_label=true_label,
                predicted_label=pred_label,
                count=data['count'],
                examples=data['examples']
            ))

        return entries[:50]  # Top 50 confusion pairs

    def _collect_error_examples(
        self,
        true_entities_list: List[List[Dict]],
        pred_entities_list: List[List[Dict]],
        texts: List[str],
        max_per_type: int = 5
    ) -> List[ErrorExample]:
        """Collect representative error examples."""
        errors_by_type = defaultdict(list)

        for text, true_entities, pred_entities in zip(texts, true_entities_list, pred_entities_list):
            true_set = {(e['text'].lower(), e['type']) for e in true_entities}
            pred_set = {(e['text'].lower(), e['type']) for e in pred_entities}

            # False negatives (missed entities)
            for entity_text, etype in true_set - pred_set:
                if len(errors_by_type[f'fn_{etype}']) < max_per_type:
                    errors_by_type[f'fn_{etype}'].append(ErrorExample(
                        text=text[:300] + ('...' if len(text) > 300 else ''),
                        true_entities=[e for e in true_entities if e['text'].lower() == entity_text],
                        predicted_entities=[],
                        error_type='false_negative',
                        entity_type=etype
                    ))

            # False positives (extra entities)
            for entity_text, etype in pred_set - true_set:
                if len(errors_by_type[f'fp_{etype}']) < max_per_type:
                    errors_by_type[f'fp_{etype}'].append(ErrorExample(
                        text=text[:300] + ('...' if len(text) > 300 else ''),
                        true_entities=[],
                        predicted_entities=[e for e in pred_entities if e['text'].lower() == entity_text],
                        error_type='false_positive',
                        entity_type=etype
                    ))

        # Flatten and limit
        all_errors = []
        for errors in errors_by_type.values():
            all_errors.extend(errors)

        return all_errors[:100]  # Max 100 examples

    def evaluate(
        self,
        checkpoint_name: str,
        epoch: Optional[int] = None,
        max_samples: Optional[int] = None,
        include_error_analysis: bool = True
    ) -> Optional[EvaluationResult]:
        """
        Run full evaluation on validation data.

        Args:
            checkpoint_name: Name of checkpoint to evaluate
            epoch: Specific epoch to evaluate (None for best)
            max_samples: Limit evaluation to N samples
            include_error_analysis: Generate detailed error analysis

        Returns:
            EvaluationResult with metrics, category analysis, and errors
        """
        # Load model if needed
        if self._loaded_checkpoint != (checkpoint_name, epoch):
            if not self.load_model(checkpoint_name, epoch):
                return None

        # Load validation data
        val_path = self._get_data_dir() / 'processed' / 'val.json'
        if not val_path.exists():
            logger.error(f"Validation data not found: {val_path}")
            return None

        with open(val_path, 'r', encoding='utf-8') as f:
            val_data = json.load(f)

        if max_samples:
            val_data = val_data[:max_samples]

        logger.info(f"Evaluating on {len(val_data)} samples...")

        # Run predictions
        true_entities_list = []
        pred_entities_list = []
        texts = []
        entity_distribution = defaultdict(int)

        for i, sample in enumerate(val_data):
            if i % 1000 == 0:
                logger.info(f"Processing sample {i}/{len(val_data)}")

            tokens = sample['tokens']
            true_labels = sample['labels']
            text = sample['text']

            # Get predictions
            pred_labels, _ = self._predict_tokens(tokens)

            # Ensure same length
            min_len = min(len(tokens), len(true_labels), len(pred_labels))
            tokens = tokens[:min_len]
            true_labels = true_labels[:min_len]
            pred_labels = pred_labels[:min_len]

            # Extract entities
            true_entities = self._extract_entities(tokens, true_labels)
            pred_entities = self._extract_entities(tokens, pred_labels)

            true_entities_list.append(true_entities)
            pred_entities_list.append(pred_entities)
            texts.append(text)

            # Count entity distribution
            for e in true_entities:
                entity_distribution[e['type']] += 1

        # Compute metrics
        entity_metrics, overall_p, overall_r, overall_f1 = self._compute_entity_metrics(
            true_entities_list, pred_entities_list
        )

        # Compute 5W1H category metrics
        category_metrics = self._compute_category_metrics(entity_metrics)

        # Build confusion matrix
        confusion_matrix = self._build_confusion_matrix(
            true_entities_list, pred_entities_list, texts
        )

        # Collect error examples
        error_examples = self._collect_error_examples(
            true_entities_list, pred_entities_list, texts
        )

        # Generate detailed error analysis
        error_analysis = None
        if include_error_analysis:
            error_analysis = self._generate_error_analysis(
                true_entities_list, pred_entities_list, texts, entity_metrics
            )

        result = EvaluationResult(
            checkpoint_name=checkpoint_name,
            epoch=epoch,
            total_samples=len(val_data),
            overall_precision=round(overall_p, 4),
            overall_recall=round(overall_r, 4),
            overall_f1=round(overall_f1, 4),
            entity_metrics=list(entity_metrics.values()),
            category_metrics=category_metrics,
            confusion_matrix=confusion_matrix,
            error_examples=error_examples,
            error_analysis=error_analysis,
            entity_distribution=dict(entity_distribution),
            timestamp=datetime.now().isoformat()
        )

        # Log category summary
        logger.info(f"Evaluation complete: Overall F1={overall_f1:.4f}")
        logger.info("5W1H Category Performance:")
        for cm in category_metrics:
            if cm.support > 0:
                logger.info(f"  {cm.category}: F1={cm.f1:.4f} (support={cm.support})")

        return result

    def generate_report(
        self,
        result: EvaluationResult,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate a human-readable evaluation report.

        Args:
            result: EvaluationResult from evaluate()
            output_path: Optional path to save report

        Returns:
            Report as string
        """
        lines = []
        lines.append("=" * 70)
        lines.append("NER MODEL EVALUATION REPORT")
        lines.append("=" * 70)
        lines.append(f"Checkpoint: {result.checkpoint_name}")
        lines.append(f"Epoch: {result.epoch if result.epoch else 'best'}")
        lines.append(f"Samples: {result.total_samples}")
        lines.append(f"Timestamp: {result.timestamp}")
        lines.append("")

        # Overall metrics
        lines.append("-" * 70)
        lines.append("OVERALL METRICS")
        lines.append("-" * 70)
        lines.append(f"Precision: {result.overall_precision:.4f}")
        lines.append(f"Recall:    {result.overall_recall:.4f}")
        lines.append(f"F1 Score:  {result.overall_f1:.4f}")
        lines.append("")

        # 5W1H Category metrics
        lines.append("-" * 70)
        lines.append("5W1H CATEGORY METRICS")
        lines.append("-" * 70)
        lines.append(f"{'Category':<10} {'Precision':<12} {'Recall':<12} {'F1':<12} {'Support':<10}")
        lines.append("-" * 56)

        for cm in sorted(result.category_metrics, key=lambda x: -x.f1):
            lines.append(
                f"{cm.category:<10} {cm.precision:<12.4f} {cm.recall:<12.4f} "
                f"{cm.f1:<12.4f} {cm.support:<10}"
            )

        lines.append("")

        # Per-entity metrics (top 10 by support)
        lines.append("-" * 70)
        lines.append("PER-ENTITY TYPE METRICS (Top 10 by support)")
        lines.append("-" * 70)
        lines.append(
            f"{'Entity':<20} {'Category':<8} {'Precision':<10} "
            f"{'Recall':<10} {'F1':<10} {'Support':<8}"
        )
        lines.append("-" * 66)

        sorted_entities = sorted(result.entity_metrics, key=lambda x: -x.support)[:10]
        for em in sorted_entities:
            lines.append(
                f"{em.entity_type:<20} {em.category:<8} {em.precision:<10.4f} "
                f"{em.recall:<10.4f} {em.f1:<10.4f} {em.support:<8}"
            )

        lines.append("")

        # Error analysis
        if result.error_analysis:
            ea = result.error_analysis
            lines.append("-" * 70)
            lines.append("ERROR ANALYSIS")
            lines.append("-" * 70)
            lines.append(f"Total errors: {ea.total_errors}")
            lines.append(f"  False positives: {ea.false_positives}")
            lines.append(f"  False negatives: {ea.false_negatives}")
            lines.append(f"  Type mismatches: {ea.type_mismatches}")
            lines.append("")

            if ea.common_fp_patterns:
                lines.append("Common False Positive Types:")
                for p in ea.common_fp_patterns[:5]:
                    lines.append(f"  - {p['entity_type']}: {p['count']} occurrences")
                lines.append("")

            if ea.common_fn_patterns:
                lines.append("Common False Negative Types:")
                for p in ea.common_fn_patterns[:5]:
                    lines.append(f"  - {p['entity_type']}: {p['count']} occurrences")
                lines.append("")

            lines.append("-" * 70)
            lines.append("RECOMMENDATIONS")
            lines.append("-" * 70)
            for i, rec in enumerate(ea.recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")

        lines.append("=" * 70)
        lines.append("END OF REPORT")
        lines.append("=" * 70)

        report = "\n".join(lines)

        if output_path:
            with open(output_path, 'w') as f:
                f.write(report)
            logger.info(f"Report saved to: {output_path}")

        return report


# Singleton instance
_evaluation_service: Optional[EvaluationService] = None


def get_evaluation_service() -> EvaluationService:
    """Get or create evaluation service singleton."""
    global _evaluation_service
    if _evaluation_service is None:
        _evaluation_service = EvaluationService()
    return _evaluation_service
