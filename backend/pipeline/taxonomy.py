"""
Violent Event Taxonomy Configuration

Based on VIONER_GUIDELINES.md - Hierarchical Violent Event Taxonomy for African Conflicts.

Author: Binalfew Kassa Mekonnen
Date: December 2025

Defines the 4-level taxonomy hierarchy:
- Level 1: 4 broad categories
- Level 2: 18 intermediate types
- Level 3: 40-60 specific types
- Level 4: 80+ detailed subtypes
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum


# ============================================================================
# LEVEL 1: BROAD CATEGORIES (4 types)
# ============================================================================

class TaxonomyL1(Enum):
    """Level 1 - Broad violence categories based on actor type and motivation."""
    POLITICAL_VIOLENCE = "Political Violence"
    CRIMINAL_VIOLENCE = "Criminal Violence"
    COMMUNAL_VIOLENCE = "Communal Violence"
    STATE_VIOLENCE = "State Violence Against Civilians"


# ============================================================================
# LEVEL 2: INTERMEDIATE TYPES (18 types)
# ============================================================================

class TaxonomyL2(Enum):
    """Level 2 - Intermediate violence sub-categories."""
    # Political Violence (6 types)
    TERRORISM = "Terrorism"
    REBELLION_INSURGENCY = "Rebellion/Armed Insurgency"
    COUP_REGIME_CHANGE = "Coup and Regime Change Violence"
    ELECTION_VIOLENCE = "Election Violence"
    POLITICAL_REPRESSION = "Political Repression"
    INTER_STATE_CONFLICT = "Inter-State Conflict"

    # Criminal Violence (4 types)
    ORGANIZED_CRIME = "Organized Crime Violence"
    ARMED_ROBBERY_BANDITRY = "Armed Robbery/Banditry"
    KIDNAPPING_RANSOM = "Kidnapping for Ransom"
    GANG_VIOLENCE = "Criminal Gang Violence"

    # Communal Violence (4 types)
    ETHNIC_TRIBAL = "Ethnic/Tribal Conflict"
    RELIGIOUS_VIOLENCE = "Religious Violence"
    RESOURCE_CONFLICT = "Resource-Based Conflict"
    PASTORALIST_FARMER = "Pastoralist-Farmer Clashes"

    # State Violence Against Civilians (4 types)
    EXTRAJUDICIAL_KILLINGS = "Extrajudicial Killings"
    PROTEST_REPRESSION = "State Repression of Protests"
    MASS_ATROCITIES = "Mass Atrocities by State Forces"
    FORCED_DISPLACEMENT = "Forced Displacement by State"


# ============================================================================
# TAXONOMY HIERARCHY - Complete Structure
# ============================================================================

TAXONOMY_HIERARCHY: Dict[str, Dict[str, List[str]]] = {
    # =========================================================================
    # POLITICAL VIOLENCE
    # =========================================================================
    "Political Violence": {
        "Terrorism": [
            "Bombing/Explosive Attack",
            "Armed Assault",
            "Kidnapping/Hostage-Taking (Terrorism)",
            "Targeted Assassination",
            "Vehicle Attack",
            "Arson Attack",
        ],
        "Rebellion/Armed Insurgency": [
            "Armed Clash/Battle",
            "Ambush",
            "Rebel Attack on Government Position",
            "Territory Capture",
            "Siege/Encirclement",
            "Hit-and-Run Attack",
        ],
        "Coup and Regime Change Violence": [
            "Military Coup",
            "Palace Coup",
            "Counter-Coup",
            "Coup-Related Clashes",
        ],
        "Election Violence": [
            "Pre-Election Violence",
            "Election-Day Violence",
            "Post-Election Violence",
            "Political Assassination",
        ],
        "Political Repression": [
            "Targeted Arrest with Violence",
            "Disappearance",
            "Political Imprisonment",
            "Suppression of Opposition",
        ],
        "Inter-State Conflict": [
            "Cross-Border Attack",
            "Territorial Dispute Combat",
            "Military Incursion",
            "Air/Drone Strike",
        ],
    },

    # =========================================================================
    # CRIMINAL VIOLENCE
    # =========================================================================
    "Criminal Violence": {
        "Organized Crime Violence": [
            "Drug-Related Violence",
            "Trafficking Violence",
            "Smuggling Violence",
            "Extortion Violence",
        ],
        "Armed Robbery/Banditry": [
            "Highway Robbery",
            "Village Raid",
            "Cattle Rustling",
            "Market Robbery",
        ],
        "Kidnapping for Ransom": [
            "Individual Kidnapping",
            "Mass Kidnapping",
            "School Kidnapping",
            "Traveler Abduction",
        ],
        "Criminal Gang Violence": [
            "Gang Clash",
            "Vigilante Attack",
            "Mob Justice",
            "Criminal Assassination",
        ],
    },

    # =========================================================================
    # COMMUNAL VIOLENCE
    # =========================================================================
    "Communal Violence": {
        "Ethnic/Tribal Conflict": [
            "Ethnic Clash",
            "Tribal Warfare",
            "Revenge Attack",
            "Land Dispute Violence",
        ],
        "Religious Violence": [
            "Sectarian Clash",
            "Anti-Religious Attack",
            "Religious Site Attack",
            "Forced Conversion Violence",
        ],
        "Resource-Based Conflict": [
            "Water Conflict",
            "Mining Conflict",
            "Land Access Conflict",
            "Forest Resource Conflict",
        ],
        "Pastoralist-Farmer Clashes": [
            "Grazing Conflict",
            "Crop Destruction Retaliation",
            "Water Source Conflict",
            "Seasonal Migration Violence",
        ],
    },

    # =========================================================================
    # STATE VIOLENCE AGAINST CIVILIANS
    # =========================================================================
    "State Violence Against Civilians": {
        "Extrajudicial Killings": [
            "Summary Execution",
            "Death Squad Operation",
            "Custodial Death",
            "Targeted Killing",
        ],
        "State Repression of Protests": [
            "Protest Crackdown",
            "Demonstration Dispersal",
            "Strike Breaking",
            "Civil Unrest Suppression",
        ],
        "Mass Atrocities by State Forces": [
            "Massacre",
            "Village Burning",
            "Collective Punishment",
            "Ethnic Cleansing",
        ],
        "Forced Displacement by State": [
            "Eviction with Violence",
            "Resettlement Violence",
            "Buffer Zone Creation",
            "Population Transfer",
        ],
    },
}


# ============================================================================
# LEVEL 4: DETAILED SUBTYPES
# ============================================================================

TAXONOMY_L4: Dict[str, List[str]] = {
    # Terrorism subtypes
    "Bombing/Explosive Attack": [
        "Suicide Bombing",
        "Car/Vehicle Bombing (VBIED)",
        "Roadside IED",
        "Building Bombing",
        "Market Bombing",
        "Mosque/Church Bombing",
    ],
    "Armed Assault": [
        "Mass Shooting/Rampage",
        "Coordinated Multi-Site Attack",
        "Single-Target Attack",
        "School/University Attack",
    ],
    "Kidnapping/Hostage-Taking (Terrorism)": [
        "Hostage Situation",
        "Mass Abduction",
        "Hijacking",
    ],

    # Rebellion subtypes
    "Armed Clash/Battle": [
        "Pitched Battle",
        "Urban Combat",
        "Rural Engagement",
        "Border Skirmish",
    ],
    "Ambush": [
        "Roadside Ambush",
        "IED Ambush",
        "Complex Ambush",
        "Convoy Ambush",
    ],
    "Rebel Attack on Government Position": [
        "Military Base Attack",
        "Police Station Attack",
        "Checkpoint Attack",
        "Government Building Attack",
    ],

    # Criminal subtypes
    "Highway Robbery": [
        "Vehicle Hijacking",
        "Road Blockade Robbery",
        "Passenger Bus Attack",
    ],
    "Village Raid": [
        "Night Raid",
        "Dawn Raid",
        "Multi-Village Raid",
    ],
    "Mass Kidnapping": [
        "School Abduction",
        "Church/Mosque Abduction",
        "Wedding/Event Abduction",
    ],

    # State violence subtypes
    "Massacre": [
        "Village Massacre",
        "Camp Massacre",
        "Market Massacre",
    ],
    "Protest Crackdown": [
        "Live Fire on Protesters",
        "Tear Gas/Water Cannon",
        "Mass Arrests with Violence",
    ],
}


# ============================================================================
# CLASSIFICATION DECISION RULES
# ============================================================================

@dataclass
class ClassificationContext:
    """Context for taxonomy classification decision."""
    actor_type: Optional[str] = None  # state, non-state armed, communal, criminal
    target_type: Optional[str] = None  # civilian, military, government, communal
    motivation: Optional[str] = None  # political, economic, identity, resource
    method: Optional[str] = None  # bombing, shooting, ambush, etc.
    is_reciprocal: bool = False  # Both sides fighting (battle) vs one-sided


class TaxonomyClassifier:
    """
    Classifies violent events into the 4-level taxonomy hierarchy.

    Implements the 4-step decision process from VIONER_GUIDELINES.md:
    1. Identify Actor Type
    2. Identify Motivation
    3. Identify Target
    4. Apply Hierarchy
    """

    # Actor type keywords
    STATE_ACTORS = [
        'army', 'military', 'police', 'forces', 'soldiers', 'troops',
        'government', 'security forces', 'paramilitary', 'gendarmerie',
        'national guard', 'presidential guard', 'riot police'
    ]

    NON_STATE_ARMED = [
        'rebels', 'insurgents', 'militants', 'fighters', 'guerrillas',
        'al-shabaab', 'boko haram', 'isis', 'aqim', 'jnim', 'm23',
        'al-qaeda', 'iswap', 'adf', 'lra', 'rsf', 'saf', 'militia'
    ]

    COMMUNAL_ACTORS = [
        'herders', 'farmers', 'fulani', 'ethnic', 'tribal', 'clan',
        'community', 'villagers', 'pastoralists', 'nomads', 'settlers'
    ]

    CRIMINAL_ACTORS = [
        'bandits', 'armed men', 'gunmen', 'kidnappers', 'robbers',
        'gang', 'criminals', 'thieves', 'cartel', 'smugglers'
    ]

    # Target type keywords
    CIVILIAN_TARGETS = [
        'civilians', 'villagers', 'residents', 'farmers', 'traders',
        'students', 'worshippers', 'passengers', 'market', 'school',
        'church', 'mosque', 'hospital', 'camp', 'village',
        'protesters', 'demonstrators', 'rally', 'crowd', 'women',
        'children', 'refugees', 'displaced', 'idp'
    ]

    MILITARY_TARGETS = [
        'military base', 'army barracks', 'checkpoint', 'convoy',
        'soldiers', 'troops', 'forces', 'positions', 'outpost'
    ]

    GOVERNMENT_TARGETS = [
        'police station', 'government building', 'official', 'minister',
        'governor', 'parliament', 'court', 'prison'
    ]

    # Event type keywords for classification
    TERRORISM_KEYWORDS = [
        'suicide bomb', 'ied', 'explosion', 'blast', 'detonated',
        'car bomb', 'vest', 'terrorist', 'terror attack'
    ]

    INSURGENCY_KEYWORDS = [
        'clash', 'battle', 'fighting', 'combat', 'ambush', 'raid',
        'attack on base', 'overran', 'captured', 'territory'
    ]

    COMMUNAL_KEYWORDS = [
        'ethnic clash', 'tribal', 'herder', 'farmer', 'grazing',
        'land dispute', 'revenge', 'retaliation', 'communal'
    ]

    CRIMINAL_KEYWORDS = [
        'kidnap', 'abduct', 'ransom', 'robbery', 'bandit', 'cattle',
        'rustling', 'gang', 'criminal'
    ]

    STATE_VIOLENCE_KEYWORDS = [
        'protest', 'crackdown', 'dispersed', 'fired on', 'massacre',
        'extrajudicial', 'execution', 'burned village', 'razed'
    ]

    def classify(
        self,
        text: str,
        perpetrator: Optional[str] = None,
        target: Optional[str] = None,
        event_type: Optional[str] = None
    ) -> Tuple[str, str, Optional[str], Optional[str]]:
        """
        Classify an event into the taxonomy hierarchy.

        Args:
            text: Full event description text
            perpetrator: Extracted perpetrator entity
            target: Extracted target entity
            event_type: Extracted event type

        Returns:
            Tuple of (L1, L2, L3, L4) - L3 and L4 may be None
        """
        text_lower = text.lower()
        perp_lower = (perpetrator or '').lower()
        target_lower = (target or '').lower()
        event_lower = (event_type or '').lower()

        # STEP 1: Identify Actor Type
        actor_type = self._identify_actor_type(perp_lower, text_lower)

        # STEP 2: Identify Motivation (from text patterns)
        motivation = self._identify_motivation(text_lower, event_lower)

        # STEP 3: Identify Target Type
        target_type = self._identify_target_type(target_lower, text_lower)

        # STEP 4: Apply Hierarchy based on decision tree
        return self._apply_hierarchy(actor_type, motivation, target_type, text_lower, event_lower)

    def _identify_actor_type(self, perpetrator: str, text: str) -> str:
        """Identify the type of actor/perpetrator."""
        combined = f"{perpetrator} {text}"

        # Check for state actors
        if any(kw in combined for kw in self.STATE_ACTORS):
            # But check if they're the victim/target, not perpetrator
            if any(kw in perpetrator for kw in self.STATE_ACTORS):
                return "state"

        # Check for non-state armed groups
        if any(kw in combined for kw in self.NON_STATE_ARMED):
            return "non_state_armed"

        # Check for communal actors
        if any(kw in combined for kw in self.COMMUNAL_ACTORS):
            return "communal"

        # Check for criminal actors
        if any(kw in combined for kw in self.CRIMINAL_ACTORS):
            return "criminal"

        # Default to non-state armed if unclear
        return "unknown"

    def _identify_motivation(self, text: str, event_type: str) -> str:
        """Identify the motivation for the violence."""
        combined = f"{text} {event_type}"

        # Check for political motivation
        if any(kw in combined for kw in ['political', 'government', 'regime', 'power', 'election']):
            return "political"

        # Check for economic motivation
        if any(kw in combined for kw in ['ransom', 'robbery', 'loot', 'steal', 'money', 'cattle']):
            return "economic"

        # Check for identity-based motivation
        if any(kw in combined for kw in ['ethnic', 'tribal', 'religious', 'sectarian']):
            return "identity"

        # Check for resource-based motivation
        if any(kw in combined for kw in ['land', 'water', 'grazing', 'farming', 'mining']):
            return "resource"

        return "unknown"

    def _identify_target_type(self, target: str, text: str) -> str:
        """Identify the type of target."""
        combined = f"{target} {text}"

        if any(kw in combined for kw in self.MILITARY_TARGETS):
            return "military"

        if any(kw in combined for kw in self.GOVERNMENT_TARGETS):
            return "government"

        if any(kw in combined for kw in self.CIVILIAN_TARGETS):
            return "civilian"

        return "unknown"

    def _apply_hierarchy(
        self,
        actor_type: str,
        motivation: str,
        target_type: str,
        text: str,
        event_type: str
    ) -> Tuple[str, str, Optional[str], Optional[str]]:
        """Apply the classification hierarchy based on decision tree."""
        combined = f"{text} {event_type}"

        # Decision Tree Implementation

        # STATE VIOLENCE
        if actor_type == "state" and target_type == "civilian":
            l1 = "State Violence Against Civilians"
            if any(kw in combined for kw in ['protest', 'demonstration', 'rally']):
                return (l1, "State Repression of Protests", "Protest Crackdown", None)
            elif any(kw in combined for kw in ['massacre', 'mass killing', 'slaughter']):
                return (l1, "Mass Atrocities by State Forces", "Massacre", None)
            elif any(kw in combined for kw in ['execution', 'shot dead', 'killed by police']):
                return (l1, "Extrajudicial Killings", "Summary Execution", None)
            elif any(kw in combined for kw in ['evict', 'displace', 'burn', 'raze']):
                return (l1, "Forced Displacement by State", "Eviction with Violence", None)
            return (l1, "Extrajudicial Killings", None, None)

        # COMMUNAL VIOLENCE
        if actor_type == "communal" or motivation in ["identity", "resource"]:
            l1 = "Communal Violence"
            if any(kw in combined for kw in ['herder', 'farmer', 'pastoralist', 'grazing']):
                return (l1, "Pastoralist-Farmer Clashes", "Grazing Conflict", None)
            elif any(kw in combined for kw in ['ethnic', 'tribal', 'clan']):
                return (l1, "Ethnic/Tribal Conflict", "Ethnic Clash", None)
            elif any(kw in combined for kw in ['religious', 'sectarian', 'church', 'mosque']):
                return (l1, "Religious Violence", "Sectarian Clash", None)
            elif any(kw in combined for kw in ['land', 'water', 'resource']):
                return (l1, "Resource-Based Conflict", "Land Dispute Violence", None)
            return (l1, "Ethnic/Tribal Conflict", None, None)

        # CRIMINAL VIOLENCE
        if actor_type == "criminal" or motivation == "economic":
            l1 = "Criminal Violence"
            if any(kw in combined for kw in ['kidnap', 'abduct', 'hostage']):
                if any(kw in combined for kw in ['school', 'students', 'mass']):
                    return (l1, "Kidnapping for Ransom", "Mass Kidnapping", "School Abduction")
                return (l1, "Kidnapping for Ransom", "Individual Kidnapping", None)
            elif any(kw in combined for kw in ['robbery', 'robbed', 'highway', 'road']):
                return (l1, "Armed Robbery/Banditry", "Highway Robbery", None)
            elif any(kw in combined for kw in ['raid', 'village', 'cattle', 'rustl']):
                return (l1, "Armed Robbery/Banditry", "Village Raid", None)
            elif any(kw in combined for kw in ['gang', 'mob', 'vigilante']):
                return (l1, "Criminal Gang Violence", "Gang Clash", None)
            return (l1, "Armed Robbery/Banditry", None, None)

        # POLITICAL VIOLENCE (default for non-state armed groups)
        l1 = "Political Violence"

        # Check for terrorism indicators
        if any(kw in combined for kw in self.TERRORISM_KEYWORDS):
            l2 = "Terrorism"
            if any(kw in combined for kw in ['suicide', 'vest']):
                return (l1, l2, "Bombing/Explosive Attack", "Suicide Bombing")
            elif any(kw in combined for kw in ['car bomb', 'vehicle bomb', 'vbied']):
                return (l1, l2, "Bombing/Explosive Attack", "Car/Vehicle Bombing (VBIED)")
            elif any(kw in combined for kw in ['ied', 'roadside', 'improvised']):
                return (l1, l2, "Bombing/Explosive Attack", "Roadside IED")
            elif any(kw in combined for kw in ['mass shooting', 'rampage', 'coordinated']):
                return (l1, l2, "Armed Assault", "Mass Shooting/Rampage")
            return (l1, l2, "Bombing/Explosive Attack", None)

        # Check for insurgency indicators
        if any(kw in combined for kw in self.INSURGENCY_KEYWORDS):
            l2 = "Rebellion/Armed Insurgency"
            if any(kw in combined for kw in ['clash', 'battle', 'fighting', 'combat']):
                return (l1, l2, "Armed Clash/Battle", None)
            elif any(kw in combined for kw in ['ambush']):
                if 'convoy' in combined:
                    return (l1, l2, "Ambush", "Convoy Ambush")
                elif 'ied' in combined:
                    return (l1, l2, "Ambush", "IED Ambush")
                return (l1, l2, "Ambush", "Roadside Ambush")
            elif any(kw in combined for kw in ['base', 'checkpoint', 'outpost', 'barracks']):
                return (l1, l2, "Rebel Attack on Government Position", "Military Base Attack")
            elif any(kw in combined for kw in ['captured', 'seized', 'overran', 'territory']):
                return (l1, l2, "Territory Capture", None)
            return (l1, l2, "Armed Clash/Battle", None)

        # Check for election violence
        if any(kw in combined for kw in ['election', 'poll', 'voting', 'ballot']):
            return (l1, "Election Violence", "Election-Day Violence", None)

        # Default to rebellion/insurgency for unknown political violence
        return (l1, "Rebellion/Armed Insurgency", "Armed Clash/Battle", None)

    def get_all_l1_categories(self) -> List[str]:
        """Get all Level 1 categories."""
        return [e.value for e in TaxonomyL1]

    def get_l2_for_l1(self, l1: str) -> List[str]:
        """Get all Level 2 categories for a given Level 1."""
        if l1 in TAXONOMY_HIERARCHY:
            return list(TAXONOMY_HIERARCHY[l1].keys())
        return []

    def get_l3_for_l2(self, l1: str, l2: str) -> List[str]:
        """Get all Level 3 categories for a given Level 1 and Level 2."""
        if l1 in TAXONOMY_HIERARCHY and l2 in TAXONOMY_HIERARCHY[l1]:
            return TAXONOMY_HIERARCHY[l1][l2]
        return []

    def get_l4_for_l3(self, l3: str) -> List[str]:
        """Get all Level 4 subtypes for a given Level 3."""
        return TAXONOMY_L4.get(l3, [])


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_taxonomy_statistics() -> Dict:
    """Get statistics about the taxonomy hierarchy."""
    l1_count = len(TAXONOMY_HIERARCHY)
    l2_count = sum(len(l2s) for l2s in TAXONOMY_HIERARCHY.values())
    l3_count = sum(
        len(l3s)
        for l2s in TAXONOMY_HIERARCHY.values()
        for l3s in l2s.values()
    )
    l4_count = sum(len(l4s) for l4s in TAXONOMY_L4.values())

    return {
        'level_1_categories': l1_count,
        'level_2_types': l2_count,
        'level_3_types': l3_count,
        'level_4_subtypes': l4_count,
        'total': l1_count + l2_count + l3_count + l4_count
    }


def print_taxonomy_tree():
    """Print the full taxonomy tree."""
    print("=" * 70)
    print("VIOLENT EVENT TAXONOMY HIERARCHY")
    print("=" * 70)

    for l1, l2_dict in TAXONOMY_HIERARCHY.items():
        print(f"\n{l1}")
        print("-" * len(l1))

        for l2, l3_list in l2_dict.items():
            print(f"  └── {l2}")

            for l3 in l3_list:
                l4_list = TAXONOMY_L4.get(l3, [])
                if l4_list:
                    print(f"      └── {l3}")
                    for l4 in l4_list:
                        print(f"          └── {l4}")
                else:
                    print(f"      └── {l3}")

    stats = get_taxonomy_statistics()
    print("\n" + "=" * 70)
    print("STATISTICS")
    print("=" * 70)
    print(f"Level 1 Categories: {stats['level_1_categories']}")
    print(f"Level 2 Types: {stats['level_2_types']}")
    print(f"Level 3 Types: {stats['level_3_types']}")
    print(f"Level 4 Subtypes: {stats['level_4_subtypes']}")
    print(f"Total: {stats['total']}")


# ============================================================================
# SINGLETON CLASSIFIER INSTANCE
# ============================================================================

_classifier_instance: Optional[TaxonomyClassifier] = None


def get_classifier() -> TaxonomyClassifier:
    """Get or create the singleton taxonomy classifier."""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = TaxonomyClassifier()
    return _classifier_instance


if __name__ == '__main__':
    print_taxonomy_tree()

    # Test classification
    print("\n" + "=" * 70)
    print("CLASSIFICATION EXAMPLES")
    print("=" * 70)

    classifier = get_classifier()

    test_cases = [
        {
            'text': "A suicide bomber detonated at a crowded market in Maiduguri, killing 32 civilians. Boko Haram claimed responsibility.",
            'perpetrator': "Boko Haram",
            'target': "market",
            'event_type': "suicide bombing"
        },
        {
            'text': "Rebels clashed with government forces in Gao region. The battle lasted several hours and left 15 soldiers and 8 rebels dead.",
            'perpetrator': "Rebels",
            'target': "government forces",
            'event_type': "clash"
        },
        {
            'text': "At least 20 people were killed in clashes between Fulani herders and farming communities in Benue State over grazing rights.",
            'perpetrator': "Fulani herders",
            'target': "farming communities",
            'event_type': "clash"
        },
        {
            'text': "Armed bandits kidnapped 50 students from a boarding school in Zamfara State, demanding ransom.",
            'perpetrator': "Armed bandits",
            'target': "students",
            'event_type': "kidnapping"
        },
        {
            'text': "Police opened fire on protesters in Khartoum, killing at least 10 demonstrators.",
            'perpetrator': "Police",
            'target': "protesters",
            'event_type': "crackdown"
        },
    ]

    for i, case in enumerate(test_cases, 1):
        result = classifier.classify(
            text=case['text'],
            perpetrator=case['perpetrator'],
            target=case['target'],
            event_type=case['event_type']
        )
        print(f"\nExample {i}:")
        print(f"  Text: {case['text'][:80]}...")
        print(f"  Classification: {result[0]} → {result[1]} → {result[2]} → {result[3]}")
