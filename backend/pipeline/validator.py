"""
Entity Validator - Phase 5
Domain-specific validation for NER predictions on African conflict text.

Author: Binalfew Kassa Mekonnen
Date: December 2025

This module validates NER predictions using:
- Knowledge base lookups (armed groups, countries, cities)
- Pattern-based validation (dates, numbers, coordinates)
- Contextual validation (entity type consistency)
- Confidence adjustment based on validation results
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import re
import logging
from datetime import datetime

# Handle both package import and direct script execution
try:
    from .kb import (
        get_knowledge_base,
        KnowledgeBase,
        AFRICAN_COUNTRIES,
        CONFLICT_CITIES,
    )
    from .config import LabelConfigs
except ImportError:
    from kb import (
        get_knowledge_base,
        KnowledgeBase,
        AFRICAN_COUNTRIES,
        CONFLICT_CITIES,
    )
    from config import LabelConfigs

logger = logging.getLogger(__name__)


# ============================================================================
# VALIDATION RESULT
# ============================================================================

@dataclass
class ValidationResult:
    """Result of entity validation."""
    is_valid: bool
    confidence_adjustment: float  # Multiplier: 1.0 = no change, >1 = boost, <1 = reduce
    reason: str
    canonical_form: Optional[str] = None  # Normalized entity text
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# VALIDATION PATTERNS
# ============================================================================

# Date patterns for African conflict reporting
DATE_PATTERNS = [
    # Full date formats
    r'\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b',
    r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})\b',
    r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b',

    # Partial dates
    r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b',
    r'\b(early|mid|late)\s+(January|February|March|April|May|June|July|August|September|October|November|December)\b',

    # Relative dates
    r'\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b',
    r'\b(yesterday|today|last\s+week|last\s+month|this\s+week|this\s+month)\b',
    r'\b(last|this|next)\s+(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b',

    # Time expressions
    r'\b(morning|afternoon|evening|night|dawn|dusk|overnight)\b',
    r'\b(\d{1,2})\s*(am|pm|AM|PM)\b',
    r'\b(\d{1,2}):(\d{2})\s*(am|pm|AM|PM)?\b',
]

# Casualty patterns
CASUALTY_PATTERNS = [
    r'\b(\d+)\s*(people\s+)?(killed|dead|died|fatalities|casualties)\b',
    r'\b(killed|dead|died)\s+(\d+)\b',
    r'\b(\d+)\s*(people\s+)?(injured|wounded|hurt)\b',
    r'\b(at\s+least|approximately|about|around|over|more\s+than)\s+(\d+)\s*(people\s+)?(killed|dead|injured|wounded)\b',
    r'\b(dozens|hundreds|thousands)\s+(of\s+)?(people\s+)?(killed|dead|injured|wounded)\b',
]

# Coordinate patterns (GPS/Geographic)
COORDINATE_PATTERNS = [
    r'\b(\d{1,3})[°]\s*(\d{1,2})[\'′]\s*(\d{1,2}(?:\.\d+)?)[\"″]?\s*([NS])',  # DMS format
    r'\b(\d{1,3})[°]\s*(\d{1,2}(?:\.\d+)?)[\'′]\s*([NS])',  # DM format
    r'\b(-?\d{1,2}(?:\.\d+)?)\s*,\s*(-?\d{1,3}(?:\.\d+)?)\b',  # Decimal format
]

# Weapon patterns
WEAPON_PATTERNS = [
    r'\b(AK-?47|AK-?74|M-?16|RPG|grenades?|machetes?|rifles?|guns?)\b',
    r'\b(IED|VBIED|SVBIED|improvised\s+explosive\s+device)\b',
    r'\b(artillery|mortar|rockets?|missiles?)\b',
    r'\b(drones?|UAV|helicopter|fighter\s+jet|aircraft)\b',
]

# Displacement patterns
DISPLACEMENT_PATTERNS = [
    r'\b(\d+(?:,\d{3})*)\s*(people\s+)?(displaced|fled|evacuated)\b',
    r'\b(displaced|fled|evacuated)\s+(\d+(?:,\d{3})*)\b',
    r'\b(refugees?|IDPs?|internally\s+displaced)\b',
]


# ============================================================================
# ENTITY VALIDATOR
# ============================================================================

class EntityValidator:
    """
    Validates NER predictions using domain knowledge and patterns.
    """

    def __init__(self):
        """Initialize the validator."""
        self.kb = get_knowledge_base()
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for efficiency."""
        self._date_patterns = [re.compile(p, re.IGNORECASE) for p in DATE_PATTERNS]
        self._casualty_patterns = [re.compile(p, re.IGNORECASE) for p in CASUALTY_PATTERNS]
        self._coordinate_patterns = [re.compile(p) for p in COORDINATE_PATTERNS]
        self._weapon_patterns = [re.compile(p, re.IGNORECASE) for p in WEAPON_PATTERNS]
        self._displacement_patterns = [re.compile(p, re.IGNORECASE) for p in DISPLACEMENT_PATTERNS]

    def validate_entity(
        self,
        text: str,
        label: str,
        context: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate a single entity prediction.

        Args:
            text: Entity text
            label: Predicted label (e.g., "B-PERPETRATOR", "I-COUNTRY")
            context: Optional surrounding text for context-aware validation

        Returns:
            ValidationResult with validity, confidence adjustment, and metadata
        """
        # Extract base label (remove B-/I- prefix)
        base_label = label
        if label.startswith('B-') or label.startswith('I-'):
            base_label = label[2:]

        # Route to specific validator based on label
        validators = {
            # WHO
            'PERPETRATOR': self._validate_perpetrator,
            'VICTIM': self._validate_victim,
            'TARGET': self._validate_target,
            'ORGANIZATION': self._validate_organization,
            'GOVERNMENT': self._validate_government,

            # WHAT
            'EVENT_TYPE': self._validate_event_type,
            'ACTION': self._validate_action,
            'WEAPON': self._validate_weapon,
            'VIOLENCE_TYPE': self._validate_violence_type,

            # WHEN
            'DATE': self._validate_date,
            'TIME': self._validate_time,
            'DURATION': self._validate_duration,
            'FREQUENCY': self._validate_frequency,

            # WHERE
            'COUNTRY': self._validate_country,
            'REGION': self._validate_region,
            'CITY': self._validate_city,
            'DISTRICT': self._validate_district,
            'FACILITY': self._validate_facility,
            'GEOGRAPHIC': self._validate_geographic,
            'COORDINATES': self._validate_coordinates,

            # HOW
            'CASUALTIES': self._validate_casualties,
            'INJURED': self._validate_injured,
            'DISPLACEMENT': self._validate_displacement,
            'DAMAGE': self._validate_damage,

            # WHY
            'MOTIVE': self._validate_motive,
            'TRIGGER': self._validate_trigger,
        }

        validator = validators.get(base_label)
        if validator:
            return validator(text, context)

        # Unknown label - return neutral result
        return ValidationResult(
            is_valid=True,
            confidence_adjustment=1.0,
            reason="Unknown label type"
        )

    def validate_entities(
        self,
        entities: List[Dict],
        full_text: Optional[str] = None
    ) -> List[Dict]:
        """
        Validate a list of entities and adjust their confidence scores.

        Args:
            entities: List of entity dicts with 'text', 'label', 'score' keys
            full_text: Full text for context-aware validation

        Returns:
            Entities with updated 'score' and added 'validation' metadata
        """
        validated = []

        for entity in entities:
            text = entity.get('text', entity.get('word', ''))
            label = entity.get('label', entity.get('entity', ''))
            score = entity.get('score', entity.get('confidence', 1.0))

            # Get context if full text available
            context = None
            if full_text and 'start' in entity and 'end' in entity:
                start = max(0, entity['start'] - 50)
                end = min(len(full_text), entity['end'] + 50)
                context = full_text[start:end]

            # Validate
            result = self.validate_entity(text, label, context)

            # Update entity
            validated_entity = entity.copy()
            validated_entity['score'] = score * result.confidence_adjustment
            validated_entity['validation'] = {
                'is_valid': result.is_valid,
                'reason': result.reason,
                'original_score': score,
            }

            if result.canonical_form:
                validated_entity['canonical'] = result.canonical_form

            if result.metadata:
                validated_entity['validation']['metadata'] = result.metadata

            validated.append(validated_entity)

        return validated

    # ========================================================================
    # WHO VALIDATORS
    # ========================================================================

    def _validate_perpetrator(self, text: str, context: Optional[str]) -> ValidationResult:
        """Validate PERPETRATOR entity."""
        is_valid, confidence, canonical = self.kb.validate_perpetrator(text)

        if canonical:
            return ValidationResult(
                is_valid=True,
                confidence_adjustment=1.2,  # Boost for known group
                reason=f"Known armed group: {canonical}",
                canonical_form=canonical,
                metadata={"source": "knowledge_base"}
            )

        if is_valid:
            return ValidationResult(
                is_valid=True,
                confidence_adjustment=1.0,
                reason="Matches perpetrator pattern"
            )

        # Check if it looks like a proper noun (potential unknown group)
        if text[0].isupper() and len(text.split()) <= 5:
            return ValidationResult(
                is_valid=True,
                confidence_adjustment=0.9,
                reason="Possible unknown perpetrator (proper noun)"
            )

        return ValidationResult(
            is_valid=False,
            confidence_adjustment=0.5,
            reason="Does not match perpetrator patterns"
        )

    def _validate_victim(self, text: str, context: Optional[str]) -> ValidationResult:
        """Validate VICTIM entity."""
        victim_patterns = [
            r'\b(civilians?|villagers?|residents?|locals?|people)\b',
            r'\b(women|children|men|students?|farmers?|traders?)\b',
            r'\b(soldiers?|officers?|officials?|workers?)\b',
            r'\b(family|families|community|communities)\b',
            r'\b(ethnic\s+\w+|tribe|clan)\b',
        ]

        for pattern in victim_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return ValidationResult(
                    is_valid=True,
                    confidence_adjustment=1.1,
                    reason="Matches victim pattern"
                )

        # Numbers with people
        if re.match(r'^\d+\s*(people|civilians?|persons?)$', text, re.IGNORECASE):
            return ValidationResult(
                is_valid=True,
                confidence_adjustment=1.0,
                reason="Numeric victim count"
            )

        return ValidationResult(
            is_valid=True,
            confidence_adjustment=0.8,
            reason="Generic victim text"
        )

    def _validate_target(self, text: str, context: Optional[str]) -> ValidationResult:
        """Validate TARGET entity."""
        target_patterns = [
            r'\b(military\s+base|camp|checkpoint|convoy|patrol)\b',
            r'\b(village|town|city|settlement|community)\b',
            r'\b(church|mosque|school|hospital|market)\b',
            r'\b(government\s+building|police\s+station|army\s+base)\b',
            r'\b(infrastructure|bridge|road|pipeline)\b',
        ]

        for pattern in target_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return ValidationResult(
                    is_valid=True,
                    confidence_adjustment=1.1,
                    reason="Matches target pattern"
                )

        return ValidationResult(
            is_valid=True,
            confidence_adjustment=0.9,
            reason="Generic target"
        )

    def _validate_organization(self, text: str, context: Optional[str]) -> ValidationResult:
        """Validate ORGANIZATION entity."""
        # Check if it's an armed group
        group = self.kb.get_armed_group(text)
        if group:
            return ValidationResult(
                is_valid=True,
                confidence_adjustment=1.2,
                reason=f"Known organization: {group.name}",
                canonical_form=group.name
            )

        org_patterns = [
            r'\b(UN|United\s+Nations|AU|African\s+Union)\b',
            r'\b(NGO|humanitarian\s+organization|aid\s+agency)\b',
            r'\b(government|ministry|department)\b',
            r'\b(party|coalition|alliance|movement)\b',
        ]

        for pattern in org_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return ValidationResult(
                    is_valid=True,
                    confidence_adjustment=1.1,
                    reason="Matches organization pattern"
                )

        return ValidationResult(
            is_valid=True,
            confidence_adjustment=0.9,
            reason="Generic organization"
        )

    def _validate_government(self, text: str, context: Optional[str]) -> ValidationResult:
        """Validate GOVERNMENT entity."""
        gov_patterns = [
            r'\b(government|state|federal|national)\b',
            r'\b(army|military|forces|troops|police)\b',
            r'\b(president|prime\s+minister|minister|governor)\b',
            r'\b(ministry|parliament|senate|assembly)\b',
        ]

        for pattern in gov_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return ValidationResult(
                    is_valid=True,
                    confidence_adjustment=1.1,
                    reason="Matches government pattern"
                )

        return ValidationResult(
            is_valid=True,
            confidence_adjustment=0.8,
            reason="Generic government entity"
        )

    # ========================================================================
    # WHAT VALIDATORS
    # ========================================================================

    def _validate_event_type(self, text: str, context: Optional[str]) -> ValidationResult:
        """Validate EVENT_TYPE entity."""
        is_valid, confidence, category = self.kb.validate_event_type(text)

        if category:
            return ValidationResult(
                is_valid=True,
                confidence_adjustment=1.2,
                reason=f"Known event type: {category}",
                metadata={"violence_category": category}
            )

        if is_valid:
            return ValidationResult(
                is_valid=True,
                confidence_adjustment=1.0,
                reason="Matches event type pattern"
            )

        return ValidationResult(
            is_valid=True,
            confidence_adjustment=0.7,
            reason="Possible event type"
        )

    def _validate_action(self, text: str, context: Optional[str]) -> ValidationResult:
        """Validate ACTION entity."""
        action_patterns = [
            r'\b(attacked?|raided?|ambushed?|stormed?|seized?)\b',
            r'\b(killed?|murdered?|executed?|assassinated?)\b',
            r'\b(bombed?|shelled?|burned?|destroyed?)\b',
            r'\b(abducted?|kidnapped?|captured?|detained?)\b',
            r'\b(clashed?|fought?|battled?|confronted?)\b',
        ]

        for pattern in action_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return ValidationResult(
                    is_valid=True,
                    confidence_adjustment=1.1,
                    reason="Matches action verb pattern"
                )

        return ValidationResult(
            is_valid=True,
            confidence_adjustment=0.8,
            reason="Generic action"
        )

    def _validate_weapon(self, text: str, context: Optional[str]) -> ValidationResult:
        """Validate WEAPON entity."""
        for pattern in self._weapon_patterns:
            if pattern.search(text):
                return ValidationResult(
                    is_valid=True,
                    confidence_adjustment=1.2,
                    reason="Known weapon type"
                )

        return ValidationResult(
            is_valid=True,
            confidence_adjustment=0.8,
            reason="Generic weapon"
        )

    def _validate_violence_type(self, text: str, context: Optional[str]) -> ValidationResult:
        """Validate VIOLENCE_TYPE entity."""
        violence_results = self.kb.extract_violence_types(text)

        if violence_results:
            return ValidationResult(
                is_valid=True,
                confidence_adjustment=1.2,
                reason=f"Known violence type: {violence_results[0]['category']}",
                metadata={"category": violence_results[0]['category']}
            )

        return ValidationResult(
            is_valid=True,
            confidence_adjustment=0.9,
            reason="Generic violence type"
        )

    # ========================================================================
    # WHEN VALIDATORS
    # ========================================================================

    def _validate_date(self, text: str, context: Optional[str]) -> ValidationResult:
        """Validate DATE entity."""
        for pattern in self._date_patterns:
            if pattern.search(text):
                return ValidationResult(
                    is_valid=True,
                    confidence_adjustment=1.2,
                    reason="Valid date format"
                )

        # Check for year only
        if re.match(r'^(19|20)\d{2}$', text.strip()):
            return ValidationResult(
                is_valid=True,
                confidence_adjustment=1.0,
                reason="Year only"
            )

        return ValidationResult(
            is_valid=False,
            confidence_adjustment=0.5,
            reason="Invalid date format"
        )

    def _validate_time(self, text: str, context: Optional[str]) -> ValidationResult:
        """Validate TIME entity."""
        time_patterns = [
            r'\b(\d{1,2}):(\d{2})\s*(am|pm|AM|PM)?\b',
            r'\b(\d{1,2})\s*(am|pm|AM|PM)\b',
            r'\b(morning|afternoon|evening|night|dawn|dusk|midnight|noon)\b',
        ]

        for pattern in time_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return ValidationResult(
                    is_valid=True,
                    confidence_adjustment=1.1,
                    reason="Valid time format"
                )

        return ValidationResult(
            is_valid=True,
            confidence_adjustment=0.7,
            reason="Possible time expression"
        )

    def _validate_duration(self, text: str, context: Optional[str]) -> ValidationResult:
        """Validate DURATION entity."""
        duration_patterns = [
            r'\b(\d+)\s*(hours?|days?|weeks?|months?|years?)\b',
            r'\b(several|few|many)\s*(hours?|days?|weeks?|months?)\b',
            r'\b(overnight|all\s+day|for\s+\w+)\b',
        ]

        for pattern in duration_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return ValidationResult(
                    is_valid=True,
                    confidence_adjustment=1.1,
                    reason="Valid duration format"
                )

        return ValidationResult(
            is_valid=True,
            confidence_adjustment=0.8,
            reason="Generic duration"
        )

    def _validate_frequency(self, text: str, context: Optional[str]) -> ValidationResult:
        """Validate FREQUENCY entity."""
        freq_patterns = [
            r'\b(daily|weekly|monthly|yearly|annually)\b',
            r'\b(once|twice|three\s+times|multiple\s+times)\b',
            r'\b(repeatedly|frequently|often|regularly)\b',
        ]

        for pattern in freq_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return ValidationResult(
                    is_valid=True,
                    confidence_adjustment=1.1,
                    reason="Valid frequency expression"
                )

        return ValidationResult(
            is_valid=True,
            confidence_adjustment=0.8,
            reason="Generic frequency"
        )

    # ========================================================================
    # WHERE VALIDATORS
    # ========================================================================

    def _validate_country(self, text: str, context: Optional[str]) -> ValidationResult:
        """Validate COUNTRY entity."""
        if self.kb.is_african_country(text):
            info = self.kb.get_country_info(text)
            return ValidationResult(
                is_valid=True,
                confidence_adjustment=1.3,  # Strong boost for known country
                reason=f"Known African country (Region: {info['region']})",
                canonical_form=text.title(),
                metadata={"region": info['region'], "capital": info['capital']}
            )

        # Check if it might be a non-African country mentioned in context
        non_african_countries = [
            "russia", "china", "usa", "united states", "france", "uk",
            "united kingdom", "turkey", "iran", "saudi arabia", "uae"
        ]

        if text.lower() in non_african_countries:
            return ValidationResult(
                is_valid=True,
                confidence_adjustment=0.8,
                reason="Non-African country (foreign involvement)",
                metadata={"is_african": False}
            )

        return ValidationResult(
            is_valid=False,
            confidence_adjustment=0.4,
            reason="Unknown country"
        )

    def _validate_region(self, text: str, context: Optional[str]) -> ValidationResult:
        """Validate REGION entity."""
        # Check if it's a known conflict zone region
        for country, info in AFRICAN_COUNTRIES.items():
            if text.lower() in [z.lower() for z in info.get('conflict_zones', [])]:
                return ValidationResult(
                    is_valid=True,
                    confidence_adjustment=1.2,
                    reason=f"Known conflict region in {country.title()}",
                    metadata={"country": country}
                )

        region_patterns = [
            r'\b(north|south|east|west|central)\s+\w+\b',
            r'\b\w+\s+(region|province|state|prefecture)\b',
        ]

        for pattern in region_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return ValidationResult(
                    is_valid=True,
                    confidence_adjustment=1.0,
                    reason="Matches region pattern"
                )

        return ValidationResult(
            is_valid=True,
            confidence_adjustment=0.8,
            reason="Generic region"
        )

    def _validate_city(self, text: str, context: Optional[str]) -> ValidationResult:
        """Validate CITY entity."""
        if self.kb.is_conflict_city(text):
            info = self.kb.get_city_info(text)
            return ValidationResult(
                is_valid=True,
                confidence_adjustment=1.3,
                reason=f"Known conflict city ({info['country']})",
                canonical_form=text.title(),
                metadata={"country": info['country'], "region": info['region']}
            )

        # Check if it's a capital
        for country, info in AFRICAN_COUNTRIES.items():
            if text.lower() == info['capital'].lower():
                return ValidationResult(
                    is_valid=True,
                    confidence_adjustment=1.2,
                    reason=f"Capital of {country.title()}",
                    canonical_form=info['capital'],
                    metadata={"country": country, "is_capital": True}
                )

        return ValidationResult(
            is_valid=True,
            confidence_adjustment=0.9,
            reason="Unknown city"
        )

    def _validate_district(self, text: str, context: Optional[str]) -> ValidationResult:
        """Validate DISTRICT entity."""
        district_patterns = [
            r'\b\w+\s+(district|county|municipality)\b',
            r'\b(local\s+government\s+area|LGA)\b',
        ]

        for pattern in district_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return ValidationResult(
                    is_valid=True,
                    confidence_adjustment=1.0,
                    reason="Matches district pattern"
                )

        return ValidationResult(
            is_valid=True,
            confidence_adjustment=0.8,
            reason="Generic district"
        )

    def _validate_facility(self, text: str, context: Optional[str]) -> ValidationResult:
        """Validate FACILITY entity."""
        facility_patterns = [
            r'\b(church|mosque|temple|shrine)\b',
            r'\b(school|university|college|hospital|clinic)\b',
            r'\b(market|mall|station|airport|port)\b',
            r'\b(prison|jail|detention\s+center)\b',
            r'\b(military\s+base|barracks|checkpoint)\b',
        ]

        for pattern in facility_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return ValidationResult(
                    is_valid=True,
                    confidence_adjustment=1.1,
                    reason="Matches facility pattern"
                )

        return ValidationResult(
            is_valid=True,
            confidence_adjustment=0.8,
            reason="Generic facility"
        )

    def _validate_geographic(self, text: str, context: Optional[str]) -> ValidationResult:
        """Validate GEOGRAPHIC entity."""
        geo_patterns = [
            r'\b(river|lake|mountain|forest|desert|valley)\b',
            r'\b(border|frontier|coastline|plain)\b',
            r'\b(national\s+park|reserve|sanctuary)\b',
        ]

        for pattern in geo_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return ValidationResult(
                    is_valid=True,
                    confidence_adjustment=1.1,
                    reason="Matches geographic feature"
                )

        return ValidationResult(
            is_valid=True,
            confidence_adjustment=0.8,
            reason="Generic geographic feature"
        )

    def _validate_coordinates(self, text: str, context: Optional[str]) -> ValidationResult:
        """Validate COORDINATES entity."""
        for pattern in self._coordinate_patterns:
            if pattern.search(text):
                return ValidationResult(
                    is_valid=True,
                    confidence_adjustment=1.3,
                    reason="Valid GPS coordinate format"
                )

        return ValidationResult(
            is_valid=False,
            confidence_adjustment=0.3,
            reason="Invalid coordinate format"
        )

    # ========================================================================
    # HOW VALIDATORS
    # ========================================================================

    def _validate_casualties(self, text: str, context: Optional[str]) -> ValidationResult:
        """Validate CASUALTIES entity."""
        for pattern in self._casualty_patterns:
            if pattern.search(text):
                return ValidationResult(
                    is_valid=True,
                    confidence_adjustment=1.2,
                    reason="Valid casualty expression"
                )

        # Just a number
        if re.match(r'^\d+$', text.strip()):
            return ValidationResult(
                is_valid=True,
                confidence_adjustment=0.9,
                reason="Numeric casualty count"
            )

        return ValidationResult(
            is_valid=True,
            confidence_adjustment=0.7,
            reason="Generic casualty expression"
        )

    def _validate_injured(self, text: str, context: Optional[str]) -> ValidationResult:
        """Validate INJURED entity."""
        injured_patterns = [
            r'\b(\d+)\s*(people\s+)?(injured|wounded|hurt)\b',
            r'\b(injured|wounded|hurt)\s+(\d+)\b',
        ]

        for pattern in injured_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return ValidationResult(
                    is_valid=True,
                    confidence_adjustment=1.2,
                    reason="Valid injury count"
                )

        return ValidationResult(
            is_valid=True,
            confidence_adjustment=0.8,
            reason="Generic injury expression"
        )

    def _validate_displacement(self, text: str, context: Optional[str]) -> ValidationResult:
        """Validate DISPLACEMENT entity."""
        for pattern in self._displacement_patterns:
            if pattern.search(text):
                return ValidationResult(
                    is_valid=True,
                    confidence_adjustment=1.2,
                    reason="Valid displacement expression"
                )

        return ValidationResult(
            is_valid=True,
            confidence_adjustment=0.8,
            reason="Generic displacement"
        )

    def _validate_damage(self, text: str, context: Optional[str]) -> ValidationResult:
        """Validate DAMAGE entity."""
        damage_patterns = [
            r'\b(\d+)\s*(houses?|buildings?|vehicles?|structures?)\s*(destroyed?|burned?|damaged?)\b',
            r'\b(destroyed?|burned?|razed?|looted?)\b',
            r'\b(infrastructure|property)\s+(damage|destruction)\b',
        ]

        for pattern in damage_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return ValidationResult(
                    is_valid=True,
                    confidence_adjustment=1.1,
                    reason="Valid damage expression"
                )

        return ValidationResult(
            is_valid=True,
            confidence_adjustment=0.8,
            reason="Generic damage"
        )

    # ========================================================================
    # WHY VALIDATORS
    # ========================================================================

    def _validate_motive(self, text: str, context: Optional[str]) -> ValidationResult:
        """Validate MOTIVE entity."""
        motive_patterns = [
            r'\b(revenge|retaliation|reprisal)\b',
            r'\b(ethnic|religious|political|territorial)\b',
            r'\b(land\s+dispute|resource\s+conflict|power\s+struggle)\b',
            r'\b(insurgency|rebellion|jihad|extremism)\b',
        ]

        for pattern in motive_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return ValidationResult(
                    is_valid=True,
                    confidence_adjustment=1.1,
                    reason="Matches motive pattern"
                )

        return ValidationResult(
            is_valid=True,
            confidence_adjustment=0.8,
            reason="Generic motive"
        )

    def _validate_trigger(self, text: str, context: Optional[str]) -> ValidationResult:
        """Validate TRIGGER entity."""
        trigger_patterns = [
            r'\b(in\s+response\s+to|following|after)\b',
            r'\b(sparked\s+by|triggered\s+by|caused\s+by)\b',
            r'\b(election|protest|demonstration|arrest)\b',
        ]

        for pattern in trigger_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return ValidationResult(
                    is_valid=True,
                    confidence_adjustment=1.1,
                    reason="Matches trigger pattern"
                )

        return ValidationResult(
            is_valid=True,
            confidence_adjustment=0.8,
            reason="Generic trigger"
        )

    # ========================================================================
    # CROSS-ENTITY CONSISTENCY VALIDATION
    # ========================================================================

    def validate_cross_entity_consistency(
        self,
        entities: List[Dict]
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Check consistency across multiple entities in the same text.

        Validates:
        - Multiple countries may indicate multiple events
        - Perpetrator without action/event type
        - Location hierarchy consistency
        - Temporal consistency

        Args:
            entities: List of entity dicts with 'text', 'label' keys

        Returns:
            Tuple of (is_consistent, issues, warnings)
        """
        issues = []
        warnings = []

        # Group entities by type
        by_type = {}
        for e in entities:
            label = e.get('label', '')
            if label.startswith('B-') or label.startswith('I-'):
                label = label[2:]
            if label not in by_type:
                by_type[label] = []
            by_type[label].append(e)

        # Check 1: Multiple countries may indicate multiple events
        countries = by_type.get('COUNTRY', [])
        if len(countries) > 2:
            warnings.append(
                f"Multiple countries detected ({len(countries)}): "
                f"{', '.join([c['text'] for c in countries[:3]])}. "
                "May contain multiple events - consider using multi-event extraction."
            )

        # Check 2: Perpetrator without action
        perpetrators = by_type.get('PERPETRATOR', []) + by_type.get('GOVERNMENT', [])
        actions = by_type.get('ACTION', []) + by_type.get('EVENT_TYPE', [])

        if perpetrators and not actions:
            warnings.append(
                "Perpetrator identified but no action/event type found. "
                "The event description may be incomplete."
            )

        # Check 3: Casualties without perpetrator
        casualties = by_type.get('CASUALTIES', []) + by_type.get('INJURED', [])
        if casualties and not perpetrators and not by_type.get('EVENT_TYPE', []):
            warnings.append(
                "Casualties reported but no perpetrator or event type identified. "
                "Consider reviewing entity extraction."
            )

        # Check 4: Location hierarchy - city should have region/country
        cities = by_type.get('CITY', [])
        regions = by_type.get('REGION', [])

        if cities and not countries and not regions:
            warnings.append(
                f"City identified ({cities[0]['text']}) but no country/region. "
                "Geographic context may be incomplete."
            )

        # Check 5: Date without event
        dates = by_type.get('DATE', []) + by_type.get('TIME', [])
        if dates and not actions and not by_type.get('EVENT_TYPE', []):
            warnings.append(
                "Temporal information found but no event type/action. "
                "May indicate incomplete extraction."
            )

        # Check 6: WHY without WHO/WHAT
        motives = by_type.get('MOTIVE', []) + by_type.get('TRIGGER', [])
        if motives and not perpetrators and not actions:
            issues.append(
                "Motive/trigger identified without perpetrator or action. "
                "This may indicate entity type confusion."
            )

        is_consistent = len(issues) == 0
        return is_consistent, issues, warnings

    def validate_event_completeness(
        self,
        entities: List[Dict]
    ) -> Dict[str, Any]:
        """
        Check how complete the 5W1H extraction is for this event.

        Returns a completeness score and missing categories.
        """
        # Group by 5W1H category
        category_mapping = {
            'WHO': ['PERPETRATOR', 'VICTIM', 'TARGET', 'ORGANIZATION', 'GOVERNMENT'],
            'WHAT': ['EVENT_TYPE', 'ACTION', 'WEAPON', 'VIOLENCE_TYPE'],
            'WHEN': ['DATE', 'TIME', 'DURATION', 'FREQUENCY'],
            'WHERE': ['COUNTRY', 'REGION', 'CITY', 'DISTRICT', 'FACILITY', 'GEOGRAPHIC', 'COORDINATES'],
            'HOW': ['CASUALTIES', 'INJURED', 'DISPLACEMENT', 'DAMAGE'],
            'WHY': ['MOTIVE', 'TRIGGER'],
        }

        found_categories = set()
        category_entities = {cat: [] for cat in category_mapping}

        for e in entities:
            label = e.get('label', '')
            if label.startswith('B-') or label.startswith('I-'):
                label = label[2:]

            for category, types in category_mapping.items():
                if label in types:
                    found_categories.add(category)
                    category_entities[category].append(e)
                    break

        # Core categories (WHO, WHAT, WHEN, WHERE) are more important
        core_categories = {'WHO', 'WHAT', 'WHEN', 'WHERE'}
        core_found = found_categories.intersection(core_categories)

        # Calculate scores
        core_score = len(core_found) / len(core_categories)
        total_score = len(found_categories) / len(category_mapping)

        missing = [cat for cat in category_mapping if cat not in found_categories]

        return {
            'completeness_score': total_score,
            'core_completeness': core_score,
            'found_categories': list(found_categories),
            'missing_categories': missing,
            'category_entities': {k: len(v) for k, v in category_entities.items()},
            'is_minimal_complete': 'WHO' in found_categories and 'WHERE' in found_categories,
        }


# ============================================================================
# MODULE-LEVEL SINGLETON
# ============================================================================

_validator: Optional[EntityValidator] = None

def get_validator() -> EntityValidator:
    """Get the singleton validator instance."""
    global _validator
    if _validator is None:
        _validator = EntityValidator()
    return _validator


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def validate_entity(text: str, label: str, context: Optional[str] = None) -> ValidationResult:
    """
    Validate a single entity.

    Args:
        text: Entity text
        label: Entity label
        context: Optional surrounding text

    Returns:
        ValidationResult
    """
    return get_validator().validate_entity(text, label, context)


def validate_entities(entities: List[Dict], full_text: Optional[str] = None) -> List[Dict]:
    """
    Validate multiple entities.

    Args:
        entities: List of entity dicts
        full_text: Full text for context

    Returns:
        Validated entities with adjusted scores
    """
    return get_validator().validate_entities(entities, full_text)


# ============================================================================
# DEMO / TESTING
# ============================================================================

if __name__ == '__main__':
    validator = get_validator()

    print("=" * 60)
    print("ENTITY VALIDATOR DEMO")
    print("=" * 60)

    # Test entities
    test_entities = [
        ("Al-Shabaab", "B-PERPETRATOR"),
        ("militants", "B-PERPETRATOR"),
        ("unknown group xyz", "B-PERPETRATOR"),
        ("Mogadishu", "B-CITY"),
        ("Nigeria", "B-COUNTRY"),
        ("Unknown Place", "B-CITY"),
        ("15 January 2024", "B-DATE"),
        ("yesterday", "B-DATE"),
        ("xyz123", "B-DATE"),
        ("30 killed", "B-CASUALTIES"),
        ("AK-47", "B-WEAPON"),
        ("attack", "B-EVENT_TYPE"),
    ]

    print("\nEntity Validation Results:")
    print("-" * 60)

    for text, label in test_entities:
        result = validator.validate_entity(text, label)
        status = "✅" if result.is_valid else "❌"
        adj = f"{result.confidence_adjustment:.2f}x"
        canonical = f" -> {result.canonical_form}" if result.canonical_form else ""
        print(f"{status} {label:20} '{text}'{canonical}")
        print(f"   Confidence: {adj}, Reason: {result.reason}")

    # Test with full entity list
    print("\n" + "=" * 60)
    print("BATCH VALIDATION")
    print("=" * 60)

    entities = [
        {"text": "Boko Haram", "label": "B-PERPETRATOR", "score": 0.85, "start": 0, "end": 10},
        {"text": "Maiduguri", "label": "B-CITY", "score": 0.75, "start": 30, "end": 39},
        {"text": "Monday", "label": "B-DATE", "score": 0.90, "start": 43, "end": 49},
        {"text": "15 killed", "label": "B-CASUALTIES", "score": 0.80, "start": 51, "end": 60},
    ]

    full_text = "Boko Haram militants attacked Maiduguri on Monday, leaving 15 killed."

    validated = validator.validate_entities(entities, full_text)

    print(f"\nText: {full_text}\n")
    for ent in validated:
        orig = ent['validation']['original_score']
        new = ent['score']
        change = "↑" if new > orig else "↓" if new < orig else "="
        print(f"  {ent['label']:20} '{ent['text']}'")
        print(f"    Score: {orig:.2f} {change} {new:.2f}")
        print(f"    Reason: {ent['validation']['reason']}")

    print("\n✅ Entity Validator OK!")
