"""
CSV Enhancement and Validation Script (v4 - Maximum Enhancement)
Automatically extracts additional entity types from Event_Description,
validates existing entities, cleans invalid values, and infers country from city.

Author: Binalfew Kassa Mekonnen
Date: December 2025

v4 Changes:
- Infer COUNTRY from CITY using CONFLICT_CITIES mapping
- Infer COUNTRY from REGION when possible
- Improved DISPLACEMENT extraction patterns
- Improved TARGET extraction patterns
- Better text normalization for matching
- All v3 improvements preserved
"""

import pandas as pd
import re
import sys
import unicodedata
from pathlib import Path
from collections import defaultdict
from typing import Tuple, List, Optional, Dict

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.kb import get_knowledge_base, AFRICAN_COUNTRIES, CONFLICT_CITIES

kb = get_knowledge_base()


# ============================================================================
# CITY TO COUNTRY MAPPING (Extended)
# ============================================================================

# Build city-to-country lookup from CONFLICT_CITIES
CITY_TO_COUNTRY = {city.lower(): info['country'] for city, info in CONFLICT_CITIES.items()}

# Add more African cities for better coverage
ADDITIONAL_CITIES = {
    # Nigeria
    'abuja': 'Nigeria', 'lagos': 'Nigeria', 'kano': 'Nigeria', 'ibadan': 'Nigeria',
    'port harcourt': 'Nigeria', 'benin city': 'Nigeria', 'jos': 'Nigeria',
    'gombe': 'Nigeria', 'bauchi': 'Nigeria', 'sokoto': 'Nigeria', 'kaduna': 'Nigeria',
    'zaria': 'Nigeria', 'aba': 'Nigeria', 'enugu': 'Nigeria', 'onitsha': 'Nigeria',
    'makurdi': 'Nigeria', 'jalingo': 'Nigeria', 'gusau': 'Nigeria', 'birnin kebbi': 'Nigeria',

    # Kenya
    'nairobi': 'Kenya', 'mombasa': 'Kenya', 'kisumu': 'Kenya', 'eldoret': 'Kenya',
    'nakuru': 'Kenya', 'garissa': 'Kenya', 'wajir': 'Kenya', 'mandera': 'Kenya',
    'lamu': 'Kenya', 'malindi': 'Kenya', 'isiolo': 'Kenya', 'marsabit': 'Kenya',

    # Somalia
    'hargeisa': 'Somalia', 'bosaso': 'Somalia', 'galkayo': 'Somalia', 'berbera': 'Somalia',
    'afgooye': 'Somalia', 'baardheere': 'Somalia', 'afmadow': 'Somalia', 'bardere': 'Somalia',

    # South Sudan
    'rumbek': 'South Sudan', 'aweil': 'South Sudan', 'renk': 'South Sudan', 'torit': 'South Sudan',
    'nimule': 'South Sudan', 'bor town': 'South Sudan', 'pibor': 'South Sudan',

    # Sudan
    'el obeid': 'Sudan', 'atbara': 'Sudan', 'al qadarif': 'Sudan', 'dongola': 'Sudan',
    'sennar': 'Sudan', 'el fasher': 'Sudan', 'kutum': 'Sudan', 'tawila': 'Sudan',

    # DRC
    'matadi': 'Democratic Republic of Congo', 'kananga': 'Democratic Republic of Congo',
    'mbuji-mayi': 'Democratic Republic of Congo', 'kolwezi': 'Democratic Republic of Congo',
    'likasi': 'Democratic Republic of Congo', 'mbandaka': 'Democratic Republic of Congo',

    # Ethiopia
    'dire dawa': 'Ethiopia', 'harar': 'Ethiopia', 'jijiga': 'Ethiopia', 'dilla': 'Ethiopia',
    'arba minch': 'Ethiopia', 'hawassa': 'Ethiopia', 'adama': 'Ethiopia', 'nekemte': 'Ethiopia',

    # Mali
    'sikasso': 'Mali', 'kayes': 'Mali', 'koulikoro': 'Mali', 'douentza': 'Mali',
    'bandiagara': 'Mali', 'djenne': 'Mali', 'niono': 'Mali', 'aguelhok': 'Mali',

    # Burkina Faso
    'bobo-dioulasso': 'Burkina Faso', 'banfora': 'Burkina Faso', 'koudougou': 'Burkina Faso',
    'ouahigouya': 'Burkina Faso', 'tenkodogo': 'Burkina Faso', 'dedougou': 'Burkina Faso',

    # Niger
    'niamey': 'Niger', 'zinder': 'Niger', 'maradi': 'Niger', 'agadez': 'Niger',
    'tahoua': 'Niger', 'dosso': 'Niger', 'diffa': 'Niger', 'tillaberi': 'Niger',

    # Chad
    "n'djamena": 'Chad', 'moundou': 'Chad', 'abeche': 'Chad', 'sarh': 'Chad',
    'faya-largeau': 'Chad', 'bongor': 'Chad', 'doba': 'Chad', 'am timan': 'Chad',

    # CAR
    'berberati': 'Central African Republic', 'bouar': 'Central African Republic',
    'bossangoa': 'Central African Republic', 'carnot': 'Central African Republic',

    # Cameroon
    'douala': 'Cameroon', 'yaounde': 'Cameroon', 'garoua': 'Cameroon', 'ngaoundere': 'Cameroon',
    'bafoussam': 'Cameroon', 'kribi': 'Cameroon', 'limbe': 'Cameroon', 'ebolowa': 'Cameroon',

    # Uganda
    'kampala': 'Uganda', 'gulu': 'Uganda', 'lira': 'Uganda', 'mbale': 'Uganda',
    'jinja': 'Uganda', 'mbarara': 'Uganda', 'fort portal': 'Uganda', 'soroti': 'Uganda',

    # Rwanda
    'kigali': 'Rwanda', 'butare': 'Rwanda', 'gisenyi': 'Rwanda', 'ruhengeri': 'Rwanda',
    'byumba': 'Rwanda', 'cyangugu': 'Rwanda', 'gitarama': 'Rwanda', 'kibuye': 'Rwanda',

    # Burundi
    'bujumbura': 'Burundi', 'gitega': 'Burundi', 'ngozi': 'Burundi', 'rumonge': 'Burundi',
    'cibitoke': 'Burundi', 'makamba': 'Burundi', 'bubanza': 'Burundi', 'kayanza': 'Burundi',

    # Tanzania
    'dar es salaam': 'Tanzania', 'dodoma': 'Tanzania', 'mwanza': 'Tanzania', 'arusha': 'Tanzania',
    'mbeya': 'Tanzania', 'morogoro': 'Tanzania', 'tanga': 'Tanzania', 'zanzibar': 'Tanzania',

    # Mozambique
    'beira': 'Mozambique', 'nampula': 'Mozambique', 'quelimane': 'Mozambique', 'tete': 'Mozambique',
    'chimoio': 'Mozambique', 'lichinga': 'Mozambique', 'inhambane': 'Mozambique',

    # Egypt
    'cairo': 'Egypt', 'alexandria': 'Egypt', 'giza': 'Egypt', 'sharm el sheikh': 'Egypt',
    'luxor': 'Egypt', 'aswan': 'Egypt', 'el arish': 'Egypt', 'rafah': 'Egypt', 'ismailia': 'Egypt',

    # Libya
    'tripoli': 'Libya', 'benghazi': 'Libya', 'misrata': 'Libya', 'sirte': 'Libya',
    'zawiya': 'Libya', 'tobruk': 'Libya', 'derna': 'Libya', 'sabha': 'Libya', 'zliten': 'Libya',

    # Tunisia
    'tunis': 'Tunisia', 'sfax': 'Tunisia', 'sousse': 'Tunisia', 'bizerte': 'Tunisia',
    'kairouan': 'Tunisia', 'gabes': 'Tunisia', 'kasserine': 'Tunisia', 'ben gardane': 'Tunisia',

    # Algeria
    'algiers': 'Algeria', 'oran': 'Algeria', 'constantine': 'Algeria', 'annaba': 'Algeria',
    'batna': 'Algeria', 'setif': 'Algeria', 'djelfa': 'Algeria', 'biskra': 'Algeria',

    # Morocco
    'rabat': 'Morocco', 'casablanca': 'Morocco', 'marrakech': 'Morocco', 'fez': 'Morocco',
    'tangier': 'Morocco', 'agadir': 'Morocco', 'meknes': 'Morocco', 'oujda': 'Morocco',

    # South Africa
    'johannesburg': 'South Africa', 'cape town': 'South Africa', 'durban': 'South Africa',
    'pretoria': 'South Africa', 'port elizabeth': 'South Africa', 'bloemfontein': 'South Africa',
    'polokwane': 'South Africa', 'pietermaritzburg': 'South Africa', 'soweto': 'South Africa',

    # Zimbabwe
    'harare': 'Zimbabwe', 'bulawayo': 'Zimbabwe', 'chitungwiza': 'Zimbabwe', 'mutare': 'Zimbabwe',
    'gweru': 'Zimbabwe', 'kwekwe': 'Zimbabwe', 'masvingo': 'Zimbabwe', 'kadoma': 'Zimbabwe',

    # Zambia
    'lusaka': 'Zambia', 'ndola': 'Zambia', 'kitwe': 'Zambia', 'livingstone': 'Zambia',
    'chipata': 'Zambia', 'kasama': 'Zambia', 'kabwe': 'Zambia', 'solwezi': 'Zambia',

    # Ghana
    'accra': 'Ghana', 'kumasi': 'Ghana', 'tamale': 'Ghana', 'takoradi': 'Ghana',
    'cape coast': 'Ghana', 'tema': 'Ghana', 'ho': 'Ghana', 'koforidua': 'Ghana',

    # Senegal
    'dakar': 'Senegal', 'saint-louis': 'Senegal', 'thies': 'Senegal', 'kaolack': 'Senegal',
    'ziguinchor': 'Senegal', 'tambacounda': 'Senegal', 'kolda': 'Senegal', 'matam': 'Senegal',

    # Ivory Coast
    'abidjan': 'Ivory Coast', 'bouake': 'Ivory Coast', 'daloa': 'Ivory Coast',
    'yamoussoukro': 'Ivory Coast', 'korhogo': 'Ivory Coast', 'san-pedro': 'Ivory Coast',

    # Liberia
    'monrovia': 'Liberia', 'gbarnga': 'Liberia', 'buchanan': 'Liberia', 'zwedru': 'Liberia',
    'harper': 'Liberia', 'kakata': 'Liberia', 'sanniquellie': 'Liberia', 'robertsport': 'Liberia',

    # Sierra Leone
    'freetown': 'Sierra Leone', 'bo': 'Sierra Leone', 'kenema': 'Sierra Leone', 'makeni': 'Sierra Leone',
    'koidu': 'Sierra Leone', 'lunsar': 'Sierra Leone', 'port loko': 'Sierra Leone', 'bonthe': 'Sierra Leone',

    # Guinea
    'conakry': 'Guinea', 'nzerekore': 'Guinea', 'kankan': 'Guinea', 'labe': 'Guinea',
    'kindia': 'Guinea', 'mamou': 'Guinea', 'boke': 'Guinea', 'faranah': 'Guinea',

    # Eritrea
    'asmara': 'Eritrea', 'massawa': 'Eritrea', 'keren': 'Eritrea', 'assab': 'Eritrea',
    'mendefera': 'Eritrea', 'barentu': 'Eritrea', 'dekemhare': 'Eritrea', 'adi keyh': 'Eritrea',

    # Djibouti
    'djibouti city': 'Djibouti', 'ali sabieh': 'Djibouti', 'tadjoura': 'Djibouti', 'obock': 'Djibouti',
    'dikhil': 'Djibouti', 'arta': 'Djibouti', 'airolaf': 'Djibouti',

    # Angola
    'luanda': 'Angola', 'huambo': 'Angola', 'benguela': 'Angola', 'lobito': 'Angola',
    'lubango': 'Angola', 'kuito': 'Angola', 'cabinda': 'Angola', 'malanje': 'Angola',
}

# Merge all city mappings
CITY_TO_COUNTRY.update({k.lower(): v for k, v in ADDITIONAL_CITIES.items()})


# Region to country mapping
REGION_TO_COUNTRY = {
    # Nigeria
    'borno': 'Nigeria', 'adamawa': 'Nigeria', 'yobe': 'Nigeria', 'katsina': 'Nigeria',
    'zamfara': 'Nigeria', 'kaduna': 'Nigeria', 'plateau': 'Nigeria', 'benue': 'Nigeria',
    'taraba': 'Nigeria', 'nasarawa': 'Nigeria', 'sokoto': 'Nigeria', 'kebbi': 'Nigeria',
    # Sudan
    'darfur': 'Sudan', 'khartoum': 'Sudan', 'kordofan': 'Sudan', 'kassala': 'Sudan',
    'north darfur': 'Sudan', 'south darfur': 'Sudan', 'west darfur': 'Sudan',
    'east darfur': 'Sudan', 'central darfur': 'Sudan', 'blue nile': 'Sudan',
    # South Sudan
    'jonglei': 'South Sudan', 'unity': 'South Sudan', 'upper nile': 'South Sudan',
    'lakes state': 'South Sudan', 'warrap state': 'South Sudan', 'equatoria state': 'South Sudan',
    # Somalia
    'lower shabelle': 'Somalia', 'middle shabelle': 'Somalia', 'banadir': 'Somalia',
    'gedo': 'Somalia', 'lower juba': 'Somalia', 'middle juba': 'Somalia', 'hiraan': 'Somalia',
    # Ethiopia
    'tigray': 'Ethiopia', 'amhara': 'Ethiopia', 'oromia': 'Ethiopia', 'afar': 'Ethiopia',
    'somali region': 'Ethiopia', 'gambella': 'Ethiopia', 'benishangul-gumuz': 'Ethiopia',
    # DRC
    'north kivu': 'Democratic Republic of Congo', 'south kivu': 'Democratic Republic of Congo',
    'ituri': 'Democratic Republic of Congo', 'kasai': 'Democratic Republic of Congo',
    'katanga': 'Democratic Republic of Congo', 'maniema': 'Democratic Republic of Congo',
    # Mali
    'mopti': 'Mali', 'gao': 'Mali', 'timbuktu': 'Mali', 'kidal': 'Mali', 'segou': 'Mali',
    # Cameroon
    'far north': 'Cameroon', 'northwest region': 'Cameroon', 'southwest region': 'Cameroon',
    # Mozambique
    'cabo delgado': 'Mozambique', 'nampula': 'Mozambique', 'niassa': 'Mozambique',
    # Niger
    'diffa': 'Niger', 'tillaberi': 'Niger', 'tahoua': 'Niger', 'maradi': 'Niger',
    # Burkina Faso
    'sahel': 'Burkina Faso',
    # Egypt
    'sinai': 'Egypt', 'north sinai': 'Egypt', 'south sinai': 'Egypt',
}


# ============================================================================
# INVALID VALUES TO CLEAN
# ============================================================================

# ACLED region codes and other invalid REGION values
INVALID_REGION_VALUES = {
    'est', 'nord', 'sud', 'ouest', 'centre',  # French direction codes
    'lac',  # Lake
    'bay',  # Could be valid for Somalia but often misused
    'car',  # Central African Republic code
    'morning', 'evening', 'night', 'afternoon', 'midnight', 'dawn', 'dusk',  # Time values
    'raid', 'raided', 'attack', 'attacked', 'offensive',  # Action values
    'islamic state',  # Not a region
}

# Valid African regions and states for reference
VALID_REGIONS = {
    # Nigeria
    'borno', 'adamawa', 'yobe', 'katsina', 'zamfara', 'kaduna', 'plateau',
    'niger state', 'benue', 'taraba', 'nasarawa', 'sokoto', 'kebbi',
    # Sudan
    'darfur', 'khartoum', 'kordofan', 'blue nile', 'white nile', 'kassala',
    'north darfur', 'south darfur', 'west darfur', 'east darfur', 'central darfur',
    # South Sudan
    'jonglei', 'unity', 'upper nile', 'lakes state', 'warrap state',
    'equatoria state', 'eastern equatoria', 'western equatoria', 'central equatoria',
    # Somalia
    'lower shabelle', 'middle shabelle', 'banadir', 'gedo', 'lower juba', 'middle juba',
    'hiraan', 'bakool', 'mudug', 'galgaduud', 'nugaal', 'puntland',
    # Ethiopia
    'tigray', 'amhara', 'oromia', 'afar', 'somali region', 'gambella',
    'benishangul-gumuz', 'southern nations',
    # DRC
    'north kivu', 'south kivu', 'ituri', 'kasai', 'katanga', 'maniema',
    # Mali
    'mopti', 'gao', 'timbuktu', 'kidal', 'segou', 'sikasso',
    # Cameroon
    'far north', 'north region', 'northwest region', 'southwest region', 'adamawa region',
    # Mozambique
    'cabo delgado', 'nampula', 'niassa', 'zambezia',
    # Niger
    'diffa', 'tillaberi', 'tahoua', 'maradi', 'agadez',
    # Burkina Faso
    'sahel', 'nord', 'centre-nord', 'est', 'boucle du mouhoun',
    # Egypt
    'sinai', 'north sinai', 'south sinai',
    # Libya
    'tripolitania', 'cyrenaica', 'fezzan', 'benghazi',
    # Chad
    'lac region', 'borno region',
    # CAR
    'bangui', 'ouham', 'ouham-pende', 'nana-grebizi',
    # General
    'lake chad region', 'sahel region', 'horn of africa',
}


# ============================================================================
# DEMONYM TO COUNTRY MAPPING
# ============================================================================

DEMONYM_TO_COUNTRY = {
    # Major African countries
    'nigerian': 'Nigeria', 'nigerians': 'Nigeria',
    'kenyan': 'Kenya', 'kenyans': 'Kenya',
    'ethiopian': 'Ethiopia', 'ethiopians': 'Ethiopia',
    'sudanese': 'Sudan',
    'south sudanese': 'South Sudan',
    'somali': 'Somalia', 'somalis': 'Somalia',
    'congolese': 'Democratic Republic of Congo',
    'cameroonian': 'Cameroon', 'cameroonians': 'Cameroon',
    'malian': 'Mali', 'malians': 'Mali',
    'burkinabe': 'Burkina Faso',
    'nigerien': 'Niger', 'nigeriens': 'Niger',
    'chadian': 'Chad', 'chadians': 'Chad',
    'ugandan': 'Uganda', 'ugandans': 'Uganda',
    'rwandan': 'Rwanda', 'rwandans': 'Rwanda',
    'burundian': 'Burundi', 'burundians': 'Burundi',
    'tanzanian': 'Tanzania', 'tanzanians': 'Tanzania',
    'mozambican': 'Mozambique', 'mozambicans': 'Mozambique',
    'south african': 'South Africa', 'south africans': 'South Africa',
    'zimbabwean': 'Zimbabwe', 'zimbabweans': 'Zimbabwe',
    'egyptian': 'Egypt', 'egyptians': 'Egypt',
    'libyan': 'Libya', 'libyans': 'Libya',
    'tunisian': 'Tunisia', 'tunisians': 'Tunisia',
    'algerian': 'Algeria', 'algerians': 'Algeria',
    'moroccan': 'Morocco', 'moroccans': 'Morocco',
    'senegalese': 'Senegal',
    'ghanaian': 'Ghana', 'ghanaians': 'Ghana',
    'ivorian': 'Ivory Coast', 'ivorians': 'Ivory Coast',
    'liberian': 'Liberia', 'liberians': 'Liberia',
    'sierra leonean': 'Sierra Leone', 'sierra leoneans': 'Sierra Leone',
    'guinean': 'Guinea', 'guineans': 'Guinea',
    'togolese': 'Togo',
    'beninese': 'Benin',
    'gabonese': 'Gabon',
    'angolan': 'Angola', 'angolans': 'Angola',
    'zambian': 'Zambia', 'zambians': 'Zambia',
    'malawian': 'Malawi', 'malawians': 'Malawi',
    'botswanan': 'Botswana', 'botswanans': 'Botswana',
    'namibian': 'Namibia', 'namibians': 'Namibia',
    'eritrean': 'Eritrea', 'eritreans': 'Eritrea',
    'djiboutian': 'Djibouti', 'djiboutians': 'Djibouti',
    'mauritanian': 'Mauritania', 'mauritanians': 'Mauritania',
    'central african': 'Central African Republic',
}


# ============================================================================
# ARMED GROUPS (for PERPETRATOR extraction)
# ============================================================================

ARMED_GROUPS = [
    # Nigeria
    'boko haram', 'iswap', 'islamic state west africa', 'ansaru',
    # Somalia
    'al shabaab', 'al-shabaab', 'alshabaab',
    # DRC
    'adf', 'allied democratic forces', 'm23', 'codeco', 'mai-mai', 'fdlr',
    # Mali/Sahel
    'jnim', 'aqim', 'isgs', 'islamic state greater sahara', 'mujao', 'ansar dine',
    # Sudan
    'rsf', 'rapid support forces', 'janjaweed', 'sla', 'jem', 'spla',
    # South Sudan
    'spla-io', 'white army',
    # CAR
    'anti-balaka', 'seleka', 'ex-seleka', '3r', 'fprc', 'unc',
    # Mozambique
    'ansar al-sunna', 'al-sunnah wa jama\'ah', 'isis mozambique',
    # Burkina Faso
    'vdp', 'volunteers for defense of the homeland',
    # Ethiopia
    'tplf', 'tigray defense forces', 'olf', 'onlf', 'fano',
    # Uganda
    'lra', 'lord\'s resistance army',
    # Libya
    'lna', 'libyan national army', 'haftar forces', 'gna forces',
    # Kenya
    'mrc', 'mombasa republican council',
    # Generic
    'rebels', 'insurgents', 'militants', 'gunmen', 'armed men', 'bandits',
    'armed group', 'militia', 'militiamen', 'unidentified gunmen',
]


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def normalize_text(text: str) -> str:
    """Normalize text for matching."""
    if not text or pd.isna(text):
        return ''
    text = str(text)
    text = unicodedata.normalize('NFC', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def entity_in_text(entity_value: str, text: str, fuzzy: bool = True) -> Tuple[bool, Optional[str]]:
    """Check if entity value appears in text."""
    if not entity_value or pd.isna(entity_value) or str(entity_value) == 'nan':
        return True, None

    entity_value = normalize_text(str(entity_value))
    text = normalize_text(text)

    if not entity_value or not text:
        return True, None

    text_lower = text.lower()
    entities = re.split(r'[;|]', entity_value)

    for entity in entities:
        entity = entity.strip()
        if not entity:
            continue

        entity_lower = entity.lower()

        if entity_lower in text_lower:
            start = text_lower.find(entity_lower)
            matched = text[start:start + len(entity)]
            return True, matched

        if fuzzy:
            entity_words = entity_lower.split()
            if len(entity_words) > 1:
                pattern = r'\b' + r'\b.*?\b'.join(re.escape(w) for w in entity_words) + r'\b'
                match = re.search(pattern, text_lower)
                if match:
                    return True, text[match.start():match.end()]

            entity_simplified = re.sub(r'[-\'\s]', '', entity_lower)
            text_simplified = re.sub(r'[-\'\s]', '', text_lower)
            if entity_simplified in text_simplified:
                return True, entity

    return False, None


def is_valid_region(value: str) -> bool:
    """Check if a REGION value is valid (not an ACLED code or misplaced value)."""
    if not value or pd.isna(value) or str(value).strip() == '':
        return True  # Empty is OK

    value_lower = str(value).lower().strip()

    # Check against invalid values
    if value_lower in INVALID_REGION_VALUES:
        return False

    # Single word that's too short (likely a code)
    if len(value_lower) <= 3 and ' ' not in value_lower:
        return False

    return True


# ============================================================================
# EXTRACTION FUNCTIONS - ENHANCED v3
# ============================================================================

def extract_all_matches(text: str, patterns: List[str], flags=re.IGNORECASE) -> List[str]:
    """Extract all matches for given patterns."""
    matches = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags):
            matches.append(match.group(0))
    return matches


def extract_perpetrator(text: str, existing: str) -> str:
    """Extract perpetrator - ENHANCED with KB armed groups."""
    if existing and str(existing) != 'nan' and existing.strip():
        # Clean trailing comma/semicolon
        existing = existing.rstrip(',;').strip()
        if existing:
            return existing

    text_lower = text.lower()

    # Check KB armed groups
    for group in ARMED_GROUPS:
        if group in text_lower:
            # Find the properly capitalized version in text
            pattern = re.compile(re.escape(group), re.IGNORECASE)
            match = pattern.search(text)
            if match:
                return match.group(0)
            return group.title()

    # Additional patterns
    patterns = [
        r'\b(suicide\s+bomber)\b',
        r'\b(armed\s+(?:men|group|robbers|attackers))\b',
        r'\b(unknown\s+(?:gunmen|attackers|assailants))\b',
        r'\b(unidentified\s+(?:gunmen|attackers|assailants|armed\s+men))\b',
        r'\b(suspected\s+(?:militants|insurgents|terrorists))\b',
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:militants?|fighters?|rebels?|insurgents?)\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)

    return ''


def extract_victim(text: str, existing: str) -> str:
    """Extract victim - ENHANCED."""
    if existing and str(existing) != 'nan' and existing.strip():
        return existing

    patterns = [
        # Specific victims
        r'\b(\d+)\s*(?:civilians?|villagers?|farmers?|herders?|traders?|students?|teachers?|workers?)\b',
        r'\b(?:civilians?|villagers?|residents?|population)\b',
        r'\b(?:farmers?|herders?|pastoralists?|nomads?)\b',
        r'\b(?:women|children|elderly|youths?|students?)\b',
        r'\b(?:refugees?|IDPs?|displaced\s+persons?)\b',
        r'\b(?:humanitarian\s+workers?|aid\s+workers?)\b',
        r'\b(?:journalists?|reporters?|media\s+workers?)\b',
        r'\b(?:health\s+workers?|doctors?|nurses?)\b',
        r'\b(?:religious\s+leader|imam|priest|pastor|sheikh)\b',
        r'\b(?:local\s+chief|traditional\s+leader|village\s+head)\b',
        # Generic
        r'\b(?:people|persons|individuals)\s+(?:were\s+)?(?:killed|murdered|shot|attacked)\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)

    return ''


def extract_casualties(text: str, existing: str) -> str:
    """Extract casualty information - ENHANCED."""
    if existing and str(existing) != 'nan' and existing.strip():
        return existing

    patterns = [
        # Specific death counts
        r'\b(\d+(?:,\d{3})*)\s*(?:people\s+)?(?:were\s+)?(?:killed|dead|died|slain|murdered|massacred)\b',
        r'\b(?:kill(?:ed|ing))\s+(?:at\s+least\s+)?(\d+(?:,\d{3})*)\b',
        r'\b(?:at\s+least\s+)?(\d+(?:,\d{3})*)\s+(?:people\s+)?(?:killed|dead|died)\b',
        r'\b(?:death\s+toll\s+(?:of|reached|rose\s+to))\s+(\d+(?:,\d{3})*)\b',
        r'\b(\d+(?:,\d{3})*)\s+(?:deaths?|fatalities?)\b',
        r'\b(?:claiming|claimed)\s+(\d+(?:,\d{3})*)\s+lives?\b',
        r'\b(?:leaving|left)\s+(\d+(?:,\d{3})*)\s+(?:people\s+)?dead\b',
        # Vague counts
        r'\b(several|many|numerous|multiple|some|few|dozens?\s+of?)\s+(?:people\s+)?(?:were\s+)?(?:killed|dead)\b',
        r'\b(hundreds?|thousands?)\s+(?:of\s+)?(?:people\s+)?(?:killed|dead)\b',
        # Combatant deaths
        r'\b(\d+)\s+(?:soldiers?|troops?|militants?|fighters?|rebels?)\s+(?:were\s+)?killed\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)

    return ''


def extract_injured(text: str, existing: str) -> str:
    """Extract injury information - ENHANCED."""
    if existing and str(existing) != 'nan' and existing.strip():
        return existing

    patterns = [
        # Number + injured
        r'\b(\d+(?:,\d{3})*)\s*(?:people\s+)?(?:were\s+)?(?:injured|wounded|hurt|maimed)\b',
        r'\b(?:injur|wound)(?:ing|ed)\s+(?:at\s+least\s+)?(\d+(?:,\d{3})*)\b',
        r'\b(?:at\s+least\s+)?(\d+(?:,\d{3})*)\s+(?:people\s+)?(?:were\s+)?(?:left\s+)?(?:injured|wounded)\b',
        r'\b(?:leaving|left)\s+(\d+(?:,\d{3})*)\s+(?:people\s+)?(?:injured|wounded)\b',
        # Vague injuries
        r'\b(several|many|numerous|multiple|some|few|dozens?\s+of?)\s+(?:people\s+)?(?:were\s+)?(?:injured|wounded)\b',
        r'\b(injuries|wounds)\s+(?:were\s+)?reported\b',
        r'\b(sustained\s+injuries|suffered\s+injuries|received\s+wounds)\b',
        # Specific injury types
        r'\b(critically\s+injured|seriously\s+wounded|severely\s+hurt)\b',
        r'\b(minor\s+injuries|non-fatal\s+injuries|light\s+wounds)\b',
        # With hospitalization
        r'\b(\d+)\s+(?:were\s+)?(?:hospitalized|taken\s+to\s+hospital|rushed\s+to\s+hospital)\b',
        r'\b(hospitalized|treated\s+for\s+(?:injuries|wounds))\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return ''


def extract_weapon(text: str, existing: str) -> str:
    """Extract weapon information - ENHANCED."""
    if existing and str(existing) != 'nan' and existing.strip():
        return existing

    patterns = [
        # Firearms
        r'\b(AK-?47|kalashnikov|assault\s+rifle|rifle|gun|firearm)\b',
        r'\b(machine\s+gun|submachine\s+gun|automatic\s+weapon)\b',
        r'\b(pistol|handgun|revolver)\b',
        r'\b(shotgun|sniper\s+rifle)\b',
        # Explosives
        r'\b(IED|improvised\s+explosive\s+device|roadside\s+bomb)\b',
        r'\b(car\s+bomb|VBIED|vehicle-borne\s+(?:explosive|bomb))\b',
        r'\b(suicide\s+(?:bomb|vest|belt))\b',
        r'\b(bomb|explosive|grenade|landmine|mine)\b',
        r'\b(RPG|rocket-propelled\s+grenade|rocket|mortar)\b',
        # Heavy weapons
        r'\b(artillery|tank|armored\s+vehicle|helicopter\s+gunship)\b',
        r'\b(airstrike|air\s+strike|aerial\s+bomb(?:ardment)?)\b',
        # Bladed weapons
        r'\b(machete|knife|dagger|sword|cutlass)\b',
        # Other
        r'\b(bow\s+and\s+arrow|spear|club|stick)\b',
        r'\b(petrol\s+bomb|molotov\s+cocktail|incendiary)\b',
        # Gunfire (generic)
        r'\b(gunfire|small\s+arms|firearms?)\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return ''


def extract_date(text: str, existing: str) -> str:
    """Extract date information - ENHANCED."""
    if existing and str(existing) != 'nan' and existing.strip():
        return existing

    patterns = [
        # Full dates
        r'\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b',
        r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})\b',
        # Month and year
        r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b',
        # Relative dates
        r'\b(on\s+)?(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b',
        r'\b(last\s+)?(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b',
        r'\b(yesterday|today|last\s+(?:week|month|night))\b',
        r'\b((?:this|last|next)\s+(?:week|month|year))\b',
        # Date ranges
        r'\b(between|from)\s+(\d{1,2})\s*(?:-|to|and)\s*(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\b',
        # Abbreviated months
        r'\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+(\d{4})\b',
        # Numeric formats
        r'\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return ''


def extract_time(text: str, existing: str) -> str:
    """Extract time expressions - ENHANCED."""
    if existing and str(existing) != 'nan' and existing.strip():
        return existing

    patterns = [
        # Time of day
        r'\b(early\s+)?morning\b',
        r'\b(late\s+)?afternoon\b',
        r'\b(early\s+)?evening\b',
        r'\b(late\s+)?night\b',
        r'\b(at\s+)?dawn\b',
        r'\b(at\s+)?dusk\b',
        r'\b(around\s+)?midnight\b',
        r'\b(around\s+)?noon\b',
        r'\b(mid-?day)\b',
        r'\b(day\s*time|daytime)\b',
        r'\b(night\s*time|nighttime)\b',
        # Clock times
        r'\b\d{1,2}:\d{2}\s*(?:am|pm|a\.m\.|p\.m\.)\b',
        r'\b\d{1,2}\s*(?:am|pm|a\.m\.|p\.m\.)\b',
        r'\b(?:around|about|approximately)\s+\d{1,2}\s*(?:am|pm|o\'?clock)\b',
        # Relative times
        r'\b(overnight)\b',
        r'\b(predawn)\b',
        r'\b(mid-?morning)\b',
        r'\b(mid-?afternoon)\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return ''


def extract_duration(text: str) -> str:
    """Extract duration information - NEW in v3."""
    patterns = [
        # Time spans
        r'\b(\d+)\s*(?:hours?|hrs?)\s+(?:of\s+)?(?:fighting|clashes?|violence)\b',
        r'\b(?:for|lasted)\s+(\d+)\s*(?:hours?|days?|weeks?|months?)\b',
        r'\b(\d+)-?(?:hour|day|week|month)\s+(?:long\s+)?(?:battle|siege|attack|conflict)\b',
        # Ongoing
        r'\b(ongoing|continuing|sustained)\s+(?:fighting|violence|conflict)\b',
        r'\b(?:fighting|clashes?)\s+(continued|resumed|persisted)\b',
        # Relative duration
        r'\b(brief|prolonged|extended|lengthy)\s+(?:fighting|battle|exchange)\b',
        r'\b(?:several|few|many)\s+(?:hours?|days?)\s+(?:of\s+)?(?:fighting|violence)\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return ''


def extract_frequency(text: str) -> str:
    """Extract frequency information - NEW in v3."""
    patterns = [
        # Repeated events
        r'\b(daily|weekly|monthly|regular)\s+(?:attacks?|incidents?|violence)\b',
        r'\b(repeated|recurring|frequent)\s+(?:attacks?|incidents?|violence)\b',
        r'\b(another|yet\s+another|second|third)\s+(?:attack|incident)\b',
        r'\b(\d+)\s+(?:separate|different)\s+(?:attacks?|incidents?)\b',
        r'\b(series\s+of|wave\s+of|spate\s+of)\s+(?:attacks?|incidents?|violence)\b',
        # Sporadic
        r'\b(sporadic|intermittent|occasional)\s+(?:fighting|violence|attacks?)\b',
        r'\b(multiple|several|numerous)\s+(?:attacks?|incidents?)\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return ''


def extract_district(text: str) -> str:
    """Extract district information - NEW in v3."""
    patterns = [
        # LGA pattern (Nigeria)
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:local\s+government\s+area|LGA)\b',
        # District pattern
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+district\b',
        # County pattern
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+county\b',
        # Ward pattern
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+ward\b',
        # Commune/Municipality
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:commune|municipality|sub-county)\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return ''


def extract_region(text: str, existing: str) -> str:
    """Extract region/state names - ENHANCED with validation."""
    # If existing is invalid, clear it
    if existing and not is_valid_region(existing):
        existing = ''

    if existing and str(existing) != 'nan' and existing.strip():
        return existing

    # Check for known conflict zones first
    for country, info in AFRICAN_COUNTRIES.items():
        for zone in info.get('conflict_zones', []):
            if zone.lower() in text.lower():
                return zone

    patterns = [
        # State/Province patterns
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:state|province|region|prefecture|governorate)\b',
        # Directional regions
        r'\b(north(?:ern)?|south(?:ern)?|east(?:ern)?|west(?:ern)?|central)\s+([A-Z][a-z]+)\s+(?:state|region|province)\b',
        # Specific regions
        r'\b(North\s+Kivu|South\s+Kivu|Cabo\s+Delgado|Lake\s+Chad\s+region)\b',
        r'\b(Sahel|Darfur|Tigray|Oromia|Amhara|Borno|Lower\s+Shabelle|Middle\s+Shabelle)\b',
        r'\b(Horn\s+of\s+Africa|Great\s+Lakes\s+region)\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result = match.group(0)
            # Validate result is not too short
            if len(result) > 3:
                return result
    return ''


def extract_facility(text: str, existing: str) -> str:
    """Extract facility names - ENHANCED."""
    if existing and str(existing) != 'nan' and existing.strip():
        return existing

    patterns = [
        # Military
        r'\b(military\s+base|army\s+base|air\s*base|naval\s+base|garrison|barracks|outpost|military\s+camp)\b',
        r'\b(military\s+headquarters|army\s+headquarters|command\s+post)\b',
        # Security
        r'\b(police\s+station|police\s+post|police\s+headquarters|checkpoint|security\s+post)\b',
        r'\b(prison|jail|detention\s+center|detention\s+facility|correctional\s+facility)\b',
        # Religious
        r'\b(church|cathedral|chapel|mosque|masjid|temple|shrine|synagogue)\b',
        # Educational
        r'\b(school|university|college|academy|madrasa|primary\s+school|secondary\s+school)\b',
        # Medical
        r'\b(hospital|clinic|health\s+center|medical\s+center|dispensary)\b',
        # Commercial
        r'\b(market|marketplace|shopping\s+center|mall|bank|hotel)\b',
        # Camps
        r'\b(refugee\s+camp|IDP\s+camp|displacement\s+camp|camp\s+for\s+displaced)\b',
        r'\b(mining\s+site|oil\s+facility|gas\s+facility|power\s+plant)\b',
        # Government
        r'\b(government\s+building|parliament|presidential\s+palace|ministry|embassy|consulate)\b',
        r'\b(town\s+hall|municipal\s+building|city\s+hall|courthouse)\b',
        # Infrastructure
        r'\b(bridge|road|highway|airport|airfield|port|bus\s+station|train\s+station)\b',
        # Residential
        r'\b(village|hamlet|settlement|compound|residential\s+area)\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return ''


def extract_organization(text: str, existing: str) -> str:
    """Extract organization names - ENHANCED."""
    if existing and str(existing) != 'nan' and existing.strip():
        return existing

    patterns = [
        # International organizations
        r'\b(United\s+Nations|UN)\b',
        r'\b(African\s+Union|AU)\b',
        r'\b(European\s+Union|EU)\b',
        r'\b(ECOWAS|IGAD|SADC|EAC|CEMAC)\b',
        # Humanitarian
        r'\b(Red\s+Cross|ICRC|Red\s+Crescent)\b',
        r'\b(MSF|Médecins\s+Sans\s+Frontières|Doctors\s+Without\s+Borders)\b',
        r'\b(UNHCR|UNICEF|WHO|WFP|FAO|UNDP|OCHA)\b',
        r'\b(Oxfam|Save\s+the\s+Children|World\s+Vision|CARE)\b',
        r'\b(Amnesty\s+International|Human\s+Rights\s+Watch|HRW)\b',
        # Peacekeeping
        r'\b(MINUSMA|MINUSCA|MONUSCO|UNMISS|AMISOM|ATMIS)\b',
        r'\b(peacekeeping\s+force|peacekeepers)\b',
        # Media
        r'\b(Reuters|AFP|AP|BBC|Al\s*Jazeera|France\s*24)\b',
        # NGOs (generic)
        r'\b(NGO|humanitarian\s+organization|aid\s+organization|relief\s+agency)\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return ''


def extract_government(text: str, existing: str) -> str:
    """Extract government/military entities - ENHANCED."""
    if existing and str(existing) != 'nan' and existing.strip():
        return existing

    patterns = [
        # Military
        r'\b([A-Z][a-z]+(?:ian|ese|i)?)\s+(?:army|military|armed\s+forces|defense\s+forces)\b',
        r'\b(national\s+army|state\s+army|government\s+(?:army|forces|troops|soldiers))\b',
        r'\b(military|army|soldiers|troops)\b',
        # Police/Security
        r'\b([A-Z][a-z]+(?:ian|ese|i)?)\s+(?:police|security\s+forces|gendarmerie)\b',
        r'\b(national\s+police|state\s+police|riot\s+police|security\s+forces)\b',
        # Government
        r'\b([A-Z][a-z]+(?:ian|ese|i)?)\s+government\b',
        r'\b(federal\s+government|state\s+government|local\s+government)\b',
        r'\b(authorities|officials|administration)\b',
        # Specific units
        r'\b(special\s+forces|elite\s+forces|rapid\s+response|counter-?terrorism)\b',
        r'\b(presidential\s+guard|republican\s+guard|national\s+guard)\b',
        r'\b(paramilitary|militia|vigilante)\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return ''


def extract_target(text: str, existing: str) -> str:
    """Extract target entities - ENHANCED v4."""
    if existing and str(existing) != 'nan' and existing.strip():
        return existing

    patterns = [
        # Infrastructure targets
        r'\b(targeted?|struck|hit)\s+(the\s+)?([a-z]+\s+)?(base|camp|facility|building|compound)\b',
        r'\b(attacked?\s+(?:the\s+)?(?:a\s+)?)(military\s+base|police\s+station|checkpoint|school|hospital|church|mosque|market)\b',
        # People as targets - v4 expanded
        r'\b(targeting|targeted)\s+([a-z]+\s+)?(civilians?|villagers?|residents?|population)\b',
        r'\b(aimed\s+at|directed\s+at|focused\s+on)\s+(.+?)\b',
        r'\b(attack(?:ed|ing)?\s+(?:on\s+)?)(civilians?|villagers?|herders?|farmers?|traders?)\b',
        r'\b(killed?|murder(?:ed|ing)?)\s+(civilians?|villagers?|innocents?)\b',
        # Ethnic/Religious targets - v4 new
        r'\b((?:ethnic|religious)\s+(?:group|community|minority))\b',
        r'\b((?:Fulani|Hausa|Yoruba|Igbo|Tuareg|Arab|Dinka|Nuer)\s+(?:herders?|farmers?|people|community))\b',
        # Convoys and vehicles
        r'\b(convoy|vehicle|truck|bus|car|patrol)\s+(was\s+)?(targeted|attacked|ambushed)\b',
        r'\b(targeted?|attacked?)\s+(a\s+)?(convoy|vehicle|patrol|motorcade)\b',
        r'\b(ambushed?\s+(?:a\s+)?)(convoy|vehicle|patrol|group)\b',
        # Groups as targets - v4 new
        r'\b(peacekeepers?|humanitarian\s+workers?|aid\s+workers?|journalists?)\b',
        r'\b(government\s+officials?|politicians?|traditional\s+leaders?)\b',
        r'\b(soldiers?|troops?|police\s+officers?|security\s+personnel)\b',
        # Location-based targets - v4 new
        r'\b(village(?:rs?)?|town|community|settlement)\s+(?:was\s+)?(?:attacked|targeted|raided)\b',
        r'\b(attacked?\s+(?:the\s+)?(?:a\s+)?)(village|town|community|settlement)\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return ''


def extract_violence_type(text: str, existing: str) -> str:
    """Extract violence type - ENHANCED."""
    if existing and str(existing) != 'nan' and existing.strip():
        return existing

    patterns = [
        # Attack types
        r'\b(armed\s+attack|gun\s+attack|knife\s+attack|machete\s+attack)\b',
        r'\b(terrorist\s+attack|suicide\s+attack|bomb\s+attack|car\s+bomb)\b',
        r'\b(ambush|raid|assault|offensive|incursion|invasion)\b',
        r'\b(massacre|genocide|ethnic\s+cleansing|pogrom)\b',
        # Violence categories
        r'\b(armed\s+conflict|civil\s+war|insurgency|rebellion|uprising)\b',
        r'\b(communal\s+violence|ethnic\s+violence|religious\s+violence)\b',
        r'\b(inter-?communal|inter-?ethnic|sectarian)\s+(?:violence|conflict|clashes?)\b',
        r'\b(gender-?based\s+violence|sexual\s+violence|rape)\b',
        # Criminal violence
        r'\b(banditry|robbery|kidnapping|extortion|cattle\s+rustling)\b',
        r'\b(gang\s+violence|criminal\s+violence|organized\s+crime)\b',
        # Specific tactics
        r'\b(IED|improvised\s+explosive|landmine|booby\s+trap)\b',
        r'\b(shelling|artillery\s+fire|mortar\s+attack|rocket\s+attack)\b',
        r'\b(airstrike|air\s+strike|bombing\s+raid|drone\s+strike)\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return ''


def extract_displacement(text: str, existing: str) -> str:
    """Extract displacement information - ENHANCED v4."""
    if existing and str(existing) != 'nan' and existing.strip():
        return existing

    patterns = [
        # Numbers displaced
        r'\b(\d+(?:,\d{3})*)\s*(?:people\s+)?(?:were\s+)?(?:displaced|fled|evacuated|uprooted)\b',
        r'\b(?:displac|evacuat)(?:ing|ed)\s+(?:at\s+least\s+)?(\d+(?:,\d{3})*)\b',
        r'\b(?:forcing|caused|led)\s+(\d+(?:,\d{3})*)\s+(?:people\s+)?to\s+flee\b',
        r'\b(\d+(?:,\d{3})*)\s+(?:people\s+)?(?:have\s+)?fled\b',
        # Vague displacement
        r'\b(thousands|hundreds|tens\s+of\s+thousands|millions?)\s+(?:of\s+)?(?:people\s+)?(?:were\s+)?(?:displaced|fled)\b',
        r'\b(mass\s+displacement|massive\s+displacement|large-scale\s+displacement)\b',
        r'\b(mass\s+exodus|mass\s+flight|mass\s+migration)\b',
        # Refugee/IDP terms
        r'\b(refugees?|IDPs?|internally\s+displaced\s+persons?)\b',
        r'\b(displaced\s+persons?|displaced\s+people|displaced\s+population)\b',
        r'\b(asylum\s+seekers?|forcibly\s+displaced)\b',
        # Fleeing actions - v4 expanded
        r'\b(fled\s+(?:their\s+)?homes?|abandoned\s+(?:their\s+)?(?:homes?|villages?))\b',
        r'\b(sought\s+refuge|took\s+refuge|seeking\s+shelter)\b',
        r'\b(crossed\s+(?:the\s+)?border|fled\s+(?:to|across|into|from))\b',
        r'\b(escape(?:d)?(?:\s+(?:from|to|into))?)\b',
        r'\b(villagers?\s+(?:have\s+)?fled)\b',
        r'\b(people\s+fled)\b',
        r'\b(residents?\s+(?:have\s+)?fled)\b',
        r'\b(civilians?\s+(?:have\s+)?fled)\b',
        r'\b(families?\s+(?:have\s+)?fled)\b',
        # Camp references
        r'\b((?:in|to|at)\s+(?:refugee|IDP|displacement)\s+camps?)\b',
        # Forced movement - v4 new
        r'\b(forced\s+to\s+(?:flee|leave|evacuate))\b',
        r'\b(driven\s+(?:out|away|from))\b',
        r'\b(uprooted\s+(?:from\s+)?(?:their\s+)?(?:homes?|villages?))\b',
        r'\b(left\s+(?:their\s+)?(?:homes?|villages?)\s+(?:behind)?)\b',
        r'\b(ran\s+(?:away|for\s+(?:their\s+)?lives?))\b',
        # Returnees and internal movement
        r'\b(returnees?|returning\s+(?:refugees?|displaced))\b',
        r'\b(internal(?:ly)?\s+displaced)\b',
        # Humanitarian crisis indicators
        r'\b(humanitarian\s+crisis|displacement\s+crisis)\b',
        r'\b(population\s+(?:movement|displacement|exodus))\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return ''


def extract_damage(text: str, existing: str) -> str:
    """Extract damage information - ENHANCED."""
    if existing and str(existing) != 'nan' and existing.strip():
        return existing

    patterns = [
        # Property destruction
        r'\b(destroyed|burned|razed|demolished|damaged)\s+(\d+\s+)?(?:homes?|houses?|buildings?|shops?|stores?)\b',
        r'\b(\d+)\s+(?:homes?|houses?|buildings?|structures?)\s+(?:were\s+)?(?:destroyed|burned|damaged)\b',
        # Infrastructure damage
        r'\b(destroyed|damaged|burned)\s+(?:the\s+)?(?:school|hospital|church|mosque|market|bridge)\b',
        # Vehicle destruction
        r'\b(\d+)\s+(?:vehicles?|cars?|trucks?|buses?)\s+(?:were\s+)?(?:destroyed|burned|damaged)\b',
        # Looting
        r'\b(looted|pillaged|ransacked|plundered)\b',
        r'\b(property\s+(?:was\s+)?(?:destroyed|damaged|stolen|looted))\b',
        # Fire/Arson
        r'\b(set\s+(?:on\s+)?fire|burned\s+down|torched|arson)\b',
        # General destruction
        r'\b(widespread\s+destruction|extensive\s+damage|significant\s+damage)\b',
        r'\b(infrastructure\s+(?:was\s+)?(?:destroyed|damaged))\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return ''


def extract_motive(text: str, existing: str) -> str:
    """Extract motive/reason - ENHANCED."""
    if existing and str(existing) != 'nan' and existing.strip():
        return existing

    patterns = [
        # Retaliation
        r'\b(?:in\s+)?(?:retaliation|revenge|response|reprisal)\s+(?:for|to|against)?\b',
        r'\b(retaliatory\s+(?:attack|strike|action))\b',
        r'\b(revenge\s+(?:attack|killing|raid))\b',
        # Conflict types
        r'\b(ethnic|religious|political|territorial|tribal|sectarian)\s+(?:conflict|tension|dispute|violence|clashes?)\b',
        r'\b(inter-?communal|inter-?ethnic|inter-?tribal)\s+(?:conflict|violence|clashes?)\b',
        # Specific motives
        r'\b(land\s+dispute|land\s+conflict|land\s+grab)\b',
        r'\b(resource\s+conflict|resource\s+competition|water\s+dispute)\b',
        r'\b(cattle\s+(?:rustling|raiding|theft)|livestock\s+(?:theft|raiding))\b',
        r'\b(power\s+struggle|political\s+rivalry|succession\s+dispute)\b',
        r'\b(border\s+dispute|territorial\s+dispute)\b',
        # Ideological
        r'\b(jihad(?:ist)?|holy\s+war|religious\s+extremism)\b',
        r'\b(separatist|secessionist|independence\s+movement)\b',
        # Economic
        r'\b(extortion|ransom|kidnapping\s+for\s+ransom|banditry)\b',
        r'\b(control\s+(?:of|over)\s+(?:territory|resources|trade\s+routes))\b',
        # Phrases indicating motive
        r'\b(believed\s+to\s+be\s+motivated\s+by)\b',
        r'\b(in\s+connection\s+with|linked\s+to|related\s+to)\b',
        r'\b(sparked\s+by|triggered\s+by|provoked\s+by)\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return ''


def extract_trigger(text: str, existing: str) -> str:
    """Extract trigger events - ENHANCED."""
    if existing and str(existing) != 'nan' and existing.strip():
        return existing

    patterns = [
        # Triggering events
        r'\b(sparked\s+by|triggered\s+by|provoked\s+by|caused\s+by)\s+(.+?)(?:\.|,)\b',
        r'\b(following|after)\s+(an?\s+)?(?:attack|killing|murder|death|arrest)\b',
        r'\b(in\s+(?:the\s+)?wake\s+of|in\s+(?:the\s+)?aftermath\s+of)\b',
        # Disputes that triggered violence
        r'\b(dispute\s+(?:over|about)|disagreement\s+(?:over|about))\b',
        r'\b(argument\s+(?:over|about)|quarrel\s+(?:over|about))\b',
        # Elections
        r'\b(election-?related|post-?election|pre-?election)\b',
        r'\b((?:during|after|before)\s+(?:the\s+)?elections?)\b',
        # Other triggers
        r'\b(allegations?\s+of|accusations?\s+of|claims?\s+of)\b',
        r'\b(rumors?\s+(?:of|about)|reports?\s+(?:of|about))\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return ''


def extract_action(text: str, existing: str) -> str:
    """Extract action verbs - ENHANCED."""
    if existing and str(existing) != 'nan' and existing.strip():
        return existing

    patterns = [
        # Attack verbs
        r'\b(attacked|raided|ambushed|stormed|assaulted|invaded|overran)\b',
        r'\b(struck|hit|targeted|engaged)\b',
        # Killing verbs
        r'\b(killed|murdered|executed|assassinated|shot|slaughtered|massacred)\b',
        r'\b(beheaded|decapitated|lynched|hanged)\b',
        # Explosive attacks
        r'\b(bombed|shelled|blasted|detonated|exploded)\b',
        # Destruction
        r'\b(burned|torched|razed|destroyed|demolished|looted|pillaged)\b',
        # Capture/Abduction
        r'\b(abducted|kidnapped|captured|seized|detained|arrested|took\s+hostage)\b',
        # Movement
        r'\b(invaded|occupied|retreated|withdrew|advanced|surrounded|besieged)\b',
        # Clashes
        r'\b(clashed|fought|battled|exchanged\s+fire|engaged\s+in\s+combat)\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return ''


def infer_country_from_city(city: str) -> str:
    """Infer country from city name using CITY_TO_COUNTRY mapping."""
    if not city or pd.isna(city) or str(city).strip() == '':
        return ''

    city_lower = str(city).lower().strip()

    # Direct lookup
    if city_lower in CITY_TO_COUNTRY:
        return CITY_TO_COUNTRY[city_lower]

    # Try without common suffixes
    for suffix in [' town', ' city', ' village']:
        if city_lower.endswith(suffix):
            base = city_lower[:-len(suffix)]
            if base in CITY_TO_COUNTRY:
                return CITY_TO_COUNTRY[base]

    return ''


def infer_country_from_region(region: str) -> str:
    """Infer country from region name using REGION_TO_COUNTRY mapping."""
    if not region or pd.isna(region) or str(region).strip() == '':
        return ''

    region_lower = str(region).lower().strip()

    # Direct lookup
    if region_lower in REGION_TO_COUNTRY:
        return REGION_TO_COUNTRY[region_lower]

    # Try without common suffixes
    for suffix in [' state', ' region', ' province']:
        if region_lower.endswith(suffix):
            base = region_lower[:-len(suffix)]
            if base in REGION_TO_COUNTRY:
                return REGION_TO_COUNTRY[base]

    return ''


def extract_country_from_text(text: str, existing_country: str) -> str:
    """Extract country - ENHANCED with demonym support."""
    if existing_country and str(existing_country) != 'nan' and existing_country.strip():
        return existing_country

    text_lower = text.lower()

    # Check demonyms first (Nigerian -> Nigeria)
    for demonym, country in DEMONYM_TO_COUNTRY.items():
        if demonym in text_lower:
            return country

    # Check country names
    for country in AFRICAN_COUNTRIES.keys():
        if country.lower() in text_lower:
            return country.title()

    # Additional country name variations
    country_variations = {
        'drc': 'Democratic Republic of Congo',
        'dr congo': 'Democratic Republic of Congo',
        'democratic republic of the congo': 'Democratic Republic of Congo',
        'car': 'Central African Republic',
        'rsa': 'South Africa',
        'cote d\'ivoire': 'Ivory Coast',
        'côte d\'ivoire': 'Ivory Coast',
    }
    for variant, country in country_variations.items():
        if variant in text_lower:
            return country

    return ''


def infer_country(row: pd.Series, text: str) -> str:
    """Infer country from all available sources."""
    # 1. Try existing COUNTRY value
    existing = row.get('COUNTRY', '')
    if existing and str(existing) != 'nan' and existing.strip():
        return existing

    # 2. Try to extract from text
    country = extract_country_from_text(text, '')
    if country:
        return country

    # 3. Try to infer from CITY
    city = row.get('CITY', '')
    country = infer_country_from_city(city)
    if country:
        return country

    # 4. Try to infer from REGION
    region = row.get('REGION', '')
    country = infer_country_from_region(region)
    if country:
        return country

    return ''


def enhance_row(row: pd.Series) -> pd.Series:
    """Enhance a single row with additional entity extractions."""
    text = str(row.get('Event_Description', ''))

    # Clean and extract entities
    row['PERPETRATOR'] = extract_perpetrator(text, row.get('PERPETRATOR', ''))
    row['VICTIM'] = extract_victim(text, row.get('VICTIM', ''))
    row['CASUALTIES'] = extract_casualties(text, row.get('CASUALTIES', ''))
    row['INJURED'] = extract_injured(text, row.get('INJURED', ''))
    row['WEAPON'] = extract_weapon(text, row.get('WEAPON', ''))
    row['DATE'] = extract_date(text, row.get('DATE', ''))
    row['TIME'] = extract_time(text, row.get('TIME', ''))
    row['DURATION'] = extract_duration(text)
    row['FREQUENCY'] = extract_frequency(text)
    row['REGION'] = extract_region(text, row.get('REGION', ''))
    row['DISTRICT'] = extract_district(text)
    row['FACILITY'] = extract_facility(text, row.get('FACILITY', ''))
    row['ORGANIZATION'] = extract_organization(text, row.get('ORGANIZATION', ''))
    row['GOVERNMENT'] = extract_government(text, row.get('GOVERNMENT', ''))
    row['TARGET'] = extract_target(text, row.get('TARGET', ''))
    row['VIOLENCE_TYPE'] = extract_violence_type(text, row.get('VIOLENCE_TYPE', ''))
    row['DISPLACEMENT'] = extract_displacement(text, row.get('DISPLACEMENT', ''))
    row['DAMAGE'] = extract_damage(text, row.get('DAMAGE', ''))
    row['MOTIVE'] = extract_motive(text, row.get('MOTIVE', ''))
    row['TRIGGER'] = extract_trigger(text, row.get('TRIGGER', ''))
    row['ACTION'] = extract_action(text, row.get('ACTION', ''))

    # Use comprehensive country inference (text, city, region)
    row['COUNTRY'] = infer_country(row, text)

    return row


# ============================================================================
# MAIN PROCESSING
# ============================================================================

def enhance_and_validate_csv(input_file: str, output_file: str, clean_invalid: bool = True):
    """Enhance CSV with additional entity columns and validate/clean existing ones."""
    print(f"Loading {input_file}...")
    df = pd.read_csv(input_file)
    print(f"Loaded {len(df)} rows")

    # Ensure all columns exist
    all_columns = [
        'Event_ID', 'Event_Description', 'Quality_Score',
        'PERPETRATOR', 'VICTIM', 'TARGET', 'ORGANIZATION', 'GOVERNMENT',
        'EVENT_TYPE', 'ACTION', 'WEAPON', 'VIOLENCE_TYPE',
        'DATE', 'TIME', 'DURATION', 'FREQUENCY',
        'COUNTRY', 'REGION', 'CITY', 'DISTRICT', 'FACILITY', 'GEOGRAPHIC', 'COORDINATES',
        'CASUALTIES', 'INJURED', 'DISPLACEMENT', 'DAMAGE',
        'MOTIVE', 'TRIGGER'
    ]

    for col in all_columns:
        if col not in df.columns:
            df[col] = ''

    # Step 1: Clean invalid REGION values
    print(f"\n=== STEP 1: Cleaning invalid REGION values ===")
    invalid_region_count = 0
    for idx, row in df.iterrows():
        region = row.get('REGION', '')
        if region and not is_valid_region(region):
            df.at[idx, 'REGION'] = ''
            invalid_region_count += 1
    print(f"  Cleaned {invalid_region_count} invalid REGION values")

    # Step 2: Enhance with extractions
    print(f"\n=== STEP 2: Enhancing with entity extractions (v3) ===")
    batch_size = 10000
    for i in range(0, len(df), batch_size):
        end_idx = min(i + batch_size, len(df))
        df.iloc[i:end_idx] = df.iloc[i:end_idx].apply(enhance_row, axis=1)
        print(f"  Enhanced {end_idx}/{len(df)} rows...")

    # Reorder columns
    final_columns = [c for c in all_columns if c in df.columns]
    df = df[final_columns]

    print(f"\nSaving to {output_file}...")
    df.to_csv(output_file, index=False)

    # Print statistics
    print("\n" + "=" * 60)
    print("ENHANCED CSV STATISTICS (v3)")
    print("=" * 60)
    for col in final_columns[3:]:
        non_empty = df[col].notna() & (df[col] != '') & (df[col].astype(str) != 'nan')
        count = non_empty.sum()
        pct = (count / len(df)) * 100
        print(f"{col:15} {count:6} rows ({pct:5.1f}%)")

    print(f"\nEnhanced CSV saved to: {output_file}")
    return df


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Enhance and validate CSV for NER training (v3)')
    parser.add_argument('--input', required=True, help='Input CSV file')
    parser.add_argument('--output', required=True, help='Output CSV file')
    parser.add_argument('--no-clean', action='store_true',
                        help='Do not clean invalid values')

    args = parser.parse_args()
    enhance_and_validate_csv(args.input, args.output, clean_invalid=not args.no_clean)
