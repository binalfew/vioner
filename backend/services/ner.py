"""
NER Service for loading and running inference on the trained BERT model.

Enhanced with:
- Entity merging post-processing (joins fragmented entities)
- Confidence-based filtering (removes low-confidence predictions)
- Multi-event extraction (handles compound texts)
"""

import torch
import re
from transformers import AutoTokenizer, AutoModelForTokenClassification
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class NERService:
    """
    Service for loading and running the trained BERT NER model.

    The model extracts entities from violent event text and structures
    them into 5W1H format (Who, Whom, What, When, Where, How).
    Based on VIONER_GUIDELINES.md.
    """

    # 5W1H category mapping - MUST match pipeline/config.py LabelConfigs
    # Total: 8 entity types across 6 categories (optimized for grounding)
    CATEGORY_MAPPING = {
        # WHO: All actors merged (1 type)
        'WHO': ['ACTOR'],

        # WHOM: Victims (1 type)
        'WHOM': ['VICTIM'],

        # WHAT: Actions only (1 type) - EVENT_TYPE handled by taxonomy classifier
        'WHAT': ['ACTION'],

        # WHEN: Temporal information (1 type)
        'WHEN': ['DATE'],

        # WHERE: Location hierarchy (3 types) - COUNTRY removed
        'WHERE': ['REGION', 'CITY', 'DISTRICT'],

        # HOW: Impact (1 type)
        'HOW': ['CASUALTIES'],
    }

    # Confidence thresholds per category (for filtering low-confidence predictions)
    CONFIDENCE_THRESHOLDS = {
        'WHO': 0.7,      # Actors need high confidence
        'WHOM': 0.7,     # Victims need high confidence
        'WHAT': 0.6,     # Events can be more flexible
        'WHEN': 0.8,     # Dates should be precise
        'WHERE': 0.7,    # Locations need good confidence
        'HOW': 0.75,     # Impact metrics should be reliable
    }

    def __init__(self, model_path: str, device: str = "cpu"):
        """
        Initialize the NER service.

        Args:
            model_path: Path to the trained model directory
            device: Device to run inference on ('cpu', 'cuda', 'mps')
        """
        self.model_path = Path(model_path)
        self.device = self._get_device(device)
        self.model: Optional[AutoModelForTokenClassification] = None
        self.tokenizer: Optional[AutoTokenizer] = None
        self.id2label: Dict[int, str] = {}
        self.label2id: Dict[str, int] = {}
        self.loaded_at: Optional[datetime] = None
        self._is_loaded = False

    def _get_device(self, device: str) -> torch.device:
        """Determine the appropriate device for inference."""
        if device == "mps" and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return torch.device("mps")
        elif device == "cuda" and torch.cuda.is_available():
            return torch.device("cuda")
        return torch.device("cpu")

    def load(self) -> None:
        """Load the model and tokenizer from the checkpoint."""
        logger.info(f"Loading model from: {self.model_path}")

        if not self.model_path.exists():
            raise FileNotFoundError(f"Model path does not exist: {self.model_path}")

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(str(self.model_path))

        # Load model
        self.model = AutoModelForTokenClassification.from_pretrained(str(self.model_path))
        self.model.to(self.device)
        self.model.eval()

        # Extract label mappings from model config
        self.id2label = {int(k): v for k, v in self.model.config.id2label.items()}
        self.label2id = {v: int(k) for k, v in self.model.config.id2label.items()}

        self._is_loaded = True
        self.loaded_at = datetime.utcnow()

        logger.info(f"Model loaded successfully on {self.device}")
        logger.info(f"Number of labels: {len(self.id2label)}")

    def is_loaded(self) -> bool:
        """Check if the model is loaded."""
        return self._is_loaded and self.model is not None and self.tokenizer is not None

    def extract(self, text: str) -> Dict:
        """
        Extract entities from text and structure in 5W1H format.

        Args:
            text: Input text to analyze

        Returns:
            Dictionary containing:
                - entities: List of extracted entities with labels and confidence
                - structured_event: 5W1H structured output
                - confidence_scores: Average confidence per category
        """
        if not self.is_loaded():
            raise RuntimeError("Model not loaded. Call load() first.")

        # Tokenize the text
        encoding = self.tokenizer(
            text,
            return_tensors='pt',
            truncation=True,
            max_length=512,
            padding=True,
            return_offsets_mapping=True
        )

        # Get offset mapping before moving to device
        offset_mapping = encoding.pop('offset_mapping')[0].tolist()

        # Move to device
        inputs = {k: v.to(self.device) for k, v in encoding.items()}

        # Run inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.argmax(outputs.logits, dim=-1)
            probs = torch.softmax(outputs.logits, dim=-1)

        # Extract entities from predictions
        entities = self._extract_entities(
            text,
            predictions[0].tolist(),
            probs[0].tolist(),
            offset_mapping
        )

        # Structure into 5W1H format
        structured = self._structure_5w1h(entities)

        # Calculate confidence scores per category
        confidence_scores = self._calculate_confidence(entities)

        return {
            'entities': entities,
            'structured_event': structured,
            'confidence_scores': confidence_scores
        }

    def _extract_entities(
        self,
        text: str,
        predictions: List[int],
        probs: List[List[float]],
        offset_mapping: List[Tuple[int, int]]
    ) -> List[Dict]:
        """
        Extract entity spans from BIO-tagged predictions.

        Args:
            text: Original input text
            predictions: List of predicted label IDs
            probs: Probability distributions for each token
            offset_mapping: Character offsets for each token

        Returns:
            List of entity dictionaries
        """
        entities = []
        current_entity_tokens = []
        current_entity_type = None
        current_confidences = []
        current_start = None

        for idx, (pred_id, token_probs, (start, end)) in enumerate(
            zip(predictions, probs, offset_mapping)
        ):
            # Skip special tokens (offset 0,0)
            if start == 0 and end == 0:
                continue

            label = self.id2label.get(pred_id, 'O')
            confidence = token_probs[pred_id]

            if label.startswith('B-'):
                # Save previous entity if exists
                if current_entity_type and current_entity_tokens:
                    entities.append(self._create_entity(
                        text, current_start, current_entity_tokens[-1][1],
                        current_entity_type, current_confidences
                    ))

                # Start new entity
                current_entity_type = label[2:]  # Remove "B-" prefix
                current_entity_tokens = [(start, end)]
                current_confidences = [confidence]
                current_start = start

            elif label.startswith('I-') and current_entity_type == label[2:]:
                # Continue current entity
                current_entity_tokens.append((start, end))
                current_confidences.append(confidence)

            else:
                # O label or mismatched I- label
                if current_entity_type and current_entity_tokens:
                    entities.append(self._create_entity(
                        text, current_start, current_entity_tokens[-1][1],
                        current_entity_type, current_confidences
                    ))
                current_entity_type = None
                current_entity_tokens = []
                current_confidences = []
                current_start = None

        # Don't forget the last entity
        if current_entity_type and current_entity_tokens:
            entities.append(self._create_entity(
                text, current_start, current_entity_tokens[-1][1],
                current_entity_type, current_confidences
            ))

        return entities

    def _create_entity(
        self,
        text: str,
        start: int,
        end: int,
        label: str,
        confidences: List[float]
    ) -> Dict:
        """Create an entity dictionary."""
        entity_text = text[start:end].strip()
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        return {
            'text': entity_text,
            'label': label,
            'start': start,
            'end': end,
            'confidence': round(avg_confidence, 4)
        }

    def _structure_5w1h(self, entities: List[Dict]) -> Dict[str, List[str]]:
        """
        Map entities to 5W1H structure.

        Args:
            entities: List of extracted entities

        Returns:
            Dictionary with who, whom, what, when, where, how keys
        """
        structured = {
            'who': [],
            'whom': [],
            'what': [],
            'when': [],
            'where': [],
            'how': [],
        }

        for entity in entities:
            label = entity['label']
            text = entity['text']

            # Skip empty text
            if not text:
                continue

            # Find which 5W1H category this label belongs to
            for category, labels in self.CATEGORY_MAPPING.items():
                if label in labels:
                    key = category.lower()
                    # Avoid duplicates
                    if text not in structured[key]:
                        structured[key].append(text)
                    break

        return structured

    def _calculate_confidence(self, entities: List[Dict]) -> Dict[str, float]:
        """
        Calculate average confidence score per 5W1H category.

        Args:
            entities: List of extracted entities

        Returns:
            Dictionary mapping category to average confidence
        """
        category_confidences = {k.lower(): [] for k in self.CATEGORY_MAPPING}

        for entity in entities:
            label = entity['label']
            confidence = entity['confidence']

            for category, labels in self.CATEGORY_MAPPING.items():
                if label in labels:
                    category_confidences[category.lower()].append(confidence)
                    break

        # Calculate averages, only for categories with entities
        return {
            k: round(sum(v) / len(v), 4)
            for k, v in category_confidences.items()
            if v
        }

    def get_info(self) -> Dict:
        """Get information about the loaded model."""
        return {
            'model_path': str(self.model_path),
            'model_type': 'BertForTokenClassification',
            'num_labels': len(self.id2label),
            'device': str(self.device),
            'loaded': self._is_loaded,
            'loaded_at': self.loaded_at.isoformat() if self.loaded_at else None,
            'labels': list(self.id2label.values()) if self.id2label else []
        }

    def get_categories(self) -> Dict[str, List[str]]:
        """Get the 5W1H category to label mapping."""
        return self.CATEGORY_MAPPING.copy()

    # =========================================================================
    # PHASE 3: Entity Merging Post-Processing
    # =========================================================================

    def _merge_adjacent_entities(self, entities: List[Dict], text: str) -> List[Dict]:
        """
        Merge adjacent entities of the same type that were fragmented by tokenization.

        Examples:
        - "Al" + "-" + "Shabaab" → "Al-Shabaab"
        - "Boko" + "Haram" → "Boko Haram"
        - "South" + "Sudan" → "South Sudan" (if both tagged as COUNTRY)

        Args:
            entities: List of extracted entities
            text: Original text for context

        Returns:
            List of entities with adjacent same-type entities merged
        """
        if not entities or len(entities) < 2:
            return entities

        # Sort by start position
        sorted_entities = sorted(entities, key=lambda e: e['start'])
        merged = []
        i = 0

        while i < len(sorted_entities):
            current = sorted_entities[i].copy()

            # Try to merge with subsequent entities
            while i + 1 < len(sorted_entities):
                next_entity = sorted_entities[i + 1]

                # Check if they should be merged
                if self._should_merge_entities(current, next_entity, text):
                    # Merge entities
                    current = self._merge_two_entities(current, next_entity, text)
                    i += 1
                else:
                    break

            merged.append(current)
            i += 1

        return merged

    def _should_merge_entities(self, e1: Dict, e2: Dict, text: str) -> bool:
        """
        Determine if two entities should be merged.

        Criteria:
        1. Same entity type
        2. Adjacent or separated only by whitespace/punctuation
        3. Gap between them is small (< 3 characters)
        """
        # Must be same type
        if e1['label'] != e2['label']:
            return False

        # Check gap between entities
        gap_start = e1['end']
        gap_end = e2['start']
        gap = gap_end - gap_start

        # Allow no gap or small gap
        if gap < 0:
            return False  # Overlapping - shouldn't happen but handle it

        if gap == 0:
            return True  # Adjacent

        if gap > 3:
            return False  # Too far apart

        # Check what's in the gap
        gap_text = text[gap_start:gap_end]

        # Allow merging if gap is whitespace, hyphen, or apostrophe
        if re.match(r'^[\s\-\']+$', gap_text):
            return True

        return False

    def _merge_two_entities(self, e1: Dict, e2: Dict, text: str) -> Dict:
        """
        Merge two entities into one.

        Args:
            e1: First entity (earlier in text)
            e2: Second entity (later in text)
            text: Original text

        Returns:
            Merged entity
        """
        # Get the full span text from original
        merged_text = text[e1['start']:e2['end']]

        # Average the confidences, weighted by token count
        # (Approximated by text length)
        len1 = e1['end'] - e1['start']
        len2 = e2['end'] - e2['start']
        total_len = len1 + len2
        weighted_conf = (e1['confidence'] * len1 + e2['confidence'] * len2) / total_len

        return {
            'text': merged_text.strip(),
            'label': e1['label'],
            'start': e1['start'],
            'end': e2['end'],
            'confidence': round(weighted_conf, 4)
        }

    # =========================================================================
    # PHASE 3: Confidence-Based Filtering
    # =========================================================================

    def _filter_by_confidence(
        self,
        entities: List[Dict],
        use_category_thresholds: bool = True,
        global_threshold: float = 0.5
    ) -> List[Dict]:
        """
        Filter out low-confidence entity predictions.

        Args:
            entities: List of extracted entities
            use_category_thresholds: Use per-category thresholds from CONFIDENCE_THRESHOLDS
            global_threshold: Fallback threshold if category not found

        Returns:
            Filtered list of entities
        """
        filtered = []

        for entity in entities:
            threshold = global_threshold

            if use_category_thresholds:
                # Find the category for this entity type
                for category, labels in self.CATEGORY_MAPPING.items():
                    if entity['label'] in labels:
                        threshold = self.CONFIDENCE_THRESHOLDS.get(category, global_threshold)
                        break

            if entity['confidence'] >= threshold:
                filtered.append(entity)
            else:
                logger.debug(
                    f"Filtered low-confidence entity: '{entity['text']}' "
                    f"({entity['label']}, conf={entity['confidence']:.3f} < {threshold})"
                )

        return filtered

    def _remove_duplicate_entities(self, entities: List[Dict]) -> List[Dict]:
        """
        Remove duplicate entities (same text and label).

        Keeps the one with highest confidence.
        """
        seen: Dict[Tuple[str, str], Dict] = {}

        for entity in entities:
            key = (entity['text'].lower(), entity['label'])

            if key not in seen:
                seen[key] = entity
            elif entity['confidence'] > seen[key]['confidence']:
                seen[key] = entity

        return list(seen.values())

    # =========================================================================
    # PHASE 3: Multi-Event Extraction
    # =========================================================================

    def extract_multi_event(self, text: str) -> Dict:
        """
        Extract entities from text that may contain multiple events.

        This method:
        1. Segments text into individual events using event_segmentation
        2. Extracts entities from each segment
        3. Merges results with segment attribution

        Args:
            text: Input text potentially containing multiple events

        Returns:
            Dictionary containing:
                - entities: List of all entities with segment_index
                - segments: List of event segments
                - structured_events: List of 5W1H structures per segment
                - is_multi_event: Whether multiple events were detected
                - confidence_scores: Overall confidence per category
        """
        if not self.is_loaded():
            raise RuntimeError("Model not loaded. Call load() first.")

        # Import event segmentation module
        try:
            from pipeline.segmentation import EventSegmenter
            segmenter = EventSegmenter()
        except ImportError:
            logger.warning("Event segmentation module not available, using single-event extraction")
            result = self.extract(text)
            return {
                'entities': result['entities'],
                'segments': [{'text': text, 'index': 0}],
                'structured_events': [result['structured_event']],
                'is_multi_event': False,
                'confidence_scores': result['confidence_scores']
            }

        # Check if multi-event
        is_multi, multi_conf = segmenter.is_multi_event_text(text)

        if not is_multi:
            # Single event - use standard extraction
            result = self.extract(text)
            return {
                'entities': result['entities'],
                'segments': [{'text': text, 'index': 0, 'confidence': 1.0}],
                'structured_events': [result['structured_event']],
                'is_multi_event': False,
                'confidence_scores': result['confidence_scores']
            }

        # Multi-event - segment and extract from each
        segments = segmenter.segment_text(text)

        all_entities = []
        structured_events = []
        segment_infos = []

        for segment in segments:
            # Extract from this segment
            segment_result = self.extract(segment.text)

            # Adjust entity offsets to original text positions
            for entity in segment_result['entities']:
                adjusted_entity = entity.copy()
                adjusted_entity['start'] += segment.start_offset
                adjusted_entity['end'] += segment.start_offset
                adjusted_entity['segment_index'] = segment.segment_index
                all_entities.append(adjusted_entity)

            structured_events.append(segment_result['structured_event'])
            segment_infos.append({
                'text': segment.text,
                'index': segment.segment_index,
                'start_offset': segment.start_offset,
                'end_offset': segment.end_offset,
                'confidence': segment.confidence,
                'boundary_type': segment.boundary_type
            })

        # Calculate overall confidence
        overall_confidence = self._calculate_confidence(all_entities)

        return {
            'entities': all_entities,
            'segments': segment_infos,
            'structured_events': structured_events,
            'is_multi_event': True,
            'confidence_scores': overall_confidence
        }

    # =========================================================================
    # Enhanced Extract Method
    # =========================================================================

    def extract_enhanced(
        self,
        text: str,
        merge_entities: bool = True,
        filter_confidence: bool = True,
        handle_multi_event: bool = False
    ) -> Dict:
        """
        Enhanced extraction with optional post-processing.

        Args:
            text: Input text to analyze
            merge_entities: Whether to merge adjacent same-type entities
            filter_confidence: Whether to filter low-confidence entities
            handle_multi_event: Whether to detect and handle multiple events

        Returns:
            Dictionary with entities, structured_event, and confidence_scores
        """
        if handle_multi_event:
            return self.extract_multi_event(text)

        # Standard extraction
        if not self.is_loaded():
            raise RuntimeError("Model not loaded. Call load() first.")

        # Tokenize the text
        encoding = self.tokenizer(
            text,
            return_tensors='pt',
            truncation=True,
            max_length=512,
            padding=True,
            return_offsets_mapping=True
        )

        # Get offset mapping before moving to device
        offset_mapping = encoding.pop('offset_mapping')[0].tolist()

        # Move to device
        inputs = {k: v.to(self.device) for k, v in encoding.items()}

        # Run inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.argmax(outputs.logits, dim=-1)
            probs = torch.softmax(outputs.logits, dim=-1)

        # Extract entities from predictions
        entities = self._extract_entities(
            text,
            predictions[0].tolist(),
            probs[0].tolist(),
            offset_mapping
        )

        # Post-processing: Merge adjacent entities
        if merge_entities:
            entities = self._merge_adjacent_entities(entities, text)

        # Post-processing: Filter by confidence
        if filter_confidence:
            entities = self._filter_by_confidence(entities)

        # Remove duplicates
        entities = self._remove_duplicate_entities(entities)

        # Sort by position
        entities = sorted(entities, key=lambda e: e['start'])

        # Structure into 5W1H format
        structured = self._structure_5w1h(entities)

        # Calculate confidence scores per category
        confidence_scores = self._calculate_confidence(entities)

        return {
            'entities': entities,
            'structured_event': structured,
            'confidence_scores': confidence_scores
        }
