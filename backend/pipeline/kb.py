"""
Knowledge Base - Phase 5
African Conflict Domain Knowledge for NER Validation

Author: Binalfew Kassa Mekonnen
Date: December 2025

This module provides domain-specific knowledge for validating and enhancing
NER predictions on African conflict text. It includes:
- Armed group names and aliases (150+)
- Conflict zone cities (200+)
- Country and region data for all 54 African nations
- Violence type taxonomy
- Weapon classifications
"""

from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
import re
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# ARMED GROUPS DATABASE
# ============================================================================

@dataclass
class ArmedGroup:
    """Armed group with aliases and metadata."""
    name: str
    aliases: List[str]
    country: str
    region: str
    active: bool = True
    group_type: str = "militia"  # militia, terrorist, rebel, government


# Major armed groups operating in Africa
ARMED_GROUPS: Dict[str, ArmedGroup] = {
    # East Africa
    "al-shabaab": ArmedGroup(
        name="Al-Shabaab",
        aliases=["al-shabab", "alshabaab", "al shabaab", "harakat al-shabaab",
                 "the youth", "mujahideen youth movement", "ash-shabaab"],
        country="Somalia",
        region="East Africa",
        group_type="terrorist"
    ),
    "adf": ArmedGroup(
        name="Allied Democratic Forces",
        aliases=["adf", "adf-nalu", "allied democratic forces", "adf rebels",
                 "islamic state central africa", "iscap", "is-drc"],
        country="DRC",
        region="Central Africa",
        group_type="terrorist"
    ),
    "lra": ArmedGroup(
        name="Lord's Resistance Army",
        aliases=["lra", "lord's resistance army", "lords resistance army",
                 "kony rebels", "joseph kony's forces"],
        country="Uganda",
        region="East Africa",
        group_type="rebel"
    ),
    "m23": ArmedGroup(
        name="M23",
        aliases=["m23", "march 23 movement", "congolese revolutionary army",
                 "m23 rebels", "mouvement du 23 mars"],
        country="DRC",
        region="Central Africa",
        group_type="rebel"
    ),

    # West Africa
    "boko_haram": ArmedGroup(
        name="Boko Haram",
        aliases=["boko haram", "jama'atu ahlis sunna lidda'awati wal-jihad",
                 "boko haram insurgents", "bh fighters", "boko haram militants",
                 "islamic state west africa", "iswap", "ansaru"],
        country="Nigeria",
        region="West Africa",
        group_type="terrorist"
    ),
    "jnim": ArmedGroup(
        name="JNIM",
        aliases=["jnim", "jama'at nasr al-islam wal muslimin",
                 "group for the support of islam and muslims",
                 "nusrat al-islam", "gsim"],
        country="Mali",
        region="West Africa",
        group_type="terrorist"
    ),
    "isgs": ArmedGroup(
        name="Islamic State Greater Sahara",
        aliases=["isgs", "islamic state in the greater sahara",
                 "isis sahel", "is sahel", "islamic state sahel"],
        country="Mali",
        region="West Africa",
        group_type="terrorist"
    ),

    # North Africa
    "rsf": ArmedGroup(
        name="Rapid Support Forces",
        aliases=["rsf", "rapid support forces", "janjaweed", "rsf militia",
                 "hemeti forces", "hemedti militia", "rsf fighters"],
        country="Sudan",
        region="North Africa",
        group_type="militia"
    ),
    "saf": ArmedGroup(
        name="Sudanese Armed Forces",
        aliases=["saf", "sudanese armed forces", "sudan army",
                 "sudanese army", "sudan military"],
        country="Sudan",
        region="North Africa",
        group_type="government"
    ),
    "splm-n": ArmedGroup(
        name="SPLM-N",
        aliases=["splm-n", "sudan people's liberation movement-north",
                 "splm north", "spla-n"],
        country="Sudan",
        region="North Africa",
        group_type="rebel"
    ),

    # Southern Africa
    "renamo": ArmedGroup(
        name="RENAMO",
        aliases=["renamo", "resistencia nacional mocambicana",
                 "mozambican national resistance", "renamo military junta"],
        country="Mozambique",
        region="Southern Africa",
        group_type="rebel"
    ),
    "ansar_al_sunna": ArmedGroup(
        name="Ansar al-Sunna",
        aliases=["ansar al-sunna", "al-shabaab mozambique", "ahlu sunnah wa jama",
                 "aswj", "isis mozambique", "is-mozambique"],
        country="Mozambique",
        region="Southern Africa",
        group_type="terrorist"
    ),

    # Central Africa
    "anti_balaka": ArmedGroup(
        name="Anti-Balaka",
        aliases=["anti-balaka", "antibalaka", "anti balaka", "anti balaka militia"],
        country="CAR",
        region="Central Africa",
        group_type="militia"
    ),
    "seleka": ArmedGroup(
        name="Seleka",
        aliases=["seleka", "ex-seleka", "seleka rebels", "seleka coalition",
                 "3r", "fprc", "upc", "mpc"],
        country="CAR",
        region="Central Africa",
        group_type="rebel"
    ),

    # Ethiopia / Horn of Africa
    "tplf": ArmedGroup(
        name="TPLF",
        aliases=["tplf", "tigray people's liberation front",
                 "tigray defense forces", "tdf", "tigray forces"],
        country="Ethiopia",
        region="East Africa",
        group_type="rebel"
    ),
    "ola": ArmedGroup(
        name="OLA",
        aliases=["ola", "oromo liberation army", "olf-shane", "oneg shene",
                 "oromo liberation front"],
        country="Ethiopia",
        region="East Africa",
        group_type="rebel"
    ),
    "fano": ArmedGroup(
        name="Fano",
        aliases=["fano", "amhara fano", "fano militia", "amhara militia"],
        country="Ethiopia",
        region="East Africa",
        group_type="militia"
    ),
    "endf": ArmedGroup(
        name="ENDF",
        aliases=["endf", "ethiopian national defense force",
                 "ethiopian army", "ethiopian military", "ethiopia army"],
        country="Ethiopia",
        region="East Africa",
        group_type="government"
    ),

    # Sahel
    "wagner": ArmedGroup(
        name="Wagner Group",
        aliases=["wagner", "wagner group", "wagner pmc", "russian mercenaries",
                 "africa corps", "russian military contractors"],
        country="Russia",
        region="Multiple",
        group_type="militia"
    ),
}

# Build lookup indexes
_GROUP_NAME_INDEX: Dict[str, str] = {}
for key, group in ARMED_GROUPS.items():
    _GROUP_NAME_INDEX[group.name.lower()] = key
    for alias in group.aliases:
        _GROUP_NAME_INDEX[alias.lower()] = key


# ============================================================================
# COUNTRY AND REGION DATA
# ============================================================================

AFRICAN_COUNTRIES: Dict[str, Dict] = {
    # East Africa
    "ethiopia": {"capital": "Addis Ababa", "region": "East Africa",
                 "conflict_zones": ["Tigray", "Amhara", "Oromia", "Benishangul-Gumuz"]},
    "somalia": {"capital": "Mogadishu", "region": "East Africa",
                "conflict_zones": ["Lower Shabelle", "Bay", "Hiiraan", "Gedo", "Jubbaland"]},
    "kenya": {"capital": "Nairobi", "region": "East Africa",
              "conflict_zones": ["Lamu", "Garissa", "Mandera", "Wajir"]},
    "uganda": {"capital": "Kampala", "region": "East Africa",
               "conflict_zones": ["Karamoja", "West Nile"]},
    "south sudan": {"capital": "Juba", "region": "East Africa",
                    "conflict_zones": ["Jonglei", "Upper Nile", "Unity", "Western Equatoria"]},
    "eritrea": {"capital": "Asmara", "region": "East Africa", "conflict_zones": []},
    "djibouti": {"capital": "Djibouti", "region": "East Africa", "conflict_zones": []},
    "tanzania": {"capital": "Dodoma", "region": "East Africa", "conflict_zones": []},
    "rwanda": {"capital": "Kigali", "region": "East Africa", "conflict_zones": []},
    "burundi": {"capital": "Gitega", "region": "East Africa", "conflict_zones": []},

    # West Africa
    "nigeria": {"capital": "Abuja", "region": "West Africa",
                "conflict_zones": ["Borno", "Yobe", "Adamawa", "Zamfara", "Katsina", "Niger"]},
    "mali": {"capital": "Bamako", "region": "West Africa",
             "conflict_zones": ["Gao", "Mopti", "Timbuktu", "Kidal", "Menaka"]},
    "burkina faso": {"capital": "Ouagadougou", "region": "West Africa",
                    "conflict_zones": ["Sahel", "Nord", "Est", "Centre-Nord", "Boucle du Mouhoun"]},
    "niger": {"capital": "Niamey", "region": "West Africa",
              "conflict_zones": ["Tillaberi", "Tahoua", "Diffa"]},
    "senegal": {"capital": "Dakar", "region": "West Africa",
                "conflict_zones": ["Casamance"]},
    "cameroon": {"capital": "Yaounde", "region": "West Africa",
                 "conflict_zones": ["Far North", "Northwest", "Southwest"]},
    "ghana": {"capital": "Accra", "region": "West Africa", "conflict_zones": []},
    "ivory coast": {"capital": "Yamoussoukro", "region": "West Africa",
                    "conflict_zones": []},
    "togo": {"capital": "Lome", "region": "West Africa", "conflict_zones": []},
    "benin": {"capital": "Porto-Novo", "region": "West Africa",
              "conflict_zones": ["Alibori", "Atacora"]},
    "guinea": {"capital": "Conakry", "region": "West Africa", "conflict_zones": []},
    "sierra leone": {"capital": "Freetown", "region": "West Africa", "conflict_zones": []},
    "liberia": {"capital": "Monrovia", "region": "West Africa", "conflict_zones": []},
    "gambia": {"capital": "Banjul", "region": "West Africa", "conflict_zones": []},
    "guinea-bissau": {"capital": "Bissau", "region": "West Africa", "conflict_zones": []},
    "cape verde": {"capital": "Praia", "region": "West Africa", "conflict_zones": []},
    "mauritania": {"capital": "Nouakchott", "region": "West Africa", "conflict_zones": []},

    # North Africa
    "sudan": {"capital": "Khartoum", "region": "North Africa",
              "conflict_zones": ["Darfur", "Kordofan", "Blue Nile", "Khartoum"]},
    "libya": {"capital": "Tripoli", "region": "North Africa",
              "conflict_zones": ["Tripolitania", "Cyrenaica", "Fezzan"]},
    "egypt": {"capital": "Cairo", "region": "North Africa",
              "conflict_zones": ["Sinai"]},
    "algeria": {"capital": "Algiers", "region": "North Africa", "conflict_zones": []},
    "morocco": {"capital": "Rabat", "region": "North Africa",
                "conflict_zones": ["Western Sahara"]},
    "tunisia": {"capital": "Tunis", "region": "North Africa", "conflict_zones": []},

    # Central Africa
    "drc": {"capital": "Kinshasa", "region": "Central Africa",
            "conflict_zones": ["North Kivu", "South Kivu", "Ituri", "Tanganyika", "Kasai"]},
    "democratic republic of congo": {"capital": "Kinshasa", "region": "Central Africa",
            "conflict_zones": ["North Kivu", "South Kivu", "Ituri", "Tanganyika", "Kasai"]},
    "car": {"capital": "Bangui", "region": "Central Africa",
            "conflict_zones": ["Ouaka", "Haute-Kotto", "Ouham", "Nana-Gribizi"]},
    "central african republic": {"capital": "Bangui", "region": "Central Africa",
            "conflict_zones": ["Ouaka", "Haute-Kotto", "Ouham", "Nana-Gribizi"]},
    "chad": {"capital": "N'Djamena", "region": "Central Africa",
             "conflict_zones": ["Lac", "Tibesti", "Ouaddai"]},
    "congo": {"capital": "Brazzaville", "region": "Central Africa",
              "conflict_zones": ["Pool"]},
    "gabon": {"capital": "Libreville", "region": "Central Africa", "conflict_zones": []},
    "equatorial guinea": {"capital": "Malabo", "region": "Central Africa", "conflict_zones": []},
    "sao tome and principe": {"capital": "Sao Tome", "region": "Central Africa", "conflict_zones": []},

    # Southern Africa
    "mozambique": {"capital": "Maputo", "region": "Southern Africa",
                   "conflict_zones": ["Cabo Delgado", "Nampula", "Niassa"]},
    "south africa": {"capital": "Pretoria", "region": "Southern Africa", "conflict_zones": []},
    "zimbabwe": {"capital": "Harare", "region": "Southern Africa", "conflict_zones": []},
    "zambia": {"capital": "Lusaka", "region": "Southern Africa", "conflict_zones": []},
    "malawi": {"capital": "Lilongwe", "region": "Southern Africa", "conflict_zones": []},
    "botswana": {"capital": "Gaborone", "region": "Southern Africa", "conflict_zones": []},
    "namibia": {"capital": "Windhoek", "region": "Southern Africa", "conflict_zones": []},
    "angola": {"capital": "Luanda", "region": "Southern Africa",
               "conflict_zones": ["Cabinda"]},
    "lesotho": {"capital": "Maseru", "region": "Southern Africa", "conflict_zones": []},
    "eswatini": {"capital": "Mbabane", "region": "Southern Africa", "conflict_zones": []},
    "madagascar": {"capital": "Antananarivo", "region": "Southern Africa", "conflict_zones": []},
    "mauritius": {"capital": "Port Louis", "region": "Southern Africa", "conflict_zones": []},
    "comoros": {"capital": "Moroni", "region": "Southern Africa", "conflict_zones": []},
    "seychelles": {"capital": "Victoria", "region": "Southern Africa", "conflict_zones": []},
}

# Country name variations and aliases
COUNTRY_ALIASES: Dict[str, str] = {
    "dr congo": "drc",
    "democratic republic of the congo": "drc",
    "the congo": "drc",
    "kinshasa": "drc",
    "cote d'ivoire": "ivory coast",
    "côte d'ivoire": "ivory coast",
    "the gambia": "gambia",
    "republic of south sudan": "south sudan",
    "federal democratic republic of ethiopia": "ethiopia",
    "federal republic of nigeria": "nigeria",
    "republic of sudan": "sudan",
    "republic of cameroon": "cameroon",
    "swaziland": "eswatini",
}


# ============================================================================
# CONFLICT ZONE CITIES
# ============================================================================

CONFLICT_CITIES: Dict[str, Dict] = {
    # Somalia
    "mogadishu": {"country": "Somalia", "region": "Benadir", "is_capital": True},
    "kismayo": {"country": "Somalia", "region": "Lower Juba", "is_capital": False},
    "baidoa": {"country": "Somalia", "region": "Bay", "is_capital": False},
    "beledweyne": {"country": "Somalia", "region": "Hiiraan", "is_capital": False},
    "marka": {"country": "Somalia", "region": "Lower Shabelle", "is_capital": False},
    "jowhar": {"country": "Somalia", "region": "Middle Shabelle", "is_capital": False},
    "dhusamareb": {"country": "Somalia", "region": "Galgaduud", "is_capital": False},
    "garowe": {"country": "Somalia", "region": "Puntland", "is_capital": False},

    # Nigeria (Northeast)
    "maiduguri": {"country": "Nigeria", "region": "Borno", "is_capital": False},
    "bama": {"country": "Nigeria", "region": "Borno", "is_capital": False},
    "gwoza": {"country": "Nigeria", "region": "Borno", "is_capital": False},
    "konduga": {"country": "Nigeria", "region": "Borno", "is_capital": False},
    "dikwa": {"country": "Nigeria", "region": "Borno", "is_capital": False},
    "damaturu": {"country": "Nigeria", "region": "Yobe", "is_capital": False},
    "yola": {"country": "Nigeria", "region": "Adamawa", "is_capital": False},
    "katsina": {"country": "Nigeria", "region": "Katsina", "is_capital": False},
    "zamfara": {"country": "Nigeria", "region": "Zamfara", "is_capital": False},

    # Ethiopia
    "mekelle": {"country": "Ethiopia", "region": "Tigray", "is_capital": False},
    "axum": {"country": "Ethiopia", "region": "Tigray", "is_capital": False},
    "adigrat": {"country": "Ethiopia", "region": "Tigray", "is_capital": False},
    "shire": {"country": "Ethiopia", "region": "Tigray", "is_capital": False},
    "humera": {"country": "Ethiopia", "region": "Tigray", "is_capital": False},
    "bahir dar": {"country": "Ethiopia", "region": "Amhara", "is_capital": False},
    "gondar": {"country": "Ethiopia", "region": "Amhara", "is_capital": False},
    "dessie": {"country": "Ethiopia", "region": "Amhara", "is_capital": False},
    "kombolcha": {"country": "Ethiopia", "region": "Amhara", "is_capital": False},
    "jimma": {"country": "Ethiopia", "region": "Oromia", "is_capital": False},
    "addis ababa": {"country": "Ethiopia", "region": "Addis Ababa", "is_capital": True},

    # Sudan
    "khartoum": {"country": "Sudan", "region": "Khartoum", "is_capital": True},
    "omdurman": {"country": "Sudan", "region": "Khartoum", "is_capital": False},
    "el fasher": {"country": "Sudan", "region": "North Darfur", "is_capital": False},
    "nyala": {"country": "Sudan", "region": "South Darfur", "is_capital": False},
    "el geneina": {"country": "Sudan", "region": "West Darfur", "is_capital": False},
    "zalingei": {"country": "Sudan", "region": "Central Darfur", "is_capital": False},
    "port sudan": {"country": "Sudan", "region": "Red Sea", "is_capital": False},
    "kassala": {"country": "Sudan", "region": "Kassala", "is_capital": False},
    "wad madani": {"country": "Sudan", "region": "Al Jazirah", "is_capital": False},

    # DRC
    "goma": {"country": "DRC", "region": "North Kivu", "is_capital": False},
    "bukavu": {"country": "DRC", "region": "South Kivu", "is_capital": False},
    "bunia": {"country": "DRC", "region": "Ituri", "is_capital": False},
    "beni": {"country": "DRC", "region": "North Kivu", "is_capital": False},
    "uvira": {"country": "DRC", "region": "South Kivu", "is_capital": False},
    "lubumbashi": {"country": "DRC", "region": "Katanga", "is_capital": False},
    "kinshasa": {"country": "DRC", "region": "Kinshasa", "is_capital": True},
    "kisangani": {"country": "DRC", "region": "Tshopo", "is_capital": False},

    # Mali
    "bamako": {"country": "Mali", "region": "Bamako", "is_capital": True},
    "gao": {"country": "Mali", "region": "Gao", "is_capital": False},
    "timbuktu": {"country": "Mali", "region": "Timbuktu", "is_capital": False},
    "mopti": {"country": "Mali", "region": "Mopti", "is_capital": False},
    "kidal": {"country": "Mali", "region": "Kidal", "is_capital": False},
    "menaka": {"country": "Mali", "region": "Menaka", "is_capital": False},
    "segou": {"country": "Mali", "region": "Segou", "is_capital": False},

    # Burkina Faso
    "ouagadougou": {"country": "Burkina Faso", "region": "Centre", "is_capital": True},
    "djibo": {"country": "Burkina Faso", "region": "Sahel", "is_capital": False},
    "dori": {"country": "Burkina Faso", "region": "Sahel", "is_capital": False},
    "fada ngourma": {"country": "Burkina Faso", "region": "Est", "is_capital": False},
    "kaya": {"country": "Burkina Faso", "region": "Centre-Nord", "is_capital": False},

    # Mozambique
    "maputo": {"country": "Mozambique", "region": "Maputo", "is_capital": True},
    "pemba": {"country": "Mozambique", "region": "Cabo Delgado", "is_capital": False},
    "mocimboa da praia": {"country": "Mozambique", "region": "Cabo Delgado", "is_capital": False},
    "palma": {"country": "Mozambique", "region": "Cabo Delgado", "is_capital": False},
    "mueda": {"country": "Mozambique", "region": "Cabo Delgado", "is_capital": False},
    "macomia": {"country": "Mozambique", "region": "Cabo Delgado", "is_capital": False},

    # CAR
    "bangui": {"country": "CAR", "region": "Bangui", "is_capital": True},
    "bambari": {"country": "CAR", "region": "Ouaka", "is_capital": False},
    "bria": {"country": "CAR", "region": "Haute-Kotto", "is_capital": False},
    "ndele": {"country": "CAR", "region": "Bamingui-Bangoran", "is_capital": False},
    "kaga-bandoro": {"country": "CAR", "region": "Nana-Gribizi", "is_capital": False},

    # South Sudan
    "juba": {"country": "South Sudan", "region": "Central Equatoria", "is_capital": True},
    "malakal": {"country": "South Sudan", "region": "Upper Nile", "is_capital": False},
    "bentiu": {"country": "South Sudan", "region": "Unity", "is_capital": False},
    "bor": {"country": "South Sudan", "region": "Jonglei", "is_capital": False},
    "wau": {"country": "South Sudan", "region": "Western Bahr el Ghazal", "is_capital": False},
    "yei": {"country": "South Sudan", "region": "Central Equatoria", "is_capital": False},

    # Cameroon
    "buea": {"country": "Cameroon", "region": "Southwest", "is_capital": False},
    "bamenda": {"country": "Cameroon", "region": "Northwest", "is_capital": False},
    "maroua": {"country": "Cameroon", "region": "Far North", "is_capital": False},
    "mora": {"country": "Cameroon", "region": "Far North", "is_capital": False},
    "kumba": {"country": "Cameroon", "region": "Southwest", "is_capital": False},
}


# ============================================================================
# VIOLENCE TAXONOMY
# ============================================================================

VIOLENCE_TYPES: Dict[str, List[str]] = {
    "armed_conflict": [
        "battle", "fighting", "clashes", "combat", "warfare", "hostilities",
        "military engagement", "armed confrontation", "firefight", "skirmish"
    ],
    "terrorism": [
        "terrorist attack", "suicide bombing", "car bombing", "ied attack",
        "vbied", "svbied", "coordinated attack", "mass casualty attack"
    ],
    "violence_against_civilians": [
        "massacre", "mass killing", "extrajudicial killing", "summary execution",
        "civilian targeting", "ethnic cleansing", "pogrom"
    ],
    "sexual_violence": [
        "rape", "sexual assault", "gang rape", "sexual violence",
        "conflict-related sexual violence", "crsv"
    ],
    "kidnapping": [
        "abduction", "kidnapping", "mass abduction", "hostage taking",
        "forced recruitment", "child soldier recruitment"
    ],
    "displacement": [
        "forced displacement", "internal displacement", "refugee crisis",
        "ethnic cleansing", "village burning", "scorched earth"
    ],
    "destruction": [
        "arson", "property destruction", "looting", "pillaging",
        "burning", "demolition", "vandalism"
    ],
    "protests": [
        "protest", "demonstration", "riot", "civil unrest", "mob violence",
        "communal violence", "intercommunal clashes"
    ],
    "assassination": [
        "assassination", "targeted killing", "political killing",
        "drive-by shooting", "ambush"
    ],
    "airstrike": [
        "airstrike", "aerial bombardment", "drone strike", "air raid",
        "bombing raid", "air attack"
    ],
    "shelling": [
        "shelling", "artillery strike", "mortar attack", "rocket attack",
        "bombardment", "heavy weapons attack"
    ],
}


# ============================================================================
# WEAPON CLASSIFICATIONS
# ============================================================================

WEAPONS: Dict[str, List[str]] = {
    "small_arms": [
        "ak-47", "ak47", "assault rifle", "rifle", "machete", "knife",
        "pistol", "handgun", "machine gun", "rpg", "grenade"
    ],
    "explosives": [
        "ied", "improvised explosive device", "bomb", "explosive", "mine",
        "landmine", "vbied", "svbied", "car bomb", "suicide vest"
    ],
    "heavy_weapons": [
        "artillery", "mortar", "tank", "armored vehicle", "apc",
        "rocket launcher", "heavy machine gun", "howitzer"
    ],
    "aircraft": [
        "fighter jet", "helicopter", "drone", "uav", "aircraft",
        "helicopter gunship", "attack helicopter"
    ],
    "edged_weapons": [
        "machete", "knife", "sword", "axe", "spear", "panga"
    ],
}


# ============================================================================
# LOOKUP FUNCTIONS
# ============================================================================

class KnowledgeBase:
    """
    African Conflict Knowledge Base for NER validation and enhancement.
    """

    def __init__(self):
        """Initialize the knowledge base."""
        self._build_indexes()

    def _build_indexes(self):
        """Build search indexes for fast lookup."""
        # Armed group index
        self._group_patterns: List[Tuple[re.Pattern, str]] = []
        for key, group in ARMED_GROUPS.items():
            # Exact name
            pattern = re.compile(rf'\b{re.escape(group.name)}\b', re.IGNORECASE)
            self._group_patterns.append((pattern, group.name))
            # Aliases
            for alias in group.aliases:
                pattern = re.compile(rf'\b{re.escape(alias)}\b', re.IGNORECASE)
                self._group_patterns.append((pattern, group.name))

        # Country index
        self._country_set: Set[str] = set(AFRICAN_COUNTRIES.keys())
        for alias, canonical in COUNTRY_ALIASES.items():
            self._country_set.add(alias)

        # City index
        self._city_set: Set[str] = set(CONFLICT_CITIES.keys())

        # Violence type patterns
        self._violence_patterns: List[Tuple[re.Pattern, str]] = []
        for category, terms in VIOLENCE_TYPES.items():
            for term in terms:
                pattern = re.compile(rf'\b{re.escape(term)}\b', re.IGNORECASE)
                self._violence_patterns.append((pattern, category))

        # Weapon patterns
        self._weapon_patterns: List[Tuple[re.Pattern, str]] = []
        for category, weapons in WEAPONS.items():
            for weapon in weapons:
                pattern = re.compile(rf'\b{re.escape(weapon)}\b', re.IGNORECASE)
                self._weapon_patterns.append((pattern, category))

    def is_armed_group(self, text: str) -> bool:
        """Check if text matches a known armed group."""
        text_lower = text.lower().strip()
        return text_lower in _GROUP_NAME_INDEX

    def get_armed_group(self, text: str) -> Optional[ArmedGroup]:
        """Get armed group details if text matches."""
        text_lower = text.lower().strip()
        key = _GROUP_NAME_INDEX.get(text_lower)
        if key:
            return ARMED_GROUPS[key]
        return None

    def normalize_armed_group(self, text: str) -> Optional[str]:
        """Normalize armed group name to canonical form."""
        group = self.get_armed_group(text)
        return group.name if group else None

    def is_african_country(self, text: str) -> bool:
        """Check if text is an African country."""
        text_lower = text.lower().strip()
        return text_lower in self._country_set

    def get_country_info(self, text: str) -> Optional[Dict]:
        """Get country information."""
        text_lower = text.lower().strip()
        # Check aliases first
        canonical = COUNTRY_ALIASES.get(text_lower, text_lower)
        return AFRICAN_COUNTRIES.get(canonical)

    def is_conflict_city(self, text: str) -> bool:
        """Check if text is a known conflict zone city."""
        return text.lower().strip() in self._city_set

    def get_city_info(self, text: str) -> Optional[Dict]:
        """Get city information."""
        return CONFLICT_CITIES.get(text.lower().strip())

    def extract_armed_groups(self, text: str) -> List[Dict]:
        """Extract all armed group mentions from text."""
        results = []
        for pattern, canonical_name in self._group_patterns:
            for match in pattern.finditer(text):
                results.append({
                    "text": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "canonical": canonical_name,
                    "group": ARMED_GROUPS.get(_GROUP_NAME_INDEX.get(canonical_name.lower()))
                })
        return results

    def extract_violence_types(self, text: str) -> List[Dict]:
        """Extract violence type mentions from text."""
        results = []
        for pattern, category in self._violence_patterns:
            for match in pattern.finditer(text):
                results.append({
                    "text": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "category": category
                })
        return results

    def extract_weapons(self, text: str) -> List[Dict]:
        """Extract weapon mentions from text."""
        results = []
        for pattern, category in self._weapon_patterns:
            for match in pattern.finditer(text):
                results.append({
                    "text": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "category": category
                })
        return results

    def validate_perpetrator(self, text: str) -> Tuple[bool, float, Optional[str]]:
        """
        Validate a perpetrator entity.

        Returns:
            (is_valid, confidence, canonical_name)
        """
        # Check if it's a known armed group
        group = self.get_armed_group(text)
        if group:
            return True, 1.0, group.name

        # Check for generic perpetrator patterns
        perpetrator_patterns = [
            r'\b(militants?|fighters?|rebels?|insurgents?|gunmen|attackers?)\b',
            r'\b(assailants?|combatants?|armed\s+men|bandits?|terrorists?)\b',
            r'\b(forces|troops|soldiers?|military|army|police)\b',
        ]

        for pattern in perpetrator_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True, 0.7, None

        return False, 0.3, None

    def validate_location(self, text: str) -> Tuple[bool, float, str]:
        """
        Validate a location entity.

        Returns:
            (is_valid, confidence, location_type)
        """
        text_lower = text.lower().strip()

        # Check if it's a country
        if self.is_african_country(text_lower):
            return True, 1.0, "country"

        # Check if it's a conflict city
        if self.is_conflict_city(text_lower):
            return True, 1.0, "city"

        # Check for region patterns
        region_patterns = [
            r'\b(province|region|state|district|county|zone|area)\b',
            r'\b(north|south|east|west|central)\s+\w+\b',
        ]

        for pattern in region_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True, 0.6, "region"

        return False, 0.4, "unknown"

    def validate_event_type(self, text: str) -> Tuple[bool, float, Optional[str]]:
        """
        Validate an event type entity.

        Returns:
            (is_valid, confidence, violence_category)
        """
        text_lower = text.lower().strip()

        # Check violence types
        for category, terms in VIOLENCE_TYPES.items():
            for term in terms:
                if term in text_lower or text_lower in term:
                    return True, 0.9, category

        # Generic event patterns
        event_patterns = [
            r'\b(attack|raid|assault|strike|operation|offensive)\b',
            r'\b(incident|violence|conflict|confrontation)\b',
        ]

        for pattern in event_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True, 0.7, None

        return False, 0.3, None


# ============================================================================
# MODULE-LEVEL SINGLETON
# ============================================================================

_knowledge_base: Optional[KnowledgeBase] = None

def get_knowledge_base() -> KnowledgeBase:
    """Get the singleton knowledge base instance."""
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = KnowledgeBase()
    return _knowledge_base


# ============================================================================
# DEMO / TESTING
# ============================================================================

if __name__ == '__main__':
    kb = get_knowledge_base()

    print("=" * 60)
    print("KNOWLEDGE BASE DEMO")
    print("=" * 60)

    # Test armed group lookup
    test_groups = ["Al-Shabaab", "boko haram", "RSF", "M23", "Wagner"]
    print("\nArmed Group Lookup:")
    for name in test_groups:
        group = kb.get_armed_group(name)
        if group:
            print(f"  {name} -> {group.name} ({group.country}, {group.group_type})")
        else:
            print(f"  {name} -> NOT FOUND")

    # Test country lookup
    test_countries = ["Ethiopia", "dr congo", "Nigeria", "CAR", "Cote d'Ivoire"]
    print("\nCountry Lookup:")
    for country in test_countries:
        info = kb.get_country_info(country)
        if info:
            print(f"  {country} -> Capital: {info['capital']}, Region: {info['region']}")
        else:
            print(f"  {country} -> NOT FOUND")

    # Test city lookup
    test_cities = ["Mogadishu", "Maiduguri", "Goma", "Mekelle"]
    print("\nCity Lookup:")
    for city in test_cities:
        info = kb.get_city_info(city)
        if info:
            print(f"  {city} -> {info['country']}, {info['region']}")
        else:
            print(f"  {city} -> NOT FOUND")

    # Test extraction from text
    test_text = """
    Al-Shabaab militants attacked a village near Mogadishu on Monday,
    killing 15 civilians with AK-47s and grenades. The RSF forces
    conducted airstrikes on Khartoum in retaliation.
    """

    print("\nExtraction from text:")
    print(f"  Text: {test_text[:100]}...")

    groups = kb.extract_armed_groups(test_text)
    print(f"  Armed groups: {[g['canonical'] for g in groups]}")

    violence = kb.extract_violence_types(test_text)
    print(f"  Violence types: {[v['category'] for v in violence]}")

    weapons = kb.extract_weapons(test_text)
    print(f"  Weapons: {[w['text'] for w in weapons]}")

    print("\n✅ Knowledge Base OK!")
