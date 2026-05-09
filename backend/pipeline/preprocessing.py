"""
Data Preprocessing - Week 9-10
Converts ACLED JSONL or CSV annotations to BIO-tagged JSONL format for NER training

Author: Binalfew Kassa Mekonnen
Date: December 2025

Features:
- 8-entity schema optimized for grounded extraction (5W1H framework)
- Supports both JSONL and CSV input formats
- Outputs JSONL format for memory-efficient training
- Improved tokenization for African names (hyphens, apostrophes, diacritics)
- Smart entity extraction with grounding verification

Note: Event type classification (taxonomy) is handled separately as a post-NER task.
"""

import pandas as pd
import json
import re
import unicodedata
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict
import logging

from .config import LabelConfigs, CSVToNERMapping

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# ENTITY COLUMNS - 8-type schema (optimized for grounded extraction)
# ============================================================================

# Entity columns for 8-type grounded schema
ENTITY_COLUMNS = [
    # WHO (1 type) - All actors merged
    'ACTOR',
    # WHOM (1 type) - Victims
    'VICTIM',
    # WHAT (1 type) - Actions
    'ACTION',
    # WHEN (1 type)
    'DATE',
    # WHERE (3 types)
    'REGION', 'CITY', 'DISTRICT',
    # HOW (1 type)
    'CASUALTIES',
]


# ============================================================================
# AFRICAN NAME PATTERNS
# ============================================================================

# African country names - should NEVER be labeled as ACTOR or VICTIM
AFRICAN_COUNTRIES = {
    'Nigeria', 'Somalia', 'Sudan', 'South Sudan', 'Ethiopia', 'Kenya',
    'Uganda', 'Tanzania', 'Rwanda', 'Burundi', 'DRC', 'Congo',
    'Democratic Republic of Congo', 'Central African Republic', 'CAR',
    'Cameroon', 'Chad', 'Niger', 'Mali', 'Burkina Faso', 'Senegal',
    'Guinea', 'Sierra Leone', 'Liberia', 'Ghana', 'Togo', 'Benin',
    'Ivory Coast', "Cote d'Ivoire", 'Mauritania', 'Libya', 'Egypt',
    'Tunisia', 'Algeria', 'Morocco', 'South Africa', 'Zimbabwe',
    'Zambia', 'Malawi', 'Mozambique', 'Angola', 'Namibia', 'Botswana',
    'Lesotho', 'Eswatini', 'Swaziland', 'Madagascar', 'Mauritius',
    'Djibouti', 'Eritrea', 'Gabon', 'Equatorial Guinea',
    'Republic of Congo', 'Congo-Brazzaville', 'Gambia', 'Guinea-Bissau',
    'Cape Verde', 'Comoros', 'Seychelles', 'São Tomé and Príncipe',
}

# Lowercase version for case-insensitive matching
AFRICAN_COUNTRIES_LOWER = {c.lower() for c in AFRICAN_COUNTRIES}

# Common African name patterns that should be kept together
AFRICAN_NAME_PATTERNS = [
    # Names with hyphens (e.g., "Al-Shabaab", "N'Djamena")
    r"[A-Z][a-z]+-[A-Z][a-z]+",
    r"Al-[A-Z][a-z]+",
    r"El-[A-Z][a-z]+",

    # Names with apostrophes (e.g., "N'Djamena", "M'Bour")
    r"[A-Z]'[A-Z][a-z]+",
    r"[A-Z][a-z]*'[a-z]+",

    # Names with diacritics (handled via Unicode normalization)
    # These are preserved during tokenization

    # Common armed group patterns
    r"Boko\s+Haram",
    r"Al[\s-]Shabaab",
    r"Al[\s-]Qaeda",
    r"Islamic\s+State",
    r"Lord's\s+Resistance\s+Army",
    r"Rapid\s+Support\s+Forces",
    r"Sudan\s+People's\s+Liberation\s+Army",
]

# Compile patterns
AFRICAN_NAME_REGEX = re.compile(
    '|'.join(f'({p})' for p in AFRICAN_NAME_PATTERNS),
    re.IGNORECASE
)


class AnnotationPreprocessor:
    """Convert ACLED JSONL or CSV annotations to BIO-tagged JSONL format."""

    def __init__(self, input_file: str, output_dir: str = 'data/processed'):
        """
        Initialize preprocessor.

        Args:
            input_file: Path to JSONL or CSV file with annotations
            output_dir: Directory to save processed data
        """
        self.input_file = input_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.label2id = LabelConfigs.get_label2id()
        self.id2label = LabelConfigs.get_id2label()

        # Determine input format
        self.is_jsonl = input_file.endswith('.jsonl')

    def load_data(self) -> List[Dict]:
        """Load data from JSONL or CSV file."""
        if self.is_jsonl:
            return self.load_jsonl()
        else:
            return self.load_csv()

    def load_jsonl(self) -> List[Dict]:
        """Load JSONL file with ACLED annotations."""
        logger.info(f"Loading JSONL from: {self.input_file}")
        events = []
        with open(self.input_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line))
        logger.info(f"Loaded {len(events)} events from JSONL")
        return events

    def load_csv(self) -> List[Dict]:
        """Load CSV file with annotations and convert to list of dicts."""
        logger.info(f"Loading CSV from: {self.input_file}")
        df = pd.read_csv(self.input_file)
        logger.info(f"Loaded {len(df)} events from CSV")
        return df.to_dict('records')

    def extract_entities_from_row(self, row: pd.Series) -> List[Dict]:
        """
        Extract entities from a cleaned CSV row.

        The cleaned CSV has entity columns (PERPETRATOR, VICTIM, etc.) that contain
        actual text spans found in Event_Description, separated by semicolons.

        Supports both:
        - Direct entity columns (PERPETRATOR, VICTIM, etc.)
        - Mapped columns via CSVToNERMapping (Actor_Normalized -> PERPETRATOR)

        Returns list of entities: [{'text': 'Boko Haram', 'type': 'PERPETRATOR', 'start': 0, 'end': 10}, ...]
        """
        entities = []
        text = row.get('Event_Description', '')

        if pd.isna(text) or not text:
            return entities

        # Normalize text for better matching
        normalized_text = self._normalize_text_for_matching(text)

        # Get available columns in this row
        available_columns = set(row.index)

        # Determine which entity columns to use
        entity_columns_to_use = []

        # First, try direct entity columns (PERPETRATOR, VICTIM, etc.)
        for entity_type in ENTITY_COLUMNS:
            if entity_type in available_columns:
                entity_columns_to_use.append((entity_type, entity_type))

        # Also check mapped columns (Actor_Normalized -> PERPETRATOR)
        for column in available_columns:
            mapped_type = CSVToNERMapping.get_entity_for_column(column)
            if mapped_type and (column, mapped_type) not in entity_columns_to_use:
                # Avoid duplicate mappings
                already_mapped = any(et == mapped_type for _, et in entity_columns_to_use)
                if not already_mapped or column != mapped_type:
                    entity_columns_to_use.append((column, mapped_type))

        # Process each entity column
        for column_name, entity_type in entity_columns_to_use:
            entity_value = row.get(column_name, '')
            if pd.isna(entity_value) or not str(entity_value).strip():
                continue

            # Handle multiple entities separated by semicolon or pipe
            separators = r'[;|]'
            for entity_text in re.split(separators, str(entity_value)):
                entity_text = entity_text.strip()
                if not entity_text or len(entity_text) < 2:
                    continue

                # Normalize entity text for matching
                normalized_entity = self._normalize_text_for_matching(entity_text)

                # Find all occurrences in text (case-insensitive)
                # Use word boundaries to avoid partial matches
                try:
                    # Escape special regex characters but handle spaces
                    escaped = re.escape(normalized_entity)
                    # Allow flexible whitespace matching
                    escaped = escaped.replace(r'\ ', r'\s+')
                    pattern = re.compile(r'\b' + escaped + r'\b', re.IGNORECASE | re.UNICODE)

                    for match in pattern.finditer(normalized_text):
                        entities.append({
                            'text': text[match.start():match.end()],  # Use original text
                            'type': entity_type,
                            'start': match.start(),
                            'end': match.end(),
                        })
                except re.error:
                    # Fallback to simple substring search if regex fails
                    start = 0
                    while True:
                        pos = text.lower().find(entity_text.lower(), start)
                        if pos == -1:
                            break
                        entities.append({
                            'text': text[pos:pos + len(entity_text)],
                            'type': entity_type,
                            'start': pos,
                            'end': pos + len(entity_text),
                        })
                        start = pos + 1

        # Remove overlapping entities
        entities = self._remove_overlapping_entities(entities)

        # Handle nested location entities (e.g., "Maiduguri, Borno State, Nigeria")
        entities = self._handle_nested_location_entities(entities)

        # Sort by start position
        entities.sort(key=lambda x: x['start'])
        return entities

    def extract_entities_from_jsonl_event(self, event: Dict) -> List[Dict]:
        """
        Extract entities from an ACLED JSONL event.

        The JSONL has an 'entities' array with entity information.
        We extract only entities that are grounded in the text.
        Also extracts DATE from natural language patterns.

        Returns list of entities: [{'text': 'M23', 'type': 'PERPETRATOR', 'start': 21, 'end': 24}, ...]
        """
        entities = []
        text = event.get('text', '')

        if not text:
            return entities

        # Extract DATE from natural language patterns first
        date_entities = self._extract_dates_from_text(text)
        entities.extend(date_entities)

        # Extract CASUALTIES from natural language patterns
        casualty_entities = self._extract_casualties_from_text(text)
        entities.extend(casualty_entities)

        # Get pre-annotated entities from JSONL
        jsonl_entities = event.get('entities', [])

        for ent in jsonl_entities:
            ent_type = ent.get('type', '')
            ent_text = ent.get('text', '')

            # Skip entity types not in our 12-type schema
            if ent_type not in ENTITY_COLUMNS:
                continue

            # Skip empty or very short entities
            if not ent_text or len(ent_text) < 2:
                continue

            # Try to find the entity text in the event text
            grounded_text = self._find_grounded_text(ent_text, text)

            if grounded_text:
                # Find position in text
                match = re.search(rf'\b{re.escape(grounded_text)}\b', text, re.IGNORECASE)
                if match:
                    actual_text = text[match.start():match.end()]

                    # CRITICAL FIX: Country names should NEVER be ACTOR or VICTIM
                    # They should be REGION or skipped entirely
                    corrected_type = self._correct_country_label(actual_text, ent_type)

                    # Skip if country name was incorrectly labeled as ACTOR/VICTIM
                    if corrected_type is None:
                        continue

                    entities.append({
                        'text': actual_text,
                        'type': corrected_type,
                        'start': match.start(),
                        'end': match.end(),
                    })

        # Remove overlapping entities
        entities = self._remove_overlapping_entities(entities)

        # Sort by start position
        entities.sort(key=lambda x: x['start'])
        return entities

    def _extract_dates_from_text(self, text: str) -> List[Dict]:
        """
        Extract DATE entities from natural language text.

        Patterns matched:
        - "20 December 2024" / "20 Dec 2024" (full and abbreviated months)
        - "December 20, 2024"
        - "December 2024"
        - "early/mid/late December 2024"
        - "On Monday" / "last Tuesday" (day of week)
        """
        entities = []

        # Full month names
        full_months = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)'
        # Abbreviated month names
        abbrev_months = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)'
        # Combined
        all_months = f'(?:{full_months}|{abbrev_months})'

        # Date patterns (ordered from most specific to least specific)
        date_patterns = [
            # "20 December 2024" or "20 Dec 2024" or "20 December, 2024"
            rf'\b(\d{{1,2}}\s+{all_months},?\s+\d{{4}})\b',
            # "December 20, 2024" or "Dec 20 2024"
            rf'\b({all_months}\s+\d{{1,2}},?\s+\d{{4}})\b',
            # "early/mid/late December 2024"
            rf'\b((?:early|mid|late)\s+{all_months}\s+\d{{4}})\b',
            # Month Year (e.g., "December 2024", "Dec 2024")
            rf'\b({all_months}\s+\d{{4}})\b',
            # Day of week with context (e.g., "on Monday", "last Tuesday")
            r'\b((?:on\s+|last\s+|this\s+)?(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)(?:\s+(?:morning|afternoon|evening|night))?)\b',
        ]

        found_spans = set()  # Track found spans to avoid duplicates

        for pattern in date_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                span = (match.start(), match.end())
                # Avoid overlapping dates
                if not any(s[0] <= span[0] < s[1] or s[0] < span[1] <= s[1] for s in found_spans):
                    entities.append({
                        'text': match.group(1),
                        'type': 'DATE',
                        'start': match.start(),
                        'end': match.end(),
                    })
                    found_spans.add(span)

        return entities

    def _extract_casualties_from_text(self, text: str) -> List[Dict]:
        """
        Extract CASUALTIES entities from natural language text.

        Patterns matched:
        - "killed 15 people" / "15 killed"
        - "at least 20 dead"
        - "5 soldiers killed"
        - "killing 10"
        - "left 3 dead"
        """
        entities = []

        # Casualty patterns (capture the number and context)
        casualty_patterns = [
            # "killed/kills X people/soldiers/etc"
            r'\b(kill(?:ed|ing|s)?\s+(?:at\s+least\s+)?(\d+)(?:\s+\w+)?)\b',
            # "X killed/dead"
            r'\b((\d+)\s+(?:\w+\s+)?(?:killed|dead|died|slain))\b',
            # "at least X dead/killed"
            r'\b(at\s+least\s+(\d+)\s+(?:\w+\s+)?(?:dead|killed|died))\b',
            # "left X dead"
            r'\b(left\s+(\d+)\s+(?:\w+\s+)?dead)\b',
            # "X fatalities/casualties/deaths"
            r'\b((\d+)\s+(?:fatalit(?:y|ies)|casualt(?:y|ies)|deaths?))\b',
            # "claiming X lives"
            r'\b(claiming\s+(\d+)\s+lives?)\b',
        ]

        found_spans = set()

        for pattern in casualty_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                span = (match.start(), match.end())
                # Avoid overlapping
                if not any(s[0] <= span[0] < s[1] or s[0] < span[1] <= s[1] for s in found_spans):
                    entities.append({
                        'text': match.group(1),
                        'type': 'CASUALTIES',
                        'start': match.start(),
                        'end': match.start() + len(match.group(1)),
                    })
                    found_spans.add(span)

        return entities

    def _correct_country_label(self, entity_text: str, original_type: str) -> Optional[str]:
        """
        Correct entity labels for country names.

        Country names should NEVER be labeled as ACTOR or VICTIM.
        - If labeled as ACTOR/VICTIM, return None (skip the entity)
        - If labeled as REGION, keep it
        - Otherwise, keep original label

        Args:
            entity_text: The actual entity text
            original_type: The original entity type from ACLED

        Returns:
            Corrected entity type, or None to skip the entity
        """
        # Check if entity is a country name
        entity_lower = entity_text.lower().strip()

        # Check against country list
        is_country = entity_lower in AFRICAN_COUNTRIES_LOWER

        # Also check if it's a partial match (e.g., "Nigeria" in "central Nigeria")
        if not is_country:
            for country in AFRICAN_COUNTRIES_LOWER:
                if entity_lower == country or entity_lower.endswith(country):
                    is_country = True
                    break

        if is_country:
            # Country names should NOT be ACTOR or VICTIM
            if original_type in ('ACTOR', 'VICTIM'):
                # Skip this entity entirely - it's incorrectly labeled
                return None
            # If it's already REGION, keep it
            elif original_type == 'REGION':
                return 'REGION'
            # Otherwise, keep the original type
            else:
                return original_type

        # Not a country - return original type
        return original_type

    def _find_grounded_text(self, normalized_text: str, event_text: str) -> Optional[str]:
        """
        Find the actual grounded text in the event text.

        Handles cases like:
        - "M23: March 23 Movement" -> "M23" (prefix before colon)
        - "Military Forces of the Democratic Republic of Congo" -> "FARDC" or "military forces"
        - "Rapid Support Forces" -> "RSF" (abbreviation)
        - "Democratic Republic of Congo" -> "DRC" or "Congo"
        - Direct match
        """
        event_text_lower = event_text.lower()

        # Strategy 1: Direct match
        if normalized_text.lower() in event_text_lower:
            return normalized_text

        # Strategy 2: Prefix before colon (e.g., "M23: March 23 Movement" -> "M23")
        if ':' in normalized_text:
            prefix = normalized_text.split(':')[0].strip()
            if prefix.lower() in event_text_lower:
                return prefix

        # Strategy 3: First word (e.g., "Al Shabaab" from full name)
        first_word = normalized_text.split()[0] if normalized_text.split() else ''
        if len(first_word) >= 2 and first_word.lower() in event_text_lower:
            return first_word

        # Strategy 4: Try first N words (for multi-word matches)
        words = normalized_text.split()
        for n in range(min(3, len(words)), 0, -1):
            partial = ' '.join(words[:n])
            if len(partial) >= 3 and partial.lower() in event_text_lower:
                return partial

        # Strategy 5: Common abbreviations and alternative names
        abbrev_map = {
            # Armed forces
            'Rapid Support Forces': ['RSF', 'Rapid Support', 'paramilitary'],
            'Military Forces of': ['military forces', 'army', 'soldiers', 'troops', 'military'],
            'Sudan Armed Forces': ['SAF', 'Sudan Armed', 'Sudanese military', 'Sudanese army'],
            'Armed Forces of the Democratic Republic of Congo': ['FARDC', 'Congolese military', 'DRC military'],
            'Sudanese Armed Forces': ['SAF', 'Sudanese military', 'army'],
            'Police Forces of': ['police', 'security forces'],
            'Military Forces of': ['military', 'army', 'soldiers', 'troops', 'forces'],
            # Countries - expanded
            'Democratic Republic of Congo': ['DRC', 'Congo', 'DR Congo', 'Congolese'],
            'Central African Republic': ['CAR', 'Central Africa', 'Central African'],
            'South Sudan': ['South Sudan', 'S. Sudan', 'South Sudanese'],
            'South Africa': ['South Africa', 'SA'],
            'Burkina Faso': ['Burkina Faso', 'Burkina', 'Burkinabe'],
            'Cote d\'Ivoire': ['Cote d\'Ivoire', 'Ivory Coast'],
            'Ethiopia': ['Ethiopia', 'Ethiopian'],
            'Nigeria': ['Nigeria', 'Nigerian'],
            'Somalia': ['Somalia', 'Somali'],
            'Sudan': ['Sudan', 'Sudanese'],
            'Kenya': ['Kenya', 'Kenyan'],
            'Mali': ['Mali', 'Malian'],
            'Cameroon': ['Cameroon', 'Cameroonian'],
            'Uganda': ['Uganda', 'Ugandan'],
            'Libya': ['Libya', 'Libyan'],
            'Niger': ['Niger', 'Nigerien'],
            'Chad': ['Chad', 'Chadian'],
            'Mozambique': ['Mozambique', 'Mozambican'],
            # Organizations
            'Al-Shabaab': ['Al-Shabaab', 'al Shabaab', 'Shabaab', 'al-Shabab'],
            'Boko Haram': ['Boko Haram', 'Boko', 'ISWAP'],
            'Islamic State': ['ISIS', 'ISIL', 'Islamic State', 'IS fighters', 'jihadists'],
            'Allied Democratic Forces': ['ADF', 'Allied Democratic'],
            # Event types - expanded
            'Armed clash': ['clash', 'clashed', 'clashes', 'fighting', 'battled', 'engagement', 'battle'],
            'Battles': ['battle', 'battles', 'clash', 'clashes', 'fighting', 'confrontation', 'combat'],
            'Violence against civilians': ['attacked', 'killed', 'assault', 'violence', 'murdered', 'targeted'],
            'Protests': ['protest', 'protesters', 'demonstration', 'rally', 'demonstrators'],
            'Riots': ['riot', 'riots', 'rioting', 'mob'],
            'Explosions/Remote violence': ['explosion', 'bomb', 'shelling', 'airstrike', 'IED', 'blast', 'strike'],
            'Strategic developments': ['ceasefire', 'agreement', 'negotiation', 'treaty', 'peace'],
            'Looting/property destruction': ['looted', 'destroyed', 'burned', 'arson', 'vandalized'],
            'Abduction/forced disappearance': ['kidnapped', 'abducted', 'seized', 'taken hostage'],
            # Casualties - expanded
            'Fatalities reported': ['killed', 'died', 'dead', 'fatalities', 'casualties', 'death', 'deaths'],
            # Victims - expanded
            'Civilians': ['civilians', 'villagers', 'residents', 'people', 'individuals', 'persons'],
        }

        normalized_lower = normalized_text.lower()
        for pattern, alternatives in abbrev_map.items():
            if pattern.lower() in normalized_lower:
                for alt in alternatives:
                    if alt.lower() in event_text_lower:
                        return alt

        # Strategy 6: Last word fallback for locations (e.g., "Borno State" -> "Borno")
        if len(words) >= 2:
            last_word = words[-1]
            if len(last_word) >= 3 and last_word.lower() in event_text_lower:
                return last_word

        return None

    def _remove_overlapping_entities(self, entities: List[Dict]) -> List[Dict]:
        """
        Resolve overlapping entities while preserving valid sub-entities.

        Priority (12-type schema):
        - WHO: PERPETRATOR(10) > GOVERNMENT(9) > ORGANIZATION(8)
        - WHOM: VICTIM(6)
        - WHAT: EVENT_TYPE(8) > ACTION(7)
        - WHEN: DATE(7)
        - WHERE: CITY(8) > DISTRICT(7) > REGION(6) > COUNTRY(5)
        - HOW: CASUALTIES(8)
        """
        if not entities:
            return entities

        # Priority mapping for 12-type schema
        type_priority = {
            # WHO (3 types)
            'PERPETRATOR': 10,
            'GOVERNMENT': 9,
            'ORGANIZATION': 8,
            # WHOM (1 type)
            'VICTIM': 6,
            # WHAT (2 types)
            'EVENT_TYPE': 8,
            'ACTION': 7,
            # WHEN (1 type)
            'DATE': 7,
            # WHERE (4 types) - specific > general
            'CITY': 8,
            'DISTRICT': 7,
            'REGION': 6,
            'COUNTRY': 5,
            # HOW (1 type)
            'CASUALTIES': 8,
        }

        def get_priority(entity_type: str) -> int:
            return type_priority.get(entity_type, 0)

        def entities_overlap(e1: Dict, e2: Dict) -> bool:
            """Check if two entities overlap."""
            return not (e1['end'] <= e2['start'] or e2['end'] <= e1['start'])

        def entity_contains(outer: Dict, inner: Dict) -> bool:
            """Check if outer fully contains inner."""
            return outer['start'] <= inner['start'] and outer['end'] >= inner['end']

        # Sort by start position, then by length (longer first), then by priority
        sorted_entities = sorted(
            entities,
            key=lambda e: (e['start'], -(e['end'] - e['start']), -get_priority(e['type']))
        )

        result = []
        used_spans: Set[Tuple[int, int]] = set()

        for entity in sorted_entities:
            span = (entity['start'], entity['end'])

            # Check for exact duplicate spans
            if span in used_spans:
                continue

            # Check for overlaps with already selected entities
            has_conflict = False
            for selected in result:
                if entities_overlap(entity, selected):
                    # Same type: keep the longer one (already selected if we're here)
                    if entity['type'] == selected['type']:
                        has_conflict = True
                        break

                    # Different types: check containment
                    if entity_contains(selected, entity):
                        # Selected contains this entity - skip (use larger span)
                        has_conflict = True
                        break
                    elif entity_contains(entity, selected):
                        # This entity contains selected - replace if higher priority
                        if get_priority(entity['type']) > get_priority(selected['type']):
                            result.remove(selected)
                            used_spans.discard((selected['start'], selected['end']))
                        else:
                            has_conflict = True
                            break
                    else:
                        # Partial overlap - use priority
                        if get_priority(entity['type']) <= get_priority(selected['type']):
                            has_conflict = True
                            break

            if not has_conflict:
                result.append(entity)
                used_spans.add(span)

        # Sort by start position for output
        result.sort(key=lambda x: x['start'])
        return result

    def _handle_nested_location_entities(self, entities: List[Dict]) -> List[Dict]:
        """
        Special handling for nested location entities.

        Examples:
        - "Luofu (Batangi, Lubero, Nord-Kivu)" - keep all levels
        - "Maiduguri, Borno State" - keep CITY and REGION

        This is called after initial overlap resolution to add back
        valid nested location hierarchies.
        """
        location_types = {'COUNTRY', 'REGION', 'CITY', 'DISTRICT'}

        # Find location entities
        location_entities = [e for e in entities if e['type'] in location_types]
        other_entities = [e for e in entities if e['type'] not in location_types]

        if len(location_entities) <= 1:
            return entities

        # For each pair of location entities, check if they form a valid hierarchy
        result_locations = []
        for loc in location_entities:
            is_valid = True
            for other_loc in location_entities:
                if loc == other_loc:
                    continue

                # If same span but different type, keep the more specific one
                if loc['start'] == other_loc['start'] and loc['end'] == other_loc['end']:
                    # Keep more specific (higher priority in location hierarchy)
                    loc_specificity = ['DISTRICT', 'CITY', 'REGION', 'COUNTRY']
                    if loc['type'] in loc_specificity and other_loc['type'] in loc_specificity:
                        if loc_specificity.index(loc['type']) > loc_specificity.index(other_loc['type']):
                            is_valid = False
                            break

            if is_valid:
                result_locations.append(loc)

        return other_entities + result_locations

    def _tokenize_with_punctuation(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Tokenize text while preserving African name patterns.

        Improvements over standard tokenization:
        1. Preserves hyphenated names (Al-Shabaab, N'Djamena)
        2. Preserves apostrophe names (M'Bour, Côte d'Ivoire)
        3. Handles diacritics properly (Médecins, São)
        4. Keeps multi-word named entities together when possible

        Returns list of (token, start_char, end_char) tuples.
        """
        tokens = []

        # First, normalize Unicode to handle diacritics consistently
        # NFC normalization keeps composed characters together
        normalized_text = unicodedata.normalize('NFC', text)

        # Enhanced pattern that preserves:
        # - Words with internal hyphens (Al-Shabaab)
        # - Words with internal apostrophes (N'Djamena, People's)
        # - Words with diacritics (Médecins, São, Côte)
        # - Numbers and dates
        # - Standalone punctuation
        pattern = r"""
            # Hyphenated words and names (Al-Shabaab, Côte-d'Ivoire)
            (?:[A-Za-zÀ-ÿ]+(?:[-'][A-Za-zÀ-ÿ]+)+)
            |
            # Words with apostrophes (N'Djamena, M'Bour, it's)
            (?:[A-Za-zÀ-ÿ]*'[A-Za-zÀ-ÿ]+)
            |
            # Regular words including diacritics
            (?:[A-Za-zÀ-ÿ]+)
            |
            # Numbers (including decimals, dates, coordinates)
            (?:\d+(?:[.,]\d+)*)
            |
            # Standalone punctuation
            (?:[.,;:!?()\[\]\"—–-])
        """

        compiled_pattern = re.compile(pattern, re.VERBOSE | re.UNICODE)

        for match in compiled_pattern.finditer(normalized_text):
            token = match.group()
            start = match.start()
            end = match.end()

            # Skip empty matches
            if not token.strip():
                continue

            tokens.append((token, start, end))

        return tokens

    def _normalize_text_for_matching(self, text: str) -> str:
        """
        Normalize text for entity matching.

        Handles variations in:
        - Unicode normalization (NFC/NFD)
        - Whitespace normalization
        - Case preservation (for matching)
        """
        # Normalize Unicode
        text = unicodedata.normalize('NFC', text)
        # Normalize whitespace (but preserve single spaces)
        text = re.sub(r'\s+', ' ', text)
        return text

    def create_bio_tags(self, text: str, entities: List[Dict]) -> List[Tuple[str, str]]:
        """
        Convert text and entities to BIO-tagged format.

        Returns: [('Armed', 'B-PERPETRATOR'), ('militants', 'I-PERPETRATOR'), ...]
        """
        token_data = self._tokenize_with_punctuation(text)
        tokens = [t[0] for t in token_data]
        token_labels = ['O'] * len(tokens)

        # Build character-to-token mapping
        char_to_token = {}
        for token_idx, (_, start_pos, end_pos) in enumerate(token_data):
            for char_pos in range(start_pos, end_pos):
                char_to_token[char_pos] = token_idx

        # Assign BIO labels
        for entity in entities:
            entity_start = entity['start']
            entity_end = entity['end']
            entity_type = entity['type']

            entity_tokens = set()
            for char_pos in range(entity_start, entity_end):
                if char_pos in char_to_token:
                    entity_tokens.add(char_to_token[char_pos])

            entity_tokens = sorted(entity_tokens)
            for idx, token_idx in enumerate(entity_tokens):
                if idx == 0:
                    token_labels[token_idx] = f'B-{entity_type}'
                else:
                    token_labels[token_idx] = f'I-{entity_type}'

        return list(zip(tokens, token_labels))

    def process_single_event(self, event: Dict) -> Optional[Dict]:
        """
        Process a single event from JSONL or CSV to NER format.

        Args:
            event: Dict with event data (from JSONL or CSV row)

        Returns:
            {
                'id': 'DRC34304',
                'text': 'On 20 December 2024, M23...',
                'tokens': ['On', '20', 'December', ...],
                'labels': ['O', 'B-DATE', 'I-DATE', ...],
                'entities': [{'text': 'M23', 'type': 'PERPETRATOR'}, ...]
            }
        """
        # Handle both JSONL and CSV formats
        if self.is_jsonl:
            event_id = event.get('event_id', '')
            text = event.get('text', '')
        else:
            event_id = event.get('Event_ID', '')
            text = event.get('Event_Description', '')

        if not text or (isinstance(text, float) and pd.isna(text)):
            return None

        text = str(text).strip()
        if not text:
            return None

        # Extract entities based on input format
        if self.is_jsonl:
            entities = self.extract_entities_from_jsonl_event(event)
        else:
            # Convert dict to Series for CSV processing
            row = pd.Series(event)
            entities = self.extract_entities_from_row(row)

        bio_tagged = self.create_bio_tags(text, entities)

        if not bio_tagged:
            return None

        tokens, labels = zip(*bio_tagged)

        return {
            'id': event_id,
            'text': text,
            'tokens': list(tokens),
            'labels': list(labels),
            'entities': entities,
        }

    def process_all(self, train_split: float = 0.8) -> Tuple[List[Dict], List[Dict]]:
        """
        Process all events and split into train/validation.

        Args:
            train_split: Fraction of data for training (default 0.8 = 80%)

        Returns:
            (train_data, val_data)
        """
        events = self.load_data()
        total_events = len(events)

        logger.info(f"Processing {total_events} events...")
        processed_events = []

        for idx, event in enumerate(events, start=1):
            event_data = self.process_single_event(event)
            if event_data:
                processed_events.append(event_data)

            if idx % 10000 == 0:
                logger.info(f"Processed {idx}/{total_events} events")

        logger.info(f"Successfully processed {len(processed_events)}/{total_events} events")

        # Shuffle and split
        import random
        random.seed(42)
        random.shuffle(processed_events)

        split_idx = int(len(processed_events) * train_split)
        train_data = processed_events[:split_idx]
        val_data = processed_events[split_idx:]

        logger.info(f"Train set: {len(train_data)} events ({train_split*100:.0f}%)")
        logger.info(f"Validation set: {len(val_data)} events ({(1-train_split)*100:.0f}%)")

        return train_data, val_data

    def save_processed_data(self, train_data: List[Dict], val_data: List[Dict]):
        """Save processed data to JSONL files."""
        train_file = self.output_dir / 'train.jsonl'
        val_file = self.output_dir / 'val.jsonl'

        logger.info(f"Saving train data to: {train_file}")
        with open(train_file, 'w', encoding='utf-8') as f:
            for event in train_data:
                f.write(json.dumps(event, ensure_ascii=False) + '\n')

        logger.info(f"Saving validation data to: {val_file}")
        with open(val_file, 'w', encoding='utf-8') as f:
            for event in val_data:
                f.write(json.dumps(event, ensure_ascii=False) + '\n')

        self.save_statistics(train_data, val_data)

    def save_statistics(self, train_data: List[Dict], val_data: List[Dict]):
        """Save dataset statistics."""
        stats = {
            'total_events': len(train_data) + len(val_data),
            'train_events': len(train_data),
            'val_events': len(val_data),
            'train_split': len(train_data) / (len(train_data) + len(val_data)) if train_data or val_data else 0,
        }

        entity_counts = defaultdict(int)
        label_counts = defaultdict(int)

        for event in train_data + val_data:
            for entity in event.get('entities', []):
                entity_counts[entity['type']] += 1
            for label in event.get('labels', []):
                label_counts[label] += 1

        stats['entity_type_counts'] = dict(entity_counts)
        stats['label_counts'] = dict(label_counts)
        stats['unique_entity_types'] = len(entity_counts)
        stats['unique_labels'] = len(label_counts)

        stats_file = self.output_dir / 'statistics.json'
        logger.info(f"Saving statistics to: {stats_file}")

        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)

        print("\n" + "=" * 60)
        print("PREPROCESSING COMPLETE")
        print("=" * 60)
        print(f"Total events: {stats['total_events']}")
        print(f"Training set: {stats['train_events']} ({stats['train_split']*100:.1f}%)")
        print(f"Validation set: {stats['val_events']} ({(1-stats['train_split'])*100:.1f}%)")
        print(f"\nEntity types: {stats['unique_entity_types']}")
        print(f"BIO labels: {stats['unique_labels']}")
        print("\nTop entity types:")
        for entity_type, count in sorted(entity_counts.items(), key=lambda x: -x[1])[:10]:
            print(f"  {entity_type}: {count}")

    def run_preprocessing(self, train_split: float = 0.8):
        """Run complete preprocessing pipeline."""
        train_data, val_data = self.process_all(train_split=train_split)
        self.save_processed_data(train_data, val_data)

        input_format = "JSONL" if self.is_jsonl else "CSV"
        print(f"\nPreprocessing complete!")
        print(f"Input format: {input_format}")
        print(f"Output directory: {self.output_dir}")
        print(f"Files created:")
        print(f"   - train.jsonl ({len(train_data)} events)")
        print(f"   - val.jsonl ({len(val_data)} events)")
        print(f"   - statistics.json")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Preprocess ACLED JSONL or CSV for NER training')
    parser.add_argument('--input', required=True, help='Path to input file (JSONL or CSV)')
    parser.add_argument('--output', default='data/processed', help='Output directory')
    parser.add_argument('--split', type=float, default=0.8, help='Train split ratio (default: 0.8)')

    args = parser.parse_args()

    preprocessor = AnnotationPreprocessor(args.input, args.output)
    preprocessor.run_preprocessing(train_split=args.split)
