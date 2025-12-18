"""
Data Preprocessing - Week 9-10
Converts cleaned CSV annotations to BIO-tagged format for NER training

Author: Binalfew Kassa Mekonnen
Date: December 2025

Enhanced with:
- Expanded 26-entity schema support
- Improved tokenization for African names (hyphens, apostrophes, diacritics)
- Better overlap resolution preserving valid sub-entities
- Multi-event text handling via event_segmentation module
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
# ENTITY COLUMNS - Expanded 26-type schema
# ============================================================================

# Core entity columns (backward compatible with original 8-type schema)
CORE_ENTITY_COLUMNS = [
    'PERPETRATOR', 'VICTIM', 'EVENT_TYPE', 'WEAPON',
    'DATE', 'COUNTRY', 'CITY', 'CASUALTIES'
]

# Extended entity columns for full 26-type schema
EXTENDED_ENTITY_COLUMNS = [
    # WHO (5 types)
    'PERPETRATOR', 'VICTIM', 'TARGET', 'ORGANIZATION', 'GOVERNMENT',
    # WHAT (4 types)
    'EVENT_TYPE', 'ACTION', 'WEAPON', 'VIOLENCE_TYPE',
    # WHEN (4 types)
    'DATE', 'TIME', 'DURATION', 'FREQUENCY',
    # WHERE (7 types)
    'COUNTRY', 'REGION', 'CITY', 'DISTRICT', 'FACILITY', 'GEOGRAPHIC', 'COORDINATES',
    # HOW (4 types)
    'CASUALTIES', 'INJURED', 'DISPLACEMENT', 'DAMAGE',
    # WHY (2 types)
    'MOTIVE', 'TRIGGER',
]

# Default to extended columns, fallback to core if columns not present
ENTITY_COLUMNS = EXTENDED_ENTITY_COLUMNS


# ============================================================================
# AFRICAN NAME PATTERNS
# ============================================================================

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
    """Convert cleaned CSV annotations to BIO-tagged NER format."""

    def __init__(self, csv_file: str, output_dir: str = 'data/processed'):
        """
        Initialize preprocessor.

        Args:
            csv_file: Path to cleaned CSV file with verified entity spans
            output_dir: Directory to save processed data
        """
        self.csv_file = csv_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.label2id = LabelConfigs.get_label2id()
        self.id2label = LabelConfigs.get_id2label()

    def load_csv(self) -> pd.DataFrame:
        """Load CSV file with annotations."""
        logger.info(f"Loading CSV from: {self.csv_file}")
        df = pd.read_csv(self.csv_file)
        logger.info(f"Loaded {len(df)} events")
        return df

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

    def _remove_overlapping_entities(self, entities: List[Dict]) -> List[Dict]:
        """
        Resolve overlapping entities while preserving valid sub-entities.

        Improved algorithm:
        1. Keep longer entities when they fully contain shorter ones of same type
        2. For different types, use priority but allow non-overlapping sub-spans
        3. Handle nested entities (e.g., "Nigerian Army" contains "Nigeria")

        Priority (expanded for 26-type schema):
        - WHO: PERPETRATOR(10) > GOVERNMENT(9) > ORGANIZATION(8) > TARGET(7) > VICTIM(6)
        - WHAT: EVENT_TYPE(8) > ACTION(7) > WEAPON(6) > VIOLENCE_TYPE(5)
        - WHEN: DATE(7) > TIME(6) > DURATION(5) > FREQUENCY(4)
        - WHERE: FACILITY(9) > CITY(8) > DISTRICT(7) > REGION(6) > COUNTRY(5) > GEOGRAPHIC(4) > COORDINATES(3)
        - HOW: CASUALTIES(8) > INJURED(7) > DISPLACEMENT(6) > DAMAGE(5)
        - WHY: MOTIVE(6) > TRIGGER(5)
        """
        if not entities:
            return entities

        # Extended priority mapping for 26-type schema
        type_priority = {
            # WHO
            'PERPETRATOR': 10,
            'GOVERNMENT': 9,
            'ORGANIZATION': 8,
            'TARGET': 7,
            'VICTIM': 6,
            # WHAT
            'EVENT_TYPE': 8,
            'ACTION': 7,
            'WEAPON': 6,
            'VIOLENCE_TYPE': 5,
            # WHEN
            'DATE': 7,
            'TIME': 6,
            'DURATION': 5,
            'FREQUENCY': 4,
            # WHERE (facility > specific > general)
            'FACILITY': 9,
            'CITY': 8,
            'DISTRICT': 7,
            'REGION': 6,
            'COUNTRY': 5,
            'GEOGRAPHIC': 4,
            'COORDINATES': 3,
            # HOW
            'CASUALTIES': 8,
            'INJURED': 7,
            'DISPLACEMENT': 6,
            'DAMAGE': 5,
            # WHY
            'MOTIVE': 6,
            'TRIGGER': 5,
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
        - "Maiduguri, Borno State, Nigeria" - keep all three levels
        - "northern Nigeria" - keep both GEOGRAPHIC and COUNTRY

        This is called after initial overlap resolution to add back
        valid nested location hierarchies.
        """
        location_types = {'COUNTRY', 'REGION', 'CITY', 'DISTRICT', 'FACILITY', 'GEOGRAPHIC'}

        # Find location entities
        location_entities = [e for e in entities if e['type'] in location_types]
        other_entities = [e for e in entities if e['type'] not in location_types]

        if len(location_entities) <= 1:
            return entities

        # For each pair of location entities, check if they form a valid hierarchy
        # (This is a simplified version - full implementation would use gazetteers)
        result_locations = []
        for loc in location_entities:
            # Check if this location is contained within another but of different granularity
            is_valid = True
            for other_loc in location_entities:
                if loc == other_loc:
                    continue

                # If same span but different type, keep the more specific one
                if loc['start'] == other_loc['start'] and loc['end'] == other_loc['end']:
                    # Keep more specific (higher priority in location hierarchy)
                    loc_specificity = ['COORDINATES', 'FACILITY', 'DISTRICT', 'CITY', 'REGION', 'COUNTRY', 'GEOGRAPHIC']
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

    def process_single_event(self, row: pd.Series) -> Optional[Dict]:
        """
        Process a single event from CSV to NER format.

        Returns:
            {
                'id': 'EVENT_001',
                'text': 'Armed militants...',
                'tokens': ['Armed', 'militants', ...],
                'labels': ['B-PERPETRATOR', 'I-PERPETRATOR', ...],
                'entities': [{'text': 'Boko Haram', 'type': 'PERPETRATOR'}, ...]
            }
        """
        event_id = row.get('Event_ID', '')
        text = row.get('Event_Description', '')

        if pd.isna(text) or not text.strip():
            return None

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
        df = self.load_csv()

        logger.info("Processing events...")
        processed_events = []

        for row_num, (_, row) in enumerate(df.iterrows(), start=1):
            event_data = self.process_single_event(row)
            if event_data:
                processed_events.append(event_data)

            if row_num % 10000 == 0:
                logger.info(f"Processed {row_num}/{len(df)} events")

        logger.info(f"Successfully processed {len(processed_events)}/{len(df)} events")

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
        """Save processed data to JSON files."""
        train_file = self.output_dir / 'train.json'
        val_file = self.output_dir / 'val.json'

        logger.info(f"Saving train data to: {train_file}")
        with open(train_file, 'w', encoding='utf-8') as f:
            json.dump(train_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saving validation data to: {val_file}")
        with open(val_file, 'w', encoding='utf-8') as f:
            json.dump(val_data, f, indent=2, ensure_ascii=False)

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

        print(f"\nPreprocessing complete!")
        print(f"Output directory: {self.output_dir}")
        print(f"Files created:")
        print(f"   - train.json ({len(train_data)} events)")
        print(f"   - val.json ({len(val_data)} events)")
        print(f"   - statistics.json")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Preprocess cleaned CSV for NER training')
    parser.add_argument('--csv', required=True, help='Path to cleaned CSV file')
    parser.add_argument('--output', default='data/processed', help='Output directory')
    parser.add_argument('--split', type=float, default=0.8, help='Train split ratio (default: 0.8)')

    args = parser.parse_args()

    preprocessor = AnnotationPreprocessor(args.csv, args.output)
    preprocessor.run_preprocessing(train_split=args.split)
