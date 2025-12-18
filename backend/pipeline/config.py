"""
Model Configurations - Week 9-10
Defines entity labels and model training configurations

Author: Binalfew Kassa Mekonnen
Date: December 2025

Enhanced with expanded entity schema (26 types) for comprehensive 5W1H+WHY extraction
from African conflict reporting.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional


# ============================================================================
# ENTITY LABEL DEFINITIONS (BIO Tagging)
# ============================================================================

class LabelConfigs:
    """
    Entity labels for violent event extraction using BIO tagging.

    Expanded to 26 core entity types for comprehensive 5W1H+WHY extraction
    from African conflict reporting.

    Categories:
    - WHO: PERPETRATOR, VICTIM, TARGET, ORGANIZATION, GOVERNMENT (5)
    - WHAT: EVENT_TYPE, ACTION, WEAPON, VIOLENCE_TYPE (4)
    - WHEN: DATE, TIME, DURATION, FREQUENCY (4)
    - WHERE: COUNTRY, REGION, CITY, DISTRICT, FACILITY, GEOGRAPHIC, COORDINATES (7)
    - HOW: CASUALTIES, INJURED, DISPLACEMENT, DAMAGE (4)
    - WHY: MOTIVE, TRIGGER (2)

    Total: 26 entity types = 53 BIO labels (26*2 + 1 for O)
    """

    # =========================================================================
    # WHO (Actors/Participants) - 5 types
    # =========================================================================
    ACTOR_LABELS = [
        'PERPETRATOR',      # Armed groups, attackers, aggressors
                            # Examples: "Boko Haram", "RSF", "Al-Shabaab",
                            # "armed militants", "gunmen"

        'VICTIM',           # Those harmed by the event
                            # Examples: "civilians", "villagers", "farmers",
                            # "45 children", "medical staff"

        'TARGET',           # Military/strategic targets (not civilian victims)
                            # Examples: "RSF positions", "military base",
                            # "government convoy", "police station"

        'ORGANIZATION',     # Non-combatant organizations involved
                            # Examples: "ICRC", "UN", "African Union",
                            # "Médecins Sans Frontières", "UNHCR"

        'GOVERNMENT',       # State/government entities as actors
                            # Examples: "Sudanese Armed Forces", "Nigerian Army",
                            # "Ethiopian government", "AU peacekeepers"
    ]

    # =========================================================================
    # WHAT (Event Type/Action) - 4 types
    # =========================================================================
    EVENT_LABELS = [
        'EVENT_TYPE',       # High-level event classification
                            # Examples: "attack", "clash", "bombing",
                            # "massacre", "kidnapping", "ambush"

        'ACTION',           # Specific action/verb describing what happened
                            # Examples: "bombarded", "conducted airstrikes",
                            # "opened fire", "detonated", "abducted"

        'WEAPON',           # Weapons and instruments of violence
                            # Examples: "mortars", "AK-47s", "IED",
                            # "rocket-propelled grenades", "machetes"

        'VIOLENCE_TYPE',    # Category of violence (for taxonomy mapping)
                            # Examples: "terrorism", "insurgency",
                            # "communal violence", "state repression"
    ]

    # =========================================================================
    # WHEN (Temporal) - 4 types
    # =========================================================================
    TEMPORAL_LABELS = [
        'DATE',             # Specific dates or date ranges
                            # Examples: "December 15, 2025", "last Tuesday",
                            # "on Tuesday morning", "January 2024"

        'TIME',             # Time of day
                            # Examples: "at dawn", "around 3 AM",
                            # "early morning", "overnight"

        'DURATION',         # How long the event lasted
                            # Examples: "for three hours", "throughout the night",
                            # "week-long", "ongoing since March"

        'FREQUENCY',        # Recurring nature
                            # Examples: "daily attacks", "weekly raids",
                            # "the third attack this month"
    ]

    # =========================================================================
    # WHERE (Location) - 7 types
    # =========================================================================
    LOCATION_LABELS = [
        'COUNTRY',          # Nation/sovereign state
                            # Examples: "Sudan", "Nigeria", "Somalia",
                            # "Democratic Republic of Congo"

        'REGION',           # State, province, region, territory
                            # Examples: "South Darfur", "Borno State",
                            # "Tigray region", "North Kivu"

        'CITY',             # Cities, towns, villages
                            # Examples: "Nyala", "Maiduguri", "Mogadishu",
                            # "Khartoum", "Juba"

        'DISTRICT',         # Sub-city areas, neighborhoods, quarters
                            # Examples: "Omdurman district", "Bakara Market area",
                            # "northern outskirts"

        'FACILITY',         # Buildings, installations, infrastructure
                            # Examples: "Al-Nao Hospital", "Garissa University",
                            # "UN compound", "refugee camp", "mosque"

        'GEOGRAPHIC',       # Natural features, borders
                            # Examples: "Lake Chad basin", "Sambisa Forest",
                            # "Nigeria-Cameroon border", "Blue Nile"

        'COORDINATES',      # GPS coordinates or precise locations
                            # Examples: "12.8628° N, 30.2176° E"
    ]

    # =========================================================================
    # HOW (Method/Impact) - 4 types
    # =========================================================================
    METHOD_LABELS = [
        'CASUALTIES',       # Death counts
                            # Examples: "120 dead", "45 killed",
                            # "dozens died", "mass casualties"

        'INJURED',          # Specifically injured (non-fatal)
                            # Examples: "30 wounded", "several injured",
                            # "critically wounded"

        'DISPLACEMENT',     # Forced movement of people
                            # Examples: "10,000 fled", "mass displacement",
                            # "evacuated", "internally displaced"

        'DAMAGE',           # Property/infrastructure damage
                            # Examples: "destroyed homes", "burned villages",
                            # "damaged infrastructure", "looted shops"
    ]

    # =========================================================================
    # WHY (Cause/Context) - 2 types [NEW CATEGORY]
    # =========================================================================
    CAUSE_LABELS = [
        'MOTIVE',           # Stated or inferred reason for attack
                            # Examples: "retaliation for", "in response to",
                            # "ethnic tensions", "territorial dispute"

        'TRIGGER',          # Immediate precipitating event
                            # Examples: "following the killing of",
                            # "after disputed election", "sparked by arrest"
    ]

    @classmethod
    def get_base_labels(cls) -> List[str]:
        """Get basic entity types (without BIO prefixes)."""
        return (
            cls.ACTOR_LABELS +
            cls.EVENT_LABELS +
            cls.TEMPORAL_LABELS +
            cls.LOCATION_LABELS +
            cls.METHOD_LABELS +
            cls.CAUSE_LABELS
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
        """Get mapping of entity types to 5W1H+WHY categories."""
        return {
            'WHO': cls.ACTOR_LABELS,
            'WHAT': cls.EVENT_LABELS,
            'WHEN': cls.TEMPORAL_LABELS,
            'WHERE': cls.LOCATION_LABELS,
            'HOW': cls.METHOD_LABELS,
            'WHY': cls.CAUSE_LABELS,
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
    num_epochs: int = 15  # Increased for larger label set
    warmup_ratio: float = 0.1  # Use ratio instead of fixed steps
    warmup_steps: int = 500  # Fallback if ratio not used
    weight_decay: float = 0.01

    # Advanced training options
    gradient_accumulation_steps: int = 2  # Effective batch size = batch_size * grad_accum
    max_grad_norm: float = 1.0
    fp16: bool = False  # Mixed precision training

    # Loss function options
    use_focal_loss: bool = True  # Better for class imbalance
    focal_gamma: float = 2.0
    use_class_weights: bool = True  # Weight rare entity types higher

    # Data processing
    max_length: int = 512  # Maximum sequence length
    stride: int = 128      # Overlap for long documents

    # Regularization
    dropout: float = 0.1
    label_smoothing: float = 0.1  # Enable label smoothing

    # Device
    device: str = 'auto'  # Auto-detect best device (mps, cuda, cpu)

    # Paths
    output_dir: str = 'models'
    no_timestamp: bool = False  # If True, use output_dir exactly without adding timestamp
    cache_dir: str = '~/.cache/huggingface'

    # Logging and checkpointing
    logging_steps: int = 50
    eval_steps: int = 100  # More frequent evaluation
    save_steps: int = 200
    save_total_limit: int = 3  # Keep only last 3 checkpoints per epoch

    # Early stopping
    early_stopping_patience: int = 5  # More patience with larger label set
    early_stopping_threshold: float = 0.001

    # Metrics
    metric_for_best_model: str = 'f1'  # Use F1 instead of loss for best model selection


# ============================================================================
# CONFIGURATION PRESETS
# ============================================================================

class ConfigPresets:
    """Pre-configured model settings for different use cases."""

    @staticmethod
    def fast_prototyping() -> ModelConfig:
        """Fast training for quick iterations (lower accuracy)."""
        return ModelConfig(
            model_name='distilbert-base-cased',  # Smaller, faster
            batch_size=32,
            num_epochs=3,
            learning_rate=3e-5,
        )

    @staticmethod
    def high_accuracy() -> ModelConfig:
        """High accuracy for production (slower training)."""
        return ModelConfig(
            model_name='bert-large-cased',  # Larger model
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
            fp16=True,  # Mixed precision for speed
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
            batch_size=32,  # Can handle larger batches with 64GB
            num_epochs=10,
            learning_rate=2e-5,
            device='mps',  # Metal Performance Shaders
            fp16=False,    # MPS doesn't support fp16 yet
        )


# ============================================================================
# LABEL MAPPING FOR WEEK 3-6 CSV FORMAT
# ============================================================================

class CSVToNERMapping:
    """Maps CSV columns to NER entity types for the expanded 26-type schema."""

    COLUMN_TO_ENTITY = {
        # =====================================================================
        # WHO: Actor columns
        # =====================================================================
        'Actor_Normalized': 'PERPETRATOR',
        'Actor_Type': 'PERPETRATOR',
        'Perpetrator': 'PERPETRATOR',
        'Attacker': 'PERPETRATOR',
        'Armed_Group': 'PERPETRATOR',

        # Victim columns
        'Victim_Normalized': 'VICTIM',
        'Victim_Type': 'VICTIM',
        'Casualties_Description': 'VICTIM',

        # Target columns
        'Target': 'TARGET',
        'Target_Type': 'TARGET',
        'Military_Target': 'TARGET',

        # Organization columns
        'Organization': 'ORGANIZATION',
        'Responding_Organization': 'ORGANIZATION',
        'NGO': 'ORGANIZATION',
        'International_Org': 'ORGANIZATION',

        # Government columns
        'Government_Actor': 'GOVERNMENT',
        'State_Forces': 'GOVERNMENT',
        'Military': 'GOVERNMENT',
        'Police': 'GOVERNMENT',

        # =====================================================================
        # WHAT: Event columns
        # =====================================================================
        'Taxonomy_L1': 'VIOLENCE_TYPE',  # High-level violence category
        'Taxonomy_L2': 'EVENT_TYPE',     # Event type
        'Taxonomy_L3': 'EVENT_TYPE',     # Specific event type
        'Event_Type': 'EVENT_TYPE',
        'Sub_Event_Type': 'ACTION',
        'Action': 'ACTION',
        'Disorder_Type': 'EVENT_TYPE',

        # Weapon columns
        'Weapon_Category': 'WEAPON',
        'Weapon': 'WEAPON',
        'Weapon_Type': 'WEAPON',

        # =====================================================================
        # WHEN: Temporal columns
        # =====================================================================
        'Date_Normalized': 'DATE',
        'Event_Date': 'DATE',
        'Date': 'DATE',
        'Year': 'DATE',
        'Time': 'TIME',
        'Time_Precision': 'TIME',
        'Duration': 'DURATION',

        # =====================================================================
        # WHERE: Location columns
        # =====================================================================
        'Location_Country': 'COUNTRY',
        'Country': 'COUNTRY',

        'Location_Region': 'REGION',
        'Admin1': 'REGION',
        'State': 'REGION',
        'Province': 'REGION',
        'Region': 'REGION',

        'Location_City': 'CITY',
        'City': 'CITY',
        'Town': 'CITY',
        'Admin2': 'CITY',
        'Admin3': 'CITY',

        'Location_District': 'DISTRICT',
        'Neighborhood': 'DISTRICT',
        'District': 'DISTRICT',

        'Facility': 'FACILITY',
        'Location_Facility': 'FACILITY',
        'Infrastructure': 'FACILITY',

        'Location_Coordinates': 'COORDINATES',
        'Latitude': 'COORDINATES',
        'Longitude': 'COORDINATES',
        'Geo_Precision': 'COORDINATES',

        'Geographic_Feature': 'GEOGRAPHIC',
        'Border': 'GEOGRAPHIC',

        # =====================================================================
        # HOW: Impact columns
        # =====================================================================
        'Deaths': 'CASUALTIES',
        'Fatalities': 'CASUALTIES',
        'Killed': 'CASUALTIES',

        'Injuries': 'INJURED',
        'Wounded': 'INJURED',

        'Displaced': 'DISPLACEMENT',
        'IDPs': 'DISPLACEMENT',
        'Refugees': 'DISPLACEMENT',

        'Damage': 'DAMAGE',
        'Property_Damage': 'DAMAGE',

        # =====================================================================
        # WHY: Cause columns
        # =====================================================================
        'Motive': 'MOTIVE',
        'Cause': 'MOTIVE',
        'Reason': 'MOTIVE',

        'Trigger': 'TRIGGER',
        'Precipitating_Event': 'TRIGGER',
    }

    # Alternative column name patterns (for fuzzy matching)
    COLUMN_PATTERNS = {
        'actor': 'PERPETRATOR',
        'perp': 'PERPETRATOR',
        'attacker': 'PERPETRATOR',
        'victim': 'VICTIM',
        'target': 'TARGET',
        'org': 'ORGANIZATION',
        'govt': 'GOVERNMENT',
        'government': 'GOVERNMENT',
        'military': 'GOVERNMENT',
        'event': 'EVENT_TYPE',
        'action': 'ACTION',
        'weapon': 'WEAPON',
        'date': 'DATE',
        'time': 'TIME',
        'country': 'COUNTRY',
        'region': 'REGION',
        'state': 'REGION',
        'province': 'REGION',
        'city': 'CITY',
        'town': 'CITY',
        'district': 'DISTRICT',
        'facility': 'FACILITY',
        'hospital': 'FACILITY',
        'school': 'FACILITY',
        'coord': 'COORDINATES',
        'lat': 'COORDINATES',
        'lon': 'COORDINATES',
        'death': 'CASUALTIES',
        'fatal': 'CASUALTIES',
        'killed': 'CASUALTIES',
        'injur': 'INJURED',
        'wound': 'INJURED',
        'displac': 'DISPLACEMENT',
        'refugee': 'DISPLACEMENT',
        'idp': 'DISPLACEMENT',
        'damage': 'DAMAGE',
        'motive': 'MOTIVE',
        'cause': 'MOTIVE',
        'trigger': 'TRIGGER',
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
    print("ENTITY LABEL STATISTICS")
    print("=" * 60)

    print(f"\nTotal entity types: {len(LabelConfigs.get_base_labels())}")
    print(f"Total BIO labels: {LabelConfigs.get_num_labels()}")

    print("\nEntity breakdown by 5W1H+WHY category:")
    print(f"  WHO (Actors):      {len(LabelConfigs.ACTOR_LABELS):2d} - {LabelConfigs.ACTOR_LABELS}")
    print(f"  WHAT (Events):     {len(LabelConfigs.EVENT_LABELS):2d} - {LabelConfigs.EVENT_LABELS}")
    print(f"  WHEN (Temporal):   {len(LabelConfigs.TEMPORAL_LABELS):2d} - {LabelConfigs.TEMPORAL_LABELS}")
    print(f"  WHERE (Location):  {len(LabelConfigs.LOCATION_LABELS):2d} - {LabelConfigs.LOCATION_LABELS}")
    print(f"  HOW (Impact):      {len(LabelConfigs.METHOD_LABELS):2d} - {LabelConfigs.METHOD_LABELS}")
    print(f"  WHY (Cause):       {len(LabelConfigs.CAUSE_LABELS):2d} - {LabelConfigs.CAUSE_LABELS}")

    print(f"\nBIO labels (first 15): {LabelConfigs.get_bio_labels()[:15]}")
    print(f"...")
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
