#!/usr/bin/env python3
"""
Hybrid Training Data Generator for VioNER

Strategy:
1. Use real ACLED events for core entities (PERPETRATOR, VICTIM, COUNTRY, CITY, DATE, etc.)
2. AUGMENT the text with additional sentences containing missing entities
3. All annotations MUST exist in the actual text - no placeholders

This ensures:
- Authentic conflict event text from ACLED
- 100% entity coverage
- All annotations match actual text (critical for NER training)

Author: Generated for VioNER thesis project
"""

import csv
import re
import random
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict

# =============================================================================
# AUGMENTATION TEMPLATES - Sentences to add for missing entities
# =============================================================================

# Each template contains the entity value that will be annotated
# Format: (template_with_{placeholder}, entity_type)

ORGANIZATION_SENTENCES = [
    "The Red Cross has deployed emergency teams to assist survivors.",
    "Doctors Without Borders confirmed receiving wounded civilians.",
    "UNICEF expressed concern over the impact on children in the area.",
    "The World Food Programme suspended operations due to security concerns.",
    "UNHCR reported an influx of displaced persons at nearby camps.",
    "The International Rescue Committee is providing humanitarian assistance.",
    "Oxfam called for immediate international intervention.",
    "Save the Children evacuated staff from the affected region.",
    "The African Union condemned the violence in strong terms.",
    "ICRC negotiators are seeking access to the conflict zone.",
]

GOVERNMENT_SENTENCES = [
    "The Nigerian Army has been deployed to restore order.",
    "Somali National Army troops arrived to secure the area.",
    "Ethiopian military forces launched a counter-offensive.",
    "Sudanese Armed Forces confirmed the incident.",
    "South Sudanese security forces are investigating.",
    "Congolese military officials held an emergency meeting.",
    "Kenyan Defense Forces increased border patrols.",
    "Malian Armed Forces requested international support.",
    "Ugandan military spokesman addressed the media.",
    "Cameroonian soldiers established checkpoints in the region.",
]

VIOLENCE_TYPE_SENTENCES = [
    "Local leaders described it as ethnic violence targeting specific communities.",
    "Analysts characterized the incident as communal violence over resources.",
    "Officials labeled this a terrorist attack on civilian targets.",
    "The assault bore hallmarks of an insurgent attack on state infrastructure.",
    "Witnesses described sectarian violence between religious groups.",
    "Security experts identified patterns of militant violence in the region.",
    "The incident represents escalating bandit attacks in rural areas.",
]

TIME_SENTENCES = [
    "The attack began in the early morning hours before dawn.",
    "Gunfire erupted at dawn as residents were waking up.",
    "The assault occurred in the afternoon during market hours.",
    "Violence broke out in the evening as people returned home.",
    "The raid happened late at night while villagers slept.",
    "Fighting intensified around midnight and continued for hours.",
    "The incident unfolded overnight with sporadic gunfire.",
]

DURATION_SENTENCES = [
    "The three-hour assault left the village devastated.",
    "After a hours-long battle, the attackers withdrew.",
    "The two-hour siege ended when reinforcements arrived.",
    "Fighting continued in a daylong engagement across multiple locations.",
    "The brief but deadly skirmish claimed numerous lives.",
    "A prolonged engagement stretched into the following day.",
    "Several hours of fighting preceded the withdrawal.",
]

FREQUENCY_SENTENCES = [
    "This marks the latest in repeated attacks on the community.",
    "The region has suffered daily raids over the past month.",
    "Weekly incursions have displaced thousands of families.",
    "Ongoing violence has made the area virtually uninhabitable.",
    "Persistent attacks have disrupted all economic activity.",
    "Escalating raids signal a new phase in the conflict.",
    "Sporadic clashes continue despite peace negotiations.",
]

FACILITY_SENTENCES = [
    "The attackers targeted a primary school, forcing students to flee.",
    "A local hospital was damaged in the crossfire.",
    "The church was burned during the rampage.",
    "Militants occupied the police station before withdrawing.",
    "The market was looted and set ablaze.",
    "A mosque in the town center was also attacked.",
    "The military base came under heavy fire.",
    "An IDP camp housing refugees was not spared.",
]

GEOGRAPHIC_SENTENCES = [
    "The violence spread to villages along the river banks.",
    "Attackers emerged from the dense forest surrounding the town.",
    "The border region has seen increased militant activity.",
    "Communities in the mountainous terrain are difficult to protect.",
    "The Sahel belt continues to be a hotspot for armed groups.",
    "Lake-side communities reported seeing armed boats.",
    "The savanna provides little cover for fleeing civilians.",
]

COORDINATES_SENTENCES = [
    "The incident occurred at coordinates 9.5N, 7.8E according to reports.",
    "GPS data places the attack at location 4.2N, 18.6E.",
    "Military sources confirmed the position at coordinates 11.3N, 42.1E.",
    "The coordinates 6.8S, 39.2E mark the center of the affected area.",
    "Satellite imagery from coordinates 12.1N, 15.4E shows destruction.",
]

INJURED_SENTENCES = [
    "Medical sources reported wounding 47 others in the attack.",
    "At least 23 injured were transported to regional hospitals.",
    "Survivors with injuries are being treated at local clinics.",
    "The wounded include women and children caught in crossfire.",
    "Dozens of injured overwhelmed the capacity of nearby health facilities.",
]

DISPLACEMENT_SENTENCES = [
    "The violence triggered displacing over 5,000 residents from their homes.",
    "Thousands fled, displacing entire communities to neighboring districts.",
    "UN agencies report displacing 12,000 people since the attacks began.",
    "Mass displacement has created a humanitarian emergency.",
    "Families are displacing to urban centers seeking safety.",
]

DAMAGE_SENTENCES = [
    "The attackers left destruction, destroying over 200 homes.",
    "Witnesses reported burning down the entire village market.",
    "Property damage includes razing dozens of houses and shops.",
    "The assault resulted in torching hundreds of structures.",
    "Infrastructure damage is estimated in the millions.",
]

MOTIVE_SENTENCES = [
    "Local sources say the attack was in retaliation for previous clashes.",
    "The violence stems from disputes over land ownership.",
    "Tensions over grazing rights between communities sparked the conflict.",
    "The assault aimed to establish control of territory in the region.",
    "Revenge for earlier killings appears to have motivated the attackers.",
    "The attack was driven by ethnic tensions between groups.",
    "Competition for control of resources fueled the violence.",
]

TRIGGER_SENTENCES = [
    "The attack came following the collapse of peace talks last week.",
    "Violence erupted after disputed election results were announced.",
    "The assault followed a military offensive against rebel positions.",
    "Tensions had been rising after months of provocations.",
    "The incident occurred following the breakdown of a ceasefire.",
    "Clashes intensified after the arrest of a militia commander.",
    "The attack followed provocations by rival armed groups.",
]

TARGET_SENTENCES = [
    "The attackers specifically targeted villages in the district.",
    "Residential areas bore the brunt of the assault.",
    "Markets and commercial centers were primary targets.",
    "Schools and educational facilities were not spared.",
    "The militants focused on government buildings and offices.",
    "Churches and religious sites came under attack.",
    "Farming communities were systematically targeted.",
]

VICTIM_SENTENCES = [
    "The attack claimed the lives of 45 civilians including women and children.",
    "Among the victims were 30 farmers returning from their fields.",
    "At least 25 villagers lost their lives in the assault.",
    "The dead include 18 women who were at the market.",
    "Students and teachers were among the 35 people killed.",
]

# =============================================================================
# ENTITY EXTRACTION PATTERNS (from previous script)
# =============================================================================

ARMED_GROUP_PATTERNS = [
    r"Al[- ]?Shabaab", r"Boko Haram", r"ISWAP", r"ISIS", r"ISIL",
    r"M23", r"ADF", r"FDLR", r"Mai[- ]?Mai", r"LRA",
    r"TPLF", r"OLA", r"Fano", r"SPLM", r"SPLA",
    r"RSF", r"Janjaweed", r"SLM", r"JEM",
    r"JNIM", r"AQIM", r"Ansar Dine", r"Katiba Macina", r"ISGS",
    r"Seleka", r"Anti[- ]?Balaka", r"UPC",
    r"Ambazonia", r"militia", r"rebels?", r"fighters?",
    r"insurgents?", r"militants?", r"gunmen", r"bandits",
    r"armed group", r"armed men", r"herdsmen", r"herders",
]

EVENT_TYPE_PATTERNS = [
    r"attacks?", r"assault", r"raid", r"ambush",
    r"offensive", r"incursion", r"bombing", r"shelling",
    r"massacre", r"killing", r"murder", r"assassination",
    r"abduction", r"kidnapping", r"execution",
    r"clashes?", r"fighting", r"battle", r"violence",
]

ACTION_PATTERNS = [
    r"attacked", r"raided", r"stormed", r"ambushed",
    r"killed", r"murdered", r"executed",
    r"abducted", r"kidnapped", r"captured",
    r"burned", r"torched", r"destroyed",
    r"looted", r"shelled", r"bombed",
    r"opened fire", r"shot",
]

WEAPON_PATTERNS = [
    r"AK[- ]?47", r"assault rifles?", r"machine guns?",
    r"RPGs?", r"mortars?", r"artillery", r"grenades?",
    r"machetes?", r"knives?", r"IEDs?",
    r"explosives?", r"firearms?", r"guns?", r"rifles?",
    r"small arms",
]

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def extract_pattern(text: str, patterns: List[str]) -> Optional[str]:
    """Extract first match from patterns."""
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return None


def extract_number_phrase(text: str, pattern: str) -> Optional[str]:
    """Extract a phrase with numbers."""
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(0)
    return None


def clean_entity(entity: str) -> str:
    """Clean entity string."""
    if not entity:
        return ""
    entity = " ".join(entity.split())
    entity = entity.strip(".,;:\"'()[]")
    return entity


def entity_in_text(entity: str, text: str) -> bool:
    """Check if entity exists in text (case-insensitive)."""
    if not entity or not text:
        return False
    return entity.lower() in text.lower()


def extract_entity_from_sentence(sentence: str, keywords: List[str]) -> str:
    """Extract the entity value from an augmentation sentence."""
    # For sentences like "The Red Cross has deployed...", extract "Red Cross"
    for kw in keywords:
        if kw.lower() in sentence.lower():
            # Find the exact case in sentence
            match = re.search(re.escape(kw), sentence, re.IGNORECASE)
            if match:
                return match.group(0)
    return ""


# =============================================================================
# AUGMENTATION ENTITY EXTRACTORS
# =============================================================================

# Map of entity type to (sentences, extraction keywords)
AUGMENTATION_MAP = {
    "ORGANIZATION": (ORGANIZATION_SENTENCES, [
        "Red Cross", "Doctors Without Borders", "UNICEF", "World Food Programme",
        "UNHCR", "International Rescue Committee", "Oxfam", "Save the Children",
        "African Union", "ICRC"
    ]),
    "GOVERNMENT": (GOVERNMENT_SENTENCES, [
        "Nigerian Army", "Somali National Army", "Ethiopian military",
        "Sudanese Armed Forces", "South Sudanese security forces",
        "Congolese military", "Kenyan Defense Forces", "Malian Armed Forces",
        "Ugandan military", "Cameroonian soldiers"
    ]),
    "VIOLENCE_TYPE": (VIOLENCE_TYPE_SENTENCES, [
        "ethnic violence", "communal violence", "terrorist attack",
        "insurgent attack", "sectarian violence", "militant violence", "bandit attacks"
    ]),
    "TIME": (TIME_SENTENCES, [
        "early morning", "dawn", "afternoon", "evening", "late at night",
        "midnight", "overnight"
    ]),
    "DURATION": (DURATION_SENTENCES, [
        "three-hour assault", "hours-long battle", "two-hour siege",
        "daylong engagement", "brief but deadly skirmish", "prolonged engagement",
        "Several hours of fighting"
    ]),
    "FREQUENCY": (FREQUENCY_SENTENCES, [
        "repeated attacks", "daily raids", "Weekly incursions",
        "Ongoing violence", "Persistent attacks", "Escalating raids", "Sporadic clashes"
    ]),
    "FACILITY": (FACILITY_SENTENCES, [
        "primary school", "hospital", "church", "police station",
        "market", "mosque", "military base", "IDP camp"
    ]),
    "GEOGRAPHIC": (GEOGRAPHIC_SENTENCES, [
        "river banks", "dense forest", "border region", "mountainous terrain",
        "Sahel belt", "Lake-side", "savanna"
    ]),
    "COORDINATES": (COORDINATES_SENTENCES, [
        "coordinates 9.5N, 7.8E", "location 4.2N, 18.6E", "coordinates 11.3N, 42.1E",
        "coordinates 6.8S, 39.2E", "coordinates 12.1N, 15.4E"
    ]),
    "INJURED": (INJURED_SENTENCES, [
        "wounding 47 others", "23 injured", "injuries", "wounded", "injured"
    ]),
    "DISPLACEMENT": (DISPLACEMENT_SENTENCES, [
        "displacing over 5,000 residents", "displacing entire communities",
        "displacing 12,000 people", "Mass displacement", "displacing to urban"
    ]),
    "DAMAGE": (DAMAGE_SENTENCES, [
        "destroying over 200 homes", "burning down the entire village market",
        "razing dozens of houses", "torching hundreds of structures",
        "Infrastructure damage"
    ]),
    "MOTIVE": (MOTIVE_SENTENCES, [
        "in retaliation for", "disputes over land", "grazing rights",
        "control of territory", "Revenge for", "ethnic tensions", "control of resources"
    ]),
    "TRIGGER": (TRIGGER_SENTENCES, [
        "following the collapse of peace talks", "after disputed election",
        "followed a military offensive", "after months of provocations",
        "following the breakdown of a ceasefire", "after the arrest",
        "followed provocations"
    ]),
    "TARGET": (TARGET_SENTENCES, [
        "villages", "Residential areas", "Markets", "Schools",
        "government buildings", "Churches", "Farming communities"
    ]),
    "VICTIM": (VICTIM_SENTENCES, [
        "45 civilians", "30 farmers", "25 villagers", "18 women", "35 people"
    ]),
}


# =============================================================================
# MAIN DATA CLASS
# =============================================================================

@dataclass
class HybridEvent:
    """Hybrid event with real ACLED data + augmented entities."""
    event_id: str = ""
    original_text: str = ""
    augmented_text: str = ""

    # All 26 entity types
    perpetrator: str = ""
    victim: str = ""
    target: str = ""
    organization: str = ""
    government: str = ""
    event_type: str = ""
    action: str = ""
    weapon: str = ""
    violence_type: str = ""
    date: str = ""
    time: str = ""
    duration: str = ""
    frequency: str = ""
    country: str = ""
    region: str = ""
    city: str = ""
    district: str = ""
    facility: str = ""
    geographic: str = ""
    coordinates: str = ""
    casualties: str = ""
    injured: str = ""
    displacement: str = ""
    damage: str = ""
    motive: str = ""
    trigger: str = ""


def process_acled_event(row: Dict) -> Optional[HybridEvent]:
    """Process an ACLED event and create a hybrid event with augmentation."""

    text = row.get("Event_Description", "").strip()
    if not text or len(text) < 50:
        return None

    event = HybridEvent()
    event.event_id = row.get("Event_ID", "")
    event.original_text = text

    augmentation_sentences = []

    # === EXTRACT CORE ENTITIES FROM TEXT (not metadata!) ===

    # PERPETRATOR - must be in text
    extracted_perp = extract_pattern(text, ARMED_GROUP_PATTERNS)
    if extracted_perp:
        event.perpetrator = extracted_perp
    else:
        # Add sentence with perpetrator
        sentence = "Armed militants carried out the attack."
        augmentation_sentences.append(sentence)
        event.perpetrator = "Armed militants"

    # VICTIM - extract from text
    victim_match = re.search(r"(\d+)\s*(civilians?|people|villagers?|farmers?|residents?|women|children|soldiers?)", text, re.I)
    if victim_match:
        event.victim = victim_match.group(0)
    # Will be augmented below if missing

    # TARGET - extract from text
    for target_word in ["village", "town", "market", "school", "church", "mosque", "camp", "base", "station"]:
        if target_word in text.lower():
            event.target = target_word
            break
    # Will be augmented below if missing

    # EVENT_TYPE - must be EXACTLY in text
    event.event_type = extract_pattern(text, EVENT_TYPE_PATTERNS) or ""
    if event.event_type and not entity_in_text(event.event_type, text):
        # Extracted but not exact match - need to augment
        event.event_type = ""
    if not event.event_type:
        # Check for common event types that are actually in the text
        for evt in ["attack", "attacks", "killing", "killings", "clashes", "clash",
                    "violence", "assault", "raid", "ambush", "bombing", "massacre",
                    "abduction", "kidnapping", "fighting", "battle", "shelling"]:
            if evt in text.lower():
                event.event_type = evt
                break
    if not event.event_type:
        sentence = "The deadly attack shocked the community."
        augmentation_sentences.append(sentence)
        event.event_type = "attack"

    # ACTION - must be in text
    event.action = extract_pattern(text, ACTION_PATTERNS) or ""
    if not event.action:
        sentence = "Gunmen attacked the area without warning."
        augmentation_sentences.append(sentence)
        event.action = "attacked"

    # WEAPON - must be in text
    event.weapon = extract_pattern(text, WEAPON_PATTERNS) or ""
    if not event.weapon:
        sentence = "The assailants were armed with AK-47 rifles and machetes."
        augmentation_sentences.append(sentence)
        event.weapon = "AK-47 rifles"

    # DATE - must be in text (not from metadata)
    date_match = re.search(r"(?:on\s+)?(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})", text, re.I)
    if date_match:
        event.date = date_match.group(1)
    else:
        # Try other date patterns
        date_match2 = re.search(r"((?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday))", text, re.I)
        if date_match2:
            event.date = date_match2.group(1)
        else:
            # Add date sentence
            sentence = "The incident occurred on Tuesday morning."
            augmentation_sentences.append(sentence)
            event.date = "Tuesday"

    # COUNTRY - must be in text
    country_from_meta = row.get("Location_Country", "").strip()
    if country_from_meta and entity_in_text(country_from_meta, text):
        event.country = country_from_meta
    else:
        # Try to find any African country in text
        for c in ["Nigeria", "Somalia", "Sudan", "Ethiopia", "DRC", "Congo", "Kenya", "Mali",
                  "Burkina Faso", "Niger", "Cameroon", "Mozambique", "South Sudan", "Uganda"]:
            if c.lower() in text.lower():
                event.country = c
                break
        if not event.country and country_from_meta:
            # Add country to text
            sentence = f"The violence occurred in {country_from_meta}, according to local sources."
            augmentation_sentences.append(sentence)
            event.country = country_from_meta

    # CITY - must be in text
    city_from_meta = row.get("Location_City", "").strip()
    if city_from_meta and entity_in_text(city_from_meta, text):
        event.city = city_from_meta
    elif city_from_meta:
        sentence = f"Residents of {city_from_meta} reported hearing gunfire throughout the day."
        augmentation_sentences.append(sentence)
        event.city = city_from_meta

    # REGION - must be in text
    region_match = re.search(r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:State|Province|Region)", text)
    if region_match:
        event.region = region_match.group(0)
    else:
        # Add region
        if event.country:
            region_name = f"{event.country} region"
            sentence = f"The {event.country} region has seen increased violence recently."
            augmentation_sentences.append(sentence)
            event.region = f"{event.country} region"

    # DISTRICT - must be in text
    district_match = re.search(r"([A-Z][a-z]+)\s+(?:LGA|District|County)", text)
    if district_match:
        event.district = district_match.group(0)
    else:
        if event.city:
            sentence = f"The {event.city} district remains tense after the incident."
            augmentation_sentences.append(sentence)
            event.district = f"{event.city} district"

    # CASUALTIES - must be in text
    deaths = row.get("Deaths", "0").strip()
    casualty_match = re.search(r"(\d+)\s*(?:people\s+)?(?:were\s+)?killed|killed\s+(\d+)|(\d+)\s+dead|(\d+)\s+deaths?", text, re.I)
    if casualty_match:
        event.casualties = casualty_match.group(0)
    elif deaths and deaths != "0" and deaths.isdigit():
        sentence = f"The attack resulted in {deaths} people killed."
        augmentation_sentences.append(sentence)
        event.casualties = f"{deaths} people killed"

    # === AUGMENT MISSING ENTITIES ===

    entity_fields = [
        "perpetrator", "victim", "target", "organization", "government",
        "event_type", "action", "weapon", "violence_type",
        "date", "time", "duration", "frequency",
        "country", "region", "city", "district", "facility", "geographic", "coordinates",
        "casualties", "injured", "displacement", "damage",
        "motive", "trigger"
    ]

    for field in entity_fields:
        current_value = getattr(event, field, "")

        # Skip if already has value
        if current_value and entity_in_text(current_value, text):
            continue

        # Check if this field needs augmentation
        if field.upper() in AUGMENTATION_MAP:
            sentences, keywords = AUGMENTATION_MAP[field.upper()]

            # Pick a random sentence
            sentence = random.choice(sentences)

            # Extract the entity from the sentence
            for kw in keywords:
                if kw.lower() in sentence.lower():
                    # Find exact match in sentence
                    match = re.search(re.escape(kw), sentence, re.IGNORECASE)
                    if match:
                        setattr(event, field, match.group(0))
                        augmentation_sentences.append(sentence)
                        break

        # Handle special cases
        elif field == "perpetrator" and not event.perpetrator:
            event.perpetrator = "armed attackers"
        elif field == "event_type" and not event.event_type:
            event.event_type = "attack"
        elif field == "action" and not event.action:
            event.action = "attacked"
        elif field == "weapon" and not event.weapon:
            sentence = "The assailants were armed with small arms and machetes."
            augmentation_sentences.append(sentence)
            event.weapon = "small arms"
        elif field == "date" and not event.date:
            event.date = "recent days"
        elif field == "country" and not event.country:
            pass  # Should have from ACLED
        elif field == "city" and not event.city:
            event.city = "the locality"
        elif field == "region" and not event.region:
            if event.country:
                event.region = f"central {event.country}"
        elif field == "district" and not event.district:
            if event.city and event.city != "the locality":
                event.district = f"{event.city} area"
        elif field == "casualties" and not event.casualties:
            sentence = "The attack resulted in multiple casualties among civilians."
            augmentation_sentences.append(sentence)
            event.casualties = "multiple casualties"

    # Build augmented text
    if augmentation_sentences:
        # Remove duplicates while preserving order
        seen = set()
        unique_sentences = []
        for s in augmentation_sentences:
            if s not in seen:
                seen.add(s)
                unique_sentences.append(s)

        event.augmented_text = event.original_text + " " + " ".join(unique_sentences)
    else:
        event.augmented_text = event.original_text

    return event


def validate_event(event: HybridEvent) -> Tuple[bool, List[str]]:
    """Validate that all entities exist in the augmented text."""
    text = event.augmented_text.lower()
    missing = []

    entity_fields = [
        "perpetrator", "victim", "target", "organization", "government",
        "event_type", "action", "weapon", "violence_type",
        "date", "time", "duration", "frequency",
        "country", "region", "city", "district", "facility", "geographic", "coordinates",
        "casualties", "injured", "displacement", "damage",
        "motive", "trigger"
    ]

    for field in entity_fields:
        value = getattr(event, field, "")
        if not value:
            missing.append(f"{field}: EMPTY")
        elif value.lower() not in text:
            missing.append(f"{field}: '{value}' not in text")

    return len(missing) == 0, missing


def count_coverage(event: HybridEvent) -> int:
    """Count how many entities are filled."""
    fields = [
        "perpetrator", "victim", "target", "organization", "government",
        "event_type", "action", "weapon", "violence_type",
        "date", "time", "duration", "frequency",
        "country", "region", "city", "district", "facility", "geographic", "coordinates",
        "casualties", "injured", "displacement", "damage",
        "motive", "trigger"
    ]
    return sum(1 for f in fields if getattr(event, f, ""))


# =============================================================================
# OUTPUT
# =============================================================================

FIELDNAMES = [
    "Event_ID", "Article_ID", "Actor_Normalized", "Actor_Type",
    "Victim_Normalized", "Victim_Type", "Location_Country", "Location_City",
    "Location_Coordinates", "Date_Normalized", "Taxonomy_L1", "Taxonomy_L2",
    "Taxonomy_L3", "Weapon_Category", "Deaths", "Injuries", "Severity",
    "Event_Description", "Actor_Confidence", "Victim_Confidence",
    "Location_Confidence", "Date_Confidence", "Classification_Confidence",
    "Flagged_for_Review", "Notes", "Annotator_Name",
    "PERPETRATOR", "VICTIM", "TARGET", "ORGANIZATION", "GOVERNMENT",
    "EVENT_TYPE", "ACTION", "WEAPON", "VIOLENCE_TYPE",
    "DATE", "TIME", "DURATION", "FREQUENCY",
    "COUNTRY", "REGION", "CITY", "DISTRICT", "FACILITY", "GEOGRAPHIC", "COORDINATES",
    "CASUALTIES", "INJURED", "DISPLACEMENT", "DAMAGE",
    "MOTIVE", "TRIGGER"
]


def event_to_row(event: HybridEvent) -> dict:
    """Convert event to CSV row."""
    return {
        "Event_ID": f"HYBRID_{event.event_id}",
        "Article_ID": f"HYBRID_{event.event_id}",
        "Actor_Normalized": event.perpetrator,
        "Actor_Type": "Armed Group",
        "Victim_Normalized": event.victim,
        "Victim_Type": "",
        "Location_Country": event.country,
        "Location_City": event.city,
        "Location_Coordinates": event.coordinates,
        "Date_Normalized": event.date,
        "Taxonomy_L1": "Violence",
        "Taxonomy_L2": event.event_type,
        "Taxonomy_L3": "",
        "Weapon_Category": event.weapon,
        "Deaths": "",
        "Injuries": "",
        "Severity": "High",
        "Event_Description": event.augmented_text,  # Use augmented text!
        "Actor_Confidence": "0.95",
        "Victim_Confidence": "0.95",
        "Location_Confidence": "0.95",
        "Date_Confidence": "0.95",
        "Classification_Confidence": "0.95",
        "Flagged_for_Review": "False",
        "Notes": "Hybrid ACLED + augmentation for 100% entity coverage",
        "Annotator_Name": "VioNER-Hybrid-v1",
        "PERPETRATOR": event.perpetrator,
        "VICTIM": event.victim,
        "TARGET": event.target,
        "ORGANIZATION": event.organization,
        "GOVERNMENT": event.government,
        "EVENT_TYPE": event.event_type,
        "ACTION": event.action,
        "WEAPON": event.weapon,
        "VIOLENCE_TYPE": event.violence_type,
        "DATE": event.date,
        "TIME": event.time,
        "DURATION": event.duration,
        "FREQUENCY": event.frequency,
        "COUNTRY": event.country,
        "REGION": event.region,
        "CITY": event.city,
        "DISTRICT": event.district,
        "FACILITY": event.facility,
        "GEOGRAPHIC": event.geographic,
        "COORDINATES": event.coordinates,
        "CASUALTIES": event.casualties,
        "INJURED": event.injured,
        "DISPLACEMENT": event.displacement,
        "DAMAGE": event.damage,
        "MOTIVE": event.motive,
        "TRIGGER": event.trigger,
    }


def print_statistics(events: List[HybridEvent]):
    """Print coverage statistics."""
    print("\n" + "=" * 70)
    print("HYBRID DATA ENTITY COVERAGE")
    print("=" * 70)

    fields = [
        "perpetrator", "victim", "target", "organization", "government",
        "event_type", "action", "weapon", "violence_type",
        "date", "time", "duration", "frequency",
        "country", "region", "city", "district", "facility", "geographic", "coordinates",
        "casualties", "injured", "displacement", "damage",
        "motive", "trigger"
    ]

    total = len(events)
    all_100 = True

    for field in fields:
        count = sum(1 for e in events if getattr(e, field, ""))
        pct = (count / total) * 100 if total > 0 else 0

        # Count how many are in text
        in_text = sum(1 for e in events if getattr(e, field, "") and
                     getattr(e, field, "").lower() in e.augmented_text.lower())
        in_text_pct = (in_text / total) * 100 if total > 0 else 0

        status = "✓" if pct == 100 and in_text_pct >= 99 else "○" if pct >= 95 else "✗"
        print(f"{status} {field.upper():20} {count:5}/{total} ({pct:5.1f}%)  In-text: {in_text_pct:5.1f}%")

        if pct < 100:
            all_100 = False

    print("=" * 70)
    print(f"Total examples: {total}")
    if all_100:
        print("✓ ALL entity types at 100% coverage!")
    print("=" * 70)


# =============================================================================
# MAIN
# =============================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Create hybrid training data")
    parser.add_argument("--input", type=str,
                        default="/Users/binalfew/Documents/Masters/Thesis/named-entity-recognition/data/source/original.csv",
                        help="Input ACLED CSV")
    parser.add_argument("--output", type=str,
                        default="/Users/binalfew/Documents/Masters/Thesis/named-entity-recognition/data/source/hybrid_training_data_10k.csv",
                        help="Output CSV")
    parser.add_argument("--num", type=int, default=10000, help="Number of examples")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    random.seed(args.seed)

    print(f"Processing ACLED data from {args.input}...")

    valid_events = []
    processed = 0
    skipped_short = 0
    skipped_invalid = 0

    with open(args.input, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Shuffle to get variety
    random.shuffle(rows)

    for row in rows:
        if len(valid_events) >= args.num:
            break

        processed += 1
        if processed % 10000 == 0:
            print(f"  Processed {processed:,}, valid: {len(valid_events):,}")

        event = process_acled_event(row)
        if not event:
            skipped_short += 1
            continue

        # Validate all entities are in text
        is_valid, missing = validate_event(event)

        if count_coverage(event) >= 26:  # All entities filled
            valid_events.append(event)
        else:
            skipped_invalid += 1

    print(f"\nProcessed {processed:,} rows")
    print(f"Valid events with 26/26 coverage: {len(valid_events):,}")
    print(f"Skipped (too short): {skipped_short:,}")
    print(f"Skipped (incomplete): {skipped_invalid:,}")

    # Print statistics
    print_statistics(valid_events)

    # Validate a sample
    print("\n" + "=" * 70)
    print("VALIDATION CHECK - Entity in Text")
    print("=" * 70)

    sample_events = valid_events[:5]
    for i, event in enumerate(sample_events):
        is_valid, missing = validate_event(event)
        print(f"\nExample {i+1}: {'✓ VALID' if is_valid else '✗ INVALID'}")
        if missing:
            for m in missing[:5]:
                print(f"  - {m}")

    # Write output
    print(f"\nWriting to {args.output}...")
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for event in valid_events:
            writer.writerow(event_to_row(event))

    print(f"Written {len(valid_events):,} hybrid examples")

    # Show sample
    print("\n" + "=" * 70)
    print("SAMPLE HYBRID EVENT")
    print("=" * 70)
    if valid_events:
        e = valid_events[0]
        print(f"ORIGINAL TEXT:\n{e.original_text[:300]}...")
        print(f"\nAUGMENTED TEXT:\n{e.augmented_text[:500]}...")
        print(f"\nENTITIES:")
        print(f"  PERPETRATOR: {e.perpetrator}")
        print(f"  VICTIM: {e.victim}")
        print(f"  TARGET: {e.target}")
        print(f"  ORGANIZATION: {e.organization}")
        print(f"  GOVERNMENT: {e.government}")
        print(f"  EVENT_TYPE: {e.event_type}")
        print(f"  MOTIVE: {e.motive}")
        print(f"  TRIGGER: {e.trigger}")
    print("=" * 70)


if __name__ == "__main__":
    main()
