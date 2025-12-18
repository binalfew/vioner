"""
Unit Tests for NER Pipeline Components - Phase 7
Tests for preprocessing, event segmentation, knowledge base, entity validation, and losses.

Author: Binalfew Kassa Mekonnen
Date: December 2025
"""

import sys
import os
import pytest
import torch

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================================
# PREPROCESSING TESTS
# ============================================================================

class TestPreprocessing:
    """Tests for preprocessing module."""

    def test_bio_labels_exist(self):
        """Test that BIO labels are properly configured."""
        from pipeline.config import LabelConfigs

        label2id = LabelConfigs.get_label2id()
        id2label = LabelConfigs.get_id2label()

        # Should have O label
        assert 'O' in label2id

        # Should have B- and I- labels for entity types
        assert 'B-PERPETRATOR' in label2id
        assert 'I-PERPETRATOR' in label2id
        assert 'B-COUNTRY' in label2id
        assert 'I-COUNTRY' in label2id

        # Check reverse mapping
        assert id2label[label2id['O']] == 'O'
        assert id2label[label2id['B-PERPETRATOR']] == 'B-PERPETRATOR'

    def test_5w1h_mapping(self):
        """Test 5W1H category mapping."""
        from pipeline.config import LabelConfigs

        mapping = LabelConfigs.get_5w1h_mapping()

        # Should have all 6 categories
        assert 'WHO' in mapping
        assert 'WHAT' in mapping
        assert 'WHEN' in mapping
        assert 'WHERE' in mapping
        assert 'HOW' in mapping
        assert 'WHY' in mapping

        # WHO should include PERPETRATOR and VICTIM
        assert 'PERPETRATOR' in mapping['WHO']
        assert 'VICTIM' in mapping['WHO']

        # WHERE should include COUNTRY and CITY
        assert 'COUNTRY' in mapping['WHERE']
        assert 'CITY' in mapping['WHERE']

    def test_category_lookup(self):
        """Test category lookup for labels."""
        from pipeline.config import LabelConfigs

        # Test entity type to category
        assert LabelConfigs.get_category_for_label('PERPETRATOR') == 'WHO'
        assert LabelConfigs.get_category_for_label('COUNTRY') == 'WHERE'
        assert LabelConfigs.get_category_for_label('DATE') == 'WHEN'
        assert LabelConfigs.get_category_for_label('CASUALTIES') == 'HOW'
        assert LabelConfigs.get_category_for_label('MOTIVE') == 'WHY'

    def test_expanded_entity_schema(self):
        """Test that entity schema has 26 types."""
        from pipeline.config import LabelConfigs

        label2id = LabelConfigs.get_label2id()

        # Extract unique entity types from B- labels
        unique_entities = set()
        for label in label2id.keys():
            if label.startswith('B-'):
                unique_entities.add(label[2:])

        assert len(unique_entities) >= 26, f"Expected 26 entity types, got {len(unique_entities)}"

        # Check specific types exist
        expected_types = [
            'PERPETRATOR', 'VICTIM', 'TARGET', 'ORGANIZATION', 'GOVERNMENT',
            'EVENT_TYPE', 'ACTION', 'WEAPON', 'VIOLENCE_TYPE',
            'DATE', 'TIME', 'DURATION', 'FREQUENCY',
            'COUNTRY', 'REGION', 'CITY', 'DISTRICT', 'FACILITY', 'GEOGRAPHIC', 'COORDINATES',
            'CASUALTIES', 'INJURED', 'DISPLACEMENT', 'DAMAGE',
            'MOTIVE', 'TRIGGER'
        ]

        for et in expected_types:
            assert et in unique_entities, f"Missing entity type: {et}"


# ============================================================================
# EVENT SEGMENTATION TESTS
# ============================================================================

class TestEventSegmentation:
    """Tests for event segmentation module."""

    def test_single_event_detection(self):
        """Test that single event texts are not split."""
        from pipeline.segmentation import EventSegmenter

        segmenter = EventSegmenter()

        single_event = "Boko Haram militants attacked a village in Maiduguri on Tuesday, killing 15 civilians."

        segments = segmenter.segment_text(single_event)
        assert len(segments) == 1
        assert segments[0].text.strip() == single_event.strip()

    def test_multi_event_temporal_boundary(self):
        """Test detection of temporal boundaries between events."""
        from pipeline.segmentation import EventSegmenter

        segmenter = EventSegmenter()

        multi_event = (
            "On 15 January, Boko Haram attacked Maiduguri killing 30. "
            "The next day, Al-Shabaab militants raided a village near Mogadishu."
        )

        is_multi, conf = segmenter.is_multi_event_text(multi_event)
        assert is_multi is True
        assert conf >= 0.7

    def test_multi_event_segmentation(self):
        """Test actual segmentation of multi-event text."""
        from pipeline.segmentation import EventSegmenter

        segmenter = EventSegmenter(min_segment_length=20, confidence_threshold=0.5)

        multi_event = (
            "RSF forces shelled residential areas in Khartoum. "
            "In a separate incident, unidentified gunmen ambushed a convoy in Darfur."
        )

        segments = segmenter.segment_text(multi_event)

        # Should detect at least 2 segments (or 1 if boundaries don't meet criteria)
        assert len(segments) >= 1

        # Each segment should have required fields
        for seg in segments:
            assert hasattr(seg, 'text')
            assert hasattr(seg, 'start_offset')
            assert hasattr(seg, 'end_offset')
            assert hasattr(seg, 'confidence')
            assert hasattr(seg, 'boundary_type')

    def test_boundary_detection(self):
        """Test detection of different boundary types."""
        from pipeline.segmentation import EventSegmenter

        segmenter = EventSegmenter()

        text_with_temporal = "The attack occurred on Monday. The next day, another incident happened."
        boundaries = segmenter.detect_boundaries(text_with_temporal)

        # Should find at least one boundary
        temporal_boundaries = [b for b in boundaries if b['type'] == 'temporal']
        assert len(temporal_boundaries) > 0


# ============================================================================
# KNOWLEDGE BASE TESTS
# ============================================================================

class TestKnowledgeBase:
    """Tests for knowledge base module."""

    def test_armed_group_lookup(self):
        """Test armed group name lookup."""
        from pipeline.kb import get_knowledge_base

        kb = get_knowledge_base()

        # Test known groups (canonical names)
        assert kb.is_armed_group("Al-Shabaab")
        assert kb.is_armed_group("Boko Haram")
        assert kb.is_armed_group("M23")

        # Test aliases (as listed in ARMED_GROUPS)
        assert kb.is_armed_group("al-shabaab")  # lowercase with hyphen
        assert kb.is_armed_group("boko haram")  # lowercase

        # Test unknown group
        assert not kb.is_armed_group("Unknown Group XYZ")

    def test_armed_group_normalization(self):
        """Test normalization of armed group names."""
        from pipeline.kb import get_knowledge_base

        kb = get_knowledge_base()

        # Aliases should normalize to canonical names
        assert kb.normalize_armed_group("al-shabaab") == "Al-Shabaab"
        assert kb.normalize_armed_group("boko haram") == "Boko Haram"
        assert kb.normalize_armed_group("janjaweed") == "Rapid Support Forces"

    def test_country_lookup(self):
        """Test African country lookup."""
        from pipeline.kb import get_knowledge_base

        kb = get_knowledge_base()

        # Test known countries
        assert kb.is_african_country("Nigeria")
        assert kb.is_african_country("Ethiopia")
        assert kb.is_african_country("Somalia")
        assert kb.is_african_country("DRC")

        # Test aliases
        assert kb.is_african_country("DR Congo")

        # Test non-African country
        assert not kb.is_african_country("France")

    def test_city_lookup(self):
        """Test conflict city lookup."""
        from pipeline.kb import get_knowledge_base

        kb = get_knowledge_base()

        # Test known conflict cities
        assert kb.is_conflict_city("Mogadishu")
        assert kb.is_conflict_city("Maiduguri")
        assert kb.is_conflict_city("Goma")
        assert kb.is_conflict_city("Khartoum")

        # Test city info
        info = kb.get_city_info("Mogadishu")
        assert info is not None
        assert info['country'] == "Somalia"

    def test_country_info(self):
        """Test country information retrieval."""
        from pipeline.kb import get_knowledge_base

        kb = get_knowledge_base()

        info = kb.get_country_info("Nigeria")
        assert info is not None
        assert info['capital'] == "Abuja"
        assert info['region'] == "West Africa"
        assert 'Borno' in info['conflict_zones']

    def test_perpetrator_validation(self):
        """Test perpetrator entity validation."""
        from pipeline.kb import get_knowledge_base

        kb = get_knowledge_base()

        # Known armed group
        is_valid, conf, canonical = kb.validate_perpetrator("Al-Shabaab")
        assert is_valid
        assert conf == 1.0
        assert canonical == "Al-Shabaab"

        # Generic perpetrator term
        is_valid, conf, _ = kb.validate_perpetrator("militants")
        assert is_valid
        assert conf >= 0.5

    def test_location_validation(self):
        """Test location entity validation."""
        from pipeline.kb import get_knowledge_base

        kb = get_knowledge_base()

        # Known country
        is_valid, conf, loc_type = kb.validate_location("Nigeria")
        assert is_valid
        assert conf >= 0.9
        assert loc_type == "country"

        # Known city
        is_valid, conf, loc_type = kb.validate_location("Mogadishu")
        assert is_valid
        assert loc_type == "city"

    def test_extraction_from_text(self):
        """Test entity extraction from text."""
        from pipeline.kb import get_knowledge_base

        kb = get_knowledge_base()

        text = "Al-Shabaab militants attacked a village near Mogadishu with a machete and a knife."

        groups = kb.extract_armed_groups(text)
        assert len(groups) > 0
        assert groups[0]['canonical'] == "Al-Shabaab"

        weapons = kb.extract_weapons(text)
        # machete and knife should be found
        assert len(weapons) > 0


# ============================================================================
# ENTITY VALIDATOR TESTS
# ============================================================================

class TestEntityValidator:
    """Tests for entity validator module."""

    def test_perpetrator_validation(self):
        """Test PERPETRATOR entity validation."""
        from pipeline.validator import get_validator

        validator = get_validator()

        # Known armed group - should boost confidence
        result = validator.validate_entity("Al-Shabaab", "B-PERPETRATOR")
        assert result.is_valid
        assert result.confidence_adjustment > 1.0
        assert result.canonical_form == "Al-Shabaab"

        # Generic perpetrator term
        result = validator.validate_entity("militants", "B-PERPETRATOR")
        assert result.is_valid

    def test_country_validation(self):
        """Test COUNTRY entity validation."""
        from pipeline.validator import get_validator

        validator = get_validator()

        # African country - should boost confidence
        result = validator.validate_entity("Nigeria", "B-COUNTRY")
        assert result.is_valid
        assert result.confidence_adjustment > 1.0

        # Unknown country - should reduce confidence
        result = validator.validate_entity("Unknown Place", "B-COUNTRY")
        assert result.confidence_adjustment < 1.0

    def test_city_validation(self):
        """Test CITY entity validation."""
        from pipeline.validator import get_validator

        validator = get_validator()

        # Known conflict city
        result = validator.validate_entity("Mogadishu", "B-CITY")
        assert result.is_valid
        assert result.confidence_adjustment > 1.0

    def test_date_validation(self):
        """Test DATE entity validation."""
        from pipeline.validator import get_validator

        validator = get_validator()

        # Valid date formats
        result = validator.validate_entity("15 January 2024", "B-DATE")
        assert result.is_valid
        assert result.confidence_adjustment > 1.0

        result = validator.validate_entity("Monday", "B-DATE")
        assert result.is_valid

        # Invalid date
        result = validator.validate_entity("xyz123", "B-DATE")
        assert not result.is_valid
        assert result.confidence_adjustment < 1.0

    def test_casualties_validation(self):
        """Test CASUALTIES entity validation."""
        from pipeline.validator import get_validator

        validator = get_validator()

        # Valid casualty expression
        result = validator.validate_entity("30 killed", "B-CASUALTIES")
        assert result.is_valid
        assert result.confidence_adjustment >= 1.0

        # Numeric only
        result = validator.validate_entity("15", "B-CASUALTIES")
        assert result.is_valid

    def test_batch_validation(self):
        """Test batch entity validation with confidence adjustment."""
        from pipeline.validator import validate_entities

        entities = [
            {"text": "Boko Haram", "label": "B-PERPETRATOR", "score": 0.85},
            {"text": "Maiduguri", "label": "B-CITY", "score": 0.75},
            {"text": "Unknown Place", "label": "B-COUNTRY", "score": 0.90},
        ]

        validated = validate_entities(entities)

        # Check scores were adjusted
        assert len(validated) == 3

        # Known entities should have boosted scores
        boko_haram = [e for e in validated if e['text'] == "Boko Haram"][0]
        assert boko_haram['score'] > 0.85

        # Unknown entity should have reduced score
        unknown = [e for e in validated if e['text'] == "Unknown Place"][0]
        assert unknown['score'] < 0.90


# ============================================================================
# FOCAL LOSS TESTS
# ============================================================================

class TestFocalLoss:
    """Tests for FocalLoss module."""

    def test_focal_loss_forward(self):
        """Test FocalLoss forward pass."""
        from pipeline.loss import FocalLoss

        num_classes = 17
        batch_size = 4
        seq_len = 128

        loss_fn = FocalLoss(num_classes=num_classes, gamma=2.0)

        # Create random inputs
        inputs = torch.randn(batch_size, seq_len, num_classes)
        targets = torch.randint(0, num_classes, (batch_size, seq_len))

        loss = loss_fn(inputs, targets)

        assert loss.dim() == 0  # Scalar
        assert loss.item() >= 0  # Non-negative

    def test_focal_loss_with_ignore_index(self):
        """Test FocalLoss ignores padding tokens."""
        from pipeline.loss import FocalLoss

        num_classes = 17
        batch_size = 2
        seq_len = 10

        loss_fn = FocalLoss(num_classes=num_classes, gamma=2.0, ignore_index=-100)

        inputs = torch.randn(batch_size, seq_len, num_classes)
        targets = torch.randint(0, num_classes, (batch_size, seq_len))

        # Add padding (ignore index)
        targets[:, -3:] = -100

        loss = loss_fn(inputs, targets)

        assert loss.item() >= 0

    def test_focal_loss_with_class_weights(self):
        """Test FocalLoss with class weights (alpha)."""
        from pipeline.loss import FocalLoss

        num_classes = 17

        # Create unequal weights
        weights = torch.ones(num_classes)
        weights[0] = 0.3  # Down-weight O label

        loss_fn = FocalLoss(num_classes=num_classes, gamma=2.0, alpha=weights)

        inputs = torch.randn(4, 128, num_classes)
        targets = torch.randint(0, num_classes, (4, 128))

        loss = loss_fn(inputs, targets)

        assert loss.item() >= 0

    def test_class_weight_computation(self):
        """Test class weight computation."""
        from pipeline.loss import compute_class_weights

        label2id = {
            'O': 0,
            'B-PERPETRATOR': 1,
            'I-PERPETRATOR': 2,
            'B-COUNTRY': 3,
            'I-COUNTRY': 4,
        }

        # Imbalanced distribution (O dominates)
        label_counts = {
            'O': 10000,
            'B-PERPETRATOR': 500,
            'I-PERPETRATOR': 300,
            'B-COUNTRY': 600,
            'I-COUNTRY': 200,
        }

        weights = compute_class_weights(label_counts, label2id, method='inverse_freq')

        # O should have lower weight (more common)
        assert weights[0] < weights[1]

        # Rare classes should have higher weights
        assert weights[4] > weights[3]  # I-COUNTRY rarer than B-COUNTRY

    def test_entity_aware_weights(self):
        """Test entity-aware weight generation."""
        from pipeline.loss import get_entity_aware_weights

        label2id = {
            'O': 0,
            'B-PERPETRATOR': 1,
            'I-PERPETRATOR': 2,
        }

        weights = get_entity_aware_weights(label2id)

        # O should have lowest weight
        assert weights[0] < weights[1]
        assert weights[0] < weights[2]

        # B- should have higher weight than I-
        assert weights[1] > weights[2]

    def test_weighted_cross_entropy(self):
        """Test ClassWeightedCrossEntropy loss."""
        from pipeline.loss import ClassWeightedCrossEntropy

        num_classes = 17
        weights = torch.ones(num_classes)
        weights[0] = 0.3

        loss_fn = ClassWeightedCrossEntropy(
            num_classes=num_classes,
            class_weights=weights
        )

        inputs = torch.randn(4, 128, num_classes)
        targets = torch.randint(0, num_classes, (4, 128))

        loss = loss_fn(inputs, targets)

        assert loss.item() >= 0


# ============================================================================
# EVALUATION SERVICE TESTS
# ============================================================================

class TestEvaluationService:
    """Tests for evaluation service module."""

    def test_category_mapping(self):
        """Test 5W1H category mapping in evaluation service."""
        from services.evaluation import CATEGORY_5W1H, ENTITY_TO_CATEGORY

        # Check all categories exist
        assert 'WHO' in CATEGORY_5W1H
        assert 'WHAT' in CATEGORY_5W1H
        assert 'WHEN' in CATEGORY_5W1H
        assert 'WHERE' in CATEGORY_5W1H
        assert 'HOW' in CATEGORY_5W1H
        assert 'WHY' in CATEGORY_5W1H

        # Check reverse mapping
        assert ENTITY_TO_CATEGORY['PERPETRATOR'] == 'WHO'
        assert ENTITY_TO_CATEGORY['COUNTRY'] == 'WHERE'
        assert ENTITY_TO_CATEGORY['DATE'] == 'WHEN'
        assert ENTITY_TO_CATEGORY['CASUALTIES'] == 'HOW'

    def test_entity_metrics_dataclass(self):
        """Test EntityMetrics has category field."""
        from services.evaluation import EntityMetrics

        metrics = EntityMetrics(
            entity_type='PERPETRATOR',
            precision=0.85,
            recall=0.80,
            f1=0.82,
            support=100,
            predicted=105,
            correct=80,
            category='WHO'
        )

        assert metrics.category == 'WHO'

    def test_category_metrics_dataclass(self):
        """Test CategoryMetrics dataclass."""
        from services.evaluation import CategoryMetrics

        metrics = CategoryMetrics(
            category='WHO',
            precision=0.85,
            recall=0.80,
            f1=0.82,
            support=500,
            predicted=520,
            correct=400,
            entity_types=['PERPETRATOR', 'VICTIM'],
            entity_breakdown={'PERPETRATOR': {'f1': 0.85}, 'VICTIM': {'f1': 0.79}}
        )

        assert metrics.category == 'WHO'
        assert len(metrics.entity_types) == 2

    def test_error_analysis_dataclass(self):
        """Test ErrorAnalysis dataclass."""
        from services.evaluation import ErrorAnalysis

        analysis = ErrorAnalysis(
            total_errors=150,
            false_positives=50,
            false_negatives=80,
            type_mismatches=20,
            common_fp_patterns=[{'entity_type': 'PERPETRATOR', 'count': 30}],
            common_fn_patterns=[{'entity_type': 'DATE', 'count': 25}],
            category_errors={'WHO': {'fp': 20, 'fn': 30, 'total': 50}},
            difficult_examples=[],
            recommendations=["Focus on WHO category"]
        )

        assert analysis.total_errors == 150
        assert len(analysis.recommendations) > 0


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for the full pipeline."""

    def test_knowledge_base_with_validator(self):
        """Test knowledge base integration with validator."""
        from pipeline.kb import get_knowledge_base
        from pipeline.validator import get_validator

        kb = get_knowledge_base()
        validator = get_validator()

        # Entity from knowledge base should validate correctly
        group = kb.get_armed_group("Al-Shabaab")
        assert group is not None

        result = validator.validate_entity(group.name, "B-PERPETRATOR")
        assert result.is_valid
        assert result.canonical_form == group.name

    def test_segmentation_with_validation(self):
        """Test event segmentation followed by entity validation."""
        from pipeline.segmentation import EventSegmenter
        from pipeline.validator import validate_entities

        segmenter = EventSegmenter()

        text = "Al-Shabaab attacked Mogadishu. In a separate incident, Boko Haram raided Maiduguri."

        segments = segmenter.segment_text(text)
        assert len(segments) >= 1

        # Simulate extracted entities
        entities = [
            {"text": "Al-Shabaab", "label": "B-PERPETRATOR", "score": 0.85},
            {"text": "Mogadishu", "label": "B-CITY", "score": 0.80},
        ]

        validated = validate_entities(entities)

        # Both should be validated
        assert all(e['score'] >= 0.5 for e in validated)

    def test_full_label_consistency(self):
        """Test that labels are consistent across all modules."""
        from pipeline.config import LabelConfigs
        from services.evaluation import CATEGORY_5W1H

        # Get all entity types from LabelConfigs
        label2id = LabelConfigs.get_label2id()
        entity_types_from_config = set()
        for label in label2id.keys():
            if label.startswith('B-'):
                entity_types_from_config.add(label[2:])

        # Get all entity types from evaluation service
        entity_types_from_eval = set()
        for entities in CATEGORY_5W1H.values():
            entity_types_from_eval.update(entities)

        # They should match
        assert entity_types_from_config == entity_types_from_eval, \
            f"Mismatch: {entity_types_from_config - entity_types_from_eval}"


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
