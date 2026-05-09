# VioNER Annotation Guidelines & Implementation Analysis

**Project:** Knowledge Discovery from Free Text: Extraction of Violent Events
**Based on:** 1-Taxonomy.docx, 2-Annotation-Guidelines.docx (Version 1.0, October 2025)
**Author:** Binalfew Kassa Mekonnen
**Institution:** Addis Ababa University
**Date:** December 2025

---

## Table of Contents

**Part I: Implementation Issues Analysis**
1. Executive Summary
2. Taxonomy Hierarchy Issues
3. Geographic Inconsistencies
4. 5W1H Schema Issues
5. Event Type Classification Issues
6. Data Quality Issues
7. Knowledge Base vs Training Data Mismatch
8. Frontend/Backend Alignment Issues
9. Summary of Required Fixes

**Part II: Entity Classification Rules (5W1H Framework)**
10. Entity Framework Overview
11. WHO Category (4 Entity Types)
12. WHOM Category (1 Entity Type)
13. WHAT Category (4 Entity Types)
14. WHEN Category (4 Entity Types)
15. WHERE Category (7 Entity Types)
16. HOW Category (4 Entity Types)
17. General Annotation Rules
18. Common Mistakes to Avoid

**Appendix**
- Document References

---

# PART I: IMPLEMENTATION ISSUES ANALYSIS

---

## 1. Executive Summary

The current training data (`data/annotations/training.csv`) contains **critical issues** that fundamentally deviate from the Taxonomy and Annotation Guidelines documents. The synthetic data generation script produces semantically inconsistent and geographically impossible data that would train a model to learn incorrect patterns.

---

## 2. Taxonomy Hierarchy Issues (CRITICAL)

### 2.1 Incorrect Level 1 Categories

**Documentation specifies 4 Level 1 categories:**
- `POLITICAL VIOLENCE`
- `CRIMINAL VIOLENCE`
- `COMMUNAL VIOLENCE`
- `STATE VIOLENCE AGAINST CIVILIANS`

**Current implementation uses:**
- `Violence` (generic catch-all)

**Evidence from training.csv:**
```
Taxonomy_L1,Taxonomy_L2,Taxonomy_L3
December 14th through December 17th,Violence,massacre
14 June 2023,Violence,mass shooting
```

**Issues:**
1. The `Taxonomy_L1` column contains **dates** (column alignment error)
2. When corrected, `Taxonomy_L2` shows "Violence" which is not a valid L2 category
3. No distinction between political, criminal, communal, or state violence

### 2.2 Missing Taxonomy Level Structure

**Per documentation:**
- Level 1: 4 broad categories
- Level 2: 18 intermediate types (e.g., "Rebellion/Armed Insurgency", "Terrorism", "Organized Crime Violence")
- Level 3: 40-60 specific types (e.g., "Armed Clash/Battle", "Ambush", "Suicide Bombing")
- Level 4: 80+ detailed subtypes (e.g., "Roadside Ambush", "Car/Vehicle Bombing (VBIED)")

**Current implementation:**
- L1: Dates (ERROR) or "Violence"
- L2: "Violence" (invalid)
- L3: Generic event words like "massacre", "mass shooting", "airstrikes"

**Missing Level 2 categories:**
- Rebellion/Armed Insurgency
- Terrorism
- Coup and Regime Change Violence
- Election Violence
- Political Repression
- Organized Crime Violence
- Armed Robbery/Banditry
- Kidnapping for Ransom
- Criminal Gang Violence
- Ethnic/Tribal Conflict
- Religious Violence
- Resource-Based Conflict
- Pastoralist-Farmer Clashes
- Extrajudicial Killings
- State Repression of Protests
- Mass Atrocities by State Forces
- Forced Displacement by State
- Arbitrary Detention with Violence

---

## 3. Geographic Inconsistencies (CRITICAL)

### 3.1 Mismatched Country-City Pairs

The training data contains geographically impossible combinations:

| Country (in data) | City (in data) | Actual Location |
|-------------------|----------------|-----------------|
| Uganda | Misrata | Misrata is in Libya |
| Burkina Faso | Nairobi | Nairobi is in Kenya |
| Kenya | Beledweyne | Beledweyne is in Somalia |
| Egypt | Jos | Jos is in Nigeria |
| Egypt | Bahir Dar | Bahir Dar is in Ethiopia |
| Somalia | Ndjamena | N'Djamena is in Chad |
| Somalia | Sirte | Sirte is in Libya |
| Niger | Goma-Bukavu | Goma/Bukavu are in DRC |
| Ethiopia | Moundou | Moundou is in Chad |
| South Sudan | Port Sudan | Port Sudan is in Sudan |
| South Sudan | El Fasher-Nyala | El Fasher/Nyala are in Sudan |
| Cameroon | Lamu | Lamu is in Kenya |
| Mozambique | Bambari | Bambari is in CAR |

**Root cause:** The data generation script (`create_hybrid_training_data_v4.py`) randomly combines countries, regions, and cities independently without validating geographic coherence.

### 3.2 Region-Country Mismatches

The data contains regions placed in wrong countries:
- "Oromia Region" with "Uganda" (Oromia is in Ethiopia)
- "Zamfara State" with various non-Nigerian countries (Zamfara is in Nigeria)
- "Unity State" with "Kenya" (Unity State is in South Sudan)
- "Kaduna State" with "Egypt" (Kaduna is in Nigeria)

---

## 4. 5W1H Schema Issues

### 4.1 Who vs Whom (CRITICAL)

**Documentation explicitly distinguishes:**
- **WHO** = Actor/Perpetrator (who committed the violence)
- **WHOM** = Victim (who was affected)

**Current entity schema in `pipeline/config.py`:**
```python
# WHO: PERPETRATOR, VICTIM, TARGET, ORGANIZATION, GOVERNMENT
```

**Issue:** The VICTIM entity is categorized under "WHO" but documentation clearly separates actors from victims:

> "For each news article, you will: ✅ Mark entities (actors, victims, locations, dates)"
> "Fill 5W1H TEMPLATE - Who: [Actor] - What: [Event type] - Whom: [Victim]"

**Required Change:** Restructure to proper 5W1H:
- **WHO (4)**: PERPETRATOR, TARGET, ORGANIZATION, GOVERNMENT
- **WHOM (1)**: VICTIM
- **WHAT (4)**: EVENT_TYPE, ACTION, WEAPON, VIOLENCE_TYPE
- **WHEN (4)**: DATE, TIME, DURATION, FREQUENCY
- **WHERE (7)**: COUNTRY, REGION, CITY, DISTRICT, FACILITY, GEOGRAPHIC, COORDINATES
- **HOW (4)**: CASUALTIES, INJURED, DISPLACEMENT, DAMAGE

**Total: 24 entity types (WHY category removed per requirements)**

### 4.2 WHY Category Should Be Removed

The documentation uses "5W1H" (Who, What, Whom, Where, When, How). The current implementation incorrectly adds a "WHY" category (MOTIVE, TRIGGER) which is NOT part of the standard framework and should be removed.

---

## 5. Event Type Classification Issues

### 5.1 Inconsistent Event Types

The `Taxonomy_L3` column contains generic event words:
```
massacre, mass shooting, airstrikes, abduction, ambush, clashes,
bombardment, fighting, suicide bombing, skirmish, incursion, etc.
```

**Per documentation, Level 3 should be structured categories like:**
- Armed Clash/Battle
- Ambush (with L4: Roadside Ambush, IED Ambush, Complex Ambush)
- Rebel Attack on Government Position
- Bombing/Explosive Attack (with L4: Suicide Bombing, Car/Vehicle Bombing, Roadside IED)
- Armed Assault (with L4: Mass Shooting/Rampage, Coordinated Multi-Site Attack)
- Kidnapping/Hostage-Taking (Terrorism)
- etc.

### 5.2 Classification Decision Rules Not Implemented

The Taxonomy document provides detailed classification criteria and distinguishing features for each category that the current implementation ignores:

**Example for "Armed Clash/Battle":**
- Both sides engaged in fighting (not one-sided)
- Use of military weapons
- Combat typically involves exchange of fire
- Usually involving combatants on both sides

The current implementation doesn't distinguish between:
- Reciprocal combat (battle/clash) vs one-sided attack (assault)
- Civilian targeting (terrorism) vs combatant targeting (insurgency)
- Criminal motivation vs political motivation

### 5.3 Taxonomy Classification Process Not Followed

**Documentation specifies a 4-step decision process:**

**STEP 1: Identify Actor Type**
- State forces? → Consider State Violence or Political Violence
- Non-state armed group? → Likely Political or Criminal Violence
- Communal groups? → Likely Communal Violence

**STEP 2: Identify Motivation**
- Political change/control? → Political Violence
- Economic/profit? → Criminal Violence
- Identity/resources? → Communal Violence

**STEP 3: Identify Target**
- Government/military? → Political Violence
- Civilians (by state)? → State Violence Against Civilians
- Symbolic/terror target? → Terrorism
- Other community? → Communal Violence

**STEP 4: Apply Hierarchy**
- Choose Level 1 category
- Choose Level 2 sub-category
- Choose Level 3 specific type
- Choose Level 4 detailed subtype (if applicable)

**Implementation Issue:** The synthetic generator assigns taxonomy randomly without following this decision tree. It produces events classified as generic "Violence" without considering actor type, motivation, or target.

### 5.4 Classification Examples from Guidelines (Not Implemented)

**Example 1: Market Bombing**
```
Text: "A suicide bomber detonated at a crowded market in Maiduguri, killing 32 civilians. Boko Haram claimed responsibility."

Classification Process:
- Actor: Boko Haram (designated terrorist group)
- Target: Civilians in public place
- Method: Suicide bombing
- Motivation: Terror/political-religious

→ Level 1: POLITICAL VIOLENCE
→ Level 2: Terrorism
→ Level 3: Bombing/Explosive Attack
→ Level 4: Suicide Bombing
```

**Example 2: Military Clash**
```
Text: "Rebels clashed with government forces in Gao region, Mali. The battle lasted several hours and left 15 soldiers and 8 rebels dead."

Classification Process:
- Actor: Rebels (armed opposition group)
- Target: Government military
- Action: Armed combat/battle
- Motivation: Political (anti-government insurgency)

→ Level 1: POLITICAL VIOLENCE
→ Level 2: Rebellion/Armed Insurgency
→ Level 3: Armed Clash/Battle
```

**Example 3: Farmer-Herder Violence**
```
Text: "At least 20 people were killed in clashes between Fulani herders and farming communities in Benue State over grazing rights and crop damage."

Classification Process:
- Actor: Fulani herders AND farmers (communal groups)
- Target: Each other (communal conflict)
- Motivation: Resource competition (land use)

→ Level 1: COMMUNAL VIOLENCE
→ Level 2: Pastoralist-Farmer Clashes
→ Level 3: Grazing Conflict
```

**Implementation Issue:** Current training data doesn't follow these classification patterns. All events are labeled with generic "Violence" instead of the specific 4-level hierarchy.

---

## 6. Data Quality Issues

### 6.1 Semantic Incoherence in Generated Descriptions

Sample from training.csv (SYNTH_V4_00000):
```
"Following failed disarmament talks, M23 and ADF launched a massacre on
trading caravans near the church in Misrata, Oromia Region, Uganda on
December 14th through December 17th overnight. Armed with technicals,
fighters killed 43 traders for more than twelve hours, leaving
approximately 200 killed and more than 218 injured."
```

**Issues:**
1. M23 (DRC-based) and ADF (DRC-based) operating together in "Uganda" at "Misrata" (Libya)
2. "Oromia Region" is in Ethiopia, not Uganda
3. "overnight" but also "for more than twelve hours" - temporal inconsistency
4. "killed 43 traders" then "leaving approximately 200 killed" - casualty inconsistency
5. "December 14th through December 17th overnight" - date range with "overnight" is contradictory

### 6.2 All Training Data is Synthetic

The entire dataset (10,000 rows) is labeled:
```
Notes: "Synthetic training data V4 - semantic consistency fixes"
Annotator_Name: "VioNER-Generator-V4"
```

No real annotated data from actual news articles, as the guidelines intended.

---

## 7. Knowledge Base vs Training Data Mismatch

### 7.1 KB Contains Correct Geographic Information

`pipeline/kb.py` correctly defines:
```python
CONFLICT_CITIES: {
    "beledweyne": {"country": "Somalia", "region": "Hiiraan"},
    "maiduguri": {"country": "Nigeria", "region": "Borno"},
    ...
}
```

But this knowledge is **not used** during training data generation to validate geographic coherence.

### 7.2 Armed Groups Not Tied to Operating Regions

The KB correctly associates groups with countries:
```python
"m23": ArmedGroup(name="M23", country="DRC", region="Central Africa")
"al-shabaab": ArmedGroup(name="Al-Shabaab", country="Somalia", region="East Africa")
```

But training data shows these groups operating in random countries.

---

## 8. Frontend/Backend Alignment Issues

### 8.1 StructuredEvent Missing "Whom"

`frontend/src/types/index.ts`:
```typescript
export interface StructuredEvent {
  who: string[]
  what: string[]
  when: string[]
  where: string[]
  how: string[]  // Missing "whom" despite guidelines separating Who/Whom
}
```

### 8.2 Taxonomy Interface Matches Documentation

The frontend `Taxonomy` interface is correct:
```typescript
export interface Taxonomy {
  level_1: string
  level_2: string | null
  level_3: string | null
}
```

But the backend doesn't populate these correctly.

---

## 9. Summary of Required Fixes

### High Priority (Blocking Issues)

1. **Restructure to 5W1H Framework**: Separate WHO and WHOM categories:
   - WHO (4): PERPETRATOR, TARGET, ORGANIZATION, GOVERNMENT
   - WHOM (1): VICTIM
   - Remove WHY category (MOTIVE, TRIGGER)
   - Total: 24 entity types

2. **Fix Taxonomy L1**: Implement the 4 documented categories (POLITICAL VIOLENCE, CRIMINAL VIOLENCE, COMMUNAL VIOLENCE, STATE VIOLENCE AGAINST CIVILIANS)

3. **Fix Taxonomy L2**: Implement the 18 intermediate types with proper parent-child relationships

4. **Fix Taxonomy L3/L4**: Implement specific event types per documentation

5. **Fix Geographic Consistency**: City-Country-Region must be validated using the KB before generating training data

6. **Implement Entity Classification Rules**: Follow the guidelines for each entity type:
   - Actor spans must be complete noun phrases (not just "militants" but "armed militants linked to AQIM")
   - Victim types must be normalized (Civilian/Combatant/Mixed/Infrastructure/Unknown)
   - Locations must follow the specificity hierarchy (site → village → city → district → region → country)
   - Dates must be normalized to YYYY-MM-DD format
   - Weapons must be categorized (Firearms/Explosives/Vehicles/Edged/Fire/Heavy)
   - Tactical methods must be separate from weapons

7. **Implement Taxonomy Classification Process**: Follow the 4-step decision tree (Actor Type → Motivation → Target → Hierarchy)

### Medium Priority

8. **Add Coreference Resolution**: Link multiple mentions of same entity (Name → Pronoun, Name → Description, etc.)

9. **Fix Semantic Coherence**: Ensure generated descriptions don't have internal contradictions

### Low Priority

10. **Real Data Integration**: Supplement synthetic data with real annotated examples

11. **Confidence Scoring**: Implement annotation confidence as specified in guidelines

12. **Multi-label Support**: Allow events that span multiple taxonomy categories

---

# PART II: ENTITY CLASSIFICATION RULES (5W1H Framework)

---

## 10. Entity Framework Overview

This section defines the classification rules for the 24 entity types used in the VioNER system following the **5W1H framework**:

| Category | Description | Entity Types | Count |
|----------|-------------|--------------|-------|
| **WHO** | Actors/Perpetrators | PERPETRATOR, TARGET, ORGANIZATION, GOVERNMENT | 4 |
| **WHOM** | Victims | VICTIM | 1 |
| **WHAT** | Event/Action | EVENT_TYPE, ACTION, WEAPON, VIOLENCE_TYPE | 4 |
| **WHEN** | Temporal | DATE, TIME, DURATION, FREQUENCY | 4 |
| **WHERE** | Location | COUNTRY, REGION, CITY, DISTRICT, FACILITY, GEOGRAPHIC, COORDINATES | 7 |
| **HOW** | Method/Impact | CASUALTIES, INJURED, DISPLACEMENT, DAMAGE | 4 |

**Total: 24 entity types**

Each entity type has:
- **Definition**: What this entity represents
- **Include**: What text spans should be tagged with this label
- **Exclude**: What should NOT be tagged with this label
- **Normalization**: How to standardize the extracted text
- **Examples**: Real examples from African conflict reporting
- **Edge Cases**: How to handle ambiguous situations

---

## 11. WHO Category (4 Entity Types) - Actors/Perpetrators

### 11.1 PERPETRATOR

**Definition:** The person, group, or organization that commits/perpetrates the violence. The actor who initiates or carries out the violent action.

**Include:**
- Named armed organizations: "Boko Haram", "Al-Shabaab", "M23 rebels", "RSF militia"
- Descriptive references to attackers: "armed men", "gunmen", "militants", "insurgents", "attackers"
- State forces when they commit violence: "police opened fire", "soldiers attacked"
- Specific individuals: "the suicide bomber", "the assailant", "a lone gunman"
- Ethnic/communal groups as aggressors: "Fulani herders", "ethnic militia"
- Multiple actors: "Boko Haram and ISWAP fighters", "armed bandits and militia"

**Exclude:**
- Inanimate objects: "the bomb", "the explosion", "IED" (these are WEAPON, not PERPETRATOR)
- Passive voice without actor: "12 were killed" → mark actor as Unknown
- Organizations responding/reporting: "Army confirmed" → use GOVERNMENT or ORGANIZATION
- Victims who defend themselves (unless they escalate to become attackers)

**Normalization Rules:**
1. Use full organization name: "Boko Haram" not "BH"
2. Expand acronyms: "Al-Qaeda in the Islamic Maghreb (AQIM)"
3. Consistent naming: Always "Al-Shabaab" not "Shabaab" or "Al Shabab"
4. For descriptive terms, keep as-is: "gunmen", "armed men", "militants"
5. For state forces, specify country: "Nigerian military" not just "military"
6. For unknown: "Unknown gunmen", "Unidentified armed men"

**Examples:**
```
✅ "Boko Haram insurgents attacked..." → PERPETRATOR: "Boko Haram insurgents"
✅ "Armed militants believed to be linked to JNIM stormed..." → PERPETRATOR: "Armed militants believed to be linked to JNIM"
✅ "A suicide bomber detonated..." → PERPETRATOR: "A suicide bomber"
✅ "RSF forces shelled..." → PERPETRATOR: "RSF forces"
✅ "Fulani herders raided..." → PERPETRATOR: "Fulani herders"
❌ "The explosion killed..." → No perpetrator (explosion is not an actor)
❌ "12 people were killed..." → PERPETRATOR: Unknown (passive voice)
```

**Edge Cases:**
- If text says "believed to be" or "suspected": Include but mark confidence as Low
- If multiple groups: Include all as single span "Al-Shabaab and ISIS fighters" or separate if clearly distinct actors
- If pronoun ("They fled"): Link via coreference to named entity

---

### 11.2 TARGET

**Definition:** Military or strategic targets of violence. Physical installations, positions, or convoys that are attacked. NOT civilian victims.

**Include:**
- Military installations: "military base", "army barracks", "checkpoint"
- Government positions: "police station", "government convoy"
- Strategic locations: "RSF positions", "rebel headquarters"
- Vehicles/convoys: "military convoy", "UN peacekeeping patrol"
- Symbolic targets: "presidential palace", "parliament building"

**Exclude:**
- Civilian victims (use VICTIM): "civilians", "farmers"
- Buildings as locations (use FACILITY): "near the hospital"
- Geographic locations (use CITY, REGION, etc.)

**Examples:**
```
✅ "attacked a military base" → TARGET: "military base"
✅ "stormed the police station" → TARGET: "police station"
✅ "ambushed the UN convoy" → TARGET: "UN convoy"
✅ "shelled RSF positions" → TARGET: "RSF positions"
❌ "attacked civilians in the market" → VICTIM, not TARGET
❌ "occurred near the hospital" → FACILITY (as location reference)
```

**Edge Cases:**
- Dual-use facilities (market used as target vs. location): Context determines - if deliberately targeted, use TARGET
- Peacekeepers: Can be both TARGET (as military target) and VICTIM (if casualties)

---

### 11.3 ORGANIZATION

**Definition:** Non-combatant organizations mentioned in the article, typically those reporting, responding, or providing humanitarian assistance. NOT armed groups.

**Include:**
- Humanitarian organizations: "Red Cross", "Doctors Without Borders", "UNICEF"
- International bodies: "UN", "African Union", "UNHCR"
- NGOs: "Oxfam", "Save the Children", "Human Rights Watch"
- Media organizations: "Reuters", "AFP", "Al Jazeera"
- Local organizations: "Nigeria Red Cross Society"

**Exclude:**
- Armed groups (use PERPETRATOR): "Al-Shabaab", "Boko Haram"
- Government forces (use GOVERNMENT): "Nigerian Army"
- Peacekeeping forces when acting militarily (use GOVERNMENT)

**Examples:**
```
✅ "UNICEF reported..." → ORGANIZATION: "UNICEF"
✅ "Red Cross is providing assistance" → ORGANIZATION: "Red Cross"
✅ "according to Human Rights Watch" → ORGANIZATION: "Human Rights Watch"
✅ "African Union peacekeepers confirmed" → ORGANIZATION: "African Union" (reporting role)
❌ "Al-Shabaab militants" → PERPETRATOR, not ORGANIZATION
```

---

### 11.4 GOVERNMENT

**Definition:** State entities, government forces, or official bodies mentioned in the article. Includes military, police, and government officials when NOT acting as perpetrators.

**Include:**
- Military forces (responding/reporting): "Army confirmed", "military sources say"
- Police forces: "police are investigating", "local police"
- Government officials: "the president condemned", "ministry spokesperson"
- Government entities: "Sudanese government", "Ethiopian authorities"
- Peacekeeping forces: "AMISOM troops responded", "UN peacekeepers confirmed"

**Exclude:**
- Government forces as perpetrators (use PERPETRATOR): "police opened fire on protesters"
- International organizations (use ORGANIZATION): "UN said" (unless military operation)
- Non-government armed groups: "RSF militia" (use PERPETRATOR)

**Critical Distinction:**
- **PERPETRATOR**: State forces DOING violent action ("Army attacked", "Police shot protesters")
- **GOVERNMENT**: State forces responding/reporting/confirming ("Army confirmed the attack", "Police are investigating")

**Examples:**
```
✅ "Nigerian Army confirmed the incident" → GOVERNMENT: "Nigerian Army"
✅ "Police are searching for suspects" → GOVERNMENT: "Police"
✅ "Government spokesperson said..." → GOVERNMENT: "Government spokesperson"
✅ "AMISOM forces responded to the attack" → GOVERNMENT: "AMISOM forces"
❌ "Police opened fire on protesters" → PERPETRATOR: "Police"
❌ "Army conducted airstrikes on villages" → PERPETRATOR: "Army"
```

---

## 12. WHOM Category (1 Entity Type) - Victims

### 12.1 VICTIM

**Definition:** The person(s), group(s), or entities that suffer harm from the violence. Those who are killed, injured, kidnapped, or otherwise affected. This is the **WHOM** in the 5W1H framework - distinct from WHO (actors).

**Include:**
- Specific individuals: "the mayor", "aid workers", "journalist John Smith"
- Groups: "civilians", "protesters", "worshippers", "students", "farmers"
- Demographic descriptions: "women and children", "displaced persons", "refugees"
- Numbers with descriptions: "12 people", "at least 45 civilians", "dozens of villagers"
- Combatants as victims: "8 soldiers", "5 militants killed"
- Mixed: "5 soldiers and 8 civilians"

**Exclude:**
- Infrastructure targets (use TARGET or FACILITY): "the hospital", "the bridge"
- The perpetrators' own casualties in one-sided attacks (these go with perpetrator description)
- Organizations as reporters: "Red Cross says..." (use ORGANIZATION)

**Normalization Categories:**
- **Civilian**: Unarmed, non-combatant persons
- **Combatant**: Military, police, armed group members
- **Mixed**: Both civilian and combatant victims
- **Unknown**: Type cannot be determined

**Casualty Recording:**
- Deaths: Number killed
- Injuries: Number wounded/injured
- Kidnapped/Abducted: Number taken
- Displaced: Number forced to flee
- Unknown: "Casualties reported but number unclear"

**Examples:**
```
✅ "killing 32 civilians" → VICTIM: "32 civilians"
✅ "at least 15 civilians including women and children" → VICTIM: "at least 15 civilians including women and children"
✅ "8 soldiers and 5 militants dead" → VICTIM: "8 soldiers and 5 militants"
✅ "protesters" → VICTIM: "protesters"
✅ "Market-goers" (implied from "bombing at market") → VICTIM: "Market-goers (implied)"
❌ "the hospital was destroyed" → TARGET/FACILITY, not VICTIM
```

**Edge Cases:**
- If text says "at least X": Include the qualifier in the span
- If range "10-20 people": Record as range with note
- If no casualties mentioned but implied (suicide bombing at market): Note "Potential victims (casualties unknown)"

**Critical Distinction (WHO vs WHOM):**
- **WHO** = Actor/Perpetrator (who committed the violence)
- **WHOM** = Victim (who was affected by the violence)

---

## 13. WHAT Category (4 Entity Types)

### 13.1 EVENT_TYPE

**Definition:** The high-level classification of the violent event. The noun or noun phrase that categorizes what type of violence occurred.

**Include:**
- Attack types: "attack", "assault", "raid", "ambush"
- Explosive events: "bombing", "explosion", "blast"
- Mass violence: "massacre", "mass shooting", "slaughter"
- Combat: "clash", "battle", "fighting", "skirmish"
- Abductions: "kidnapping", "abduction", "hostage-taking"
- Targeted violence: "assassination", "execution"

**Exclude:**
- Action verbs (use ACTION): "attacked", "killed", "bombed"
- Weapons (use WEAPON): "IED", "gun", "machete"
- Violence category (use VIOLENCE_TYPE): "terrorism", "insurgency"

**Examples:**
```
✅ "The massacre in Giwa..." → EVENT_TYPE: "massacre"
✅ "a suicide bombing at..." → EVENT_TYPE: "suicide bombing"
✅ "the ambush occurred..." → EVENT_TYPE: "ambush"
✅ "during the raid..." → EVENT_TYPE: "raid"
✅ "clashes between..." → EVENT_TYPE: "clashes"
❌ "attacked" → ACTION, not EVENT_TYPE
❌ "terrorism" → VIOLENCE_TYPE, not EVENT_TYPE
```

---

### 13.2 ACTION

**Definition:** The specific verb or action phrase describing what the perpetrator did. The violence-indicating action word.

**Include:**
- Attack verbs: "attacked", "raided", "stormed", "assaulted"
- Killing verbs: "killed", "murdered", "assassinated", "massacred", "executed"
- Destruction verbs: "bombed", "shelled", "burned", "destroyed", "razed"
- Abduction verbs: "kidnapped", "abducted", "seized", "captured"
- Combat verbs: "clashed", "fought", "battled"
- Movement verbs with violence: "overran", "invaded", "occupied"

**Exclude:**
- Event nouns (use EVENT_TYPE): "attack", "massacre", "bombing"
- Weapons (use WEAPON): "with guns", "using IED"
- Results (use CASUALTIES/INJURED): "killing 10" - "killing" is ACTION, "10" goes to CASUALTIES

**Examples:**
```
✅ "militants attacked the village" → ACTION: "attacked"
✅ "gunmen killed 12 people" → ACTION: "killed"
✅ "rebels stormed the base" → ACTION: "stormed"
✅ "forces shelled the positions" → ACTION: "shelled"
✅ "armed men burned homes" → ACTION: "burned"
❌ "the attack killed..." → "attack" is EVENT_TYPE
```

---

### 13.3 WEAPON

**Definition:** The instruments, tools, or weapons used to perpetrate the violence. Physical objects used in the attack.

**Include:**
- Firearms: "guns", "rifles", "AK-47s", "automatic weapons", "machine guns"
- Explosives: "bomb", "IED", "grenade", "explosives", "suicide vest", "car bomb"
- Vehicles as weapons: "vehicle-borne explosives", "car bomb", "truck bomb"
- Edged weapons: "knives", "machetes", "swords", "pangas"
- Heavy weapons: "artillery", "mortars", "rocket launchers", "RPGs"
- Fire: "burned", "set ablaze" (method = arson)

**Exclude:**
- Tactics (tactical methods go to EVENT_TYPE): "ambush", "raid"
- Results of weapons: "explosion" (result, not weapon - unless "explosive device")
- Perpetrators using weapons: "gunmen" (PERPETRATOR, not WEAPON)

**Weapon Categories:**
1. **Firearms**: Small arms, automatic weapons, sniper fire
2. **Explosives**: IED, suicide bomb, car bomb, grenade, landmine
3. **Vehicles**: As weapon (ramming), as delivery mechanism
4. **Edged Weapons**: Knives, machetes, swords
5. **Fire/Arson**: Building burning, village burning
6. **Heavy Weapons**: Artillery, mortars, rockets

**Examples:**
```
✅ "armed with AK-47s and machetes" → WEAPON: "AK-47s and machetes"
✅ "using improvised explosive devices" → WEAPON: "improvised explosive devices"
✅ "rocket-propelled grenades" → WEAPON: "rocket-propelled grenades"
✅ "wearing suicide vests" → WEAPON: "suicide vests"
❌ "ambushed with guns" → "ambushed" is EVENT_TYPE/ACTION, "guns" is WEAPON
❌ "the explosion" → Result, not weapon (use "explosive device" if mentioned)
```

---

### 13.4 VIOLENCE_TYPE

**Definition:** The category or classification of violence based on the Taxonomy. Maps to taxonomy hierarchy.

**Include:**
- Political violence types: "terrorism", "insurgency", "political repression"
- Criminal violence types: "armed robbery", "banditry", "gang violence"
- Communal violence types: "ethnic violence", "sectarian violence", "communal clashes"
- Contextual types: "farmer-herder violence", "election violence"

**Exclude:**
- Specific event types (use EVENT_TYPE): "bombing", "ambush"
- Actions (use ACTION): "attacked", "killed"

**Taxonomy Mapping:**
- Level 1: POLITICAL VIOLENCE, CRIMINAL VIOLENCE, COMMUNAL VIOLENCE, STATE VIOLENCE AGAINST CIVILIANS
- Level 2: Terrorism, Rebellion/Insurgency, Election Violence, Armed Robbery, Ethnic Conflict, etc.

**Examples:**
```
✅ "terrorist attack" → VIOLENCE_TYPE: "terrorist attack"
✅ "ethnic violence erupted" → VIOLENCE_TYPE: "ethnic violence"
✅ "communal clashes" → VIOLENCE_TYPE: "communal clashes"
✅ "insurgent violence" → VIOLENCE_TYPE: "insurgent violence"
✅ "farmer-herder conflict" → VIOLENCE_TYPE: "farmer-herder conflict"
```

---

## 14. WHEN Category (4 Entity Types)

### 14.1 DATE

**Definition:** Specific dates or date ranges when the violence occurred.

**Include:**
- Absolute dates: "January 15, 2024", "March 3", "15 March"
- Relative dates: "yesterday", "last Tuesday", "three days ago", "last week"
- Date ranges: "from Monday to Wednesday", "over the weekend"
- Month/year references: "in January", "early 2024"

**Exclude:**
- Time of day (use TIME): "at dawn", "in the morning"
- Duration (use DURATION): "for three hours", "lasted all day"
- Frequency (use FREQUENCY): "daily attacks", "weekly raids"

**Normalization Rules:**
1. Convert ALL dates to YYYY-MM-DD format
2. Use article publication date as reference for relative dates
3. "yesterday" + article date (2024-03-15) = 2024-03-14
4. "last Tuesday" + article date (Friday 2024-03-15) = 2024-03-12
5. Uncertain dates: Add "(approximate)" and mark Low confidence

**Examples:**
```
✅ "on Tuesday, March 19" → DATE: "on Tuesday, March 19" (normalize to 2024-03-19)
✅ "yesterday" → DATE: "yesterday" (normalize based on article date)
✅ "last weekend" → DATE: "last weekend" (normalize to Sat-Sun before article)
✅ "December 14th through December 17th" → DATE: "December 14th through December 17th"
❌ "at dawn" → TIME, not DATE
❌ "for three hours" → DURATION, not DATE
```

---

### 14.2 TIME

**Definition:** Time of day when the violence occurred. NOT the date, but the specific time or time period within a day.

**Include:**
- Specific times: "at 3 AM", "around 10:30 PM", "08:00"
- Time periods: "at dawn", "in the morning", "overnight", "at dusk"
- General periods: "early hours", "in the afternoon", "during the night"

**Exclude:**
- Dates (use DATE): "on Tuesday", "March 15"
- Duration (use DURATION): "for three hours"

**Time Period Categories:**
- Early morning: 00:00-06:00
- Morning: 06:00-12:00
- Afternoon: 12:00-18:00
- Evening: 18:00-21:00
- Night: 21:00-00:00

**Examples:**
```
✅ "at dawn" → TIME: "at dawn"
✅ "around 3 AM" → TIME: "around 3 AM"
✅ "during the night" → TIME: "during the night"
✅ "overnight" → TIME: "overnight"
✅ "in the early hours" → TIME: "in the early hours"
❌ "on Monday overnight" → "on Monday" is DATE, "overnight" is TIME
```

---

### 14.3 DURATION

**Definition:** How long the violent event lasted. The temporal extent of the action.

**Include:**
- Specific durations: "for three hours", "lasted two days"
- Duration phrases: "throughout the night", "all day long"
- Approximate durations: "several hours", "about 45 minutes"
- Ongoing indicators: "week-long siege", "month-long offensive"

**Exclude:**
- Dates (use DATE): "from Monday to Wednesday"
- Times (use TIME): "overnight" (when indicating time of day, not duration)
- Frequency (use FREQUENCY): "daily", "repeated"

**Critical Rule:** Duration should ONLY contain pure temporal duration words, NOT event words.
- ✅ "three hours"
- ❌ "three-hour attack" (split: "three hours" = DURATION, "attack" = EVENT_TYPE)

**Examples:**
```
✅ "lasted for three hours" → DURATION: "three hours"
✅ "throughout the night" → DURATION: "throughout the night"
✅ "the siege lasted two weeks" → DURATION: "two weeks"
✅ "more than twelve hours" → DURATION: "more than twelve hours"
❌ "overnight attack" → Split into TIME: "overnight", EVENT_TYPE: "attack"
```

---

### 14.4 FREQUENCY

**Definition:** Recurring nature or pattern of violence. How often attacks occur.

**Include:**
- Frequency words: "daily attacks", "weekly raids", "monthly incursions"
- Pattern indicators: "repeated attacks", "ongoing violence", "persistent assaults"
- Sequence indicators: "the third attack this month", "another in a series"
- Escalation: "intensified operations", "escalating violence"

**Exclude:**
- Single event descriptions (no frequency)
- Duration (use DURATION): "for three hours"

**Examples:**
```
✅ "daily attacks on villages" → FREQUENCY: "daily attacks"
✅ "the third raid this week" → FREQUENCY: "third raid this week"
✅ "ongoing violence" → FREQUENCY: "ongoing violence"
✅ "repeated assaults" → FREQUENCY: "repeated assaults"
✅ "sporadic clashes" → FREQUENCY: "sporadic clashes"
```

---

## 15. WHERE Category (7 Entity Types)

### 15.1 COUNTRY

**Definition:** The nation or sovereign state where the violence occurred.

**Include:**
- Full country names: "Nigeria", "Somalia", "Democratic Republic of Congo"
- Common short forms: "DRC", "CAR"
- With articles: "the Sudan" (normalize to "Sudan")

**Normalization:**
- Use official country name
- Standard forms: "DRC" → "Democratic Republic of Congo"
- "DR Congo", "Democratic Republic of the Congo" → "DRC"

**Examples:**
```
✅ "in Nigeria" → COUNTRY: "Nigeria"
✅ "Democratic Republic of Congo" → COUNTRY: "Democratic Republic of Congo"
✅ "across Mali and Burkina Faso" → COUNTRY: "Mali", "Burkina Faso"
```

---

### 15.2 REGION

**Definition:** State, province, region, or territory within a country. First-level administrative division.

**Include:**
- States: "Borno State", "Zamfara State"
- Regions: "Tigray region", "Oromia region", "Gao region"
- Provinces: "North Kivu", "South Kivu", "Ituri Province"
- Territories: "Masisi territory"

**Exclude:**
- Countries (use COUNTRY)
- Cities (use CITY)
- Districts/Counties (use DISTRICT)

**Examples:**
```
✅ "in Borno State, Nigeria" → REGION: "Borno State"
✅ "Tigray region of Ethiopia" → REGION: "Tigray region"
✅ "North Kivu province" → REGION: "North Kivu"
❌ "Maiduguri, Borno State" → "Maiduguri" is CITY, "Borno State" is REGION
```

---

### 15.3 CITY

**Definition:** Cities, towns, or villages where the violence occurred.

**Include:**
- Major cities: "Mogadishu", "Maiduguri", "Khartoum"
- Towns: "Gao", "Baidoa", "Mubi"
- Villages: "Giwa village", "Tiloa village"
- With descriptors: "the town of Bama"

**Exclude:**
- Regions/States (use REGION)
- Specific sites within cities (use FACILITY)
- Neighborhoods/Districts (use DISTRICT)

**Examples:**
```
✅ "in Mogadishu" → CITY: "Mogadishu"
✅ "near the town of Bama" → CITY: "Bama"
✅ "Giwa village" → CITY: "Giwa village"
✅ "three villages near Mubi" → CITY: "three villages near Mubi"
```

---

### 15.4 DISTRICT

**Definition:** Sub-city areas, neighborhoods, quarters, counties, or local government areas.

**Include:**
- Neighborhoods: "Bakara district", "northern outskirts"
- Counties: "Garissa County", "Lamu County"
- Local areas: "Omdurman district", "Bakasi neighborhood"
- Quarters: "the old quarter"

**Critical Rule:** Counties should be tagged as DISTRICT, not REGION.

**Examples:**
```
✅ "Omdurman district" → DISTRICT: "Omdurman district"
✅ "Garissa County" → DISTRICT: "Garissa County"
✅ "in the northern outskirts" → DISTRICT: "northern outskirts"
✅ "Bakara Market area" → DISTRICT: "Bakara Market area"
```

---

### 15.5 FACILITY

**Definition:** Buildings, installations, infrastructure, or specific sites where violence occurred or was targeted.

**Include:**
- Educational: "school", "university", "Garissa University"
- Medical: "hospital", "clinic", "Al-Nao Hospital"
- Religious: "church", "mosque", "Central Mosque"
- Military: "military base", "army barracks", "checkpoint"
- Government: "government building", "court", "prison"
- Commercial: "market", "hotel", "restaurant"
- Humanitarian: "UN compound", "refugee camp", "IDP camp"
- Infrastructure: "power plant", "water treatment facility", "bridge"

**Exclude:**
- Cities (use CITY)
- Geographic features (use GEOGRAPHIC)

**Examples:**
```
✅ "attacked the hospital" → FACILITY: "hospital"
✅ "near the UN compound" → FACILITY: "UN compound"
✅ "at Garissa University" → FACILITY: "Garissa University"
✅ "bombed the market" → FACILITY: "market"
✅ "the church in Maiduguri" → FACILITY: "church"
```

---

### 15.6 GEOGRAPHIC

**Definition:** Natural geographic features, borders, and physical landscape descriptions.

**Include:**
- Water features: "Lake Chad basin", "Niger River", "Nile River valley"
- Terrain: "Sahel region", "Sambisa Forest", "mountainous terrain"
- Borders: "Nigeria-Cameroon border", "Somali border"
- Valleys/basins: "Great Rift Valley", "Congo River basin"

**Exclude:**
- Administrative regions (use REGION)
- Cities (use CITY)

**Examples:**
```
✅ "in the Lake Chad basin" → GEOGRAPHIC: "Lake Chad basin"
✅ "near the Somali border" → GEOGRAPHIC: "Somali border"
✅ "in the Sahel" → GEOGRAPHIC: "Sahel"
✅ "along the Niger River" → GEOGRAPHIC: "Niger River"
✅ "in the dense forest" → GEOGRAPHIC: "dense forest"
```

---

### 15.7 COORDINATES

**Definition:** GPS coordinates, latitude/longitude, or precise location markers.

**Include:**
- Lat/Long: "11.8464, 13.0784"
- GPS format: "coordinates 9.5N, 7.8E"
- Precise locations: "at grid reference..."

**Normalization:** Convert to standard decimal format: "Lat, Long"

**Examples:**
```
✅ "at coordinates 9.5N, 7.8E" → COORDINATES: "9.5N, 7.8E"
✅ "11.8464, 13.0784" → COORDINATES: "11.8464, 13.0784"
```

---

## 16. HOW Category (4 Entity Types)

### 16.1 CASUALTIES

**Definition:** Death counts and fatality information. Number of people killed.

**Include:**
- Specific numbers: "12 killed", "at least 45 dead"
- Descriptive: "dozens died", "mass casualties"
- Ranges: "between 10 and 20 killed"
- Qualifiers: "at least", "approximately", "more than"

**Exclude:**
- Injured (use INJURED)
- Displaced (use DISPLACEMENT)
- Victims as entities (use VICTIM)

**Examples:**
```
✅ "killing 32 people" → CASUALTIES: "32" (or "32 people")
✅ "at least 45 dead" → CASUALTIES: "at least 45"
✅ "approximately 200 killed" → CASUALTIES: "approximately 200"
✅ "dozens died" → CASUALTIES: "dozens"
❌ "30 injured" → INJURED, not CASUALTIES
```

---

### 16.2 INJURED

**Definition:** Injury counts. Number of people wounded but not killed.

**Include:**
- Specific numbers: "30 wounded", "injured 15"
- Descriptive: "several injured", "critically wounded"
- Medical status: "hospitalized", "in critical condition"

**Exclude:**
- Deaths (use CASUALTIES)
- Kidnapped (note separately)

**Examples:**
```
✅ "30 others were injured" → INJURED: "30"
✅ "at least 165 wounded" → INJURED: "at least 165"
✅ "several injured" → INJURED: "several"
✅ "critically wounded" → INJURED: "critically wounded"
```

---

### 16.3 DISPLACEMENT

**Definition:** Forced movement of people. Numbers displaced, refugees created, or evacuations.

**Include:**
- Displacement numbers: "10,000 fled", "displaced 50,000"
- Descriptive: "mass displacement", "forced to flee"
- Status: "internally displaced", "became refugees"
- Actions: "evacuated", "fled their homes"

**Examples:**
```
✅ "displacing approximately 450,000 civilians" → DISPLACEMENT: "approximately 450,000"
✅ "mass displacement" → DISPLACEMENT: "mass displacement"
✅ "10,000 people fled" → DISPLACEMENT: "10,000 fled"
✅ "causing mass displacement" → DISPLACEMENT: "mass displacement"
```

---

### 16.4 DAMAGE

**Definition:** Property damage, infrastructure destruction, or material impact.

**Include:**
- Destruction: "destroyed homes", "burned villages"
- Specific damage: "50 houses razed", "market destroyed"
- Infrastructure: "damaged roads", "destroyed bridges"
- Looting: "looted shops", "pillaged warehouses"

**Examples:**
```
✅ "torching hundreds of structures" → DAMAGE: "torching hundreds of structures"
✅ "burned 20 homes" → DAMAGE: "burned 20 homes"
✅ "destroying critical infrastructure" → DAMAGE: "destroying critical infrastructure"
✅ "looted the village" → DAMAGE: "looted the village"
```

---

## 17. General Annotation Rules

### 17.1 Entity Span Rules

1. **Complete Noun Phrases**: Always mark the COMPLETE noun phrase including all modifiers
   - ✅ "Armed militants believed to be linked to JNIM"
   - ❌ "militants" (too narrow)

2. **Include Qualifiers**: Include "at least", "approximately", "more than", "about"
   - ✅ "at least 32 civilians"
   - ❌ "32 civilians" (missing qualifier)

3. **Numbers with Context**: Include the number AND what it refers to
   - ✅ "45 people killed"
   - ❌ "45" (missing context)

### 17.2 Coreference Rules

Link multiple mentions of the same entity:

**Pattern 1: Name → Pronoun**
```
"Al-Shabaab attacked the base. They killed 10 soldiers."
→ "Al-Shabaab" = "They"
```

**Pattern 2: Name → Description**
```
"Boko Haram bombed a market. The militants then fled."
→ "Boko Haram" = "The militants"
```

**Pattern 3: Name → Acronym**
```
"The Lord's Resistance Army raided villages. The LRA has been active..."
→ "Lord's Resistance Army" = "LRA"
```

**Pattern 4: General → Specific**
```
"Armed men attacked the village. Witnesses identified the attackers as Fulani herders."
→ "Armed men" = "the attackers" = "Fulani herders"
```

### 17.3 Handling Missing Information

- **NEVER leave blank** - mark as "Unknown" or "Not mentioned"
- **DO NOT infer** from other sources or background knowledge
- **Only annotate what the text explicitly states**

### 17.4 Confidence Scoring

| Score | Description |
|-------|-------------|
| 0.9-1.0 | Very high confidence, clear and unambiguous |
| 0.7-0.8 | High confidence, minor uncertainty |
| 0.5-0.6 | Medium confidence, some ambiguity |
| 0.3-0.4 | Low confidence, significant ambiguity |
| 0.1-0.2 | Very low confidence, major uncertainty |

---

## 18. Common Mistakes to Avoid

| Mistake | Wrong | Correct |
|---------|-------|---------|
| Merging events | Two attacks = one event | Each distinct incident = separate event |
| Too narrow spans | "militants" | "armed militants linked to AQIM" |
| Using external knowledge | Assume Al-Shabaab because location | Only what article states |
| Wrong entity type | FACILITY as TARGET | Distinguish based on context |
| Missing coreference | "They" as new entity | Link to antecedent |
| Inanimate perpetrator | "The bomb killed..." | Bomb is WEAPON, actor is Unknown |
| Conflating types | "overnight attack" | TIME: "overnight", EVENT_TYPE: "attack" |
| Wrong taxonomy level | Jump to Level 4 | Complete all levels 1-2-3-4 |
| Ignoring ambiguity | Guess when uncertain | Document ambiguity, mark low confidence |

---

# APPENDIX

## Document References

- **1-Taxonomy.docx**: Hierarchical Violent Event Taxonomy for African Conflicts (Version 1.0)
- **2-Annotation-Guidelines.docx**: Violent Event Annotation Guidelines - Training Data Collection Manual (Version 1.0)
- **training.csv**: Current training data (10,000 synthetic rows, Version V4)
- **pipeline/config.py**: Entity label definitions (BIO format)
- **pipeline/kb.py**: Knowledge base (armed groups, countries, cities)
- **create_hybrid_training_data_v4.py**: Synthetic data generator

---

## Document Version

- **Version:** 1.0
- **Entity Types:** 24 (5W1H framework)
- **Categories:** WHO (4), WHOM (1), WHAT (4), WHEN (4), WHERE (7), HOW (4)
- **Framework:** 5W1H (Who, Whom, What, When, Where, How)
- **Last Updated:** December 2025
