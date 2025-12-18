#!/usr/bin/env python3
"""
Hybrid Training Data Generator for VioNER - V4

FIXES from V3 (based on BIO tagging analysis report):
1. DURATION - Only pure temporal words, NO event words (split "overnight attack" → TIME + EVENT_TYPE)
2. TARGET - Only people/groups being attacked, NOT physical locations
3. FACILITY - Physical locations (base, compound, hospital, market, etc.)
4. DISTRICT - All counties consistently tagged as DISTRICT, not REGION
5. TIME - "overnight" is TIME, not DURATION
6. PERPETRATOR vs GOVERNMENT - Clear separation based on role in sentence

Key semantic rules:
- Armed forces doing violent actions → PERPETRATOR
- Armed forces responding/reporting → GOVERNMENT
- Physical locations (buildings, bases) → FACILITY (never TARGET)
- People/groups being attacked → TARGET
- Temporal when (overnight, morning) → TIME
- Temporal duration (hours-long, prolonged) → DURATION (no event words!)

Author: Generated for VioNER thesis project
"""

import csv
import random
from typing import Dict, List, Tuple

# =============================================================================
# IMPROVED DATA LISTS - V4
# =============================================================================

# PERPETRATORS - Groups that commit violent acts
# These are ALWAYS tagged as PERPETRATOR in generated text
PERPETRATORS = [
    # Militant groups (always perpetrators)
    "Boko Haram insurgents",
    "ISWAP fighters",
    "Al Shabaab militants",
    "ISIS-affiliated militants",
    "M23 rebels",
    "ADF fighters",
    "RSF militia",
    "Janjaweed raiders",
    "TPLF forces",
    "OLA rebels",
    "JNIM militants",
    "ISGS fighters",
    "Seleka rebels",
    "Anti-Balaka militia",
    "Fulani herdsmen",
    "armed bandits",
    "unknown gunmen",
    "Ambazonia separatists",
    "LRA fighters",
    "Mai-Mai militia",
    "FDLR rebels",
    "Ansar Dine militants",
    "Al Qaeda in the Islamic Maghreb",
    "Ansaru militants",
    "Boko Haram faction",
    "Islamic State West Africa",
    "Somali pirates",
    "Wagner Group mercenaries",
    "Russian mercenaries",
    "armed militia",
    "rebel fighters",
    "insurgent forces",
]

# GOVERNMENT - Forces that respond/intervene (NOT perpetrators in our templates)
# These appear in "GOVERNMENT responded/confirmed" context
GOVERNMENT_FORCES = [
    "Nigerian Army",
    "Somali National Army",
    "Ethiopian military",
    "Sudanese Armed Forces",
    "Congolese military",
    "Kenyan Defense Forces",
    "Malian Armed Forces",
    "Ugandan military",
    "Cameroonian soldiers",
    "Burkinabe armed forces",
    "Chadian military",
    "South Sudanese forces",
    "Mozambican military",
    "Central African armed forces",
    "Libyan armed forces",
    "Rwandan Defense Forces",
    "African Union peacekeepers",
    "UN peacekeeping forces",
    "MONUSCO peacekeepers",
    "AMISOM troops",
]

# Perpetrator pairs for dual-perpetrator sentences
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
    ("FDLR", "Mai-Mai"),
    ("M23 rebels", "allied militias"),
]

# TARGET - ONLY people/groups being attacked (NOT physical locations!)
TARGETS_PEOPLE = [
    "three villages",
    "several communities",
    "multiple settlements",
    "farming villages",
    "residential areas",
    "civilian populations",
    "local residents",
    "displaced communities",
    "refugee populations",
    "nomadic herders",
    "fishing communities",
    "trading caravans",
    "humanitarian convoys",
    "peacekeeping patrols",
    "border communities",
]

# FACILITY - Physical locations/buildings (NOT targets!)
FACILITIES = [
    "primary school",
    "hospital",
    "church",
    "mosque",
    "police station",
    "military base",
    "market",
    "IDP camp",
    "health center",
    "government building",
    "UN compound",
    "humanitarian warehouse",
    "refugee camp",
    "prison",
    "court building",
    "community center",
    "Al-Nao Hospital",
    "General Hospital",
    "Teaching Hospital",
    "Central Mosque",
    "Catholic Church",
    "checkpoint",
    "border post",
    "army barracks",
    "airport",
    "bus station",
]

# Full country names
COUNTRIES = [
    "Nigeria",
    "Somalia",
    "Democratic Republic of Congo",
    "South Sudan",
    "Sudan",
    "Ethiopia",
    "Mali",
    "Burkina Faso",
    "Niger",
    "Cameroon",
    "Kenya",
    "Uganda",
    "Mozambique",
    "Central African Republic",
    "Libya",
    "Chad",
    "Rwanda",
    "Burundi",
    "Tanzania",
    "Egypt",
    "Eritrea",
    "Djibouti",
]

# REGION - Named administrative regions (NOT counties!)
REGIONS = [
    "Borno State",
    "Adamawa State",
    "Yobe State",
    "Kaduna State",
    "Plateau State",
    "Katsina State",
    "Zamfara State",
    "North Kivu",
    "South Kivu",
    "Ituri Province",
    "Tanganyika Province",
    "Tigray Region",
    "Amhara Region",
    "Oromia Region",
    "Afar Region",
    "North Darfur",
    "South Darfur",
    "West Darfur",
    "East Darfur",
    "Central Darfur",
    "Blue Nile State",
    "Cabo Delgado Province",
    "Gao Region",
    "Mopti Region",
    "Timbuktu Region",
    "Sahel Region",
    "Centre-Nord Region",
    "Upper Nile State",
    "Jonglei State",
    "Unity State",
    "Lakes State",
]

# DISTRICT - All counties and administrative subdivisions
# (Counties are ALWAYS DISTRICT, not REGION!)
DISTRICTS = [
    # Kenyan counties → DISTRICT
    "Lamu County",
    "Garissa County",
    "Mandera County",
    "Wajir County",
    "Turkana County",
    # South Sudanese counties → DISTRICT
    "Jur River County",
    "Yei River County",
    "Kapoeta County",
    # Other districts
    "Omdurman district",
    "Khartoum North district",
    "Jos South",
    "Jos North",
    "Konduga district",
    "Bama district",
    "Chibok district",
    "Gwoza district",
    "Rutshuru territory",
    "Masisi territory",
    "Nyiragongo territory",
    "Beni territory",
    "Irumu territory",
    "Djugu territory",
    "Central Equatoria",
    "Eastern Equatoria",
    "Western Equatoria",
]

# Cities
CITIES_COMPOUND = [
    "Maiduguri-Damaturu",
    "Kano-Kaduna",
    "Abuja-Lokoja",
    "Jos-Bauchi",
    "Goma-Bukavu",
    "Beni-Butembo",
    "Juba-Bor",
    "Malakal-Bentiu",
    "Khartoum-Omdurman",
    "El Fasher-Nyala",
    "Tripoli-Benghazi",
]

CITIES_SINGLE = [
    "Maiduguri", "Kano", "Kaduna", "Jos", "Yola", "Damaturu", "Chibok",
    "Baga", "Bama", "Dikwa", "Gwoza", "Konduga", "Monguno",
    "Mogadishu", "Kismayo", "Baidoa", "Beledweyne", "Afgooye", "Merka",
    "Goma", "Bukavu", "Beni", "Butembo", "Bunia", "Uvira",
    "Juba", "Malakal", "Bentiu", "Bor", "Wau", "Yei", "Torit",
    "Khartoum", "Omdurman", "El Fasher", "Nyala", "Kassala", "Port Sudan",
    "Bamako", "Timbuktu", "Gao", "Mopti", "Kidal", "Segou",
    "Ouagadougou", "Djibo", "Dori", "Sebba",
    "Bangui", "Bambari", "Bria", "Kaga-Bandoro",
    "Nairobi", "Garissa", "Mombasa", "Lamu",
    "Addis Ababa", "Mekelle", "Bahir Dar", "Gondar",
    "Tripoli", "Benghazi", "Sirte", "Misrata",
    "Ndjamena", "Abeche", "Moundou",
    "Pemba", "Mocimboa da Praia", "Palma", "Mueda",
]

# Compound victims
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
    "women and elderly",
    "women and children",
    "men, women and children",
    "civilians and aid workers",
    "farmers and their families",
    "medical staff and patients",
    "teachers and students",
    "herders and farmers",
    "villagers and market traders",
    "internally displaced persons",
    "refugees and host community members",
    "ethnic Berom farmers",
    "ethnic Fulani herders",
    "ethnic Hausa traders",
    "ethnic Dinka civilians",
    "ethnic Nuer fighters",
    "ethnic Tigray civilians",
]

SINGLE_VICTIMS = [
    "47 soldiers",
    "34 militia members",
    "25 civilians",
    "12 farmers",
    "18 villagers",
    "52 refugees",
    "28 police officers",
    "15 children",
    "67 residents",
    "43 traders",
    "22 students",
    "38 women",
    "56 peacekeepers",
    "14 journalists",
    "23 health workers",
    "31 aid workers",
    "19 local officials",
    "27 bus passengers",
    "41 worshippers",
    "33 market vendors",
]

# Date components
MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def ordinal(n):
    """Convert number to ordinal (1st, 2nd, 3rd, etc.)"""
    if 11 <= n <= 13:
        return f"{n}th"
    return f"{n}{['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]}"

def generate_date():
    """Generate a realistic date string with high variety."""
    month = random.choice(MONTHS)
    day = random.randint(1, 28)
    year = random.randint(2020, 2024)
    day_of_week = random.choice(DAYS_OF_WEEK)

    formats = [
        f"{month} {day}, {year}",
        f"{month} {ordinal(day)}, {year}",
        f"{ordinal(day)} {month} {year}",
        f"{day} {month} {year}",
        f"{ordinal(day)} of {month} {year}",
        f"{month} {ordinal(day)}",
        f"{ordinal(day)} {month}",
        f"{day_of_week}, {month} {ordinal(day)}",
        f"{day_of_week} {month} {day}",
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
        f"from the {ordinal(day1)} to the {ordinal(day2)} of {month}",
        f"{month} {ordinal(day1)} through {month} {ordinal(day2)}",
    ]
    return random.choice(formats)

# TIME - When something happened (includes "overnight"!)
TIME_EXPRESSIONS = [
    "early morning",
    "at dawn",
    "in the afternoon",
    "in the evening",
    "late at night",
    "around midnight",
    "overnight",  # This is TIME, not DURATION!
    "before sunrise",
    "after sunset",
    "Tuesday morning",
    "Saturday night",
    "Sunday afternoon",
    "Monday evening",
    "Friday night",
    "Wednesday morning",
    "Thursday afternoon",
    "around 3 AM",
    "approximately 6 PM",
    "in the early hours",
    "during the night",
]

# DURATION - ONLY pure temporal duration (NO event words!)
# These describe HOW LONG, not WHAT happened
DURATION_EXPRESSIONS = [
    "three hours",
    "several hours",
    "two hours",
    "all day",
    "a full day",
    "multiple days",
    "over a week",
    "the entire night",
    "forty-eight hours",
    "six hours",
    "throughout the day",
    "more than twelve hours",
]

# EVENT_TYPE - Types of violent events
EVENT_TYPES = [
    "raid",
    "raids",
    "attack",
    "attacks",
    "assault",
    "ambush",
    "massacre",
    "bombing",
    "shelling",
    "offensive",
    "incursion",
    "abduction",
    "kidnapping",
    "execution",
    "clashes",
    "bombardment",
    "airstrike",
    "airstrikes",
    "ground offensive",
    "coordinated attack",
    "suicide bombing",
    "car bombing",
    "roadside bombing",
    "armed robbery",
    "mass shooting",
    "siege",
    "engagement",
    "battle",
    "skirmish",
    "fighting",
]

# Weapons
WEAPONS = [
    "AK-47 rifles",
    "machine guns",
    "rocket-propelled grenades",
    "improvised explosive devices",
    "machetes and knives",
    "automatic weapons",
    "mortars and artillery",
    "hand grenades",
    "assault rifles",
    "heavy machine guns",
    "RPG launchers",
    "mortars",
    "artillery shells",
    "suicide vests",
    "car bombs",
    "landmines",
    "small arms",
    "light weapons",
    "anti-aircraft guns",
    "technicals",
]

# Actions
ACTIONS = [
    "attacked",
    "raided",
    "stormed",
    "ambushed",
    "besieged",
    "burned",
    "looted",
    "abducted",
    "executed",
    "killed",
    "bombarded",
    "shelled",
    "destroyed",
    "overran",
    "seized",
    "captured",
    "invaded",
    "occupied",
    "torched",
    "ransacked",
    "massacred",
    "targeted",
    "struck",
    "hit",
]

# Violence types
VIOLENCE_TYPES = [
    "ethnic violence",
    "communal violence",
    "terrorist attack",
    "insurgent attack",
    "sectarian violence",
    "militant violence",
    "bandit attacks",
    "armed violence",
    "retaliatory violence",
    "intercommunal clashes",
    "farmer-herder violence",
    "political violence",
    "election-related violence",
    "religious violence",
    "land dispute violence",
]

# Organizations
ORGANIZATIONS = [
    "Red Cross",
    "Doctors Without Borders",
    "UNICEF",
    "World Food Programme",
    "UNHCR",
    "Oxfam",
    "Save the Children",
    "African Union",
    "ICRC",
    "Human Rights Watch",
    "Amnesty International",
    "International Crisis Group",
    "Medecins Sans Frontieres",
    "World Health Organization",
]

# Geographic features (NOT "region" in the name to avoid confusion)
GEOGRAPHIC_FEATURES = [
    "river banks",
    "dense forest",
    "border area",
    "mountainous terrain",
    "Sahel belt",
    "savanna",
    "lake shores",
    "desert area",
    "highland area",
    "coastal area",
    "Lake Chad basin",
    "Nile River valley",
    "Congo River basin",
    "Great Rift Valley",
]

# Frequency expressions
FREQUENCY_EXPRESSIONS = [
    "repeated attacks",
    "daily raids",
    "weekly incursions",
    "ongoing violence",
    "persistent attacks",
    "escalating raids",
    "intensified operations",
    "sporadic clashes",
    "continuous fighting",
    "recurring violence",
]

# Motive expressions
MOTIVE_EXPRESSIONS = [
    "in retaliation for previous attacks",
    "over land disputes",
    "for control of the area",
    "due to ethnic tensions",
    "for revenge",
    "over grazing rights",
    "for religious reasons",
    "over political grievances",
    "for economic gain",
    "to expand their control",
]

# Trigger expressions
TRIGGER_EXPRESSIONS = [
    "following the collapse of peace talks",
    "after disputed election results",
    "following a military offensive",
    "after months of tensions",
    "following the breakdown of a ceasefire",
    "after peace negotiations failed",
    "following ethnic clashes",
    "after government crackdown",
    "following failed disarmament talks",
    "after the withdrawal of peacekeepers",
]

# Damage expressions
DAMAGE_EXPRESSIONS = [
    "destroying over 200 homes",
    "burning the village market",
    "razing dozens of houses",
    "torching hundreds of structures",
    "destroying critical infrastructure",
    "burning schools and clinics",
    "demolishing residential areas",
    "setting fire to crops and granaries",
]

# Displacement expressions
DISPLACEMENT_EXPRESSIONS = [
    "displacing over 15,000 residents",
    "forcing 10,000 people to flee",
    "displacing thousands of families",
    "causing mass displacement",
    "forcing entire villages to flee",
    "creating a new wave of refugees",
    "displacing approximately 450,000 civilians",
    "forcing residents to seek shelter",
]

# Coordinates
COORDINATES = [
    "coordinates 9.5N, 7.8E",
    "coordinates 4.2N, 18.6E",
    "coordinates 11.3N, 42.1E",
    "GPS location 6.8S, 39.2E",
    "coordinates 12.1N, 15.0E",
    "coordinates 8.5N, 13.2W",
    "coordinates 0.5S, 25.0E",
    "coordinates 4.8N, 31.5E",
]

# Casualties patterns
def generate_casualties():
    """Generate casualty count with variety."""
    count = random.randint(3, 200)
    patterns = [
        f"{count} people killed",
        f"{count} dead",
        f"at least {count} killed",
        f"more than {count} dead",
        f"{count} fatalities",
        f"approximately {count} killed",
        f"an estimated {count} dead",
        f"{count} people dead",
    ]
    return random.choice(patterns)

def generate_injured():
    """Generate injured count with variety."""
    count = random.randint(5, 300)
    patterns = [
        f"{count} wounded",
        f"{count} injured",
        f"at least {count} wounded",
        f"more than {count} injured",
        f"approximately {count} wounded",
        f"{count} people injured",
        f"an estimated {count} wounded",
    ]
    return random.choice(patterns)

# =============================================================================
# TEMPLATE GENERATION - V4
# =============================================================================

def generate_training_example():
    """Generate a single training example with all 26 entity types.

    Key semantic rules enforced:
    - PERPETRATOR: Always the group doing violent action
    - GOVERNMENT: Always the responding/reporting force
    - FACILITY: Physical locations (buildings, bases)
    - TARGET: Only people/communities being attacked
    - TIME: When it happened (includes "overnight")
    - DURATION: How long it lasted (pure temporal, no event words)
    """

    # Perpetrator selection
    perp_type = random.choice(['single', 'pair'])
    if perp_type == 'pair':
        perp1, perp2 = random.choice(PERPETRATOR_PAIRS)
        perpetrator = f"{perp1} and {perp2}"
    else:
        perpetrator = random.choice(PERPETRATORS)

    # Victim selection
    if random.random() < 0.5:
        victim = random.choice(COMPOUND_VICTIMS)
    else:
        victim = random.choice(SINGLE_VICTIMS)

    # Date selection
    if random.random() < 0.25:
        date = generate_date_range()
    else:
        date = generate_date()

    # City selection
    if random.random() < 0.15:
        city = random.choice(CITIES_COMPOUND)
    else:
        city = random.choice(CITIES_SINGLE)

    # Select other entities
    country = random.choice(COUNTRIES)
    region = random.choice(REGIONS)
    district = random.choice(DISTRICTS)
    weapon = random.choice(WEAPONS)
    event_type = random.choice(EVENT_TYPES)
    action = random.choice(ACTIONS)
    violence_type = random.choice(VIOLENCE_TYPES)
    target = random.choice(TARGETS_PEOPLE)  # Only people, not facilities!
    organization = random.choice(ORGANIZATIONS)
    government = random.choice(GOVERNMENT_FORCES)
    facility = random.choice(FACILITIES)
    geographic = random.choice(GEOGRAPHIC_FEATURES)
    time_expr = random.choice(TIME_EXPRESSIONS)
    duration = random.choice(DURATION_EXPRESSIONS)  # Pure temporal only!
    frequency = random.choice(FREQUENCY_EXPRESSIONS)
    motive = random.choice(MOTIVE_EXPRESSIONS)
    trigger = random.choice(TRIGGER_EXPRESSIONS)
    damage = random.choice(DAMAGE_EXPRESSIONS)
    displacement = random.choice(DISPLACEMENT_EXPRESSIONS)
    coordinates = random.choice(COORDINATES)
    casualties = generate_casualties()
    injured = generate_injured()

    # Build the text using templates that enforce semantic rules
    template_num = random.randint(1, 8)

    if template_num == 1:
        # Clear PERPETRATOR (doing action) vs GOVERNMENT (responding)
        text = (
            f"On {date}, {perpetrator} conducted a {event_type} on {target} "
            f"in {region}, {country}, near {city}, using {weapon}, "
            f"resulting in {casualties} and {injured}. "
            f"The {violence_type} lasted {duration} and {action} {victim}, {motive}. "
            f"{government} responded but found {damage} at the {facility}. "
            f"{organization} reported {displacement} from the {geographic} at {coordinates}. "
            f"The incident occurred {time_expr}, {trigger}. "
            f"This is part of {frequency} affecting {district}."
        )
    elif template_num == 2:
        text = (
            f"{trigger.capitalize()}, {perpetrator} launched a {event_type} "
            f"on {target} near the {facility} in {city}, {region}, {country} on {date} {time_expr}. "
            f"Armed with {weapon}, fighters {action} {victim} for {duration}, "
            f"leaving {casualties} and {injured}. "
            f"The {violence_type} was {motive}. "
            f"{government} confirmed {damage} in the {geographic} at {coordinates}. "
            f"{organization} says {displacement} as {frequency} continue in {district}."
        )
    elif template_num == 3:
        text = (
            f"{organization} has reported a devastating {event_type} in {country} "
            f"where {perpetrator} {action} {target} in {city}, {district}, {region} "
            f"on {date}. The {time_expr} assault using {weapon} lasted {duration}, "
            f"resulting in {casualties}, {injured}, and {displacement}. "
            f"The {violence_type} targeted {victim} {motive}. "
            f"{government} found {damage} near the {facility} in the {geographic} at {coordinates}. "
            f"This is part of {frequency} {trigger}."
        )
    elif template_num == 4:
        text = (
            f"On {date}, {perpetrator} carried out {frequency} "
            f"in {region}, {country}, {action} {target} near {city} and the {facility}. "
            f"The {violence_type} using {weapon} lasted {duration}, claiming {victim}, "
            f"with {casualties} and {injured}. "
            f"{government} reported {damage} and {displacement} "
            f"from the {geographic} in {district} at {coordinates}. "
            f"The attacks occurred {time_expr} {motive}. "
            f"{organization} condemned the incident {trigger}."
        )
    elif template_num == 5:
        text = (
            f"Witnesses in {city}, {region}, {country} described how {perpetrator} "
            f"launched a {event_type} on {date} {time_expr}, {action} {target} near the {facility}. "
            f"Armed with {weapon}, the attackers targeted {victim} {motive} for {duration}, "
            f"resulting in {casualties} and {injured}. "
            f"The {violence_type} led to {displacement} from {district}. "
            f"{government} found {damage} in the {geographic} at {coordinates}. "
            f"{organization} says this is part of {frequency} {trigger}."
        )
    elif template_num == 6:
        # RSF-style
        text = (
            f"The {perpetrator} {action} the {district} of {city} with {weapon} "
            f"on {date} {time_expr}. The {event_type} lasted {duration}, while {government} "
            f"jets conducted airstrikes on positions in {city}, {region}, "
            f"resulting in {casualties} and {injured}. "
            f"The {violence_type} targeted {victim} at the {facility}. "
            f"{damage} and {displacement} from the {geographic} were reported. "
            f"{organization} said the incident was {motive} at {coordinates} in {country}. "
            f"This is part of {frequency} {trigger} affecting {target}."
        )
    elif template_num == 7:
        # DRC-style
        text = (
            f"{perpetrator}, allegedly backed by foreign powers, seized control of {city} "
            f"in {region} of {country} on {date} {trigger}. "
            f"The {event_type} with {government} troops lasted {duration}, resulting in "
            f"{casualties} and {injured}. "
            f"The {violence_type} using {weapon} {action} {target}, {motive}. "
            f"{victim} fled toward {city} amid {displacement}. "
            f"{organization} reported {damage} near the {facility} "
            f"in the {geographic} at {coordinates} in {district}. "
            f"This continues {frequency} {time_expr}."
        )
    else:
        # General comprehensive
        text = (
            f"On {date}, the {perpetrator} launched a {event_type} lasting {duration} "
            f"against {target} in {city}, {district}, {region}, {country}. "
            f"The assault {time_expr} saw fighters armed with {weapon} "
            f"{action} {victim}, resulting in {casualties} and {injured}. "
            f"The {violence_type} {motive} caused {damage} near the {facility}. "
            f"{government} confirmed {displacement} from the {geographic} at {coordinates}. "
            f"{organization} said this continues {frequency} {trigger}."
        )

    # Build entity annotations
    entities = {
        "PERPETRATOR": perpetrator,
        "VICTIM": victim,
        "TARGET": target,  # Only people/communities now!
        "ORGANIZATION": organization,
        "GOVERNMENT": government,
        "EVENT_TYPE": event_type,
        "ACTION": action,
        "WEAPON": weapon,
        "VIOLENCE_TYPE": violence_type,
        "DATE": date,
        "TIME": time_expr,
        "DURATION": duration,  # Pure temporal only!
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


def generate_dataset(num_examples: int = 10000, max_attempts: int = 100000):
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
                "Event_ID": f"SYNTH_V4_{i:05d}",
                "Article_ID": f"SYNTH_V4_{i:05d}",
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
                "Notes": "Synthetic training data V4 - semantic consistency fixes",
                "Annotator_Name": "VioNER-Generator-V4",
                **entities
            }
            writer.writerow(row)

    print(f"Written {len(examples)} examples to {output_path}")


def print_statistics(examples):
    """Print coverage statistics."""
    print("\n" + "=" * 70)
    print("ENTITY COVERAGE STATISTICS - V4")
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
        count = sum(1 for _, entities in examples if entities.get(entity_type))
        pct = (count / total) * 100

        in_text = sum(1 for text, entities in examples
                     if entities.get(entity_type) and
                     entities[entity_type].lower() in text.lower())
        in_text_pct = (in_text / total) * 100

        status = "✓" if pct == 100 and in_text_pct == 100 else "✗"
        print(f"{status} {entity_type:20} Filled: {pct:5.1f}%  In-text: {in_text_pct:5.1f}%")

    print("=" * 70)


def print_semantic_checks(examples):
    """Print semantic consistency checks."""
    print("\n" + "=" * 70)
    print("SEMANTIC CONSISTENCY CHECKS - V4")
    print("=" * 70)

    # Check 1: No facility words in TARGET
    facility_keywords = ['base', 'compound', 'hospital', 'clinic', 'school', 'church',
                        'mosque', 'camp', 'prison', 'warehouse', 'market', 'building',
                        'station', 'post', 'checkpoint', 'airport']

    target_has_facility = sum(1 for _, e in examples
                              if any(kw in e['TARGET'].lower() for kw in facility_keywords))
    print(f"✓ TARGETs with facility words: {target_has_facility} (should be 0)")

    # Check 2: No event words in DURATION
    event_words = ['attack', 'assault', 'siege', 'engagement', 'offensive',
                   'operation', 'fighting', 'battle', 'skirmish', 'raid', 'bombardment']

    duration_has_event = sum(1 for _, e in examples
                             if any(kw in e['DURATION'].lower() for kw in event_words))
    print(f"✓ DURATIONs with event words: {duration_has_event} (should be 0)")

    # Check 3: Counties are in DISTRICT, not REGION
    counties_in_region = sum(1 for _, e in examples
                             if 'county' in e['REGION'].lower())
    print(f"✓ Counties tagged as REGION: {counties_in_region} (should be 0)")

    # Check 4: "overnight" is in TIME, not DURATION
    overnight_in_duration = sum(1 for _, e in examples
                                if 'overnight' in e['DURATION'].lower())
    overnight_in_time = sum(1 for _, e in examples
                           if 'overnight' in e['TIME'].lower())
    print(f"✓ 'overnight' in DURATION: {overnight_in_duration} (should be 0)")
    print(f"✓ 'overnight' in TIME: {overnight_in_time} (can be >0)")

    print("=" * 70)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate improved synthetic training data V4")
    parser.add_argument("--num", type=int, default=10000, help="Number of examples")
    parser.add_argument("--output", type=str,
                        default="/Users/binalfew/Documents/Masters/Thesis/named-entity-recognition/data/source/synthetic_training_data_v4.csv",
                        help="Output CSV path")
    parser.add_argument("--seed", type=int, default=2024, help="Random seed")
    args = parser.parse_args()

    random.seed(args.seed)

    print(f"Generating {args.num} synthetic training examples (V4 - semantic consistency)...")
    print("Key fixes in V4:")
    print("  - DURATION: Pure temporal only (no event words like 'attack', 'siege')")
    print("  - TARGET: Only people/communities (no physical locations)")
    print("  - FACILITY: Physical locations (buildings, bases, etc.)")
    print("  - DISTRICT: All counties consistently tagged as DISTRICT")
    print("  - TIME: 'overnight' is TIME, not DURATION")
    print("  - PERPETRATOR vs GOVERNMENT: Clear semantic separation")
    print()

    examples = generate_dataset(args.num)

    print_statistics(examples)
    print_semantic_checks(examples)

    write_dataset(examples, args.output)

    # Show samples
    print("\n" + "=" * 70)
    print("SAMPLE EXAMPLES")
    print("=" * 70)

    for i, (text, entities) in enumerate(examples[:2]):
        print(f"\n--- Example {i+1} ---")
        print(f"TEXT: {text[:400]}...")
        print(f"\nKEY ENTITIES:")
        print(f"  PERPETRATOR: {entities['PERPETRATOR']}")
        print(f"  GOVERNMENT: {entities['GOVERNMENT']}")
        print(f"  TARGET: {entities['TARGET']}")
        print(f"  FACILITY: {entities['FACILITY']}")
        print(f"  DURATION: {entities['DURATION']}")
        print(f"  TIME: {entities['TIME']}")
        print(f"  DISTRICT: {entities['DISTRICT']}")

    print("=" * 70)


if __name__ == "__main__":
    main()
