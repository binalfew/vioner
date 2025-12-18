"""
Event Segmentation - Phase 2
Handles multi-event text by detecting event boundaries and splitting compound texts.

Author: Binalfew Kassa Mekonnen
Date: December 2025

The ACLED dataset often contains multiple events in a single text entry:
"On 15 January, Boko Haram attacked Maiduguri killing 30. The next day,
Al-Shabaab militants raided a village in Mogadishu."

This module detects event boundaries and segments text for proper extraction.
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class EventSegment:
    """A single event segment extracted from compound text."""
    text: str
    start_offset: int
    end_offset: int
    segment_index: int
    confidence: float
    boundary_type: str  # 'temporal', 'actor', 'location', 'conjunction', 'sentence'


# ============================================================================
# EVENT BOUNDARY PATTERNS
# ============================================================================

# Temporal markers that often indicate new events
TEMPORAL_BOUNDARY_PATTERNS = [
    # Explicit time transitions
    r'\b(the next day|the following day|later that day|hours later|days later)\b',
    r'\b(the previous day|earlier that day|the day before)\b',
    r'\b(meanwhile|at the same time|simultaneously|concurrently)\b',
    r'\b(subsequently|afterwards|thereafter|later)\b',

    # Date patterns that restart narratives
    r'\b(on|by)\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}',
    r'\b(on|by)\s+\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)',
    r'\b(on|by)\s+\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',

    # Relative time
    r'\b(the same day|that morning|that evening|that night|overnight)\b',
    r'\b(a day earlier|a week later|months before|years ago)\b',
]

# Actor transition patterns
ACTOR_BOUNDARY_PATTERNS = [
    # New actor introduction
    r'\b(in a separate incident|in another attack|separately|elsewhere)\b',
    r'\b(in retaliation|in response to|following the attack)\b',
    r'\b(unidentified gunmen|unknown assailants|other militants)\b',

    # Contrast markers
    r'\b(however|but|yet|on the other hand|in contrast)\b',
    r'\b(while|whereas|although)\b',
]

# Location transition patterns
LOCATION_BOUNDARY_PATTERNS = [
    r'\b(in|at|near)\s+(nearby|neighboring|adjacent)\s+\w+',
    r'\b(in another part of|elsewhere in|across)\s+\w+',
    r'\b(to the north|to the south|to the east|to the west)\s+of',
]

# Strong sentence boundary patterns
SENTENCE_BOUNDARY_PATTERNS = [
    r'\.\s+[A-Z]',           # Period followed by capital letter
    r'[.!?]\s*\n',           # End punctuation followed by newline
    r'\.\s*-\s*',            # Period followed by dash (list style)
]

# Conjunction patterns that may indicate multiple events
CONJUNCTION_PATTERNS = [
    r'\b(and also|and then|and subsequently)\b',
    r'\b(as well as|in addition to)\b',
    r';\s+',                  # Semicolon as event separator
]


class EventSegmenter:
    """
    Segments compound text into individual event descriptions.

    Handles texts containing multiple violent events by detecting
    temporal, actor, and location boundaries.
    """

    def __init__(
        self,
        min_segment_length: int = 30,
        max_segment_length: int = 1000,
        confidence_threshold: float = 0.5
    ):
        """
        Initialize the event segmenter.

        Args:
            min_segment_length: Minimum characters for valid segment
            max_segment_length: Maximum characters before forcing split
            confidence_threshold: Minimum confidence to accept a boundary
        """
        self.min_segment_length = min_segment_length
        self.max_segment_length = max_segment_length
        self.confidence_threshold = confidence_threshold

        # Compile patterns
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for efficiency."""
        self.temporal_patterns = [
            re.compile(p, re.IGNORECASE) for p in TEMPORAL_BOUNDARY_PATTERNS
        ]
        self.actor_patterns = [
            re.compile(p, re.IGNORECASE) for p in ACTOR_BOUNDARY_PATTERNS
        ]
        self.location_patterns = [
            re.compile(p, re.IGNORECASE) for p in LOCATION_BOUNDARY_PATTERNS
        ]
        self.sentence_patterns = [
            re.compile(p) for p in SENTENCE_BOUNDARY_PATTERNS
        ]
        self.conjunction_patterns = [
            re.compile(p, re.IGNORECASE) for p in CONJUNCTION_PATTERNS
        ]

    def detect_boundaries(self, text: str) -> List[Dict]:
        """
        Detect potential event boundaries in text.

        Args:
            text: Input text to analyze

        Returns:
            List of boundary candidates with position and confidence
        """
        boundaries = []

        # Check temporal boundaries (highest confidence)
        for pattern in self.temporal_patterns:
            for match in pattern.finditer(text):
                boundaries.append({
                    'position': match.start(),
                    'match': match.group(),
                    'type': 'temporal',
                    'confidence': 0.9,
                })

        # Check actor boundaries
        for pattern in self.actor_patterns:
            for match in pattern.finditer(text):
                boundaries.append({
                    'position': match.start(),
                    'match': match.group(),
                    'type': 'actor',
                    'confidence': 0.8,
                })

        # Check location boundaries
        for pattern in self.location_patterns:
            for match in pattern.finditer(text):
                boundaries.append({
                    'position': match.start(),
                    'match': match.group(),
                    'type': 'location',
                    'confidence': 0.7,
                })

        # Check sentence boundaries
        for pattern in self.sentence_patterns:
            for match in pattern.finditer(text):
                boundaries.append({
                    'position': match.end() - 1,  # Position after punctuation
                    'match': match.group(),
                    'type': 'sentence',
                    'confidence': 0.5,
                })

        # Check conjunction boundaries (lower confidence)
        for pattern in self.conjunction_patterns:
            for match in pattern.finditer(text):
                boundaries.append({
                    'position': match.start(),
                    'match': match.group(),
                    'type': 'conjunction',
                    'confidence': 0.4,
                })

        # Sort by position
        boundaries.sort(key=lambda x: x['position'])

        return boundaries

    def _filter_boundaries(
        self,
        boundaries: List[Dict],
        text_length: int
    ) -> List[Dict]:
        """
        Filter boundaries based on minimum segment length and confidence.

        Args:
            boundaries: List of boundary candidates
            text_length: Total length of text

        Returns:
            Filtered list of valid boundaries
        """
        if not boundaries:
            return []

        filtered = []
        last_position = 0

        for boundary in boundaries:
            # Check minimum segment length
            if boundary['position'] - last_position < self.min_segment_length:
                continue

            # Check remaining text length
            if text_length - boundary['position'] < self.min_segment_length:
                continue

            # Check confidence threshold
            if boundary['confidence'] < self.confidence_threshold:
                continue

            filtered.append(boundary)
            last_position = boundary['position']

        return filtered

    def segment_text(self, text: str) -> List[EventSegment]:
        """
        Segment text into individual event descriptions.

        Args:
            text: Input text potentially containing multiple events

        Returns:
            List of EventSegment objects
        """
        if not text or len(text) < self.min_segment_length:
            return [EventSegment(
                text=text,
                start_offset=0,
                end_offset=len(text) if text else 0,
                segment_index=0,
                confidence=1.0,
                boundary_type='single'
            )]

        # Detect boundaries
        boundaries = self.detect_boundaries(text)

        # Filter boundaries
        valid_boundaries = self._filter_boundaries(boundaries, len(text))

        # If no valid boundaries, return entire text as single segment
        if not valid_boundaries:
            return [EventSegment(
                text=text,
                start_offset=0,
                end_offset=len(text),
                segment_index=0,
                confidence=1.0,
                boundary_type='single'
            )]

        # Create segments
        segments = []
        start = 0

        for idx, boundary in enumerate(valid_boundaries):
            segment_text = text[start:boundary['position']].strip()

            if len(segment_text) >= self.min_segment_length:
                segments.append(EventSegment(
                    text=segment_text,
                    start_offset=start,
                    end_offset=boundary['position'],
                    segment_index=len(segments),
                    confidence=boundary['confidence'],
                    boundary_type=boundary['type']
                ))

            start = boundary['position']

        # Add final segment
        final_text = text[start:].strip()
        if len(final_text) >= self.min_segment_length:
            segments.append(EventSegment(
                text=final_text,
                start_offset=start,
                end_offset=len(text),
                segment_index=len(segments),
                confidence=1.0,
                boundary_type='final'
            ))

        # If segmentation produced nothing usable, return original
        if not segments:
            return [EventSegment(
                text=text,
                start_offset=0,
                end_offset=len(text),
                segment_index=0,
                confidence=1.0,
                boundary_type='single'
            )]

        return segments

    def is_multi_event_text(self, text: str) -> Tuple[bool, float]:
        """
        Check if text likely contains multiple events.

        Args:
            text: Text to check

        Returns:
            Tuple of (is_multi_event, confidence)
        """
        boundaries = self.detect_boundaries(text)

        if not boundaries:
            return False, 1.0

        # Filter to high-confidence boundaries only
        high_conf_boundaries = [
            b for b in boundaries
            if b['confidence'] >= 0.7
        ]

        if not high_conf_boundaries:
            return False, 0.8

        # Check if boundaries would create valid segments
        valid_boundaries = self._filter_boundaries(
            high_conf_boundaries, len(text)
        )

        if len(valid_boundaries) >= 1:
            max_confidence = max(b['confidence'] for b in valid_boundaries)
            return True, max_confidence

        return False, 0.5

    def get_primary_event(self, text: str) -> EventSegment:
        """
        Extract the primary (first) event from compound text.

        Args:
            text: Input text

        Returns:
            EventSegment for the primary event
        """
        segments = self.segment_text(text)
        return segments[0] if segments else EventSegment(
            text=text,
            start_offset=0,
            end_offset=len(text),
            segment_index=0,
            confidence=1.0,
            boundary_type='single'
        )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def count_events_in_text(text: str) -> int:
    """
    Estimate the number of distinct events in text.

    Args:
        text: Input text

    Returns:
        Estimated number of events
    """
    segmenter = EventSegmenter()
    segments = segmenter.segment_text(text)
    return len(segments)


def split_compound_events(
    text: str,
    min_segment_length: int = 30
) -> List[str]:
    """
    Split compound event text into individual event descriptions.

    Args:
        text: Input text potentially containing multiple events
        min_segment_length: Minimum length for valid segment

    Returns:
        List of individual event texts
    """
    segmenter = EventSegmenter(min_segment_length=min_segment_length)
    segments = segmenter.segment_text(text)
    return [seg.text for seg in segments]


def adjust_entity_offsets(
    entities: List[Dict],
    segment: EventSegment
) -> List[Dict]:
    """
    Adjust entity character offsets relative to segment.

    When extracting entities from a segment, offsets need to be
    adjusted relative to the segment's position in the original text.

    Args:
        entities: List of entities with start/end offsets
        segment: The segment they were extracted from

    Returns:
        Entities with adjusted offsets for original text
    """
    adjusted = []
    for entity in entities:
        adjusted.append({
            **entity,
            'start': entity['start'] + segment.start_offset,
            'end': entity['end'] + segment.start_offset,
            'segment_index': segment.segment_index,
        })
    return adjusted


# ============================================================================
# DEMO / TESTING
# ============================================================================

if __name__ == '__main__':
    # Test with example compound text
    test_texts = [
        # Single event
        "Boko Haram militants attacked a village in Maiduguri on Tuesday, killing 15 civilians.",

        # Multiple events with temporal boundary
        "On 15 January, Boko Haram attacked Maiduguri killing 30. The next day, "
        "Al-Shabaab militants raided a village near Mogadishu injuring 12.",

        # Multiple events with actor boundary
        "RSF forces shelled residential areas in Khartoum. In a separate incident, "
        "unidentified gunmen ambushed a convoy in Darfur.",

        # Complex multi-event
        "Government forces launched airstrikes on rebel positions in Tigray region "
        "on Monday. Meanwhile, ethnic clashes in Oromia left 20 dead. The following "
        "day, protests erupted in Addis Ababa against the ongoing violence.",
    ]

    segmenter = EventSegmenter()

    for i, text in enumerate(test_texts, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}")
        print(f"{'='*60}")
        print(f"Input ({len(text)} chars):\n{text[:200]}...")

        is_multi, conf = segmenter.is_multi_event_text(text)
        print(f"\nMulti-event: {is_multi} (confidence: {conf:.2f})")

        segments = segmenter.segment_text(text)
        print(f"\nSegments found: {len(segments)}")

        for seg in segments:
            print(f"\n  [{seg.segment_index}] {seg.boundary_type} (conf: {seg.confidence:.2f})")
            print(f"      Offset: {seg.start_offset}-{seg.end_offset}")
            print(f"      Text: {seg.text[:100]}...")
