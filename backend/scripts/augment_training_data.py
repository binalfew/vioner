#!/usr/bin/env python3
"""
Training Data Augmentation Script for VioNER

Adds synthetic examples with missing vocabulary to improve model coverage.
Addresses gaps in: ACTION verbs, ACTOR terms, VICTIM terms.

Usage:
    python scripts/augment_training_data.py --output ../data/processed/train_augmented.jsonl

    # Or append to existing training data:
    python scripts/augment_training_data.py --append ../data/processed/train.jsonl
"""

import json
import random
import argparse
from pathlib import Path
from typing import List, Dict, Tuple

# ============================================================================
# MISSING VOCABULARY TO ADD
# ============================================================================

# ============================================================================
# ACTION VERBS - Organized by syntax type for grammatically correct sentences
# ============================================================================

# Simple transitive verbs: "{actor} {action} {location}"
# These work directly with a location object
SIMPLE_ACTION_VERBS = [
    # === ATTACK/ASSAULT ===
    'attacked', 'raided', 'stormed', 'invaded',
    'struck', 'hit', 'overran', 'sacked',

    # === DESTRUCTION ===
    'bombed', 'shelled', 'destroyed', 'burned', 'burnt',
    'torched', 'razed', 'demolished',
    'devastated', 'ravaged', 'gutted', 'wrecked', 'ruined',

    # === CAPTURE/CONTROL ===
    'captured', 'seized', 'occupied', 'surrounded', 'encircled',
    'besieged', 'blockaded', 'conquered',

    # === LOOTING ===
    'looted', 'ransacked', 'pillaged', 'plundered',

    # === OTHER ===
    'breached', 'sabotaged', 'vandalized',
]

# Verbs for "{actor} {action} {num} {victim} in {location}" pattern
VICTIM_ACTION_VERBS = [
    # === KILLING ===
    'killed', 'murdered', 'slaughtered', 'massacred', 'executed',
    'shot', 'butchered', 'beheaded', 'decapitated',
    'hanged', 'lynched', 'strangled', 'drowned', 'poisoned',

    # === INJURY ===
    'wounded', 'injured', 'maimed',

    # === ABDUCTION ===
    'kidnapped', 'abducted',

    # === DETENTION ===
    'detained', 'arrested', 'apprehended',

    # === VIOLENCE ===
    'tortured', 'brutalized', 'assaulted',

    # === DISPLACEMENT ===
    'displaced', 'expelled', 'evicted',
]

# Single-word clash verbs (can take direct object): "{actor} {verb} {other_actor}"
SINGLE_CLASH_VERBS = [
    'battled', 'fought', 'engaged', 'confronted',
    'repelled', 'routed', 'defeated', 'overpowered',
]

# Multi-word clash verbs: "{actor} {verb phrase} {other_actor}"
MULTI_CLASH_VERBS = [
    'clashed with', 'skirmished with', 'exchanged fire with',
    'traded fire with', 'fought against', 'battled against',
]

# Combined for template selection
CLASH_VERBS = SINGLE_CLASH_VERBS + MULTI_CLASH_VERBS

# All action verbs combined for backward compatibility and labeling
MISSING_ACTIONS = SIMPLE_ACTION_VERBS + VICTIM_ACTION_VERBS + SINGLE_CLASH_VERBS

# ============================================================================
# ACTOR TERMS - Single and two-word terms only (for correct labeling)
# ============================================================================
MISSING_ACTORS = [
    # === GENERIC ARMED GROUP TERMS (1-2 words only) ===
    'Militants', 'Rebels', 'Insurgents', 'Guerrillas', 'Fighters',
    'Combatants', 'Belligerents', 'Hostiles', 'Adversaries',
    'Armed men', 'Armed groups', 'Armed elements', 'Armed gangs',
    'Unknown gunmen', 'Masked gunmen', 'Uniformed men',

    # === ATTACKER TERMS ===
    'Gunmen', 'Attackers', 'Assailants', 'Perpetrators', 'Aggressors',
    'Shooters', 'Snipers', 'Bombers', 'Arsonists',
    'Assassins', 'Hitmen', 'Killers', 'Murderers', 'Executioners',

    # === EXTREMIST/TERRORIST TERMS ===
    'Terrorists', 'Extremists', 'Jihadists', 'Islamists', 'Radicals',
    'Fundamentalists', 'Hardliners', 'Fanatics', 'Zealots',
    'Takfiris', 'Salafists', 'Kharijites',

    # === CRIMINAL TERMS ===
    'Bandits', 'Raiders', 'Marauders', 'Brigands', 'Outlaws',
    'Kidnappers', 'Abductors',
    'Criminals', 'Criminal gangs',
    'Gangs', 'Gang members', 'Gangsters', 'Thugs', 'Hoodlums', 'Goons',
    'Looters', 'Robbers', 'Thieves', 'Armed robbers',
    'Cattle rustlers', 'Rustlers', 'Poachers', 'Smugglers',
    'Traffickers', 'Pirates',

    # === MILITARY/PARAMILITARY TERMS ===
    'Paramilitaries', 'Militias', 'Militia groups',
    'Militiamen', 'Militia members', 'Militia fighters',
    'Vigilantes', 'Vigilante groups', 'Mercenaries',
    'Soldiers', 'Troops', 'Infantry', 'Commandos',
    'Forces', 'Armed forces', 'Military forces', 'Government forces',
    'Army', 'Military', 'Security forces',
    'Police', 'Riot police', 'Gendarmes', 'Gendarmerie',
    'Officers', 'Servicemen', 'Guards', 'Sentries',

    # === LEADERSHIP TERMS ===
    'Warlords', 'Commanders',
    'Leaders', 'Rebel leaders',
    'Chiefs', 'Chieftains', 'Kingpins', 'Bosses',
    'Generals', 'Colonels', 'Captains',

    # === POLITICAL/IDEOLOGICAL TERMS ===
    'Separatists', 'Secessionists', 'Nationalists',
    'Dissidents', 'Defectors', 'Deserters', 'Mutineers',
    'Loyalists',

    # === ETHNIC/TRIBAL/COMMUNAL TERMS ===
    'Herders', 'Herdsmen', 'Pastoralists', 'Nomads',
    'Farmers', 'Tribesmen', 'Tribal militias',

    # === SPECIFIC GROUP REFERENCES ===
    'Operatives', 'Agents', 'Cadres', 'Cells',
    'Members', 'Affiliates', 'Associates', 'Sympathizers', 'Supporters',
    'Recruits', 'Conscripts', 'Veterans',

    # === NAMED ARMED GROUPS (abbreviations and 1-2 word names) ===
    'Boko Haram', 'ISWAP',
    'Al-Shabaab', 'Al Shabaab', 'Shabaab',
    'Al-Qaeda', 'AQIM',
    'JNIM', 'Ansar Dine', 'Ansarul Islam',
    'M23', 'ADF', 'CODECO',
    'Mai-Mai', 'Mayi-Mayi', 'FDLR', 'Interahamwe',
    'LRA', 'RSF', 'Janjaweed',
    'SAF', 'Sudanese military',
    'TPLF', 'Tigray forces', 'Fano', 'OLA',
    'Seleka', 'Anti-balaka', '3R', 'UPC',
    'Renamo', 'Al-Sunnah', 'ISIS Mozambique',
    'AMISOM', 'AU forces', 'UN peacekeepers', 'MONUSCO',
]

# ============================================================================
# VICTIM TERMS - Single and two-word terms only (for correct labeling)
# ============================================================================
VICTIM_TERMS = [
    # === GENERAL CIVILIAN TERMS ===
    'civilians', 'people', 'persons', 'individuals', 'citizens',
    'inhabitants', 'population', 'masses', 'public',
    'community members',
    'non-combatants', 'innocent civilians',
    'bystanders', 'onlookers', 'passersby',

    # === LOCATION-BASED TERMS ===
    'villagers', 'village residents',
    'residents', 'local residents',
    'locals', 'local people',
    'townsfolk', 'townspeople', 'city dwellers',
    'camp residents',
    'rural residents', 'urban residents',

    # === OCCUPATIONAL TERMS ===
    'farmers', 'peasants', 'farmworkers',
    'herders', 'pastoralists',
    'traders', 'merchants', 'businessmen', 'businesswomen', 'entrepreneurs',
    'shopkeepers', 'vendors', 'hawkers',
    'fishermen', 'fishers',
    'miners', 'workers', 'laborers',

    # === TRANSPORT-RELATED ===
    'passengers', 'travelers', 'travellers', 'commuters',
    'motorists', 'drivers', 'truckers',
    'motorcyclists', 'cyclists', 'pedestrians',

    # === EDUCATION-RELATED ===
    'students', 'pupils', 'schoolchildren',
    'teachers', 'schoolteachers', 'educators', 'instructors',
    'professors', 'lecturers', 'academics', 'researchers',
    'principals',

    # === HEALTHCARE-RELATED ===
    'health workers', 'medical workers',
    'doctors', 'physicians', 'surgeons',
    'nurses', 'midwives', 'paramedics', 'medics',
    'pharmacists', 'patients',

    # === HUMANITARIAN ===
    'aid workers', 'relief workers',
    'volunteers',
    'NGO workers', 'NGO staff',
    'UN staff', 'UN workers',
    'ICRC staff', 'MSF staff',

    # === MEDIA ===
    'journalists', 'reporters', 'correspondents', 'press',
    'media workers',
    'cameramen', 'photographers',
    'broadcasters', 'editors', 'bloggers',

    # === RELIGIOUS ===
    'worshippers', 'worshipers', 'faithful', 'congregants',
    'churchgoers', 'parishioners',
    'Christians', 'Muslims', 'believers',
    'clergy', 'clerics',
    'priests', 'pastors', 'bishops',
    'imams', 'sheikhs', 'monks', 'nuns',

    # === VULNERABLE GROUPS ===
    'women', 'girls', 'females', 'mothers',
    'children', 'kids', 'minors', 'boys',
    'infants', 'babies', 'toddlers', 'newborns',
    'elderly', 'aged', 'youth', 'teenagers', 'adolescents',
    'orphans', 'widows', 'widowers',

    # === DISPLACED PERSONS ===
    'refugees', 'displaced persons', 'displaced people',
    'IDPs', 'returnees',
    'migrants', 'asylum seekers',
    'camp dwellers',

    # === SECURITY PERSONNEL AS VICTIMS ===
    'peacekeepers', 'soldiers', 'troops', 'servicemen',
    'police officers', 'policemen',
    'security guards',

    # === GOVERNMENT/OFFICIALS ===
    'government officials', 'civil servants',
    'politicians', 'lawmakers', 'parliamentarians', 'senators',
    'mayors', 'governors', 'administrators',
    'diplomats', 'judges', 'magistrates', 'lawyers', 'prosecutors',

    # === FAMILY/SOCIAL TERMS ===
    'families', 'households', 'family members',
    'relatives', 'mourners', 'celebrants',
]

# ============================================================================
# LOCATIONS - Exhaustive African conflict zones
# ============================================================================
LOCATIONS = {
    'cities': [
        # === NIGERIA ===
        'Maiduguri', 'Kano', 'Lagos', 'Abuja', 'Kaduna', 'Jos', 'Yola', 'Damaturu',
        'Bama', 'Gwoza', 'Monguno', 'Dikwa', 'Konduga', 'Damboa', 'Chibok',
        'Biu', 'Askira', 'Hawul', 'Gubio', 'Magumeri', 'Mafa', 'Kaga',
        'Gusau', 'Sokoto', 'Katsina', 'Zamfara', 'Minna', 'Makurdi',

        # === SOMALIA ===
        'Mogadishu', 'Kismayo', 'Baidoa', 'Beledweyne', 'Hargeisa',
        'Bosaso', 'Garowe', 'Galkayo', 'Merca', 'Barawe', 'Afgoye',
        'Jowhar', 'Dhusamareb', 'El Bur', 'Hudur', 'Belet Hawa',

        # === SUDAN/SOUTH SUDAN ===
        'Khartoum', 'Omdurman', 'Port Sudan', 'Kassala', 'Gedaref',
        'El Fasher', 'Nyala', 'El Geneina', 'Zalingei', 'El Daein',
        'Juba', 'Wau', 'Malakal', 'Bor', 'Bentiu', 'Aweil', 'Rumbek',
        'Yei', 'Torit', 'Kapoeta', 'Pibor', 'Renk', 'Kodok',

        # === DRC ===
        'Goma', 'Bukavu', 'Beni', 'Butembo', 'Kinshasa', 'Lubumbashi',
        'Kisangani', 'Mbuji-Mayi', 'Kananga', 'Uvira', 'Kalemie',
        'Bunia', 'Ituri', 'Rutshuru', 'Masisi', 'Walikale', 'Shabunda',
        'Dungu', 'Isiro', 'Buta', 'Gbadolite', 'Gemena',

        # === CENTRAL AFRICAN REPUBLIC ===
        'Bangui', 'Bambari', 'Kaga-Bandoro', 'Bria', 'Ndele', 'Birao',
        'Obo', 'Zemio', 'Rafai', 'Bangassou', 'Mobaye', 'Bossangoa',
        'Bouar', 'Berberati', 'Carnot', 'Nola',

        # === SAHEL - MALI ===
        'Bamako', 'Mopti', 'Gao', 'Timbuktu', 'Kidal', 'Menaka',
        'Sevare', 'Djenne', 'Bandiagara', 'Douentza', 'Niono',
        'Segou', 'Sikasso', 'Kayes', 'Koulikoro',

        # === SAHEL - BURKINA FASO ===
        'Ouagadougou', 'Djibo', 'Dori', 'Sebba', 'Arbinda',
        'Kaya', 'Kongoussi', 'Titao', 'Ouahigouya',
        'Bobo-Dioulasso', 'Dedougou', 'Fada N\'gourma',

        # === SAHEL - NIGER ===
        'Niamey', 'Tillaberi', 'Tahoua', 'Maradi', 'Zinder', 'Diffa',
        'Agadez', 'Dosso', 'Torodi', 'Ouallam', 'Banibangou',

        # === CAMEROON ===
        'Douala', 'Yaoundé', 'Bamenda', 'Buea', 'Maroua', 'Kousseri',
        'Mora', 'Mokolo', 'Fotokol', 'Kolofata', 'Limbe', 'Kumba',

        # === CHAD ===
        'N\'Djamena', 'Moundou', 'Sarh', 'Abeche', 'Bol', 'Baga Sola',
        'Ati', 'Mongo', 'Faya-Largeau', 'Am Timan',

        # === ETHIOPIA ===
        'Addis Ababa', 'Mekelle', 'Axum', 'Adwa', 'Shire', 'Humera',
        'Bahir Dar', 'Gondar', 'Dessie', 'Kombolcha', 'Debre Birhan',
        'Dire Dawa', 'Harar', 'Jijiga', 'Moyale', 'Negele',
        'Gambella', 'Assosa', 'Jimma', 'Nekemte',

        # === ERITREA ===
        'Asmara', 'Massawa', 'Keren', 'Assab', 'Mendefera',

        # === MOZAMBIQUE ===
        'Maputo', 'Pemba', 'Mocímboa da Praia', 'Palma', 'Macomia',
        'Mueda', 'Montepuez', 'Nampula', 'Beira', 'Chimoio',
        'Quissanga', 'Muidumbe', 'Meluco', 'Ibo',

        # === EAST AFRICA ===
        'Nairobi', 'Mombasa', 'Garissa', 'Mandera', 'Wajir', 'Lamu',
        'Kampala', 'Gulu', 'Kitgum', 'Karamoja', 'Moroto',
        'Bujumbura', 'Gitega', 'Ngozi', 'Bubanza',
        'Kigali', 'Butare', 'Gisenyi', 'Byumba',
        'Dar es Salaam', 'Dodoma', 'Arusha', 'Mwanza',

        # === NORTH AFRICA ===
        'Tripoli', 'Benghazi', 'Sirte', 'Misrata', 'Sabha', 'Derna',
        'Cairo', 'Alexandria', 'El Arish', 'Sinai',
        'Algiers', 'Oran', 'Constantine', 'Tizi Ouzou',
        'Tunis', 'Sousse', 'Sfax', 'Kasserine',

        # === WEST AFRICA ===
        'Dakar', 'Ziguinchor', 'Casamance',
        'Conakry', 'Nzérékoré', 'Kankan',
        'Monrovia', 'Ganta', 'Buchanan',
        'Freetown', 'Bo', 'Kenema',
        'Abidjan', 'Bouake', 'Korhogo', 'Man',
        'Accra', 'Kumasi', 'Tamale',
        'Lomé', 'Sokodé', 'Dapaong',
        'Cotonou', 'Parakou', 'Kandi',
    ],

    'regions': [
        # === NIGERIA ===
        'Borno State', 'Adamawa State', 'Yobe State', 'Gombe State',
        'Kaduna State', 'Zamfara State', 'Katsina State', 'Sokoto State',
        'Niger State', 'Plateau State', 'Benue State', 'Taraba State',
        'Nasarawa State', 'Kogi State', 'North East', 'North West',
        'Middle Belt', 'Lake Chad region',

        # === DRC ===
        'North Kivu', 'South Kivu', 'Ituri', 'Tanganyika', 'Haut-Katanga',
        'Kasai', 'Kasai-Central', 'Kasai-Oriental', 'Maniema',
        'Haut-Uele', 'Bas-Uele', 'Tshopo', 'Equateur',
        'Mai-Ndombe', 'Kwilu', 'Kwango',

        # === SUDAN ===
        'Darfur', 'West Darfur', 'North Darfur', 'South Darfur', 'Central Darfur',
        'Blue Nile', 'South Kordofan', 'North Kordofan', 'West Kordofan',
        'Kassala', 'Gedaref', 'Red Sea', 'River Nile', 'Northern',
        'Khartoum State', 'White Nile', 'Sennar',

        # === SOUTH SUDAN ===
        'Central Equatoria', 'Eastern Equatoria', 'Western Equatoria',
        'Jonglei', 'Unity', 'Upper Nile', 'Warrap', 'Lakes',
        'Western Bahr el Ghazal', 'Northern Bahr el Ghazal',
        'Greater Pibor', 'Ruweng', 'Abyei',

        # === ETHIOPIA ===
        'Tigray', 'Amhara', 'Oromia', 'Afar', 'Somali Region',
        'Benishangul-Gumuz', 'Gambella', 'SNNPR', 'Sidama',
        'South West Ethiopia', 'Central Ethiopia',

        # === MOZAMBIQUE ===
        'Cabo Delgado', 'Nampula', 'Niassa', 'Zambezia',
        'Sofala', 'Manica', 'Tete', 'Gaza', 'Inhambane',

        # === SAHEL ===
        'Lake Chad Basin', 'Sahel region', 'Liptako-Gourma',
        'Tillaberi region', 'Tahoua region', 'Diffa region',
        'Mopti region', 'Gao region', 'Menaka region', 'Kidal region',
        'Sahel region', 'Nord region', 'Est region', 'Centre-Nord',

        # === SOMALIA ===
        'Jubaland', 'South West State', 'Galmudug', 'Hirshabelle',
        'Puntland', 'Somaliland', 'Banadir', 'Middle Shabelle',
        'Lower Shabelle', 'Bay', 'Bakool', 'Gedo', 'Middle Juba',
        'Lower Juba', 'Mudug', 'Nugal', 'Sool', 'Sanaag',

        # === CAR ===
        'Haute-Kotto', 'Ouaka', 'Mbomou', 'Haut-Mbomou',
        'Vakaga', 'Bamingui-Bangoran', 'Nana-Gribizi', 'Kemo',
        'Ouham', 'Ouham-Pende', 'Nana-Mambere', 'Mambere-Kadei',
        'Sangha-Mbaere', 'Lobaye', 'Ombella-M\'Poko',

        # === CAMEROON ===
        'Far North', 'North Region', 'Adamawa', 'East Region',
        'North West Region', 'South West Region', 'Anglophone regions',

        # === OTHER ===
        'Central African Republic', 'Great Lakes region',
        'Horn of Africa', 'Maghreb', 'Sub-Saharan Africa',
        'Bantu territories', 'Swahili coast',
    ],

    'countries': [
        # Main conflict countries
        'Nigeria', 'Somalia', 'Sudan', 'South Sudan',
        'DRC', 'DR Congo', 'Democratic Republic of Congo', 'Congo',
        'Mali', 'Burkina Faso', 'Niger', 'Cameroon', 'Chad',
        'Ethiopia', 'Eritrea', 'Mozambique',
        'Central African Republic', 'CAR',
        'Kenya', 'Uganda', 'Burundi', 'Rwanda', 'Tanzania',

        # North Africa
        'Libya', 'Egypt', 'Algeria', 'Tunisia', 'Morocco',

        # West Africa
        'Senegal', 'Gambia', 'Guinea', 'Guinea-Bissau', 'Sierra Leone',
        'Liberia', 'Ivory Coast', 'Cote d\'Ivoire', 'Ghana',
        'Togo', 'Benin', 'Mauritania',

        # Southern Africa
        'Angola', 'Zimbabwe', 'Zambia', 'Malawi',
        'South Africa', 'Namibia', 'Botswana', 'Lesotho', 'Eswatini',

        # Other
        'Djibouti', 'Comoros', 'Madagascar', 'Mauritius', 'Seychelles',
        'Sao Tome', 'Cape Verde', 'Equatorial Guinea', 'Gabon',
        'Republic of Congo', 'Congo-Brazzaville',
    ],

    'districts': [
        # DRC districts
        'Rutshuru', 'Masisi', 'Walikale', 'Lubero', 'Beni territory',
        'Djugu', 'Irumu', 'Mahagi', 'Mambasa', 'Aru',
        'Fizi', 'Uvira territory', 'Kalehe', 'Kabare', 'Walungu',

        # Nigeria LGAs
        'Gwoza LGA', 'Bama LGA', 'Konduga LGA', 'Maiduguri LGA',
        'Chibok LGA', 'Damboa LGA', 'Askira/Uba LGA', 'Biu LGA',

        # South Sudan counties
        'Juba County', 'Bor South', 'Pibor County', 'Akobo',
        'Mayendit', 'Leer', 'Koch', 'Rubkona', 'Bentiu County',

        # CAR prefectures
        'Vakaga Prefecture', 'Haute-Kotto Prefecture', 'Ouaka Prefecture',

        # Generic
        'district', 'county', 'municipality', 'commune', 'territory',
    ],
}

# Date templates
DATE_TEMPLATES = [
    'On {month} {day}, {year}',
    'On {weekday}',
    'Last {weekday}',
    '{month} {day}',
    'Earlier this week',
    'On {weekday} morning',
    'On {weekday} night',
]

MONTHS = ['January', 'February', 'March', 'April', 'May', 'June',
          'July', 'August', 'September', 'October', 'November', 'December']
WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# ============================================================================
# SENTENCE TEMPLATES - Organized by verb type for grammatical correctness
# ============================================================================

# Templates using SIMPLE_ACTION_VERBS (verb + location)
LOCATION_TEMPLATES = [
    # Actor + Action + Location + Casualties
    "{actor} {action} {location}, killing {num_killed} {victim_type}.",

    # Actor + Action + Location + Casualties + Injured
    "{actor} {action} {location}, leaving {num_killed} dead and {num_injured} injured.",

    # Date + Actor + Action + Location
    "{date}, {actor} {action} {location}.",

    # Actor + Action + Location + additional action
    "{actor} {action} {location} and looted several buildings.",

    # Passive voice with location
    "{num_killed} {victim_type} were killed when {actor} {action} {location}.",

    # With weapon mention
    "{actor} armed with heavy weapons {action} {location}, resulting in {num_killed} casualties.",

    # Multiple locations in region
    "{actor} {action} several villages in {region}, leaving at least {num_killed} dead.",

    # Action + abduction combo
    "{actor} {action} {location} and abducted {num_killed} {victim_type}.",

    # Morning/night attack
    "{actor} {action} {location} in a dawn raid, killing {num_killed} {victim_type}.",

    # Siege pattern
    "{actor} seized {location} after a prolonged siege.",
]

# Templates using VICTIM_ACTION_VERBS (verb + victim + in + location)
VICTIM_TEMPLATES = [
    # Basic victim + location
    "{actor} {action} {num_killed} {victim_type} in {location}.",

    # Date + victim action
    "{date}, {actor} {action} {num_killed} {victim_type} in {location}.",

    # With additional context
    "{actor} {action} at least {num_killed} {victim_type} in {region}.",

    # Overnight/during
    "{actor} {action} {num_killed} {victim_type} during an overnight raid in {location}.",

    # And injured
    "{actor} {action} {num_killed} {victim_type} and injured {num_injured} others in {location}.",

    # Near location
    "{actor} {action} {num_killed} {victim_type} near {location}.",

    # In region
    "{actor} {action} {num_killed} {victim_type} in {region}.",
]

# Templates using CLASH_VERBS (verb + other_actor + in + location)
CLASH_TEMPLATES = [
    # Basic clash
    "{actor} {clash_action} {actor2} in {location}.",

    # Clash with casualties
    "{actor} {clash_action} {actor2} in {location}, leaving {num_killed} dead.",

    # Date + clash
    "{date}, {actor} {clash_action} {actor2} near {location}.",

    # Heavy fighting
    "Heavy fighting erupted when {actor} {clash_action} {actor2} in {region}.",

    # Clash with aftermath
    "{actor} {clash_action} {actor2} in {location}, with {num_killed} casualties reported.",
]

# Combined for backward compatibility
TEMPLATES = LOCATION_TEMPLATES


def generate_date() -> Tuple[str, List[Tuple[str, str]]]:
    """Generate a random date string and its token labels."""
    template = random.choice(DATE_TEMPLATES)

    if '{month}' in template:
        month = random.choice(MONTHS)
        day = str(random.randint(1, 28))
        year = str(random.randint(2020, 2025))
        date_str = template.format(month=month, day=day, year=year)
    elif '{weekday}' in template:
        weekday = random.choice(WEEKDAYS)
        date_str = template.format(weekday=weekday)
    else:
        date_str = template

    # Tokenize and label
    tokens = date_str.replace(',', ' ,').split()
    labels = []
    for i, tok in enumerate(tokens):
        if tok in ['On', 'Last', 'Earlier', 'this', 'week']:
            labels.append('O')
        elif i == 0 or labels[-1] == 'O':
            labels.append('B-DATE')
        else:
            labels.append('I-DATE')

    return date_str, list(zip(tokens, labels))


def generate_example() -> Dict:
    """Generate a single augmented training example."""
    # Randomly choose template type with weights
    template_type = random.choices(
        ['location', 'victim', 'clash'],
        weights=[0.4, 0.4, 0.2],  # 40% location, 40% victim, 20% clash
        k=1
    )[0]

    # Select template and appropriate verb based on type
    if template_type == 'location':
        template = random.choice(LOCATION_TEMPLATES)
        action = random.choice(SIMPLE_ACTION_VERBS)
    elif template_type == 'victim':
        template = random.choice(VICTIM_TEMPLATES)
        action = random.choice(VICTIM_ACTION_VERBS)
    else:  # clash
        template = random.choice(CLASH_TEMPLATES)
        action = random.choice(SIMPLE_ACTION_VERBS)  # for the main action
        clash_action = random.choice(CLASH_VERBS)

    # Select components
    actor = random.choice(MISSING_ACTORS)
    actor2 = random.choice(MISSING_ACTORS)  # For clash templates
    while actor2 == actor:  # Ensure different actors in clashes
        actor2 = random.choice(MISSING_ACTORS)
    victim_type = random.choice(VICTIM_TERMS)
    location = random.choice(LOCATIONS['cities'])
    region = random.choice(LOCATIONS['regions'])
    num_killed = str(random.randint(3, 50))
    num_injured = str(random.randint(5, 100))

    # Generate date
    date_str, date_tokens = generate_date()

    # Build sentence with appropriate parameters
    format_args = {
        'actor': actor,
        'actor2': actor2,
        'action': action,
        'victim_type': victim_type,
        'location': location,
        'region': region,
        'num_killed': num_killed,
        'num_injured': num_injured,
        'date': date_str
    }
    if template_type == 'clash':
        format_args['clash_action'] = clash_action

    sentence = template.format(**format_args)

    # Tokenize and label
    tokens = []
    labels = []

    # Create sets for faster lookup
    all_action_verbs = set(SIMPLE_ACTION_VERBS + VICTIM_ACTION_VERBS + SINGLE_CLASH_VERBS)
    all_action_verbs_lower = set(v.lower() for v in all_action_verbs)
    actors_lower = set(a.lower() for a in MISSING_ACTORS)
    victims_lower = set(v.lower() for v in VICTIM_TERMS)

    # Simple tokenization (split on spaces, handle punctuation)
    raw_tokens = sentence.replace(',', ' ,').replace('.', ' .').split()

    # Context tracking for ACTOR vs VICTIM disambiguation
    # Words like "soldiers" can be ACTOR (subject) or VICTIM (object)
    # If we've seen ACTION + number, subsequent person words are likely VICTIM
    seen_action = False
    seen_number_after_action = False

    i = 0
    while i < len(raw_tokens):
        tok = raw_tokens[i]
        tok_lower = tok.lower()
        tok_clean = tok.rstrip(',.')

        # Handle multi-word actors (e.g., "Armed men", "Armed groups", "Boko Haram")
        if i + 1 < len(raw_tokens):
            two_word = f"{tok} {raw_tokens[i + 1].rstrip(',.')}"
            if two_word in MISSING_ACTORS:
                # Only label as ACTOR if we haven't seen action+number (i.e., in subject position)
                if not seen_number_after_action:
                    tokens.extend([tok, raw_tokens[i + 1].rstrip(',.')])
                    labels.extend(['B-ACTOR', 'I-ACTOR'])
                else:
                    # In object position - this is a VICTIM
                    tokens.extend([tok, raw_tokens[i + 1].rstrip(',.')])
                    labels.extend(['B-VICTIM', 'I-VICTIM'])
                if raw_tokens[i + 1].endswith(','):
                    tokens.append(',')
                    labels.append('O')
                elif raw_tokens[i + 1].endswith('.'):
                    tokens.append('.')
                    labels.append('O')
                i += 2
                continue

        # Handle multi-word clash verbs (e.g., "clashed with", "skirmished with")
        if i + 1 < len(raw_tokens):
            two_word_action = f"{tok_lower} {raw_tokens[i + 1].lower()}"
            if two_word_action in [v.lower() for v in MULTI_CLASH_VERBS]:
                tokens.extend([tok, raw_tokens[i + 1]])
                labels.extend(['B-ACTION', 'I-ACTION'])
                seen_action = True
                i += 2
                continue

        # Check if this is a number (for context tracking)
        is_number = tok.isdigit()
        if is_number and seen_action:
            seen_number_after_action = True

        # Actor labels - but check context first
        # Words in both ACTOR and VICTIM lists should be VICTIM if after action+number
        is_in_both_lists = (tok_lower in actors_lower) and (tok_lower in victims_lower)

        if tok in MISSING_ACTORS or tok_lower in actors_lower:
            if is_in_both_lists and seen_number_after_action:
                # This word appears after "verb + number", so it's a VICTIM
                tokens.append(tok)
                labels.append('B-VICTIM')
            elif not seen_action:
                # Before any action verb - this is the subject (ACTOR)
                tokens.append(tok)
                labels.append('B-ACTOR')
            else:
                # After action but context unclear - default to ACTOR
                tokens.append(tok)
                labels.append('B-ACTOR')

        # Action labels
        elif tok_lower in all_action_verbs_lower:
            tokens.append(tok)
            labels.append('B-ACTION')
            seen_action = True

        # Victim labels
        elif tok_lower in victims_lower:
            tokens.append(tok)
            labels.append('B-VICTIM')

        # Location labels (cities)
        elif tok_clean in LOCATIONS['cities']:
            tokens.append(tok_clean)
            labels.append('B-CITY')
            if tok.endswith(','):
                tokens.append(',')
                labels.append('O')
            elif tok.endswith('.'):
                tokens.append('.')
                labels.append('O')

        # Region labels (handle multi-word)
        elif any(tok_clean in region.split() for region in LOCATIONS['regions']):
            tokens.append(tok_clean)
            # Check if this starts a region
            for region in LOCATIONS['regions']:
                region_words = region.split()
                if tok_clean == region_words[0]:
                    labels.append('B-REGION')
                    break
            else:
                labels.append('I-REGION')
            if tok.endswith(','):
                tokens.append(',')
                labels.append('O')
            elif tok.endswith('.'):
                tokens.append('.')
                labels.append('O')

        # Casualty numbers
        elif tok.isdigit() and int(tok) > 31:
            tokens.append(tok)
            labels.append('B-CASUALTIES')

        # Casualty context words
        elif tok_lower in ['dead', 'killed', 'injured', 'wounded', 'casualties'] and labels and labels[-1] in ['B-CASUALTIES', 'I-CASUALTIES']:
            tokens.append(tok)
            labels.append('I-CASUALTIES')

        # Date tokens (from template)
        elif tok in MONTHS or tok in WEEKDAYS:
            tokens.append(tok)
            labels.append('B-DATE')
        elif tok.isdigit() and int(tok) <= 31:
            # Could be a day
            if labels and labels[-1] in ['B-DATE', 'I-DATE']:
                tokens.append(tok)
                labels.append('I-DATE')
            else:
                tokens.append(tok)
                labels.append('B-CASUALTIES')  # Default to casualties for standalone numbers
        elif tok in ['2020', '2021', '2022', '2023', '2024', '2025']:
            tokens.append(tok)
            if labels and labels[-1] in ['B-DATE', 'I-DATE']:
                labels.append('I-DATE')
            else:
                labels.append('B-DATE')

        # Default: O label
        else:
            tokens.append(tok)
            labels.append('O')

        i += 1

    return {
        'tokens': tokens,
        'labels': labels,
        'text': sentence,
        'source': 'augmentation'
    }


def validate_example(example: Dict) -> bool:
    """Validate that tokens and labels have same length."""
    if len(example['tokens']) != len(example['labels']):
        return False
    # Must have at least one entity
    if all(l == 'O' for l in example['labels']):
        return False
    return True


def generate_augmented_data(num_examples: int = 1000) -> List[Dict]:
    """Generate multiple augmented examples."""
    examples = []
    attempts = 0
    max_attempts = num_examples * 3

    while len(examples) < num_examples and attempts < max_attempts:
        example = generate_example()
        if validate_example(example):
            examples.append(example)
        attempts += 1

    return examples


def main():
    parser = argparse.ArgumentParser(description='Augment NER training data')
    parser.add_argument('--num-examples', type=int, default=1000,
                        help='Number of augmented examples to generate')
    parser.add_argument('--output', type=str, default='./data/processed/train_augmented.jsonl',
                        help='Output file path')
    parser.add_argument('--append', type=str, default=None,
                        help='Append to existing file instead of creating new one')
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed for reproducibility')

    args = parser.parse_args()
    random.seed(args.seed)

    print(f"Generating {args.num_examples} augmented examples...")
    augmented = generate_augmented_data(args.num_examples)
    print(f"Generated {len(augmented)} valid examples")

    # Show sample
    print("\nSample augmented examples:")
    print("-" * 60)
    for i, ex in enumerate(augmented[:3]):
        print(f"\nExample {i+1}:")
        print(f"  Text: {ex['text']}")
        print(f"  Entities: ", end="")
        entities = [(t, l) for t, l in zip(ex['tokens'], ex['labels']) if l != 'O']
        for tok, lbl in entities[:5]:
            print(f"{lbl}:{tok}", end=" ")
        print()

    # Write output
    if args.append:
        # Append to existing file
        output_path = Path(args.append)
        print(f"\nAppending to: {output_path}")

        # Count existing
        with open(output_path, 'r') as f:
            existing_count = sum(1 for _ in f)

        with open(output_path, 'a') as f:
            for ex in augmented:
                f.write(json.dumps(ex) + '\n')

        print(f"Original examples: {existing_count:,}")
        print(f"Added examples: {len(augmented):,}")
        print(f"Total examples: {existing_count + len(augmented):,}")
    else:
        # Create new file
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"\nWriting to: {output_path}")
        with open(output_path, 'w') as f:
            for ex in augmented:
                f.write(json.dumps(ex) + '\n')

        print(f"Wrote {len(augmented):,} examples")

    # Summary of vocabulary coverage
    print("\n" + "=" * 60)
    print("VOCABULARY COVERAGE ADDED")
    print("=" * 60)

    action_coverage = set()
    actor_coverage = set()

    for ex in augmented:
        for tok, lbl in zip(ex['tokens'], ex['labels']):
            if lbl == 'B-ACTION':
                action_coverage.add(tok.lower())
            elif lbl == 'B-ACTOR':
                actor_coverage.add(tok)

    print(f"\nACTION verbs added: {len(action_coverage)}")
    print(f"  {', '.join(sorted(action_coverage)[:10])}...")

    print(f"\nACTOR terms added: {len(actor_coverage)}")
    print(f"  {', '.join(sorted(actor_coverage)[:10])}...")

    print("\n✅ Done! Next steps:")
    if args.append:
        print(f"   Your training data has been augmented.")
        print(f"   Run training with: ./train_local.sh")
    else:
        print(f"   1. Merge with original: cat ../data/processed/train.jsonl {output_path} > train_merged.jsonl")
        print(f"   2. Or use directly for fine-tuning on augmented data only")


if __name__ == '__main__':
    main()
