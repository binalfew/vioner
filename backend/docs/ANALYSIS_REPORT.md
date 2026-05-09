# VioNER Analysis Report: Data Generation and Annotation Issues

**Date:** December 2025
**Analyst:** Claude Code
**Purpose:** Identify discrepancies between implementation and documentation guidelines

---

## Executive Summary

The current training data (`data/annotations/training.csv`) contains **critical issues** that fundamentally deviate from the Taxonomy and Annotation Guidelines documents. The synthetic data generation script produces semantically inconsistent and geographically impossible data that would train a model to learn incorrect patterns.

---

## 1. Taxonomy Hierarchy Issues (CRITICAL)

### 1.1 Incorrect Level 1 Categories

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

### 1.2 Missing Taxonomy Level Structure

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

## 2. Geographic Inconsistencies (CRITICAL)

### 2.1 Mismatched Country-City Pairs

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

### 2.2 Region-Country Mismatches

The data contains regions placed in wrong countries:
- "Oromia Region" with "Uganda" (Oromia is in Ethiopia)
- "Zamfara State" with various non-Nigerian countries (Zamfara is in Nigeria)
- "Unity State" with "Kenya" (Unity State is in South Sudan)
- "Kaduna State" with "Egypt" (Kaduna is in Nigeria)

---

## 3. 5W1H Schema Issues

### 3.1 Who vs Whom (CRITICAL)

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

### 3.2 WHY Category Should Be Removed

The documentation uses "5W1H" (Who, What, Whom, Where, When, How). The current implementation incorrectly adds a "WHY" category (MOTIVE, TRIGGER) which is NOT part of the standard framework and should be removed.

---

## 4. Entity Classification Rules Not Followed (CRITICAL)

The Annotation Guidelines (`2-Annotation-Guidelines.docx`) provide explicit rules for what to include/exclude for each entity type. The current implementation violates many of these rules.

**See:** `ENTITY_CLASSIFICATION_RULES.md` for the complete 26-entity-type rule set extracted from the guidelines.

### 4.1 Actor (WHO) Classification Rules

**Documentation specifies:**

**Include:**
- ✅ Named organizations: "Boko Haram," "Al-Shabaab," "M23 rebels"
- ✅ Descriptive references: "armed men," "gunmen," "militants," "insurgents"
- ✅ State forces: "police," "military," "army," "security forces"
- ✅ Specific individuals: "suicide bomber," "the assailant"
- ✅ Ethnic/communal groups: "Fulani herders," "ethnic militia"

**Exclude:**
- ❌ Inanimate objects: "the bomb," "the explosion" (these are methods, not actors)
- ❌ Passive constructions without clear actor: "12 were killed" (mark as Unknown Actor)

**Implementation Issue:** The synthetic data generator doesn't distinguish between actors doing violent actions vs. actors responding/reporting. The guidelines specify:
- Armed forces doing violent actions → Actor/Perpetrator
- Armed forces responding/reporting → Government entity (non-perpetrator role)

### 4.2 Victim (WHOM) Classification Rules

**Documentation specifies:**

**Include:**
- ✅ Specific individuals: "the mayor," "aid workers," "journalist John Smith"
- ✅ Groups: "civilians," "protesters," "worshippers," "students"
- ✅ Organizations: "the UN compound," "the hospital"
- ✅ Demographic descriptions: "women and children," "displaced persons"
- ✅ Numbers/casualties: "12 people," "dozens of civilians"
- ✅ Infrastructure as victim (when violence targets it): "the power plant," "the bridge"

**Victim Normalization Categories:**
- Civilian (unarmed, non-combatant)
- Combatant (military, police, armed group members)
- Mixed (both civilian and combatant)
- Infrastructure
- Unknown

**Implementation Issue:** Current code doesn't normalize victim types. The `VICTIM` entity is grouped under "WHO" category instead of being a separate "WHOM" category.

### 4.3 Location (WHERE) Classification Rules

**Documentation specifies a hierarchy:**

1. **Most specific** → Specific site: "Bama market," "military base"
2. Village/neighborhood: "Giwa village," "Bakasi neighborhood"
3. City/town: "Maiduguri," "Gao"
4. District/county: "Bama district"
5. State/province/region: "Borno State," "Gao region"
6. Country: "Nigeria," "Mali"
7. **Least specific** → Sub-region: "Lake Chad Basin," "Sahel region"

**Rule:** Annotate at the most specific level mentioned.

**Implementation Issue:** The synthetic data randomly assigns:
- Cities that don't exist in the specified country
- Regions that belong to different countries
- No validation against the geographic hierarchy

### 4.4 Date/Time (WHEN) Classification Rules

**Documentation specifies date normalization:**

| Text Expression | Article Date | Normalized Date |
|-----------------|--------------|-----------------|
| "yesterday" | 2024-03-15 | 2024-03-14 |
| "last Tuesday" | 2024-03-15 (Friday) | 2024-03-12 |
| "three days ago" | 2024-03-15 | 2024-03-12 |
| "on Monday" | 2024-03-15 (Friday) | 2024-03-11 |

**Time categories:**
- Early morning (00:00-06:00)
- Morning (06:00-12:00)
- Afternoon (12:00-18:00)
- Evening (18:00-21:00)
- Night (21:00-00:00)

**Implementation Issue:** Current data has contradictory temporal expressions like:
- "December 14th through December 17th overnight" (multi-day range + single night)
- "overnight" combined with "for more than twelve hours"

### 4.5 Weapon/Method (HOW) Classification Rules

**Documentation specifies categories:**

**Firearms:** Small arms (pistols, rifles), Automatic weapons, Sniper fire, Unspecified guns

**Explosives:** IED, Suicide bomb/vest, Car bomb/VBIED, Grenade, Landmine, Unspecified explosives

**Vehicles:** As weapon (ramming), As explosive delivery

**Edged Weapons:** Knives, Machetes, Swords

**Fire/Arson:** Building burning, Village burning

**Heavy Weapons:** Artillery, Mortars, Rocket launchers

**Tactical Methods (separate from weapons):**
- Ambush
- Raid
- Assault/frontal attack
- Siege
- Hit-and-run
- Coordinated multi-site attack
- Targeted killing
- Mass shooting/rampage

**Implementation Issue:** The current schema conflates:
- `WEAPON` (physical instruments)
- `ACTION` (verbs like "attacked", "killed")
- `EVENT_TYPE` (tactical methods like "ambush", "raid")

The guidelines clearly separate weapons from tactical methods.

### 4.6 Entity Span Rules

**Documentation specifies:**
> "Highlight the complete noun phrase"

**Good examples:**
- ✅ "[Armed militants believed to be linked to JNIM] attacked…"
- ✅ "[The rebel group's fighters] stormed…"
- ✅ "[A suicide bomber] detonated…"

**Bad examples:**
- ❌ "[militants] attacked…" (too narrow - missing modifiers)

**Implementation Issue:** No validation that entity spans capture complete noun phrases.

### 4.7 Coreference Resolution Rules

**Documentation specifies patterns to handle:**

**Pattern 1: Name → Pronoun**
> "Al-Shabaab attacked the base. **They** killed 10 soldiers."
> "Al-Shabaab" = "They"

**Pattern 2: Name → Description**
> "Boko Haram bombed a market. **The militants** then fled."
> "Boko Haram" = "The militants"

**Pattern 3: Name → Acronym**
> "The Lord's Resistance Army raided villages. **The LRA** has been active..."

**Pattern 4: General → Specific**
> "Armed men attacked the village. Witnesses identified **the attackers** as **Fulani herders**."

**Implementation Issue:** The synthetic data generator creates independent sentences without coreference chains. Each mention is standalone rather than being linked.

### 4.8 Common Mistakes Listed in Guidelines

The guidelines explicitly warn against these mistakes that the current implementation makes:

| Mistake | Wrong Approach | Correct Approach |
|---------|----------------|------------------|
| Merging events | Treating sequential attacks as single event | Each distinct incident is separate event |
| Incomplete coreference | Not linking "The militants" back to "Al-Shabaab" | Identify all mentions of same entity |
| Using external knowledge | "I know Al-Shabaab operates here, so they probably did it" | Only annotate what article explicitly states |
| Too narrow entity spans | Marking only "militants" | Mark complete noun phrase "armed militants linked to AQIM" |
| Wrong taxonomy level | Jumping directly to Level 4 | Complete all hierarchical levels 1-2-3-4 |
| Ignoring ambiguity | Guessing when uncertain | Document ambiguity, mark low confidence |

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

## 10. Appendix: Document References

- **1-Taxonomy.docx**: Hierarchical Violent Event Taxonomy for African Conflicts (Version 1.0)
- **2-Annotation-Guidelines.docx**: Violent Event Annotation Guidelines - Training Data Collection Manual (Version 1.0)
- **ENTITY_CLASSIFICATION_RULES.md**: Complete entity classification rules for all 26 entity types (extracted from guidelines)
- **training.csv**: Current training data (10,000 synthetic rows, Version V4)
- **pipeline/config.py**: Entity label definitions (26 types, BIO format)
- **pipeline/kb.py**: Knowledge base (armed groups, countries, cities)
- **create_hybrid_training_data_v4.py**: Synthetic data generator
