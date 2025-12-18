#!/usr/bin/env python3
"""
Hybrid Training Data Generator for VioNER - V2

FIXES from V1:
1. DATE patterns - ordinal dates (March 3rd), date ranges, full month names
2. Multiple PERPETRATORS in same sentence (Boko Haram and ISWAP)
3. Compound VICTIM patterns (200 women and children)
4. Hyphenated city names (Maiduguri-Damaturu)
5. Better entity extraction ensuring full phrases are captured

Author: Generated for VioNER thesis project
"""

import csv
import re
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# =============================================================================
# IMPROVED DATA LISTS
# =============================================================================

# Multiple perpetrator combinations
PERPETRATOR_PAIRS = [
    ("Boko Haram", "ISWAP"),
    ("Al Shabaab", "ISIS"),
    ("M23", "ADF"),
    ("RSF", "Janjaweed"),
    ("TPLF", "OLA"),
    ("JNIM", "ISGS"),
    ("Seleka", "Anti-Balaka"),
    ("Al Shabaab", "Al Qaeda"),
    ("Boko Haram", "Ansaru"),
    ("Mai-Mai", "ADF"),
]

SINGLE_PERPETRATORS = [
    "Boko Haram insurgents", "ISWAP fighters", "Al Shabaab militants",
    "ISIS-affiliated militants", "M23 rebels", "ADF fighters",
    "RSF militia", "Janjaweed raiders", "TPLF forces", "OLA rebels",
    "JNIM militants", "ISGS fighters", "Seleka rebels", "Anti-Balaka militia",
    "Fulani herdsmen", "armed bandits", "unknown gunmen", "Ambazonia separatists",
    "LRA fighters", "Mai-Mai militia", "FDLR rebels", "Ansar Dine militants",
]

# Compound victim patterns
COMPOUND_VICTIMS = [
    "200 women and children",
    "150 farmers and herders",
    "85 civilians including women and children",
    "120 villagers and traders",
    "75 students and teachers",
    "45 soldiers and police officers",
    "90 refugees and aid workers",
    "60 men, women and children",
    "35 health workers and patients",
    "180 displaced persons and locals",
]

SINGLE_VICTIMS = [
    "47 soldiers", "34 militia members", "25 civilians", "12 farmers",
    "18 villagers", "52 refugees", "28 police officers", "15 children",
    "67 residents", "43 traders", "22 students", "38 women",
]

# Date patterns with ordinals
MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]

def ordinal(n):
    """Convert number to ordinal (1st, 2nd, 3rd, etc.)"""
    if 11 <= n <= 13:
        return f"{n}th"
    return f"{n}{['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]}"

def generate_date():
    """Generate a realistic date string."""
    month = random.choice(MONTHS)
    day = random.randint(1, 28)
    year = random.randint(2020, 2024)

    formats = [
        f"{month} {day}, {year}",           # January 15, 2024
        f"{month} {ordinal(day)}, {year}",  # January 15th, 2024
        f"{ordinal(day)} {month} {year}",   # 15th January 2024
        f"{day} {month} {year}",            # 15 January 2024
    ]
    return random.choice(formats)

def generate_date_range():
    """Generate a date range string."""
    month = random.choice(MONTHS)
    day1 = random.randint(1, 25)
    day2 = day1 + random.randint(1, 5)

    formats = [
        f"between {month} {ordinal(day1)} and {month} {ordinal(day2)}",
        f"from {month} {day1} to {month} {day2}",
        f"between {ordinal(day1)} and {ordinal(day2)} of {month}",
    ]
    return random.choice(formats)

# Hyphenated and compound city names
COMPOUND_CITIES = [
    "Maiduguri-Damaturu", "Kano-Kaduna", "Abuja-Lokoja", "Jos-Bauchi",
    "Goma-Bukavu", "Beni-Butembo", "Juba-Bor", "Malakal-Bentiu",
    "Khartoum-Omdurman", "El Fasher-Nyala", "Tripoli-Benghazi",
]

SINGLE_CITIES = [
    "Maiduguri", "Kano", "Kaduna", "Jos", "Yola", "Damaturu", "Chibok",
    "Mogadishu", "Kismayo", "Baidoa", "Beledweyne", "Afgooye",
    "Goma", "Bukavu", "Beni", "Butembo", "Bunia",
    "Juba", "Malakal", "Bentiu", "Bor", "Wau",
    "Khartoum", "Omdurman", "El Fasher", "Nyala", "Kassala",
    "Bamako", "Timbuktu", "Gao", "Mopti", "Kidal",
]

# Countries
COUNTRIES = [
    "Nigeria", "Somalia", "DRC", "South Sudan", "Sudan", "Ethiopia",
    "Mali", "Burkina Faso", "Niger", "Cameroon", "Kenya", "Uganda",
    "Mozambique", "CAR", "Libya", "Chad",
]

# Regions/States
REGIONS = [
    "Borno State", "Adamawa State", "Yobe State", "Kaduna State", "Plateau State",
    "North Kivu", "South Kivu", "Ituri Province",
    "Tigray Region", "Amhara Region", "Oromia Region",
    "North Darfur", "South Darfur", "West Darfur",
    "Cabo Delgado Province", "Gao Region", "Mopti Region",
]

# Weapons
WEAPONS = [
    "AK-47 rifles", "machine guns", "rocket-propelled grenades",
    "improvised explosive devices", "machetes and knives",
    "automatic weapons", "mortars and artillery", "hand grenades",
    "assault rifles", "heavy machine guns", "RPG launchers",
]

# Event types
EVENT_TYPES = [
    "raid", "raids", "attack", "attacks", "assault", "ambush",
    "massacre", "bombing", "shelling", "offensive", "incursion",
    "abduction", "kidnapping", "execution", "clashes",
]

# Actions
ACTIONS = [
    "attacked", "raided", "stormed", "ambushed", "besieged",
    "burned", "looted", "abducted", "executed", "killed",
    "bombarded", "shelled", "destroyed", "overran",
]

# Violence types
VIOLENCE_TYPES = [
    "ethnic violence", "communal violence", "terrorist attack",
    "insurgent attack", "sectarian violence", "militant violence",
    "bandit attacks", "armed violence", "retaliatory violence",
]

# Targets
TARGETS = [
    "three villages", "several communities", "multiple settlements",
    "farming villages", "residential areas", "market areas",
    "military positions", "police stations", "government buildings",
    "churches", "mosques", "schools", "IDP camps",
]

# Organizations
ORGANIZATIONS = [
    "Red Cross", "Doctors Without Borders", "UNICEF",
    "World Food Programme", "UNHCR", "Oxfam",
    "Save the Children", "African Union", "ICRC",
]

# Government forces
GOVERNMENT_FORCES = [
    "Nigerian Army", "Somali National Army", "Ethiopian military",
    "Sudanese Armed Forces", "Congolese military", "Kenyan Defense Forces",
    "Malian Armed Forces", "Ugandan military", "Cameroonian soldiers",
]

# Facilities
FACILITIES = [
    "primary school", "hospital", "church", "mosque",
    "police station", "military base", "market",
    "IDP camp", "health center", "government building",
]

# Geographic features
GEOGRAPHIC_FEATURES = [
    "river banks", "dense forest", "border region",
    "mountainous terrain", "Sahel belt", "savanna",
    "lake shores", "desert area", "highland region",
]

# Time expressions
TIME_EXPRESSIONS = [
    "early morning", "at dawn", "in the afternoon",
    "in the evening", "late at night", "around midnight",
    "overnight", "before sunrise", "after sunset",
]

# Duration expressions
DURATION_EXPRESSIONS = [
    "three-hour assault", "hours-long battle", "two-hour siege",
    "daylong engagement", "brief skirmish", "prolonged fighting",
]

# Frequency expressions
FREQUENCY_EXPRESSIONS = [
    "repeated attacks", "daily raids", "weekly incursions",
    "ongoing violence", "persistent attacks", "escalating raids",
]

# Motive expressions
MOTIVE_EXPRESSIONS = [
    "in retaliation for previous attacks",
    "over land disputes",
    "for control of territory",
    "due to ethnic tensions",
    "for revenge",
    "over grazing rights",
]

# Trigger expressions
TRIGGER_EXPRESSIONS = [
    "following the collapse of peace talks",
    "after disputed election results",
    "following a military offensive",
    "after months of tensions",
    "following the breakdown of a ceasefire",
]

# Damage expressions
DAMAGE_EXPRESSIONS = [
    "destroying over 200 homes",
    "burning the village market",
    "razing dozens of houses",
    "torching hundreds of structures",
]

# Displacement expressions
DISPLACEMENT_EXPRESSIONS = [
    "displacing over 15,000 residents",
    "forcing 10,000 people to flee",
    "displacing thousands of families",
    "causing mass displacement",
]

# Coordinates
COORDINATES = [
    "coordinates 9.5N, 7.8E",
    "coordinates 4.2N, 18.6E",
    "coordinates 11.3N, 42.1E",
    "GPS location 6.8S, 39.2E",
]

# =============================================================================
# TEMPLATE GENERATION
# =============================================================================

def generate_training_example():
    """Generate a single training example with all 26 entity types."""

    # Decide on single vs dual perpetrators
    use_dual_perps = random.random() < 0.4  # 40% chance of dual perpetrators

    if use_dual_perps:
        perp1, perp2 = random.choice(PERPETRATOR_PAIRS)
        perpetrator_text = f"{perp1} and {perp2}"
        perpetrators = [perp1, perp2]
    else:
        perpetrator_text = random.choice(SINGLE_PERPETRATORS)
        perpetrators = [perpetrator_text]

    # Decide on compound vs single victims
    use_compound_victim = random.random() < 0.4
    if use_compound_victim:
        victim = random.choice(COMPOUND_VICTIMS)
    else:
        victim = random.choice(SINGLE_VICTIMS)

    # Generate date (single or range)
    use_date_range = random.random() < 0.3
    if use_date_range:
        date = generate_date_range()
    else:
        date = generate_date()

    # Use compound or single city
    use_compound_city = random.random() < 0.2
    if use_compound_city:
        city = random.choice(COMPOUND_CITIES)
    else:
        city = random.choice(SINGLE_CITIES)

    # Select other entities
    country = random.choice(COUNTRIES)
    region = random.choice(REGIONS)
    district = f"{city} district"
    weapon = random.choice(WEAPONS)
    event_type = random.choice(EVENT_TYPES)
    action = random.choice(ACTIONS)
    violence_type = random.choice(VIOLENCE_TYPES)
    target = random.choice(TARGETS)
    organization = random.choice(ORGANIZATIONS)
    government = random.choice(GOVERNMENT_FORCES)
    facility = random.choice(FACILITIES)
    geographic = random.choice(GEOGRAPHIC_FEATURES)
    time_expr = random.choice(TIME_EXPRESSIONS)
    duration = random.choice(DURATION_EXPRESSIONS)
    frequency = random.choice(FREQUENCY_EXPRESSIONS)
    motive = random.choice(MOTIVE_EXPRESSIONS)
    trigger = random.choice(TRIGGER_EXPRESSIONS)
    damage = random.choice(DAMAGE_EXPRESSIONS)
    displacement = random.choice(DISPLACEMENT_EXPRESSIONS)
    coordinates = random.choice(COORDINATES)

    # Generate casualties and injured
    killed_count = random.randint(10, 150)
    injured_count = random.randint(20, 200)
    casualties = f"{killed_count} people killed"
    injured = f"{injured_count} wounded"

    # Build the text using various templates
    template_num = random.randint(1, 5)

    if template_num == 1:
        text = (
            f"On {date}, {perpetrator_text} conducted {event_type} on {target} "
            f"in {region}, {country}, near {city}, using {weapon}, "
            f"resulting in {casualties} and {injured}. "
            f"The {violence_type} {action} {victim}, {motive}. "
            f"{government} responded but found {damage}. "
            f"{organization} reported the {duration} caused {displacement} "
            f"from the {geographic} at {coordinates}. "
            f"The incident occurred {time_expr}, {trigger}. "
            f"This is part of {frequency} affecting the {facility} in {district}."
        )
    elif template_num == 2:
        text = (
            f"{trigger.capitalize()}, {perpetrator_text} launched a {event_type} "
            f"on {target} near {facility} in {city}, {region}, {country} on {date} {time_expr}. "
            f"Armed with {weapon}, fighters {action} {victim}, "
            f"leaving {casualties} and {injured}. "
            f"The {duration} of {violence_type} was {motive}. "
            f"{government} confirmed {damage} in the {geographic} at {coordinates}. "
            f"{organization} says {displacement} as {frequency} continue in {district}."
        )
    elif template_num == 3:
        text = (
            f"{organization} has reported a devastating {event_type} in {country} "
            f"where {perpetrator_text} {action} {target} in {city}, {district}, {region} "
            f"on {date}. The {time_expr} assault using {weapon} resulted in {casualties}, "
            f"{injured}, and {displacement}. "
            f"The {violence_type} targeted {victim} {motive}. "
            f"{government} found {damage} near {facility} in the {geographic} at {coordinates}. "
            f"This {duration} is part of {frequency} {trigger}."
        )
    elif template_num == 4:
        text = (
            f"Between {date}, {perpetrator_text} carried out {frequency} "
            f"in {region}, {country}, {action} {target} near {city} and {facility}. "
            f"The {violence_type} using {weapon} claimed {victim}, with {casualties} and {injured}. "
            f"{government} reported the {duration} caused {damage} and {displacement} "
            f"from the {geographic} in {district} at {coordinates}. "
            f"The attacks occurred {time_expr} {motive}. "
            f"{organization} condemned the incident {trigger}."
        )
    else:
        text = (
            f"Witnesses in {city}, {region}, {country} described how {perpetrator_text} "
            f"launched a {event_type} on {date} {time_expr}, {action} {target} near {facility}. "
            f"Armed with {weapon}, the attackers targeted {victim} {motive}, "
            f"resulting in {casualties} and {injured}. "
            f"The {duration} of {violence_type} led to {displacement} from {district}. "
            f"{government} found {damage} in the {geographic} at {coordinates}. "
            f"{organization} says this is part of {frequency} {trigger}."
        )

    # Build entity annotations
    entities = {
        "PERPETRATOR": perpetrator_text,
        "VICTIM": victim,
        "TARGET": target,
        "ORGANIZATION": organization,
        "GOVERNMENT": government,
        "EVENT_TYPE": event_type,
        "ACTION": action,
        "WEAPON": weapon,
        "VIOLENCE_TYPE": violence_type,
        "DATE": date,
        "TIME": time_expr,
        "DURATION": duration,
        "FREQUENCY": frequency,
        "COUNTRY": country,
        "REGION": region,
        "CITY": city,
        "DISTRICT": district,
        "FACILITY": facility,
        "GEOGRAPHIC": geographic,
        "COORDINATES": coordinates,
        "CASUALTIES": casualties,
        "INJURED": injured,
        "DISPLACEMENT": displacement,
        "DAMAGE": damage,
        "MOTIVE": motive,
        "TRIGGER": trigger,
    }

    return text, entities


def validate_entities_in_text(text: str, entities: Dict[str, str]) -> Tuple[bool, List[str]]:
    """Validate that all entities exist in the text."""
    missing = []
    text_lower = text.lower()

    for entity_type, value in entities.items():
        if value and value.lower() not in text_lower:
            missing.append(f"{entity_type}: '{value}'")

    return len(missing) == 0, missing


def generate_dataset(num_examples: int = 10000, max_attempts: int = 50000):
    """Generate a dataset with validated examples."""
    examples = []
    attempts = 0

    while len(examples) < num_examples and attempts < max_attempts:
        attempts += 1
        text, entities = generate_training_example()

        is_valid, missing = validate_entities_in_text(text, entities)

        if is_valid:
            examples.append((text, entities))

        if attempts % 1000 == 0:
            print(f"  Generated {len(examples)}/{num_examples} valid examples (attempts: {attempts})")

    return examples


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


def write_dataset(examples, output_path: str):
    """Write dataset to CSV."""
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()

        for i, (text, entities) in enumerate(examples):
            row = {
                "Event_ID": f"SYNTH_V2_{i:05d}",
                "Article_ID": f"SYNTH_V2_{i:05d}",
                "Actor_Normalized": entities.get("PERPETRATOR", ""),
                "Actor_Type": "Armed Group",
                "Victim_Normalized": entities.get("VICTIM", ""),
                "Victim_Type": "",
                "Location_Country": entities.get("COUNTRY", ""),
                "Location_City": entities.get("CITY", ""),
                "Location_Coordinates": entities.get("COORDINATES", ""),
                "Date_Normalized": entities.get("DATE", ""),
                "Taxonomy_L1": "Violence",
                "Taxonomy_L2": entities.get("EVENT_TYPE", ""),
                "Taxonomy_L3": "",
                "Weapon_Category": entities.get("WEAPON", ""),
                "Deaths": "",
                "Injuries": "",
                "Severity": "High",
                "Event_Description": text,
                "Actor_Confidence": "0.99",
                "Victim_Confidence": "0.99",
                "Location_Confidence": "0.99",
                "Date_Confidence": "0.99",
                "Classification_Confidence": "0.99",
                "Flagged_for_Review": "False",
                "Notes": "Synthetic training data V2 - improved patterns",
                "Annotator_Name": "VioNER-Generator-V2",
                **entities
            }
            writer.writerow(row)

    print(f"Written {len(examples)} examples to {output_path}")


def print_statistics(examples):
    """Print coverage statistics."""
    print("\n" + "=" * 70)
    print("ENTITY COVERAGE STATISTICS")
    print("=" * 70)

    entity_types = [
        "PERPETRATOR", "VICTIM", "TARGET", "ORGANIZATION", "GOVERNMENT",
        "EVENT_TYPE", "ACTION", "WEAPON", "VIOLENCE_TYPE",
        "DATE", "TIME", "DURATION", "FREQUENCY",
        "COUNTRY", "REGION", "CITY", "DISTRICT", "FACILITY", "GEOGRAPHIC", "COORDINATES",
        "CASUALTIES", "INJURED", "DISPLACEMENT", "DAMAGE",
        "MOTIVE", "TRIGGER"
    ]

    total = len(examples)

    for entity_type in entity_types:
        # Count filled
        count = sum(1 for _, entities in examples if entities.get(entity_type))
        pct = (count / total) * 100

        # Count in-text matches
        in_text = sum(1 for text, entities in examples
                     if entities.get(entity_type) and
                     entities[entity_type].lower() in text.lower())
        in_text_pct = (in_text / total) * 100

        status = "✓" if pct == 100 and in_text_pct == 100 else "✗"
        print(f"{status} {entity_type:20} Filled: {pct:5.1f}%  In-text: {in_text_pct:5.1f}%")

    print("=" * 70)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate improved synthetic training data V2")
    parser.add_argument("--num", type=int, default=10000, help="Number of examples")
    parser.add_argument("--output", type=str,
                        default="/Users/binalfew/Documents/Masters/Thesis/named-entity-recognition/data/source/synthetic_training_data_v2.csv",
                        help="Output CSV path")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    random.seed(args.seed)

    print(f"Generating {args.num} synthetic training examples (V2 - improved patterns)...")
    examples = generate_dataset(args.num)

    print_statistics(examples)

    write_dataset(examples, args.output)

    # Show samples
    print("\n" + "=" * 70)
    print("SAMPLE EXAMPLES")
    print("=" * 70)

    for i, (text, entities) in enumerate(examples[:3]):
        print(f"\n--- Example {i+1} ---")
        print(f"TEXT: {text[:400]}...")
        print(f"\nKEY ENTITIES:")
        print(f"  PERPETRATOR: {entities['PERPETRATOR']}")
        print(f"  VICTIM: {entities['VICTIM']}")
        print(f"  DATE: {entities['DATE']}")
        print(f"  CITY: {entities['CITY']}")
        print(f"  COUNTRY: {entities['COUNTRY']}")
        print(f"  WEAPON: {entities['WEAPON']}")

    print("=" * 70)


if __name__ == "__main__":
    main()
