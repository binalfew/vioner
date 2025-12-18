#!/usr/bin/env python3
"""
Hybrid Training Data Generator for VioNER - V3

FIXES from V2:
1. More perpetrator patterns - "Rapid Support Forces", "Somali pirates", multi-word groups
2. Better DATE patterns - Day names ("Tuesday morning"), more ordinal contexts
3. Full country names - "Democratic Republic of Congo", "Central African Republic"
4. More compound victims - "women and elderly", "medical staff", ethnic groups as targets
5. Better entity diversity and real-world patterns
6. Improved text templates for natural language variation

Author: Generated for VioNER thesis project
"""

import csv
import random
from typing import Dict, List, Tuple

# =============================================================================
# IMPROVED DATA LISTS - V3
# =============================================================================

# Multi-word perpetrator groups (critical fix)
MULTI_WORD_PERPETRATORS = [
    "Rapid Support Forces",
    "Sudanese Armed Forces",
    "Somali pirates",
    "Rwandan forces",
    "Ethiopian forces",
    "Eritrean forces",
    "Ugandan forces",
    "Nigerian Army soldiers",
    "Kenyan Defense Forces",
    "Congolese military forces",
    "South Sudanese forces",
    "Malian Armed Forces",
    "Burkinabe security forces",
    "Cameroonian military",
    "Chadian forces",
    "Mozambican forces",
    "Central African forces",
    "Libyan National Army",
    "Government of National Accord forces",
    "Wagner Group mercenaries",
    "Russian mercenaries",
    "Private military contractors",
    "Local defense forces",
    "Community vigilantes",
    "Civilian joint task force",
    "Local hunters militia",
]

# Militant/rebel groups
MILITANT_GROUPS = [
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
    ("Rapid Support Forces", "Janjaweed militia"),
    ("Sudanese Armed Forces", "allied militias"),
    ("M23 rebels", "Rwandan forces"),
    ("FDLR", "Mai-Mai Yakutumba"),
]

# Full country names (critical fix for DRC, CAR, etc.)
COUNTRIES_FULL = [
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

# Country abbreviations/short forms (to train model on both)
COUNTRIES_SHORT = [
    "DRC",
    "CAR",
    "South Sudan",
    "Burkina Faso",
]

# Regions/States/Provinces
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
    "Lamu County",
    "Garissa County",
    "Mandera County",
]

# Cities (including compound names)
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
    "Goma", "Bukavu", "Beni", "Butembo", "Bunia", "Ituri", "Uvira",
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

# Districts
DISTRICTS = [
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
    "Yei River County",
    "Jur River County",
    "Central Equatoria",
    "Eastern Equatoria",
]

# Compound victims (critical fix)
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
    "police and soldiers",
    "villagers and market traders",
    "internally displaced persons",
    "refugees and host community members",
    "ethnic Berom farmers",
    "ethnic Fulani herders",
    "ethnic Hausa traders",
    "ethnic Dinka civilians",
    "ethnic Nuer fighters",
    "ethnic Tigray civilians",
    "ethnic Amhara militia",
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
        # Standard formats
        f"{month} {day}, {year}",
        f"{month} {ordinal(day)}, {year}",
        f"{ordinal(day)} {month} {year}",
        f"{day} {month} {year}",
        f"{ordinal(day)} of {month} {year}",
        f"{month} {ordinal(day)}",
        f"{ordinal(day)} {month}",
        # With day of week
        f"{day_of_week}, {month} {ordinal(day)}",
        f"{day_of_week} {month} {day}",
        f"on {day_of_week}, {month} {ordinal(day)}, {year}",
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

# Time expressions (with day parts)
TIME_EXPRESSIONS = [
    "early morning",
    "at dawn",
    "in the afternoon",
    "in the evening",
    "late at night",
    "around midnight",
    "overnight",
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

# Event types
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

# Targets/Locations targeted
TARGETS = [
    "three villages",
    "several communities",
    "multiple settlements",
    "farming villages",
    "residential areas",
    "market areas",
    "military positions",
    "police stations",
    "government buildings",
    "churches",
    "mosques",
    "schools",
    "IDP camps",
    "refugee camps",
    "convoy",
    "checkpoint",
    "military base",
    "border post",
    "humanitarian convoy",
    "UN compound",
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
    "MONUSCO",
    "UNMISS",
    "AMISOM",
    "MINUSMA",
    "Human Rights Watch",
    "Amnesty International",
    "International Crisis Group",
]

# Government forces
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
]

# Facilities
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
]

# Geographic features
GEOGRAPHIC_FEATURES = [
    "river banks",
    "dense forest",
    "border region",
    "mountainous terrain",
    "Sahel belt",
    "savanna",
    "lake shores",
    "desert area",
    "highland region",
    "coastal region",
    "Lake Chad basin",
    "Nile River valley",
    "Congo River basin",
    "Great Rift Valley",
]

# Duration expressions
DURATION_EXPRESSIONS = [
    "three-hour assault",
    "hours-long battle",
    "two-hour siege",
    "daylong engagement",
    "brief skirmish",
    "prolonged fighting",
    "week-long offensive",
    "overnight attack",
    "multi-day operation",
    "sustained bombardment",
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
    "for control of territory",
    "due to ethnic tensions",
    "for revenge",
    "over grazing rights",
    "for religious reasons",
    "over political grievances",
    "for economic gain",
    "to expand territorial control",
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
# TEMPLATE GENERATION
# =============================================================================

def generate_training_example():
    """Generate a single training example with all 26 entity types."""

    # Perpetrator selection - mix of multi-word, militant groups, and pairs
    perp_type = random.choice(['multi_word', 'militant', 'pair'])

    if perp_type == 'multi_word':
        perpetrator = random.choice(MULTI_WORD_PERPETRATORS)
    elif perp_type == 'militant':
        perpetrator = random.choice(MILITANT_GROUPS)
    else:  # pair
        perp1, perp2 = random.choice(PERPETRATOR_PAIRS)
        perpetrator = f"{perp1} and {perp2}"

    # Victim selection - mix of compound and single
    if random.random() < 0.5:
        victim = random.choice(COMPOUND_VICTIMS)
    else:
        victim = random.choice(SINGLE_VICTIMS)

    # Date selection - mix of single and range
    if random.random() < 0.25:
        date = generate_date_range()
    else:
        date = generate_date()

    # City selection - mix of compound and single
    if random.random() < 0.15:
        city = random.choice(CITIES_COMPOUND)
    else:
        city = random.choice(CITIES_SINGLE)

    # Country - mix of full names and abbreviations
    if random.random() < 0.85:
        country = random.choice(COUNTRIES_FULL)
    else:
        country = random.choice(COUNTRIES_SHORT)

    # Select other entities
    region = random.choice(REGIONS)
    district = random.choice(DISTRICTS)
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
    casualties = generate_casualties()
    injured = generate_injured()

    # Build the text using various templates
    template_num = random.randint(1, 10)

    if template_num == 1:
        text = (
            f"On {date}, {perpetrator} conducted {event_type} on {target} "
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
            f"{trigger.capitalize()}, {perpetrator} launched a {event_type} "
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
            f"where {perpetrator} {action} {target} in {city}, {district}, {region} "
            f"on {date}. The {time_expr} assault using {weapon} resulted in {casualties}, "
            f"{injured}, and {displacement}. "
            f"The {violence_type} targeted {victim} {motive}. "
            f"{government} found {damage} near {facility} in the {geographic} at {coordinates}. "
            f"This {duration} is part of {frequency} {trigger}."
        )
    elif template_num == 4:
        text = (
            f"On {date}, {perpetrator} carried out {frequency} "
            f"in {region}, {country}, {action} {target} near {city} and {facility}. "
            f"The {violence_type} using {weapon} claimed {victim}, with {casualties} and {injured}. "
            f"{government} reported the {duration} caused {damage} and {displacement} "
            f"from the {geographic} in {district} at {coordinates}. "
            f"The attacks occurred {time_expr} {motive}. "
            f"{organization} condemned the incident {trigger}."
        )
    elif template_num == 5:
        text = (
            f"Witnesses in {city}, {region}, {country} described how {perpetrator} "
            f"launched a {event_type} on {date} {time_expr}, {action} {target} near {facility}. "
            f"Armed with {weapon}, the attackers targeted {victim} {motive}, "
            f"resulting in {casualties} and {injured}. "
            f"The {duration} of {violence_type} led to {displacement} from {district}. "
            f"{government} found {damage} in the {geographic} at {coordinates}. "
            f"{organization} says this is part of {frequency} {trigger}."
        )
    elif template_num == 6:
        # RSF-style template
        text = (
            f"The {perpetrator} {action} the {district} of {city} with {weapon} "
            f"on {date} {time_expr}, while {government} jets conducted airstrikes on positions "
            f"in {city}, {region}, with {casualties} and {injured}. "
            f"The {event_type} targeted {victim} at the {facility}. "
            f"The {violence_type} caused {damage} and {displacement} from the {geographic}. "
            f"{organization} reported the {duration} {motive} at {coordinates} in {country}. "
            f"This is part of {frequency} {trigger}."
        )
    elif template_num == 7:
        # M23/DRC-style template
        text = (
            f"{perpetrator}, allegedly backed by foreign forces, seized control of {city} "
            f"in {region} province of the {country} on {date} {trigger}. "
            f"The {event_type} with {government} troops and peacekeepers resulted in "
            f"{casualties} and {injured}. "
            f"The {violence_type} using {weapon} {action} {target}, {motive}. "
            f"{victim} fled toward {city} and {displacement}. "
            f"{organization} reported the {duration} caused {damage} near {facility} "
            f"in the {geographic} at {coordinates} in {district}. "
            f"This continues {frequency}."
        )
    elif template_num == 8:
        # Fulani/farmer-herder template
        text = (
            f"In {motive}, {perpetrator} armed with {weapon} {action} communities "
            f"in {city}, {region}, {country} on {date} {time_expr}, "
            f"killing {victim}, while survivors reported that {government} "
            f"stationed nearby failed to intervene. "
            f"The {event_type} caused {casualties} and {injured}. "
            f"The {violence_type} {trigger} led to {damage} and {displacement}. "
            f"{organization} said the {duration} affected {target} and {facility} "
            f"in {district} near the {geographic} at {coordinates}. "
            f"This is part of {frequency}."
        )
    elif template_num == 9:
        # Piracy/maritime template
        text = (
            f"{perpetrator} operating from {region} {action} a vessel with {victim} "
            f"off the coast of {city}, {country} on {date}. "
            f"The {event_type} {time_expr} using {weapon} resulted in {casualties} and {injured}. "
            f"Meanwhile, militants simultaneously {action} the {government} base in {district}, "
            f"{motive}. "
            f"The {violence_type} caused {damage} and {displacement} from the {geographic}. "
            f"{organization} reported the {duration} affected {target} near {facility} "
            f"at {coordinates}. This continues {frequency} {trigger}."
        )
    else:
        # General comprehensive template
        text = (
            f"On {date}, the {perpetrator} launched a {duration} against {target} "
            f"in {city}, {district}, {region}, {country}. "
            f"The {event_type} {time_expr} saw fighters armed with {weapon} "
            f"{action} {victim}, resulting in {casualties} and {injured}. "
            f"The {violence_type} {motive} caused {damage} near the {facility}. "
            f"{government} confirmed {displacement} from the {geographic} at {coordinates}. "
            f"{organization} said this continues {frequency} {trigger}."
        )

    # Build entity annotations
    entities = {
        "PERPETRATOR": perpetrator,
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
                "Event_ID": f"SYNTH_V3_{i:05d}",
                "Article_ID": f"SYNTH_V3_{i:05d}",
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
                "Notes": "Synthetic training data V3 - comprehensive patterns",
                "Annotator_Name": "VioNER-Generator-V3",
                **entities
            }
            writer.writerow(row)

    print(f"Written {len(examples)} examples to {output_path}")


def print_statistics(examples):
    """Print coverage statistics."""
    print("\n" + "=" * 70)
    print("ENTITY COVERAGE STATISTICS - V3")
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


def print_sample_patterns(examples):
    """Print sample patterns to verify diversity."""
    print("\n" + "=" * 70)
    print("SAMPLE PATTERNS (to verify diversity)")
    print("=" * 70)

    # Sample perpetrators
    perps = list(set(e["PERPETRATOR"] for _, e in examples[:500]))[:10]
    print(f"\nSample PERPETRATORS: {perps}")

    # Sample dates
    dates = list(set(e["DATE"] for _, e in examples[:500]))[:10]
    print(f"\nSample DATES: {dates}")

    # Sample victims
    victims = list(set(e["VICTIM"] for _, e in examples[:500]))[:10]
    print(f"\nSample VICTIMS: {victims}")

    # Sample countries
    countries = list(set(e["COUNTRY"] for _, e in examples[:500]))[:10]
    print(f"\nSample COUNTRIES: {countries}")

    print("=" * 70)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate improved synthetic training data V3")
    parser.add_argument("--num", type=int, default=10000, help="Number of examples")
    parser.add_argument("--output", type=str,
                        default="/Users/binalfew/Documents/Masters/Thesis/named-entity-recognition/data/source/synthetic_training_data_v3.csv",
                        help="Output CSV path")
    parser.add_argument("--seed", type=int, default=2024, help="Random seed")
    args = parser.parse_args()

    random.seed(args.seed)

    print(f"Generating {args.num} synthetic training examples (V3 - comprehensive patterns)...")
    print("This version includes:")
    print("  - Multi-word perpetrators (Rapid Support Forces, Somali pirates)")
    print("  - Full country names (Democratic Republic of Congo)")
    print("  - Day-based dates (Tuesday morning, Saturday night)")
    print("  - Ordinal dates (March 3rd, April 8th)")
    print("  - Compound victims (women and children, medical staff)")
    print("  - Better entity diversity overall")
    print()

    examples = generate_dataset(args.num)

    print_statistics(examples)
    print_sample_patterns(examples)

    write_dataset(examples, args.output)

    # Show sample texts
    print("\n" + "=" * 70)
    print("SAMPLE EXAMPLES")
    print("=" * 70)

    for i, (text, entities) in enumerate(examples[:3]):
        print(f"\n--- Example {i+1} ---")
        print(f"TEXT: {text[:500]}...")
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
