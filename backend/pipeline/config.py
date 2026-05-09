"""
Model Configurations - Week 9-10
Defines entity labels and model training configurations

Author: Binalfew Kassa Mekonnen
Date: December 2025

Entity schema (8 types) for 5W1H extraction from African conflict reporting.
Optimized for grounded entity extraction from ACLED event descriptions.

Note: Event type classification (taxonomy) is handled separately as a post-NER task.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional


# ============================================================================
# ENTITY LABEL DEFINITIONS (BIO Tagging)
# ============================================================================

class LabelConfigs:
    """
    Entity labels for violent event extraction using BIO tagging.

    8 entity types optimized for grounded extraction from text.

    Categories:
    - WHO: ACTOR (1) - All actors (perpetrators, organizations, government forces)
    - WHOM: VICTIM (1) - Those affected by violence
    - WHAT: ACTION (1) - Verbs describing what happened
    - WHEN: DATE (1) - Temporal expressions
    - WHERE: REGION, CITY, DISTRICT (3) - Location hierarchy
    - HOW: CASUALTIES (1) - Death/injury counts

    Total: 8 entity types = 17 BIO labels (8*2 + 1 for O)

    Note: EVENT_TYPE and COUNTRY removed as they have poor grounding rates.
    Event classification is handled by the taxonomy classifier post-NER.
    """

    # =========================================================================
    # WHO (Actors) - 1 type (merged)
    # =========================================================================
    ACTOR_LABELS = [
        'ACTOR',            # All actors: armed groups, organizations, government forces
                            # Examples: "Boko Haram", "M23", "RSF", "Al-Shabaab",
                            # "military forces", "police", "FARDC", "UN peacekeepers",
                            # "gunmen", "armed militants", "security forces"
    ]

    # =========================================================================
    # WHOM (Victims) - 1 type
    # =========================================================================
    VICTIM_LABELS = [
        'VICTIM',           # Those harmed by the event
                            # Examples: "civilians", "villagers", "residents",
                            # "farmers", "protesters", "passengers", "traders"
    ]

    # =========================================================================
    # WHAT (Action) - 1 type
    # =========================================================================
    EVENT_LABELS = [
        'ACTION',           # Verbs/actions describing what happened
                            # Examples: "attacked", "killed", "clashed", "ambushed",
                            # "abducted", "bombed", "raided", "looted", "burned"
    ]

    # =========================================================================
    # WHEN (Temporal) - 1 type
    # =========================================================================
    TEMPORAL_LABELS = [
        'DATE',             # Specific dates or date expressions
                            # Examples: "20 December 2024", "last Tuesday",
                            # "on Tuesday morning", "January 2024"
    ]

    # =========================================================================
    # WHERE (Location) - 3 types
    # =========================================================================
    LOCATION_LABELS = [
        'REGION',           # State, province, region, territory
                            # Examples: "North Darfur", "Borno State",
                            # "Amhara", "Nord-Kivu", "Oromia"

        'CITY',             # Cities, towns, villages, localities
                            # Examples: "Nyala", "Maiduguri", "Mogadishu",
                            # "Khartoum", "Goma", "Luofu"

        'DISTRICT',         # Administrative districts, sub-regions
                            # Examples: "Lubero", "Momo", "Bandiagara",
                            # "Logone-et-Chari"
    ]

    # =========================================================================
    # HOW (Impact) - 1 type
    # =========================================================================
    METHOD_LABELS = [
        'CASUALTIES',       # Death/injury counts and descriptions
                            # Examples: "killed 15", "7 dead", "3 injured",
                            # "left 10 dead", "claiming 5 lives"
    ]

    @classmethod
    def get_base_labels(cls) -> List[str]:
        """Get basic entity types (without BIO prefixes)."""
        return (
            cls.ACTOR_LABELS +
            cls.VICTIM_LABELS +
            cls.EVENT_LABELS +
            cls.TEMPORAL_LABELS +
            cls.LOCATION_LABELS +
            cls.METHOD_LABELS
        )

    @classmethod
    def get_bio_labels(cls) -> List[str]:
        """Get all labels with BIO tagging (B-, I-, O)."""
        base_labels = cls.get_base_labels()
        bio_labels = ['O']  # Outside any entity

        for label in base_labels:
            bio_labels.append(f'B-{label}')  # Beginning
            bio_labels.append(f'I-{label}')  # Inside

        return bio_labels

    @classmethod
    def get_label2id(cls) -> Dict[str, int]:
        """Get label to ID mapping."""
        labels = cls.get_bio_labels()
        return {label: idx for idx, label in enumerate(labels)}

    @classmethod
    def get_id2label(cls) -> Dict[int, str]:
        """Get ID to label mapping."""
        labels = cls.get_bio_labels()
        return {idx: label for idx, label in enumerate(labels)}

    @classmethod
    def get_num_labels(cls) -> int:
        """Get total number of labels."""
        return len(cls.get_bio_labels())

    @classmethod
    def get_5w1h_mapping(cls) -> Dict[str, List[str]]:
        """Get mapping of entity types to 5W1H categories."""
        return {
            'WHO': cls.ACTOR_LABELS,
            'WHOM': cls.VICTIM_LABELS,
            'WHAT': cls.EVENT_LABELS,
            'WHEN': cls.TEMPORAL_LABELS,
            'WHERE': cls.LOCATION_LABELS,
            'HOW': cls.METHOD_LABELS,
        }

    @classmethod
    def get_category_for_label(cls, label: str) -> Optional[str]:
        """Get the 5W1H category for a given entity label."""
        for category, labels in cls.get_5w1h_mapping().items():
            if label in labels:
                return category
        return None


# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

@dataclass
class ModelConfig:
    """Configuration for model training."""

    # Model architecture
    model_name: str = 'bert-base-cased'
    num_labels: int = LabelConfigs.get_num_labels()

    # Training hyperparameters
    learning_rate: float = 2e-5
    batch_size: int = 16
    num_epochs: int = 15
    warmup_ratio: float = 0.1
    warmup_steps: int = 500
    weight_decay: float = 0.01

    # Advanced training options
    gradient_accumulation_steps: int = 2
    max_grad_norm: float = 1.0
    fp16: bool = False

    # Loss function options
    use_focal_loss: bool = True
    focal_gamma: float = 2.0
    use_class_weights: bool = True

    # Data processing
    max_length: int = 512
    stride: int = 128

    # Regularization
    dropout: float = 0.1
    label_smoothing: float = 0.1

    # Device
    device: str = 'auto'

    # Paths
    output_dir: str = 'models'
    no_timestamp: bool = False
    cache_dir: str = '~/.cache/huggingface'

    # Logging and checkpointing
    logging_steps: int = 50
    eval_steps: int = 100
    save_steps: int = 200
    save_total_limit: int = 3

    # Early stopping
    early_stopping_patience: int = 5
    early_stopping_threshold: float = 0.001
    use_early_stopping: bool = True

    # Learning rate scheduler
    lr_scheduler: str = 'reduce_on_plateau'  # 'linear', 'reduce_on_plateau', or 'none'
    lr_reduce_factor: float = 0.5  # Factor to reduce LR by when plateau detected
    lr_reduce_patience: int = 2    # Epochs to wait before reducing LR

    # Metrics
    metric_for_best_model: str = 'f1'


# ============================================================================
# CONFIGURATION PRESETS
# ============================================================================

class ConfigPresets:
    """Pre-configured model settings for different use cases."""

    @staticmethod
    def fast_prototyping() -> ModelConfig:
        """Fast training for quick iterations (lower accuracy)."""
        return ModelConfig(
            model_name='distilbert-base-cased',
            batch_size=32,
            num_epochs=3,
            learning_rate=3e-5,
        )

    @staticmethod
    def high_accuracy() -> ModelConfig:
        """High accuracy for production (slower training)."""
        return ModelConfig(
            model_name='bert-large-cased',
            batch_size=8,
            num_epochs=15,
            learning_rate=1e-5,
            gradient_accumulation_steps=2,
        )

    @staticmethod
    def multilingual() -> ModelConfig:
        """For African multilingual news (English, French, Arabic)."""
        return ModelConfig(
            model_name='xlm-roberta-base',
            batch_size=16,
            num_epochs=10,
            learning_rate=2e-5,
        )

    @staticmethod
    def domain_specific() -> ModelConfig:
        """Optimized for violent event domain (recommended for thesis)."""
        return ModelConfig(
            model_name='bert-base-cased',
            batch_size=16,
            num_epochs=10,
            learning_rate=2e-5,
            warmup_steps=500,
            weight_decay=0.01,
            dropout=0.1,
        )

    @staticmethod
    def efficient_inference() -> ModelConfig:
        """Fast inference with minimal accuracy loss."""
        return ModelConfig(
            model_name='distilbert-base-cased',
            batch_size=32,
            num_epochs=8,
            learning_rate=3e-5,
            fp16=True,
        )

    @staticmethod
    def roberta_baseline() -> ModelConfig:
        """RoBERTa model (often better than BERT)."""
        return ModelConfig(
            model_name='roberta-base',
            batch_size=16,
            num_epochs=10,
            learning_rate=2e-5,
        )

    @staticmethod
    def apple_silicon_optimized() -> ModelConfig:
        """Optimized for Mac M1/M2/M3 with 64GB RAM."""
        return ModelConfig(
            model_name='bert-base-cased',
            batch_size=32,
            num_epochs=10,
            learning_rate=2e-5,
            device='mps',
            fp16=False,
        )


# ============================================================================
# LABEL MAPPING FOR ACLED JSONL AND CSV FORMAT
# ============================================================================

class CSVToNERMapping:
    """Maps CSV/JSONL columns to NER entity types for the 8-type schema."""

    COLUMN_TO_ENTITY = {
        # =====================================================================
        # WHO: Actor columns (merged into ACTOR)
        # =====================================================================
        'Actor_Normalized': 'ACTOR',
        'Actor_Type': 'ACTOR',
        'Perpetrator': 'ACTOR',
        'PERPETRATOR': 'ACTOR',
        'Attacker': 'ACTOR',
        'Armed_Group': 'ACTOR',
        'ACTOR': 'ACTOR',

        # Organization -> ACTOR
        'Organization': 'ACTOR',
        'ORGANIZATION': 'ACTOR',
        'Responding_Organization': 'ACTOR',
        'NGO': 'ACTOR',
        'International_Org': 'ACTOR',

        # Government -> ACTOR
        'Government_Actor': 'ACTOR',
        'GOVERNMENT': 'ACTOR',
        'State_Forces': 'ACTOR',
        'Military': 'ACTOR',
        'Police': 'ACTOR',

        # =====================================================================
        # WHOM: Victim columns
        # =====================================================================
        'Victim_Normalized': 'VICTIM',
        'Victim_Type': 'VICTIM',
        'VICTIM': 'VICTIM',
        'Casualties_Description': 'VICTIM',

        # =====================================================================
        # WHAT: Action columns (EVENT_TYPE removed)
        # =====================================================================
        'Sub_Event_Type': 'ACTION',
        'Action': 'ACTION',
        'ACTION': 'ACTION',

        # =====================================================================
        # WHEN: Temporal columns
        # =====================================================================
        'Date_Normalized': 'DATE',
        'Event_Date': 'DATE',
        'Date': 'DATE',
        'DATE': 'DATE',
        'Year': 'DATE',

        # =====================================================================
        # WHERE: Location columns (COUNTRY removed)
        # =====================================================================
        'Location_Region': 'REGION',
        'Admin1': 'REGION',
        'State': 'REGION',
        'Province': 'REGION',
        'Region': 'REGION',
        'REGION': 'REGION',

        'Location_City': 'CITY',
        'City': 'CITY',
        'CITY': 'CITY',
        'Town': 'CITY',
        'Admin2': 'CITY',
        'Locality': 'CITY',

        'Location_District': 'DISTRICT',
        'Neighborhood': 'DISTRICT',
        'District': 'DISTRICT',
        'DISTRICT': 'DISTRICT',
        'Admin3': 'DISTRICT',

        # =====================================================================
        # HOW: Impact columns
        # =====================================================================
        'Deaths': 'CASUALTIES',
        'Fatalities': 'CASUALTIES',
        'CASUALTIES': 'CASUALTIES',
        'Killed': 'CASUALTIES',
    }

    # Alternative column name patterns (for fuzzy matching)
    COLUMN_PATTERNS = {
        'actor': 'ACTOR',
        'perp': 'ACTOR',
        'attacker': 'ACTOR',
        'org': 'ACTOR',
        'govt': 'ACTOR',
        'government': 'ACTOR',
        'military': 'ACTOR',
        'victim': 'VICTIM',
        'action': 'ACTION',
        'date': 'DATE',
        'region': 'REGION',
        'state': 'REGION',
        'province': 'REGION',
        'city': 'CITY',
        'town': 'CITY',
        'district': 'DISTRICT',
        'death': 'CASUALTIES',
        'fatal': 'CASUALTIES',
        'killed': 'CASUALTIES',
    }

    @classmethod
    def get_entity_for_column(cls, column_name: str) -> Optional[str]:
        """Get entity type for a CSV column."""
        # Direct match
        if column_name in cls.COLUMN_TO_ENTITY:
            return cls.COLUMN_TO_ENTITY[column_name]

        # Pattern matching (case-insensitive)
        column_lower = column_name.lower()
        for pattern, entity_type in cls.COLUMN_PATTERNS.items():
            if pattern in column_lower:
                return entity_type

        return None

    @classmethod
    def get_all_mappings(cls) -> Dict[str, str]:
        """Get all column to entity mappings."""
        return cls.COLUMN_TO_ENTITY.copy()


# ============================================================================
# MODEL METADATA
# ============================================================================

AVAILABLE_MODELS = {
    'bert-base-cased': {
        'size': '110M parameters',
        'download': '~440 MB',
        'speed': 'Fast',
        'accuracy': 'Good',
        'recommended': True,
    },
    'bert-large-cased': {
        'size': '340M parameters',
        'download': '~1.3 GB',
        'speed': 'Slow',
        'accuracy': 'Excellent',
        'recommended': False,
    },
    'roberta-base': {
        'size': '125M parameters',
        'download': '~500 MB',
        'speed': 'Fast',
        'accuracy': 'Better than BERT',
        'recommended': True,
    },
    'xlm-roberta-base': {
        'size': '270M parameters',
        'download': '~1.1 GB',
        'speed': 'Medium',
        'accuracy': 'Excellent for multilingual',
        'recommended': True,
    },
    'distilbert-base-cased': {
        'size': '67M parameters',
        'download': '~260 MB',
        'speed': 'Very fast',
        'accuracy': 'Good',
        'recommended': False,
    },
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def print_label_statistics():
    """Print statistics about entity labels."""
    print("=" * 60)
    print("ENTITY LABEL STATISTICS (8-type grounded schema)")
    print("=" * 60)

    print(f"\nTotal entity types: {len(LabelConfigs.get_base_labels())}")
    print(f"Total BIO labels: {LabelConfigs.get_num_labels()}")

    print("\nEntity breakdown by 5W1H category:")
    print(f"  WHO (Actors):      {len(LabelConfigs.ACTOR_LABELS):2d} - {LabelConfigs.ACTOR_LABELS}")
    print(f"  WHOM (Victims):    {len(LabelConfigs.VICTIM_LABELS):2d} - {LabelConfigs.VICTIM_LABELS}")
    print(f"  WHAT (Actions):    {len(LabelConfigs.EVENT_LABELS):2d} - {LabelConfigs.EVENT_LABELS}")
    print(f"  WHEN (Temporal):   {len(LabelConfigs.TEMPORAL_LABELS):2d} - {LabelConfigs.TEMPORAL_LABELS}")
    print(f"  WHERE (Location):  {len(LabelConfigs.LOCATION_LABELS):2d} - {LabelConfigs.LOCATION_LABELS}")
    print(f"  HOW (Impact):      {len(LabelConfigs.METHOD_LABELS):2d} - {LabelConfigs.METHOD_LABELS}")

    print(f"\nAll BIO labels: {LabelConfigs.get_bio_labels()}")
    print(f"Total: {LabelConfigs.get_num_labels()} labels")


def print_available_models():
    """Print information about available models."""
    print("=" * 60)
    print("AVAILABLE MODELS")
    print("=" * 60)

    for model_name, info in AVAILABLE_MODELS.items():
        recommended = " [RECOMMENDED]" if info['recommended'] else ""
        print(f"\n{model_name}{recommended}")
        print(f"  Size: {info['size']}")
        print(f"  Download: {info['download']}")
        print(f"  Speed: {info['speed']}")
        print(f"  Accuracy: {info['accuracy']}")


if __name__ == '__main__':
    # Demo
    print_label_statistics()
    print()
    print_available_models()

    print("\n" + "=" * 60)
    print("CONFIGURATION PRESETS")
    print("=" * 60)

    presets = [
        ('Fast Prototyping', ConfigPresets.fast_prototyping()),
        ('High Accuracy', ConfigPresets.high_accuracy()),
        ('Domain Specific', ConfigPresets.domain_specific()),
        ('Apple Silicon Optimized', ConfigPresets.apple_silicon_optimized()),
    ]

    for name, config in presets:
        print(f"\n{name}:")
        print(f"  Model: {config.model_name}")
        print(f"  Batch size: {config.batch_size}")
        print(f"  Epochs: {config.num_epochs}")
        print(f"  Learning rate: {config.learning_rate}")
