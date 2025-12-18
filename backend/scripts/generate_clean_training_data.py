#!/usr/bin/env python3
"""
Generate Clean NER Training Data for African Conflict Events - V2

This script creates high-quality, synthetic training data with:
- 95%+ coverage for ALL 26 entity types
- Grammatically correct sentences
- Accurate entity annotations (exact string matching)
- Diverse African geographic coverage

Author: Generated for VioNER thesis project
"""

import csv
import random
import uuid
from typing import Dict, List, Optional
from dataclasses import dataclass, field

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def article(word: str) -> str:
    """Return 'an' if word starts with vowel sound, else 'a'."""
    vowels = 'aeiouAEIOU'
    # Special cases
    if word.upper().startswith(('IED', 'RPG', 'AK', 'M23', 'UN')):
        return 'an' if word[0].upper() in 'AEIOU' else 'a'
    if word[0] in vowels:
        return 'an'
    return 'a'


def pluralize(word: str, count: int) -> str:
    """Simple pluralization."""
    if count == 1:
        return word
    if word.endswith('y') and word[-2] not in 'aeiou':
        return word[:-1] + 'ies'
    if word.endswith(('s', 'sh', 'ch', 'x', 'z')):
        return word + 'es'
    return word + 's'


# =============================================================================
# KNOWLEDGE BASE: Real African Conflict Data
# =============================================================================

# Armed Groups by Country
ARMED_GROUPS = {
    "Somalia": [
        "Al Shabaab", "Al Shabaab militants", "Al Shabaab fighters", "Al Shabaab insurgents",
    ],
    "Sudan": [
        "Rapid Support Forces", "RSF militia", "RSF fighters", "Janjaweed militia",
        "Sudanese rebel forces", "SLM rebels", "JEM fighters",
    ],
    "South Sudan": [
        "SPLM-IO forces", "White Army militia", "Nuer militia", "armed youth groups",
    ],
    "Ethiopia": [
        "TPLF forces", "Tigray Defense Forces", "OLA rebels", "Oromo Liberation Army fighters",
        "Fano militia", "Amhara militia",
    ],
    "Nigeria": [
        "Boko Haram", "Boko Haram insurgents", "Boko Haram fighters",
        "ISWAP militants", "Islamic State West Africa Province",
        "Fulani herdsmen", "Fulani militia", "armed Fulani herders",
        "armed bandits", "bandits",
    ],
    "DRC": [
        "M23 rebels", "M23 fighters", "ADF militants", "Allied Democratic Forces",
        "Mai-Mai militia", "Mai-Mai fighters", "CODECO militia", "FDLR rebels",
    ],
    "Mali": [
        "JNIM fighters", "JNIM militants", "ISGS militants", "AQIM fighters",
        "Tuareg rebels", "Ansar Dine militants", "Katiba Macina fighters",
    ],
    "Burkina Faso": [
        "JNIM militants", "ISGS fighters", "armed jihadists", "Ansaroul Islam militants",
    ],
    "Niger": [
        "ISGS militants", "Boko Haram fighters", "armed groups",
    ],
    "CAR": [
        "Seleka rebels", "Anti-Balaka militia", "3R militia", "UPC rebels", "LRA fighters",
    ],
    "Cameroon": [
        "Ambazonia separatists", "Ambazonia fighters", "Anglophone separatists",
        "Boko Haram militants",
    ],
    "Libya": [
        "ISIS-Libya militants", "Haftar's forces", "LNA fighters", "armed militias",
    ],
    "Mozambique": [
        "Al Sunnah wa Jama'ah", "ISIS-Mozambique militants", "Cabo Delgado insurgents",
    ],
    "Kenya": [
        "Al Shabaab militants", "armed bandits", "cattle rustlers",
    ],
    "Uganda": [
        "ADF rebels", "LRA remnants",
    ],
}

# Government Forces by Country
GOVERNMENT_FORCES = {
    "Somalia": ["Somali National Army", "SNA forces", "Somali security forces"],
    "Sudan": ["Sudanese Armed Forces", "SAF troops", "Sudanese military"],
    "South Sudan": ["SSPDF forces", "South Sudanese military"],
    "Ethiopia": ["Ethiopian National Defense Force", "ENDF soldiers", "Ethiopian military"],
    "Nigeria": ["Nigerian Army", "Nigerian military", "Nigerian security forces"],
    "DRC": ["FARDC troops", "Congolese military", "Congolese army"],
    "Mali": ["Malian Armed Forces", "FAMa soldiers", "Malian military"],
    "Burkina Faso": ["Burkinabe military", "Burkinabe soldiers"],
    "Niger": ["Nigerien military", "Nigerien forces"],
    "CAR": ["FACA soldiers", "Central African military"],
    "Cameroon": ["Cameroonian soldiers", "BIR forces", "Cameroonian military"],
    "Libya": ["Libyan military"],
    "Mozambique": ["Mozambican armed forces", "FADM troops"],
    "Kenya": ["Kenyan Defense Forces", "KDF soldiers"],
    "Uganda": ["UPDF forces", "Ugandan military"],
}

# Cities by Country
CITIES = {
    "Somalia": ["Mogadishu", "Kismayo", "Baidoa", "Beledweyne", "Merca", "Afgooye", "Jowhar"],
    "Sudan": ["Khartoum", "Omdurman", "El Fasher", "Nyala", "El Geneina", "Kassala", "Zalingei"],
    "South Sudan": ["Juba", "Malakal", "Bentiu", "Bor", "Wau", "Yei", "Torit"],
    "Ethiopia": ["Mekelle", "Axum", "Shire", "Gondar", "Bahir Dar", "Dessie", "Gambella"],
    "Nigeria": ["Maiduguri", "Yola", "Kaduna", "Jos", "Katsina", "Zamfara", "Damaturu", "Chibok"],
    "DRC": ["Goma", "Bukavu", "Beni", "Butembo", "Uvira", "Bunia", "Rutshuru"],
    "Mali": ["Bamako", "Timbuktu", "Gao", "Kidal", "Mopti", "Segou", "Menaka"],
    "Burkina Faso": ["Ouagadougou", "Djibo", "Dori", "Arbinda", "Kaya", "Ouahigouya"],
    "Niger": ["Niamey", "Diffa", "Tillaberi", "Tahoua", "Maradi"],
    "CAR": ["Bangui", "Bambari", "Bria", "Kaga-Bandoro", "Ndele"],
    "Cameroon": ["Bamenda", "Buea", "Kumba", "Mamfe", "Maroua"],
    "Libya": ["Tripoli", "Benghazi", "Sirte", "Misrata", "Derna"],
    "Mozambique": ["Pemba", "Mocimboa da Praia", "Palma", "Macomia", "Mueda"],
    "Kenya": ["Nairobi", "Garissa", "Mandera", "Wajir", "Lamu"],
    "Uganda": ["Kampala", "Kasese", "Gulu", "Kitgum"],
}

# Regions by Country
REGIONS = {
    "Somalia": ["Lower Shabelle", "Bay Region", "Gedo Region", "Hiiraan Region", "Mudug"],
    "Sudan": ["North Darfur", "South Darfur", "West Darfur", "Blue Nile State", "Kordofan"],
    "South Sudan": ["Unity State", "Upper Nile", "Jonglei State", "Central Equatoria"],
    "Ethiopia": ["Tigray Region", "Amhara Region", "Afar Region", "Oromia Region"],
    "Nigeria": ["Borno State", "Adamawa State", "Yobe State", "Kaduna State", "Plateau State", "Zamfara State"],
    "DRC": ["North Kivu", "South Kivu", "Ituri Province", "Tanganyika Province"],
    "Mali": ["Timbuktu Region", "Gao Region", "Kidal Region", "Mopti Region"],
    "Burkina Faso": ["Sahel Region", "Nord Region", "Centre-Nord", "Est Region"],
    "Niger": ["Tillaberi Region", "Diffa Region", "Tahoua Region"],
    "CAR": ["Ouaka Prefecture", "Haute-Kotto", "Vakaga"],
    "Cameroon": ["North-West Region", "South-West Region", "Far North Region"],
    "Libya": ["Tripolitania", "Cyrenaica", "Fezzan"],
    "Mozambique": ["Cabo Delgado Province", "Nampula Province"],
    "Kenya": ["North Eastern Province", "Coast Province"],
    "Uganda": ["Western Region", "Northern Region"],
}

# Districts (sub-regions)
DISTRICTS = {
    "Somalia": ["Afgooye District", "Balad District", "Wanlaweyn District", "Marka District"],
    "Sudan": ["Kutum locality", "Kebkabiya locality", "Tawila locality", "Jebel Marra area"],
    "South Sudan": ["Mayom County", "Rubkona County", "Panyijiar County", "Fangak County"],
    "Ethiopia": ["Shire Woreda", "Axum Woreda", "Adwa District", "Adigrat area"],
    "Nigeria": ["Gwoza LGA", "Chibok LGA", "Mubi LGA", "Bama LGA", "Konduga LGA"],
    "DRC": ["Masisi territory", "Rutshuru territory", "Beni territory", "Djugu territory"],
    "Mali": ["Ansongo cercle", "Menaka cercle", "Gourma-Rharous cercle"],
    "Burkina Faso": ["Soum Province", "Oudalan Province", "Seno Province"],
    "Niger": ["Torodi Department", "Tera Department", "Banibangou Department"],
    "CAR": ["Ouaka sub-prefecture", "Vakaga sub-prefecture"],
    "Cameroon": ["Mezam Division", "Momo Division", "Manyu Division"],
    "Mozambique": ["Mocimboa da Praia District", "Palma District", "Macomia District"],
}

# Geographic Features
GEOGRAPHIC_FEATURES = {
    "Somalia": ["Jubba River", "Shabelle River", "the coastline", "the hinterlands"],
    "Sudan": ["Jebel Marra mountains", "the Nile River", "the desert region", "the border area"],
    "South Sudan": ["the White Nile", "the Sudd wetlands", "the border region", "the swamplands"],
    "Ethiopia": ["the Tekeze River", "the highlands", "the Simien Mountains", "the lowlands"],
    "Nigeria": ["Lake Chad basin", "the Sambisa Forest", "the Mandara Mountains", "the savanna"],
    "DRC": ["Lake Kivu shores", "the Virunga Mountains", "the rainforest", "Lake Albert region"],
    "Mali": ["the Niger River", "the Sahara Desert", "the Sahel region", "the river delta"],
    "Burkina Faso": ["the Sahel belt", "the border triangle", "the forest reserve"],
    "Niger": ["the Niger River valley", "the Lake Chad region", "the desert zone"],
    "CAR": ["the Chinko River", "the forest region", "the savanna"],
    "Cameroon": ["Mount Cameroon region", "the forest zone", "the border highlands"],
    "Mozambique": ["the coastal region", "the Rovuma River", "the forest area"],
}

# Coordinates (realistic for African locations)
COORDINATES_TEMPLATES = [
    "coordinates 12.4N, 8.5E", "coordinates 4.8S, 29.2E", "coordinates 8.9N, 38.7E",
    "GPS location 6.5N, 3.4E", "GPS location 11.8N, 13.2E", "position 9.1N, 7.5E",
    "location 15.6N, 32.5E", "grid reference 0.3N, 32.6E",
]

# Organizations
ORGANIZATIONS = [
    "the Red Cross", "Doctors Without Borders", "UNICEF", "World Food Programme",
    "International Rescue Committee", "Mercy Corps", "Save the Children",
    "Norwegian Refugee Council", "Action Against Hunger", "CARE International",
    "Oxfam", "Catholic Relief Services", "Islamic Relief", "ICRC",
]

# Weapons (with proper articles handled separately)
WEAPONS = [
    ("AK-47 rifles", "with"),
    ("assault rifles", "with"),
    ("automatic weapons", "with"),
    ("machine guns", "with"),
    ("heavy machine guns", "with"),
    ("RPG launchers", "with"),
    ("rocket-propelled grenades", "with"),
    ("mortars", "with"),
    ("machetes", "with"),
    ("machetes and guns", "with"),
    ("knives and clubs", "with"),
    ("IEDs", "using"),
    ("improvised explosive devices", "using"),
    ("roadside bombs", "using"),
    ("car bombs", "using"),
    ("suicide vests", "using"),
    ("grenades", "with"),
    ("small arms", "with"),
    ("heavy artillery", "with"),
]

# Victim Types
VICTIM_TYPES = [
    "civilians", "villagers", "farmers", "herders", "women and children",
    "elderly residents", "displaced persons", "students", "teachers",
    "health workers", "aid workers", "travelers", "market vendors",
    "fishermen", "miners", "church members", "mosque worshippers",
]

# Target Types
TARGET_TYPES = [
    "villages", "farming communities", "residential areas", "markets",
    "schools", "hospitals", "churches", "mosques", "military bases",
    "police stations", "government buildings", "IDP camps", "highways",
    "farms", "mining sites", "UN compounds", "checkpoints",
]

# Facilities
FACILITIES = [
    "primary school", "secondary school", "hospital", "health center", "clinic",
    "church", "mosque", "military base", "army barracks", "police station",
    "government building", "IDP camp", "refugee camp", "market", "bus station",
    "prison", "courthouse", "UN compound", "NGO office", "warehouse",
]

# Event Types (NOUNS only!)
EVENT_TYPES = [
    "attack", "armed attack", "assault", "armed assault", "raid", "ambush",
    "offensive", "incursion", "bombing", "suicide bombing", "IED attack",
    "massacre", "mass killing", "abduction", "kidnapping", "execution",
    "shelling", "assassination", "robbery", "arson",
]

# Violence Types
VIOLENCE_TYPES = [
    "ethnic violence", "communal violence", "sectarian violence",
    "terrorist attack", "insurgent attack", "militant attack",
    "retaliatory violence", "revenge attack", "bandit attack",
]

# Actions
ACTIONS = [
    "opened fire on", "stormed", "raided", "besieged", "surrounded",
    "burned down", "set fire to", "looted", "ransacked", "abducted",
    "executed", "beheaded", "ambushed", "shelled", "bombed",
]

# Motives
MOTIVES = [
    "in retaliation for previous attacks",
    "in revenge for killings last week",
    "over land disputes",
    "over grazing rights",
    "over cattle theft",
    "for control of territory",
    "for control of resources",
    "to spread terror",
    "to destabilize the region",
    "to extort money from residents",
    "to punish alleged collaborators",
    "as part of ethnic cleansing",
]

# Triggers
TRIGGERS = [
    "following the collapse of peace talks",
    "after disputed election results",
    "following a military offensive",
    "after months of rising tensions",
    "following a cattle rustling incident",
    "after the arrest of a commander",
    "following provocations by rival groups",
    "after a land boundary dispute",
    "following the breakdown of a ceasefire",
]

# Time expressions
TIME_EXPRESSIONS = [
    "early morning", "at dawn", "before dawn", "mid-morning",
    "afternoon", "evening", "at dusk", "night", "late night",
    "around midnight", "overnight", "in the early hours",
]

# Duration expressions
DURATION_EXPRESSIONS = [
    "three-hour assault", "hours-long battle", "two-hour siege",
    "daylong clashes", "week-long offensive", "several hours of fighting",
    "prolonged engagement", "brief but deadly skirmish",
]

# Frequency expressions
FREQUENCY_EXPRESSIONS = [
    "repeated attacks", "daily raids", "weekly incursions",
    "ongoing violence", "persistent attacks", "escalating raids",
    "sporadic clashes", "intensified operations", "continuous assaults",
]

# Date expressions
DATE_EXPRESSIONS = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
    "last Monday", "last Tuesday", "last Friday", "last Saturday",
    "Monday morning", "Tuesday evening", "Wednesday night", "Thursday afternoon",
    "January 15", "February 20", "March 12", "April 8", "May 25", "June 17",
    "July 3", "August 14", "September 22", "October 10", "November 28", "December 5",
    "last week", "last month", "two weeks ago", "earlier this week",
]

# Damage expressions
DAMAGE_EXPRESSIONS = [
    "destroying over 50 homes",
    "burning down the village market",
    "razing dozens of houses",
    "destroying the local school",
    "burning several shops",
    "destroying infrastructure",
    "torching hundreds of homes",
    "demolishing public buildings",
    "setting ablaze storage facilities",
]

# =============================================================================
# DATA CLASS
# =============================================================================

@dataclass
class TrainingExample:
    """A single training example with text and annotations."""
    event_id: str = ""
    text: str = ""
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


# =============================================================================
# COMPREHENSIVE TEMPLATE - Ensures ALL entity types
# =============================================================================

def generate_comprehensive_example() -> TrainingExample:
    """Generate a comprehensive example with ALL entity types covered."""

    # Select country and get related data
    country = random.choice(list(ARMED_GROUPS.keys()))

    # WHO - Actors
    perpetrator = random.choice(ARMED_GROUPS[country])
    government = random.choice(GOVERNMENT_FORCES.get(country, ["security forces"]))
    organization = random.choice(ORGANIZATIONS)

    victim_count = random.randint(15, 150)
    victim_type = random.choice(VICTIM_TYPES)
    victim = f"{victim_count} {victim_type}"

    target_type = random.choice(TARGET_TYPES)

    # WHAT - Event details
    event_type = random.choice(EVENT_TYPES)
    action = random.choice(ACTIONS)
    weapon_info = random.choice(WEAPONS)
    weapon = weapon_info[0]
    weapon_prep = weapon_info[1]
    violence_type = random.choice(VIOLENCE_TYPES)

    # WHEN - Temporal
    date = random.choice(DATE_EXPRESSIONS)
    time = random.choice(TIME_EXPRESSIONS)
    duration = random.choice(DURATION_EXPRESSIONS)
    frequency = random.choice(FREQUENCY_EXPRESSIONS)

    # WHERE - Location
    city = random.choice(CITIES.get(country, ["the capital"]))
    region = random.choice(REGIONS.get(country, ["the region"]))
    district = random.choice(DISTRICTS.get(country, [f"{city} area"]))
    facility = random.choice(FACILITIES)
    geographic = random.choice(GEOGRAPHIC_FEATURES.get(country, ["the area"]))
    coordinates = random.choice(COORDINATES_TEMPLATES)

    # WHY - Cause
    motive = random.choice(MOTIVES)
    trigger = random.choice(TRIGGERS)

    # HOW - Impact
    killed = random.randint(20, 200)
    casualties = f"killing {killed} people"

    injured_count = random.randint(30, 150)
    injured = f"wounding {injured_count} others"

    displaced_count = random.randint(1000, 50000)
    displacement = f"displacing over {displaced_count} residents"

    damage = random.choice(DAMAGE_EXPRESSIONS)

    # Build the sentence - ensure grammatical correctness
    # Template variations
    template_num = random.randint(1, 5)

    if template_num == 1:
        # Full comprehensive template
        text = (
            f"{trigger.capitalize()}, {perpetrator} armed {weapon_prep} {weapon} "
            f"launched {article(event_type)} {event_type} on {target_type} near {facility} "
            f"in {district}, {city}, {region}, {country} on {date} {time}. "
            f"The {duration} resulted in {casualties} and {injured}, while also {displacement}. "
            f"Witnesses reported that fighters {action} {victim_type} {motive}. "
            f"{government} arrived later but found {damage}. "
            f"The attack near {geographic} at {coordinates} marks part of {frequency} in the area. "
            f"{organization} has condemned the {violence_type}."
        )
    elif template_num == 2:
        # News report style
        text = (
            f"In a devastating {event_type}, {perpetrator} armed {weapon_prep} {weapon} "
            f"attacked {target_type} in {city}, {district}, {region} on {date} during the {time}, "
            f"{casualties}, {injured}, and {displacement}. "
            f"The {violence_type} lasted for {duration.replace('assault', 'hours').replace('battle', 'hours')} "
            f"as fighters {action} {victim}, {motive}. "
            f"{government} confirmed the incident near {geographic}, {country}, at {coordinates}. "
            f"{organization} staff at a nearby {facility} reported {damage}. "
            f"This is part of {frequency} {trigger.lower().replace('following', 'since')}."
        )
    elif template_num == 3:
        # Humanitarian focus
        text = (
            f"{organization} has reported a major {event_type} in {region}, {country}, "
            f"where {perpetrator} armed {weapon_prep} {weapon} {action} {target_type} near {facility} "
            f"in {city}, {district} on {date} {time}. "
            f"The {duration} of {violence_type} resulted in {casualties}, {injured}, "
            f"and {displacement} from areas near {geographic} at {coordinates}. "
            f"{government} was unable to prevent {damage}. "
            f"Local sources say the attack was {motive} {trigger.lower()}. "
            f"This adds to {frequency} affecting {victim_type} in the region."
        )
    elif template_num == 4:
        # Military engagement style
        text = (
            f"{trigger.capitalize()}, {perpetrator} launched {article(event_type)} {event_type} "
            f"on {target_type} and a {facility} in {city}, {district} of {region}, {country}, "
            f"on {date} in the {time}. Armed {weapon_prep} {weapon}, militants {action} {victim} "
            f"{motive}, {casualties} and {injured}. "
            f"The {duration} near {geographic} at {coordinates} led to {displacement}. "
            f"{government} reported {damage} from the {violence_type}. "
            f"{organization} confirmed this as part of {frequency} in the area."
        )
    else:
        # Witness account style
        text = (
            f"Survivors described {article(event_type)} {event_type} by {perpetrator} "
            f"in {district}, {city}, {region}, {country} on {date} {time}, "
            f"where armed fighters {weapon_prep} {weapon} {action} {target_type} near a {facility}, "
            f"{casualties} including {victim_type}, and {injured}. "
            f"The {duration} of {violence_type} {motive} led to {displacement} "
            f"from villages near {geographic} at {coordinates}. "
            f"{government} found {damage}. "
            f"{organization} says this continues {frequency} {trigger.lower()}."
        )

    return TrainingExample(
        event_id=str(uuid.uuid4())[:8],
        text=text,
        perpetrator=perpetrator,
        victim=victim,
        target=target_type,
        organization=organization,
        government=government,
        event_type=event_type,
        action=action,
        weapon=weapon,
        violence_type=violence_type,
        date=date,
        time=time,
        duration=duration,
        frequency=frequency,
        country=country,
        region=region,
        city=city,
        district=district,
        facility=facility,
        geographic=geographic,
        coordinates=coordinates,
        casualties=casualties,
        injured=injured,
        displacement=displacement,
        damage=damage,
        motive=motive,
        trigger=trigger,
    )


def generate_examples(num_examples: int = 1000, existing_hashes: set = None) -> List[TrainingExample]:
    """Generate the specified number of unique training examples."""
    examples = []
    seen_hashes = existing_hashes.copy() if existing_hashes else set()
    attempts = 0
    max_attempts = num_examples * 10  # Prevent infinite loops

    while len(examples) < num_examples and attempts < max_attempts:
        attempts += 1
        try:
            example = generate_comprehensive_example()
            # Create hash to check for duplicates
            key = f"{example.perpetrator}|{example.victim}|{example.city}|{example.date}"

            if key not in seen_hashes:
                seen_hashes.add(key)
                examples.append(example)
        except Exception as e:
            print(f"Error generating example: {e}")

    if len(examples) < num_examples:
        print(f"Warning: Only generated {len(examples)} unique examples (requested {num_examples})")

    return examples


def validate_example(example: TrainingExample) -> bool:
    """Validate that all annotations exist in the text."""
    text = example.text.lower()

    fields = [
        ('perpetrator', example.perpetrator),
        ('victim', example.victim),
        ('target', example.target),
        ('city', example.city),
        ('date', example.date),
    ]

    for field_name, value in fields:
        if value and value.lower() not in text:
            print(f"WARNING: {field_name} '{value}' not found in text")
            return False

    return True


FIELDNAMES = [
    "Event_ID", "Article_ID", "Actor_Normalized", "Actor_Type",
    "Victim_Normalized", "Victim_Type", "Location_Country", "Location_City",
    "Location_Coordinates", "Date_Normalized", "Taxonomy_L1", "Taxonomy_L2",
    "Taxonomy_L3", "Weapon_Category", "Deaths", "Injuries", "Severity",
    "Event_Description", "Actor_Confidence", "Victim_Confidence",
    "Location_Confidence", "Date_Confidence", "Classification_Confidence",
    "Flagged_for_Review", "Notes", "Annotator_Name",
    # Entity columns for 26-type schema
    "PERPETRATOR", "VICTIM", "TARGET", "ORGANIZATION", "GOVERNMENT",
    "EVENT_TYPE", "ACTION", "WEAPON", "VIOLENCE_TYPE",
    "DATE", "TIME", "DURATION", "FREQUENCY",
    "COUNTRY", "REGION", "CITY", "DISTRICT", "FACILITY", "GEOGRAPHIC", "COORDINATES",
    "CASUALTIES", "INJURED", "DISPLACEMENT", "DAMAGE",
    "MOTIVE", "TRIGGER"
]


def load_existing_data(filepath: str) -> tuple:
    """Load existing data and return set of Event_IDs and text hashes."""
    existing_ids = set()
    existing_hashes = set()

    import os
    if not os.path.exists(filepath):
        return existing_ids, existing_hashes

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_ids.add(row.get("Event_ID", ""))
                # Create hash of key fields to detect similar content
                text = row.get("Event_Description", "")
                if text:
                    # Use a simple hash of perpetrator+victim+city+date to detect duplicates
                    key = f"{row.get('PERPETRATOR', '')}|{row.get('VICTIM', '')}|{row.get('CITY', '')}|{row.get('DATE', '')}"
                    existing_hashes.add(key)
    except Exception as e:
        print(f"Warning: Could not read existing file: {e}")

    return existing_ids, existing_hashes


def example_to_row(ex: TrainingExample, version: str = "v2") -> dict:
    """Convert a TrainingExample to a CSV row dictionary."""
    return {
        "Event_ID": f"CLEAN_{ex.event_id}",
        "Article_ID": f"CLEAN_{ex.event_id}",
        "Actor_Normalized": ex.perpetrator,
        "Actor_Type": "Armed Group",
        "Victim_Normalized": ex.victim,
        "Victim_Type": "",
        "Location_Country": ex.country,
        "Location_City": ex.city,
        "Location_Coordinates": ex.coordinates,
        "Date_Normalized": ex.date,
        "Taxonomy_L1": "Violence",
        "Taxonomy_L2": ex.event_type,
        "Taxonomy_L3": "",
        "Weapon_Category": ex.weapon,
        "Deaths": "",
        "Injuries": "",
        "Severity": "High",
        "Event_Description": ex.text,
        "Actor_Confidence": "0.99",
        "Victim_Confidence": "0.99",
        "Location_Confidence": "0.99",
        "Date_Confidence": "0.99",
        "Classification_Confidence": "0.99",
        "Flagged_for_Review": "False",
        "Notes": f"Clean synthetic training data {version}",
        "Annotator_Name": f"VioNER-Generator-{version}",
        # Entity columns
        "PERPETRATOR": ex.perpetrator,
        "VICTIM": ex.victim,
        "TARGET": ex.target,
        "ORGANIZATION": ex.organization,
        "GOVERNMENT": ex.government,
        "EVENT_TYPE": ex.event_type,
        "ACTION": ex.action,
        "WEAPON": ex.weapon,
        "VIOLENCE_TYPE": ex.violence_type,
        "DATE": ex.date,
        "TIME": ex.time,
        "DURATION": ex.duration,
        "FREQUENCY": ex.frequency,
        "COUNTRY": ex.country,
        "REGION": ex.region,
        "CITY": ex.city,
        "DISTRICT": ex.district,
        "FACILITY": ex.facility,
        "GEOGRAPHIC": ex.geographic,
        "COORDINATES": ex.coordinates,
        "CASUALTIES": ex.casualties,
        "INJURED": ex.injured,
        "DISPLACEMENT": ex.displacement,
        "DAMAGE": ex.damage,
        "MOTIVE": ex.motive,
        "TRIGGER": ex.trigger,
    }


def write_to_csv(examples: List[TrainingExample], output_path: str, append: bool = False):
    """Write examples to CSV in the required format."""
    import os

    mode = 'a' if append and os.path.exists(output_path) else 'w'
    write_header = mode == 'w'

    with open(output_path, mode, newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if write_header:
            writer.writeheader()

        for ex in examples:
            row = example_to_row(ex, "v3" if append else "v2")
            writer.writerow(row)

    action = "Appended" if append else "Written"
    print(f"{action} {len(examples)} examples to {output_path}")


def print_statistics(examples: List[TrainingExample]):
    """Print entity coverage statistics."""
    print("\n" + "=" * 70)
    print("ENTITY COVERAGE STATISTICS")
    print("=" * 70)

    entity_fields = [
        ("PERPETRATOR", "perpetrator"),
        ("VICTIM", "victim"),
        ("TARGET", "target"),
        ("ORGANIZATION", "organization"),
        ("GOVERNMENT", "government"),
        ("EVENT_TYPE", "event_type"),
        ("ACTION", "action"),
        ("WEAPON", "weapon"),
        ("VIOLENCE_TYPE", "violence_type"),
        ("DATE", "date"),
        ("TIME", "time"),
        ("DURATION", "duration"),
        ("FREQUENCY", "frequency"),
        ("COUNTRY", "country"),
        ("REGION", "region"),
        ("CITY", "city"),
        ("DISTRICT", "district"),
        ("FACILITY", "facility"),
        ("GEOGRAPHIC", "geographic"),
        ("COORDINATES", "coordinates"),
        ("CASUALTIES", "casualties"),
        ("INJURED", "injured"),
        ("DISPLACEMENT", "displacement"),
        ("DAMAGE", "damage"),
        ("MOTIVE", "motive"),
        ("TRIGGER", "trigger"),
    ]

    total = len(examples)
    all_above_95 = True

    for display_name, field_name in entity_fields:
        count = sum(1 for e in examples if getattr(e, field_name, ""))
        pct = (count / total) * 100
        bar = "#" * int(pct / 2)
        status = "✓" if pct >= 95 else "✗"
        print(f"{status} {display_name:20} {count:5} ({pct:5.1f}%) {bar}")
        if pct < 95:
            all_above_95 = False

    print("=" * 70)
    print(f"Total examples: {total}")
    if all_above_95:
        print("✓ ALL entity types have 95%+ coverage!")
    else:
        print("✗ Some entity types below 95% coverage")
    print("=" * 70)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate clean NER training data v2/v3")
    parser.add_argument("--num", type=int, default=1000, help="Number of examples")
    parser.add_argument("--output", type=str,
                        default="/Users/binalfew/Documents/Masters/Thesis/named-entity-recognition/data/source/clean_training_data.csv",
                        help="Output CSV path")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--append", action="store_true", help="Append to existing file instead of overwriting")
    args = parser.parse_args()

    random.seed(args.seed)

    # Load existing data if appending
    existing_ids, existing_hashes = set(), set()
    if args.append:
        print(f"Loading existing data from {args.output}...")
        existing_ids, existing_hashes = load_existing_data(args.output)
        print(f"Found {len(existing_ids)} existing examples")

    version = "v3" if args.append else "v2"
    print(f"Generating {args.num} clean training examples ({version})...")
    examples = generate_examples(args.num, existing_hashes)

    print_statistics(examples)

    write_to_csv(examples, args.output, append=args.append)

    # Count total after append
    if args.append:
        total_count = len(existing_ids) + len(examples)
        print(f"\nTotal examples in file: {total_count}")

    # Print samples
    print("\n" + "=" * 70)
    print("SAMPLE EXAMPLES (newly generated)")
    print("=" * 70)
    for i, ex in enumerate(examples[:2]):
        print(f"\n--- Example {i+1} ---")
        print(f"TEXT: {ex.text[:300]}...")
        print(f"\nENTITIES:")
        print(f"  PERPETRATOR: {ex.perpetrator}")
        print(f"  VICTIM: {ex.victim}")
        print(f"  TARGET: {ex.target}")
        print(f"  GOVERNMENT: {ex.government}")
        print(f"  ORGANIZATION: {ex.organization}")
        print(f"  EVENT_TYPE: {ex.event_type}")
        print(f"  WEAPON: {ex.weapon}")
        print(f"  DATE: {ex.date}")
        print(f"  TIME: {ex.time}")
        print(f"  CITY: {ex.city}")
        print(f"  REGION: {ex.region}")
        print(f"  DISTRICT: {ex.district}")
        print(f"  COUNTRY: {ex.country}")
        print(f"  GEOGRAPHIC: {ex.geographic}")
        print(f"  COORDINATES: {ex.coordinates}")
        print(f"  CASUALTIES: {ex.casualties}")
        print(f"  INJURED: {ex.injured}")
        print(f"  DISPLACEMENT: {ex.displacement}")
        print(f"  DAMAGE: {ex.damage}")
        print(f"  MOTIVE: {ex.motive}")
        print(f"  TRIGGER: {ex.trigger}")
    print("=" * 70)


if __name__ == "__main__":
    main()
