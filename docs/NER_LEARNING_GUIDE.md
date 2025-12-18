# Named Entity Recognition: A Complete Guide

## Master Your Thesis Defense

**Author:** Binalfew Kassa Mekonnen
**Institution:** Addis Ababa University
**Purpose:** Complete understanding of NER for Knowledge Discovery from Free Text
**Last Updated:** December 2025

---

## How to Use This Guide

This guide is designed to make you an **expert** in NER. Read it in order, but return to specific sections when preparing for your thesis defense.

Each section includes:
- **The Concept** - What it is
- **The Intuition** - Why it makes sense
- **The Math** (where needed) - The technical details
- **Thesis Defense Tips** - How to explain it to your committee

---

## Table of Contents

### Part I: Foundations
1. [What is Named Entity Recognition?](#1-what-is-named-entity-recognition)
2. [The BIO Tagging Scheme](#2-the-bio-tagging-scheme)
3. [Your Entity Schema: The 5W1H Framework](#3-your-entity-schema-the-5w1h-framework)

### Part II: The Data Pipeline
4. [From Raw Text to Training Data](#4-from-raw-text-to-training-data)
5. [Your Enhanced Dataset](#5-your-enhanced-dataset)
6. [Data Quality and Class Imbalance](#6-data-quality-and-class-imbalance)

### Part III: The Model
7. [Neural Networks: The Foundation](#7-neural-networks-the-foundation)
8. [Transformers and Attention](#8-transformers-and-attention)
9. [BERT: Why It's Revolutionary](#9-bert-why-its-revolutionary)
10. [Fine-tuning BERT for NER](#10-fine-tuning-bert-for-ner)
11. [Inference: How Prediction Works](#11-inference-how-prediction-works)

### Part IV: Training Deep Dive
12. [The Training Loop Explained](#12-the-training-loop-explained)
13. [Loss Functions and FocalLoss](#13-loss-functions-and-focalloss)
14. [Optimization and Learning](#14-optimization-and-learning)
15. [Preventing Overfitting](#15-preventing-overfitting)

### Part V: Evaluation
16. [Metrics That Matter](#16-metrics-that-matter)
17. [5W1H Evaluation Framework](#17-5w1h-evaluation-framework)

### Part VI: Your System
18. [VioNER Architecture](#18-vioner-architecture)
19. [The Knowledge Base](#19-the-knowledge-base)
20. [Thesis Defense Preparation](#20-thesis-defense-preparation)

### Appendices
- [A. Glossary](#appendix-a-glossary)
- [B. Common Questions and Answers](#appendix-b-common-questions-and-answers)
- [C. Key Papers to Reference](#appendix-c-key-papers-to-reference)

---

# Part I: Foundations

## 1. What is Named Entity Recognition?

### 1.1 The Core Idea

**Named Entity Recognition (NER)** is teaching a computer to read text and identify the important "things" mentioned in it - people, places, organizations, dates, and more.

**Think of it like this:**

Imagine you're a journalist reading this headline:
> "Al Shabaab militants attacked a military base in Mogadishu on Monday, killing 15 soldiers."

You naturally identify:
- **Who attacked?** → Al Shabaab militants
- **What happened?** → attacked
- **Where?** → Mogadishu, military base
- **When?** → Monday
- **How many casualties?** → 15 soldiers killed

NER teaches a computer to do exactly this, automatically.

### 1.2 Why is NER Hard?

**Challenge 1: Ambiguity**
```
"Washington announced new sanctions"
```
Is "Washington" a person (George Washington) or a place (Washington D.C.)?
The computer must understand context.

**Challenge 2: Multi-word entities**
```
"Rapid Support Forces attacked the village"
```
"Rapid Support Forces" is ONE entity (3 words). The computer must know they belong together.

**Challenge 3: Rare entities**
```
"The Janjaweed militia..."
```
If the model never saw "Janjaweed" during training, can it still recognize it as a perpetrator?

### 1.3 Your Use Case: Violent Event Extraction

Your thesis addresses a real-world problem: **The African Union Continental Early Warning System (AU-CEWS)** needs to monitor conflicts across Africa.

**Current situation:**
- Analysts manually read thousands of news articles
- Slow, expensive, inconsistent
- Can't keep up with the volume

**Your solution:**
- Automated extraction using NER
- Process articles in milliseconds
- Consistent, scalable analysis

**Thesis Defense Tip:**
> "My NER system extracts structured information from unstructured conflict reports, enabling the AU-CEWS to process thousands of articles daily instead of manually reading each one."

---

## 2. The BIO Tagging Scheme

### 2.1 The Problem: Word Boundaries

Consider:
```
"Al Shabaab attacked Mogadishu"
```

"Al Shabaab" is ONE perpetrator, but it's TWO words. How do we represent this?

**Bad approach:** Just label each word
```
Al        → PERPETRATOR
Shabaab   → PERPETRATOR
attacked  → EVENT
Mogadishu → CITY
```

Problem: We can't tell if "Al" and "Shabaab" are one entity or two separate ones.

### 2.2 The Solution: BIO Tags

**B** = **B**egin - First word of an entity
**I** = **I**nside - Continuation of an entity
**O** = **O**utside - Not part of any entity

```
Word:      Al          Shabaab       attacked    Mogadishu
           ↓           ↓             ↓           ↓
BIO Tag:   B-PERP      I-PERP        O           B-CITY
           ↓           ↓             ↓           ↓
Meaning:   START of    CONTINUES     Not an      START of
           perpetrator perpetrator   entity      city
```

### 2.3 Why B and I Matter

**Scenario: Two perpetrators next to each other**
```
"RSF and Janjaweed forces clashed"
```

**With BIO:**
```
RSF        → B-PERPETRATOR  (Start of entity 1)
and        → O
Janjaweed  → B-PERPETRATOR  (Start of entity 2 - NEW B means NEW entity!)
forces     → I-PERPETRATOR  (Continues entity 2)
clashed    → O
```

The two `B-PERPETRATOR` tags tell us these are TWO SEPARATE perpetrators.

### 2.4 Reconstructing Entities from BIO Tags

**Algorithm to extract entities:**
```
1. When you see B-X: Start a new entity of type X
2. When you see I-X: Add this word to the current entity
3. When you see O or B-Y (different type): End the current entity
```

**Example:**
```
Tokens: ["Boko", "Haram", "fighters", "attacked", "Maiduguri"]
Tags:   [B-PERP, I-PERP,  I-PERP,    B-EVENT,   B-CITY    ]

Extracted entities:
- PERPETRATOR: "Boko Haram fighters" (tokens 0-2)
- EVENT: "attacked" (token 3)
- CITY: "Maiduguri" (token 4)
```

### 2.5 The Complete BIO Label Set

**Critical Concept:** Every entity type in your schema gets its own B- and I- tags.

**Formula:**
```
(Number of Entity Types × 2) + 1 = Total BIO Labels
(26 × 2) + 1 = 53 labels
```

**Your 53 BIO Labels:**

| # | Entity Type | B- Tag | I- Tag | Example Text |
|---|-------------|--------|--------|--------------|
| 1 | PERPETRATOR | B-PERPETRATOR | I-PERPETRATOR | "Al Shabaab militants" |
| 2 | VICTIM | B-VICTIM | I-VICTIM | "civilian women" |
| 3 | TARGET | B-TARGET | I-TARGET | "military convoy" |
| 4 | ORGANIZATION | B-ORGANIZATION | I-ORGANIZATION | "Red Cross" |
| 5 | GOVERNMENT | B-GOVERNMENT | I-GOVERNMENT | "Nigerian Army" |
| 6 | EVENT_TYPE | B-EVENT_TYPE | I-EVENT_TYPE | "armed assault" |
| 7 | ACTION | B-ACTION | I-ACTION | "opened fire" |
| 8 | WEAPON | B-WEAPON | I-WEAPON | "AK-47 rifles" |
| 9 | VIOLENCE_TYPE | B-VIOLENCE_TYPE | I-VIOLENCE_TYPE | "ethnic violence" |
| 10 | DATE | B-DATE | I-DATE | "January 15" |
| 11 | TIME | B-TIME | I-TIME | "early morning" |
| 12 | DURATION | B-DURATION | I-DURATION | "three-hour battle" |
| 13 | FREQUENCY | B-FREQUENCY | I-FREQUENCY | "daily attacks" |
| 14 | COUNTRY | B-COUNTRY | I-COUNTRY | "South Sudan" |
| 15 | REGION | B-REGION | I-REGION | "North Kivu" |
| 16 | CITY | B-CITY | I-CITY | "Addis Ababa" |
| 17 | DISTRICT | B-DISTRICT | I-DISTRICT | "Zone Five" |
| 18 | FACILITY | B-FACILITY | I-FACILITY | "military base" |
| 19 | GEOGRAPHIC | B-GEOGRAPHIC | I-GEOGRAPHIC | "Lake Chad" |
| 20 | COORDINATES | B-COORDINATES | I-COORDINATES | "9.0820° N" |
| 21 | CASUALTIES | B-CASUALTIES | I-CASUALTIES | "15 people killed" |
| 22 | INJURED | B-INJURED | I-INJURED | "dozens wounded" |
| 23 | DISPLACEMENT | B-DISPLACEMENT | I-DISPLACEMENT | "thousands fled" |
| 24 | DAMAGE | B-DAMAGE | I-DAMAGE | "homes destroyed" |
| 25 | MOTIVE | B-MOTIVE | I-MOTIVE | "land dispute" |
| 26 | TRIGGER | B-TRIGGER | I-TRIGGER | "election dispute" |
| — | **O** | — | — | "the", "attacked", "in" |

**Total: 26 B-tags + 26 I-tags + 1 O-tag = 53 labels**

### 2.6 Why Verbs Like "attacked" Get the O Tag

**NER extracts NOUNS (named things), not VERBS (actions).**

| Word Type | Tag | Reason |
|-----------|-----|--------|
| "Al Shabaab" | B-PERPETRATOR, I-PERPETRATOR | Noun - a named armed group |
| "attacked" | O | Verb - describes action, not an entity |
| "Mogadishu" | B-CITY | Noun - a named place |
| "the", "in", "on" | O | Function words - not entities |

**How do we capture WHAT happened?**

The "WHAT" in 5W1H is captured through **EVENT_TYPE** - but as a **noun**, not a verb:

```
Sentence: "An armed assault by Al Shabaab occurred"

Word:      armed          assault        by    Al            Shabaab
Tag:       B-EVENT_TYPE   I-EVENT_TYPE   O     B-PERPETRATOR I-PERPETRATOR
```

Here "armed assault" (noun phrase) is tagged as EVENT_TYPE.

**Verb vs Noun Forms:**
```
VERBS (O):              NOUNS (can be entities):
───────────────────────────────────────────────────
attacked                attack, assault
killed                  killing, massacre
bombed                  bombing, explosion
clashed                 clash, clashes
abducted                abduction, kidnapping
```

**Key Insight:** NER answers "What things are mentioned?" not "What grammatical actions occurred?"

### 2.7 Why Each Type Needs Its Own B- and I-

**Without type-specific tags (wrong):**
```
Word:      Al         Shabaab     attacked    Mogadishu
Tag:       B-ENTITY   I-ENTITY    O           B-ENTITY
```
Problem: We know "Al Shabaab" is an entity, but WHAT KIND? Perpetrator? Victim? Location?

**With type-specific tags (correct):**
```
Word:      Al              Shabaab         attacked    Mogadishu
Tag:       B-PERPETRATOR   I-PERPETRATOR   O           B-CITY
```
Now we know: "Al Shabaab" = PERPETRATOR, "Mogadishu" = CITY

### 2.8 Multi-Word Entity Examples by Type

```
"Democratic Republic of Congo"
 B-COUNTRY  I-COUNTRY I-COUNTRY I-COUNTRY   → 1 COUNTRY entity (4 words)

"Rapid Support Forces"
 B-PERPETRATOR I-PERPETRATOR I-PERPETRATOR  → 1 PERPETRATOR entity (3 words)

"at least 50 civilians"
 B-CASUALTIES I-CASUALTIES I-CASUALTIES     → 1 CASUALTIES entity (4 words)

"AK-47 assault rifles"
 B-WEAPON I-WEAPON I-WEAPON                 → 1 WEAPON entity (3 words)

"early Monday morning"
 B-DATE I-DATE I-DATE                       → 1 DATE entity (3 words)
```

### 2.9 Adjacent Entities of Different Types

When entities of DIFFERENT types are adjacent, the B- tag signals a new entity:

```
"RSF forces attacked Khartoum Monday"

Word:      RSF              forces           attacked    Khartoum    Monday
Tag:       B-PERPETRATOR    I-PERPETRATOR    O           B-CITY      B-DATE
                                                         ↑           ↑
                                                   New entity!   New entity!

Extracted:
1. PERPETRATOR: "RSF forces"
2. CITY: "Khartoum"
3. DATE: "Monday"
```

### 2.10 Adjacent Entities of SAME Type

When entities of the SAME type are adjacent, B- separates them:

```
"RSF and Janjaweed attacked the village"

Word:      RSF              and    Janjaweed        attacked    the    village
Tag:       B-PERPETRATOR    O      B-PERPETRATOR    O           O      B-FACILITY
           ↑                       ↑
      First perpetrator       Second perpetrator (B- = new entity!)

Extracted:
1. PERPETRATOR: "RSF"
2. PERPETRATOR: "Janjaweed"     ← Two separate perpetrators!
3. FACILITY: "village"
```

### 2.11 Visualization

```
Sentence: "The RSF shelled Khartoum on Tuesday"

Token:     The    RSF    shelled    Khartoum    on    Tuesday
           │      │      │          │           │     │
BIO:       O      B-PERP O          B-CITY      O     B-DATE
           │      │      │          │           │     │
Entity:    -      ├──────┤          ├───────────┤     ├──────┤
                  RSF               Khartoum          Tuesday
                  (PERPETRATOR)     (CITY)            (DATE)
```

### 2.12 Summary: The BIO System

| Concept | Explanation |
|---------|-------------|
| **B- prefix** | Marks the BEGINNING of an entity |
| **I- prefix** | Marks tokens INSIDE (continuation) of an entity |
| **O tag** | Marks tokens OUTSIDE any entity (verbs, articles, prepositions) |
| **Entity type** | The category (PERPETRATOR, CITY, etc.) attached to B- and I- |
| **53 labels** | 26 entity types × 2 (B + I) + 1 (O) = 53 |
| **Multi-word** | Multiple tokens with B-X followed by I-X form ONE entity |
| **Adjacent** | New B- tag always starts a NEW entity, even if same type |

**Thesis Defense Tip:**
> "BIO tagging solves the multi-word entity problem by marking the beginning and inside tokens separately. Each of my 26 entity types has its own B- and I- tags, yielding 53 total labels. This allows the model to correctly identify both entity boundaries AND entity types, even when entities are adjacent."

---

## 3. Your Entity Schema: The 5W1H Framework

### 3.1 The Journalism Framework

Your system extracts the **5W1H** - the fundamental questions journalists answer:

| Question | Category | Entity Types |
|----------|----------|--------------|
| **W**HO | Actors | PERPETRATOR, VICTIM, TARGET, ORGANIZATION, GOVERNMENT |
| **W**HAT | Actions | EVENT_TYPE, ACTION, WEAPON, VIOLENCE_TYPE |
| **W**HEN | Temporal | DATE, TIME, DURATION, FREQUENCY |
| **W**HERE | Location | COUNTRY, REGION, CITY, DISTRICT, FACILITY, GEOGRAPHIC, COORDINATES |
| **W**HY | Cause | MOTIVE, TRIGGER |
| **H**OW | Impact | CASUALTIES, INJURED, DISPLACEMENT, DAMAGE |

**5 W's + 1 H = 5W1H**

**Total: 26 entity types → 53 BIO labels** (26×2 for B/I + 1 for O)

### 3.2 Entity Type Details

#### WHO - Actors (5 types)

| Type | Description | Examples |
|------|-------------|----------|
| **PERPETRATOR** | Who committed violence | "Al Shabaab", "RSF", "armed militants", "gunmen" |
| **VICTIM** | Who was harmed | "civilians", "villagers", "15 children", "farmers" |
| **TARGET** | Strategic/military targets | "military base", "convoy", "checkpoint" |
| **ORGANIZATION** | Non-state organizations | "Red Cross", "UN", "MSF", "AU" |
| **GOVERNMENT** | State actors | "Nigerian Army", "Ethiopian forces", "police" |

#### WHAT - Actions (4 types)

| Type | Description | Examples |
|------|-------------|----------|
| **EVENT_TYPE** | Type of violent event | "attack", "massacre", "bombing", "kidnapping" |
| **ACTION** | Specific action verbs | "killed", "abducted", "shelled", "ambushed" |
| **WEAPON** | Arms used | "AK-47", "machete", "IED", "mortar" |
| **VIOLENCE_TYPE** | Category of violence | "ethnic violence", "terrorism", "banditry" |

#### WHEN - Temporal (4 types)

| Type | Description | Examples |
|------|-------------|----------|
| **DATE** | Calendar dates | "Monday", "15 January 2024", "last week" |
| **TIME** | Time of day | "morning", "midnight", "3:00 PM" |
| **DURATION** | How long | "three-hour battle", "week-long siege" |
| **FREQUENCY** | How often | "daily attacks", "repeated incidents" |

#### WHERE - Location (7 types)

| Type | Description | Examples |
|------|-------------|----------|
| **COUNTRY** | Nation | "Nigeria", "Sudan", "DRC" |
| **REGION** | State/Province | "Borno State", "Darfur", "North Kivu" |
| **CITY** | Town/City | "Maiduguri", "Khartoum", "Goma" |
| **DISTRICT** | Sub-city area | "Konduga LGA", "Zone 5" |
| **FACILITY** | Buildings/infrastructure | "hospital", "school", "military base" |
| **GEOGRAPHIC** | Natural features | "Lake Chad", "Nile River" |
| **COORDINATES** | GPS coordinates | "9.0820° N, 7.4926° E" |

#### HOW - Impact (4 types)

| Type | Description | Examples |
|------|-------------|----------|
| **CASUALTIES** | Deaths | "15 killed", "death toll of 50" |
| **INJURED** | Injuries | "23 wounded", "dozens injured" |
| **DISPLACEMENT** | Population movement | "5000 fled", "refugees", "IDPs" |
| **DAMAGE** | Property destruction | "homes burned", "market destroyed" |

#### WHY - Cause (2 types)

| Type | Description | Examples |
|------|-------------|----------|
| **MOTIVE** | Reason for violence | "land dispute", "religious conflict", "retaliation" |
| **TRIGGER** | Immediate cause | "sparked by election", "following arrest" |

### 3.3 Complete Example

**Input text:**
```
Al Shabaab militants attacked a military base in Mogadishu on Monday morning,
killing 15 soldiers and injuring 23 others. The attack was carried out using
explosives and small arms fire, forcing hundreds of residents to flee.
```

**Extracted entities:**

| Question | Type | Value |
|----------|------|-------|
| WHO (perpetrator) | PERPETRATOR | Al Shabaab militants |
| WHO (victim) | VICTIM | soldiers |
| WHAT (event) | EVENT_TYPE | attacked |
| WHAT (weapon) | WEAPON | explosives, small arms |
| WHEN (date) | DATE | Monday |
| WHEN (time) | TIME | morning |
| WHERE (city) | CITY | Mogadishu |
| WHERE (facility) | FACILITY | military base |
| HOW (killed) | CASUALTIES | 15 killed |
| HOW (injured) | INJURED | 23 injured |
| HOW (displaced) | DISPLACEMENT | hundreds fled |

**Thesis Defense Tip:**
> "I designed a comprehensive 26-entity type schema based on the journalistic 5W1H framework, extended with WHY to capture conflict motivations. This enables complete event understanding, not just named entity identification."

---

# Part II: The Data Pipeline

## 4. From Raw Text to Training Data

### 4.1 The Preprocessing Pipeline

Your system converts ACLED conflict data into training format:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   ACLED CSV     │────▶│   enhance_csv   │────▶│ preprocessing   │
│ (raw conflict   │     │   (extract      │     │ (convert to     │
│  descriptions)  │     │    entities)    │     │  BIO format)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                      │                       │
         ▼                      ▼                       ▼
   118,834 events        Enhanced with           train.json
   with descriptions     24 entity types         val.json
```

### 4.2 Step 1: Raw ACLED Data

**Input format (CSV):**
```csv
Event_ID,Event_Description,PERPETRATOR,CITY,DATE,...
12345,"Al Shabaab attacked Mogadishu","Al Shabaab","Mogadishu","Monday",...
```

### 4.3 Step 2: Entity Enhancement

The `enhance_csv.py` script extracts additional entities using:

1. **Pattern matching:** Regular expressions for dates, casualties, etc.
2. **Knowledge base lookup:** Armed groups, cities, countries
3. **Demonym conversion:** "Nigerian" → "Nigeria"
4. **City-to-country inference:** "Mogadishu" → "Somalia"

**Example enhancement:**
```
Original COUNTRY: (empty)
After enhancement: "Somalia" (inferred from CITY="Mogadishu")
```

### 4.4 Step 3: BIO Conversion

The `preprocessing.py` script:

1. **Tokenizes** the text into words
2. **Locates** each entity in the text
3. **Assigns** BIO tags to each token
4. **Handles** overlapping entities (prioritizes longer matches)

**Example transformation:**

**Input:**
```
Event_Description: "RSF shelled Khartoum on Tuesday"
PERPETRATOR: "RSF"
CITY: "Khartoum"
DATE: "Tuesday"
```

**Output:**
```json
{
  "id": "12345",
  "text": "RSF shelled Khartoum on Tuesday",
  "tokens": ["RSF", "shelled", "Khartoum", "on", "Tuesday"],
  "labels": ["B-PERPETRATOR", "O", "B-CITY", "O", "B-DATE"],
  "entities": [
    {"type": "PERPETRATOR", "text": "RSF", "start": 0, "end": 1},
    {"type": "CITY", "text": "Khartoum", "start": 2, "end": 3},
    {"type": "DATE", "text": "Tuesday", "start": 4, "end": 5}
  ]
}
```

### 4.5 Why This Pipeline Matters

**Without enhancement:**
- COUNTRY field: 22.8% filled
- TARGET field: 0.7% filled
- Many entities missed

**After enhancement (v4):**
- COUNTRY field: 57.6% filled (+153%)
- TARGET field: 23.7% filled (+3,166%)
- Much richer training signal

**Thesis Defense Tip:**
> "I developed a multi-stage preprocessing pipeline that combines rule-based extraction with knowledge base lookup to maximize entity coverage. This addressed a key challenge: the original data had many implicit entities that needed to be made explicit for effective training."

---

## 5. Your Enhanced Dataset

### 5.1 Dataset Statistics

| Metric | Value |
|--------|-------|
| Total events | 118,834 |
| Training set | 95,067 (80%) |
| Validation set | 23,767 (20%) |
| Entity types | 24 |
| BIO labels | 49 |

### 5.2 Entity Distribution

```
Entity Type        Count      Percentage
─────────────────────────────────────────
CITY               128,342    Most common
PERPETRATOR        101,681
DATE               100,387
EVENT_TYPE          95,938
REGION              58,906
GOVERNMENT          57,676
ACTION              52,627
ORGANIZATION        47,557
FACILITY            40,712
VICTIM              36,631
WEAPON              24,821
TARGET              20,952
DISTRICT            18,013
CASUALTIES          15,334
MOTIVE               6,444
TIME                 6,322
VIOLENCE_TYPE        4,930
COUNTRY              4,379
INJURED              4,132
DISPLACEMENT         3,934
DAMAGE               3,151
TRIGGER              2,164
DURATION             1,091
FREQUENCY              212    Rarest
```

### 5.3 The Class Imbalance Challenge

**Problem:** The "O" (Outside) label dominates your training data.

#### What is Class Imbalance?

In NER, most words in a sentence are NOT entities. They're articles ("the", "a"), prepositions ("in", "on", "by"), verbs ("attacked", "killed"), and other function words.

**Concrete Example:**

```
Sentence: "The armed militants attacked the village in the northern region on Monday"

Word:        The   armed   militants   attacked   the   village   in   the   northern   region   on   Monday
BIO Tag:     O     B-PERP  I-PERP      O          O     B-FAC     O    O     B-REGION   I-REGION O    B-DATE
             ↓     ↓       ↓           ↓          ↓     ↓         ↓    ↓     ↓          ↓        ↓    ↓
Entity?      No    Yes     Yes         No         No    Yes       No   No    Yes        Yes      No   Yes
```

**Count:**
- Total tokens: 12
- O tokens: 6 (The, attacked, the, in, the, on)
- Entity tokens: 6 (armed, militants, village, northern, region, Monday)
- **O percentage: 50%** (and this is a entity-rich sentence!)

In typical news text, the O percentage is even higher: **68.3%** in your dataset.

#### Why This Is a Problem

**The Lazy Model Problem:**

If the model learns to ALWAYS predict "O" for every token:

```
Sentence: "Al Shabaab attacked Mogadishu on Monday"

Correct:     B-PERP    I-PERP     O         B-CITY      O    B-DATE
Lazy model:  O         O          O         O           O    O

Accuracy = 2/6 = 33%? No! Let's count ALL tokens in training data...
```

**In your training data:**
- Total tokens: ~2,000,000
- O tokens: ~1,366,000 (68.3%)
- Entity tokens: ~634,000 (31.7%)

**A model that predicts ALL "O" achieves 68.3% accuracy!**

This is misleading because:
- ✗ It finds ZERO perpetrators
- ✗ It finds ZERO locations
- ✗ It finds ZERO dates
- ✓ But it's "68% accurate"

#### Visual: The Imbalance in Your Data

```
Label Distribution (simplified):

O (Outside)        ████████████████████████████████████████████████████████████████████ 68.3%
B-PERPETRATOR      █████                                                                  3.2%
I-PERPETRATOR      ███                                                                    2.1%
B-EVENT_TYPE       █████                                                                  2.8%
B-CITY             ████                                                                   2.4%
B-DATE             ███                                                                    1.9%
...
B-MOTIVE           ▏                                                                      0.2%
B-TRIGGER          ▏                                                                      0.1%
B-FREQUENCY        ▏                                                                      0.02%
```

The O label is **30× more common** than typical entity labels!

#### What Happens During Training Without Fix

**Epoch 1:**
```
Model: "Hmm, when I predict O, I'm usually right. When I predict entities, I'm often wrong."
       "I'll just predict O more often to reduce my loss!"
```

**Epoch 2:**
```
Model: "Predicting O works great! My accuracy is 65%!"
       "I'll predict O even more!"
```

**Epoch 5:**
```
Model: "I predict O for everything. 68% accuracy. I'm a genius!"
       (Actually useless - finds no entities)
```

#### Your Solution: FocalLoss + Class Weights

**FocalLoss** (explained in detail in Section 12) solves this by:

1. **Down-weighting easy predictions:** When the model confidently predicts O correctly, that contributes almost nothing to learning
2. **Up-weighting hard predictions:** Entity boundaries where the model struggles contribute more
3. **Class weights:** Rare entities (FREQUENCY, TRIGGER) get higher importance

**Result:** The model is forced to learn entity patterns, not just predict O.

```
Without FocalLoss: "Just predict O" → 68% accuracy, 0% useful
With FocalLoss:    "Learn entity patterns" → 90%+ F1 on entities
```

---

## 6. Data Quality and Class Imbalance

### 6.1 The Imbalance Problem Visualized

```
Token distribution in your training data:

O (Outside)        ████████████████████████████████████████ 68.3%
B-CITY             ████                                      3.4%
I-DATE             ████                                      3.3%
B-PERPETRATOR      ███                                       3.1%
...
B-FREQUENCY        ▏                                         0.003%
```

If a model just predicts "O" for every token, it's correct 68.3% of the time!

### 6.2 Why Standard Training Fails

**Cross-entropy loss treats all errors equally:**

```
Error predicting "O" as "B-PERP":      Loss = -log(0.1) = 2.3
Error predicting "B-PERP" as "O":      Loss = -log(0.1) = 2.3
```

But we care more about entity errors! Missing a perpetrator is worse than wrongly predicting an extra "O".

### 6.3 Solutions Implemented

1. **Class Weights:** Multiply loss by rarity
   - Rare entities (FREQUENCY) get weight ~1.5
   - Common labels (O) get weight ~0.02

2. **FocalLoss:** Focus on hard examples
   - Easy "O" predictions contribute less to learning
   - Hard entity boundaries contribute more

3. **Data Enhancement:** Extract more entities
   - v4 enhancement increased entity coverage significantly

**Thesis Defense Tip:**
> "NER datasets inherently suffer from class imbalance because the O label dominates. I addressed this with a combination of FocalLoss and class weighting, which down-weights easy predictions and focuses learning on entity boundaries."

---

# Part III: The Model

## 7. Neural Networks: The Foundation

### 7.1 What is a Neural Network?

A neural network is a **function approximator** that learns from examples.

**Analogy: Learning to recognize cats**

```
Stage 1: Baby sees 1000 cat pictures
         Brain notices patterns: pointy ears, whiskers, fur

Stage 2: Baby sees new cat (never seen before)
         Matches patterns → "That's a cat!"
```

Neural networks do the same:
1. See many examples (training)
2. Learn patterns (weights)
3. Apply patterns to new data (inference)

### 7.2 The Basic Unit: The Neuron

A single neuron computes:

```
output = activation(w₁x₁ + w₂x₂ + w₃x₃ + ... + b)
```

Where:
- `x₁, x₂, x₃...` are inputs
- `w₁, w₂, w₃...` are weights (learned)
- `b` is bias (learned)
- `activation` is a non-linear function (like ReLU)

**Visual:**
```
    Inputs         Weights        Sum         Activation     Output

    x₁ ─────────── w₁ ──┐
                        ├─── Σ ───────── ReLU ──────── output
    x₂ ─────────── w₂ ──┤
                        │
    x₃ ─────────── w₃ ──┘
```

### 7.3 Layers of Neurons

Neural networks stack neurons in layers:

```
Input Layer      Hidden Layer      Output Layer
(features)       (learned)         (predictions)

   [x₁]             [h₁]              [y₁] ← P(O)
   [x₂]   ──────▶   [h₂]   ──────▶    [y₂] ← P(B-PERP)
   [x₃]             [h₃]              [y₃] ← P(I-PERP)
   [x₄]             [h₄]              ...
```

**Each layer learns more abstract features:**
- Layer 1: Basic patterns (word shapes)
- Layer 2: Word types (noun, verb)
- Layer 3: Semantic meaning
- ...
- Final layer: Entity predictions

### 7.4 What Are Weights?

**Weights are the knowledge of the network.**

- Before training: Random weights → Random predictions
- After training: Optimized weights → Accurate predictions

**Your BERT model has 110 million weights!**

These weights encode everything BERT knows about language.

---

## 8. Transformers and Attention

### 8.1 The Attention Revolution

Before Transformers (2017), models processed text sequentially:

```
Traditional (RNN/LSTM):
"Al Shabaab attacked Mogadishu"
 ↓
 Al → Shabaab → attacked → Mogadishu
 (processes one word at a time, left to right)
```

**Problem:** By the time we reach "Mogadishu", information about "Al Shabaab" has degraded.

**Transformers process all words simultaneously:**
```
Transformer:
"Al Shabaab attacked Mogadishu"
 ↓      ↓       ↓         ↓
 All words processed in parallel
 Each word can "attend" to every other word
```

### 8.2 Self-Attention Explained

**Self-attention** lets each word look at every other word to understand context.

**Example:**
```
"The bank by the river was flooded"
```

When processing "bank", attention helps:
- High attention to "river" → riverbank (not financial)
- Low attention to "was" → less relevant

**Attention weights example:**
```
                bank  river  flooded
For "bank":     0.2   0.6    0.2     ← "bank" attends most to "river"
```

### 8.3 The Attention Formula

```
Attention(Q, K, V) = softmax(QKᵀ / √d) × V
```

**In plain English:**
1. **Q (Query):** What am I looking for?
2. **K (Key):** What do I contain?
3. **V (Value):** What information do I provide?
4. **QKᵀ:** How relevant is each word to my query?
5. **softmax:** Normalize to get probabilities
6. **× V:** Weighted combination of information

### 8.4 Multi-Head Attention

BERT uses **12 attention heads** (in base model).

Each head learns to focus on different relationships:
- Head 1: Subject-verb agreement
- Head 2: Entity boundaries
- Head 3: Coreference (he/she → who?)
- etc.

```
┌─────────────────────────────────────────────────┐
│                Multi-Head Attention              │
│                                                  │
│  ┌──────┐ ┌──────┐ ┌──────┐     ┌──────┐       │
│  │Head 1│ │Head 2│ │Head 3│ ... │Head 12│      │
│  └──────┘ └──────┘ └──────┘     └──────┘       │
│      ↓        ↓        ↓            ↓           │
│      └────────┴────────┴────────────┘           │
│                    ↓                             │
│              Concatenate                         │
│                    ↓                             │
│            Linear projection                     │
└─────────────────────────────────────────────────┘
```

**Thesis Defense Tip:**
> "Transformers use self-attention to model relationships between all words in a sentence simultaneously. This is crucial for NER because entity classification often depends on context words that may be far away in the sentence."

---

## 9. BERT: Why It's Revolutionary

### 9.1 BERT = Bidirectional Encoder Representations from Transformers

Let's break this down:

| Word | Meaning |
|------|---------|
| **Bidirectional** | Looks at context in both directions |
| **Encoder** | Creates representations of text |
| **Representations** | Meaningful numerical vectors |
| **Transformers** | Uses attention mechanism |

### 9.2 The Bidirectional Advantage

**Older models (left-to-right):**
```
"I went to the bank to deposit money"
              ↑
When processing "bank", only sees: "I went to the"
Doesn't know if it's a river bank or financial bank!
```

**BERT (bidirectional):**
```
"I went to the bank to deposit money"
              ↑
When processing "bank", sees: entire sentence
"deposit money" → clearly financial bank!
```

### 9.3 How BERT Was Pre-trained

BERT was trained on massive text (Wikipedia + Books, 3.3 billion words):

**Task 1: Masked Language Model (MLM)**
```
Input:  "The cat [MASK] on the mat"
BERT learns to predict: [MASK] = "sat"
```
This teaches BERT to understand context.

**Task 2: Next Sentence Prediction (NSP)**
```
Sentence A: "The cat sat on the mat"
Sentence B: "It was very comfortable"
BERT learns: These are related (True)
```
This teaches BERT document-level understanding.

### 9.4 BERT Architecture

```
Input: "Al Shabaab attacked"
         ↓
┌─────────────────────────────────────┐
│           Tokenizer                  │
│  "Al" "Sha" "##baab" "attacked"     │
│   ↓     ↓      ↓         ↓          │
│  101   234    5678      9012        │ (Token IDs)
└──────────────────┬──────────────────┘
                   ↓
┌─────────────────────────────────────┐
│       Embedding Layer               │
│  Each ID → 768-dimensional vector   │
└──────────────────┬──────────────────┘
                   ↓
┌─────────────────────────────────────┐
│   Transformer Block 1               │
│   (Self-Attention + Feed-Forward)   │
└──────────────────┬──────────────────┘
                   ↓
               ... (×12 blocks)
                   ↓
┌─────────────────────────────────────┐
│   Transformer Block 12              │
└──────────────────┬──────────────────┘
                   ↓
Output: Contextualized representations
        (768-dim vector per token)
```

### 9.5 BERT Model Sizes

| Model | Layers | Hidden Size | Parameters |
|-------|--------|-------------|------------|
| BERT-base | 12 | 768 | 110 million |
| BERT-large | 24 | 1024 | 340 million |

**Your system uses BERT-base-cased:**
- 110M parameters
- Case-sensitive (important for proper nouns!)

### 9.6 Why "Cased" Matters for NER

```
Cased:   "Al Shabaab" → recognized as entity
Uncased: "al shabaab" → might miss capitalization cues
```

For NER, capitalization is a strong signal for proper nouns (names, places).

---

## 10. Fine-tuning BERT for NER

### 10.1 Transfer Learning

**Traditional approach:**
```
Your data (95k examples) → Train from scratch → Weak model
```

**With BERT:**
```
Wikipedia (3.3B words) → Pre-train BERT → General language understanding
                                                    ↓
Your data (95k examples) → Fine-tune → Strong NER model
```

**Analogy:**
- Traditional: Teaching a baby to be a conflict analyst
- Transfer learning: Training a linguistics PhD to analyze conflicts

### 10.2 What Fine-tuning Changes

```
┌─────────────────────────────────────────┐
│          Pre-trained BERT               │ ← Slightly adjusted
│  (already understands language)          │    (learning rate: 2e-5)
└────────────────────┬────────────────────┘
                     ↓
┌─────────────────────────────────────────┐
│       Classification Head               │ ← Trained from scratch
│  (768 dimensions → 53 BIO labels)       │    (random initialization)
└─────────────────────────────────────────┘
```

### 10.3 The Classification Head

For each token, BERT outputs a 768-dimensional vector. The classification head converts this to label probabilities:

```
BERT output for "Shabaab": [0.23, -0.45, 0.78, ..., 0.12]  (768 numbers)
                                      ↓
                            Linear layer (768 → 53)
                                      ↓
                            [2.1, 8.5, 0.3, ..., 0.1]  (53 logits)
                                      ↓
                                  Softmax
                                      ↓
Probabilities:  O: 0.01, B-PERP: 0.02, I-PERP: 0.95, ...
                                            ↑
                                    Prediction: I-PERP
```

### 10.4 Why Fine-tuning Works

BERT already knows:
- ✅ Grammar and syntax
- ✅ That "Al Shabaab" is a named entity
- ✅ That entities often follow patterns ("the X forces")
- ✅ Context matters for meaning

You just teach it:
- ❓ Which entities are PERPETRATORS in conflict context
- ❓ Which entities are VICTIMS vs TARGETS
- ❓ Your specific domain vocabulary

**Thesis Defense Tip:**
> "Fine-tuning leverages BERT's pre-trained knowledge of language structure and semantics. We only need to teach it our specific entity types, which requires far less data than training from scratch."

---

## 11. Inference: How Prediction Works

### 11.1 The Prediction Pipeline

When your trained model receives new text, here's what happens step by step:

```
Input Text: "Al Shabaab attacked Mogadishu on Monday"
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: TOKENIZATION                                           │
│  Split text into tokens (may create subwords)                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: ADD SPECIAL TOKENS                                     │
│  Add [CLS] at start, [SEP] at end, [PAD] for batching          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: CREATE MASKS                                           │
│  Attention mask, special token mask, subword mask               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 4: FORWARD PASS                                           │
│  BERT encodes → Classification head predicts BIO labels         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 5: APPLY MASKS                                            │
│  Only keep predictions for real word tokens                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 6: EXTRACT ENTITIES                                       │
│  Convert BIO sequence to entity spans                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
Output: [("Al Shabaab", PERPETRATOR), ("Mogadishu", CITY), ("Monday", DATE)]
```

### 11.2 Step 1: Tokenization and Subwords

BERT uses **WordPiece tokenization**, which may split words into subwords:

```
Original text:    "Al Shabaab attacked Mogadishu"
                   ↓
Tokenization:     ["Al", "Sha", "##baab", "attacked", "Moga", "##dish", "##u"]
                         ↑      ↑                      ↑       ↑        ↑
                         └──────┘                      └───────┴────────┘
                         "Shabaab" split               "Mogadishu" split
                         into 2 pieces                 into 3 pieces
```

**Why does BERT split words?**

BERT was trained on a fixed vocabulary of ~30,000 tokens. Words not in the vocabulary are split into known pieces:

| Word | In Vocabulary? | Tokenization |
|------|----------------|--------------|
| "attacked" | Yes | ["attacked"] |
| "Shabaab" | No | ["Sha", "##baab"] |
| "Mogadishu" | No | ["Moga", "##dish", "##u"] |
| "Janjaweed" | No | ["Jan", "##ja", "##weed"] |

The `##` prefix means "this continues the previous token."

### 11.3 Step 2: Special Tokens

BERT requires special tokens around the input:

```
Original tokens:  ["Al", "Sha", "##baab", "attacked", "Moga", "##dish", "##u"]
                   ↓
With special:     ["[CLS]", "Al", "Sha", "##baab", "attacked", "Moga", "##dish", "##u", "[SEP]"]
                    ↑                                                                      ↑
                 Classification token                                               Separator token
                 (start of sequence)                                               (end of sequence)
```

**For batching, add padding:**

```
Sentence 1: ["[CLS]", "Al", "Sha", "##baab", "attacked", "[SEP]", "[PAD]", "[PAD]"]
Sentence 2: ["[CLS]", "RSF", "shelled", "Khartoum", "on", "Tuesday", "[SEP]", "[PAD]"]
                                                                              ↑
                                                                    Padding to equal length
```

### 11.4 Why We Need Masking

**Problem:** We have predictions for ALL tokens, but we only want predictions for REAL WORDS.

```
Tokens:        [CLS]  Al    Sha   ##baab  attacked  Moga  ##dish  ##u   [SEP]  [PAD]
               ↓      ↓     ↓     ↓       ↓         ↓     ↓       ↓     ↓      ↓
Raw prediction: O     B-P   I-P   I-P     O         B-C   I-C     I-C   O      O
                ↑                 ↑                       ↑       ↑     ↑      ↑
              WRONG!         WRONG!                    WRONG!  WRONG! WRONG! WRONG!
```

**Problems to solve:**
1. **[CLS] and [SEP]** - Not real words, shouldn't have predictions
2. **[PAD]** - Just padding, not real content
3. **##subwords** - Only predict for the FIRST piece of each word

### 11.5 The Three Types of Masks

#### Mask 1: Attention Mask (for padding)

Tells BERT which tokens are real vs padding:

```
Tokens:         [CLS]  Al   Sha  ##baab  attacked  [SEP]  [PAD]  [PAD]
Attention mask:   1     1    1     1        1        1      0      0
                  ↑                                         ↑      ↑
               Real tokens                            Ignore these
```

**Purpose:** BERT's attention mechanism ignores [PAD] tokens completely.

#### Mask 2: Special Token Mask

Marks [CLS] and [SEP] for exclusion from predictions:

```
Tokens:              [CLS]  Al   Sha  ##baab  attacked  [SEP]  [PAD]
Special token mask:    0     1    1     1        1        0      0
                       ↑                                  ↑
                  Don't predict                    Don't predict
```

**Purpose:** We don't want entity labels for [CLS] or [SEP].

#### Mask 3: Subword Mask (Most Important for NER!)

Only predict for the FIRST subword of each original word:

```
Original words:     Al      Shabaab           attacked    Mogadishu
                    ↓       ↓                 ↓           ↓
Tokens:           [CLS]  Al   Sha  ##baab  attacked  Moga  ##dish  ##u  [SEP]
Subword mask:       0     1    1     0        1        1      0      0    0
                          ↑    ↑     ↑        ↑        ↑      ↑      ↑
                         OK  FIRST  SKIP     OK      FIRST  SKIP   SKIP
                              token  (##)             token  (##)   (##)
```

**Why only predict for first subword?**

Because our labels are at the WORD level, not subword level:

```
Word-level labels:    Al         Shabaab      attacked    Mogadishu
                    B-PERP      I-PERP          O          B-CITY
                      ↓           ↓             ↓            ↓
Subword tokens:      Al       Sha  ##baab   attacked   Moga ##dish ##u
                      ↓         ↓     ?        ↓         ↓     ?    ?
We predict:       B-PERP    I-PERP  skip      O       B-CITY skip skip
```

If we predicted for ##baab, ##dish, ##u, we'd have MORE predictions than labels!

### 11.6 Combined Mask Example

```
Text: "Al Shabaab attacked Mogadishu"

Tokens:           [CLS]  Al   Sha  ##baab  attacked  Moga  ##dish  ##u  [SEP]
Token IDs:         101   2632 12821  8425    3358    19842  6571   1206  102

Attention mask:      1     1    1     1        1        1      1     1    1
Special mask:        0     1    1     1        1        1      1     1    0
Subword mask:        0     1    1     0        1        1      0     0    0
                     ↓     ↓    ↓     ↓        ↓        ↓      ↓     ↓    ↓
FINAL (AND all):     0     1    1     0        1        1      0     0    0
                           ↑    ↑              ↑        ↑
                         These 4 tokens get predictions
```

**Final predictions:**
```
Tokens we predict for:  Al      Sha      attacked    Moga
Raw predictions:       B-PERP  I-PERP      O        B-CITY
                         ↓       ↓         ↓          ↓
Map back to words:  "Al Shabaab"      "attacked"  "Mogadishu"
                    (PERPETRATOR)                   (CITY)
```

### 11.7 The Forward Pass

After masking, the actual prediction is straightforward:

```python
# Pseudocode for inference
def predict(text):
    # Step 1-3: Tokenize and create masks
    tokens = tokenizer(text)
    input_ids = tokens.input_ids           # [101, 2632, 12821, ...]
    attention_mask = tokens.attention_mask  # [1, 1, 1, ...]

    # Step 4: Forward pass through BERT + classifier
    with torch.no_grad():                   # No gradient computation for inference
        outputs = model(input_ids, attention_mask)
        logits = outputs.logits             # Shape: [batch, seq_len, 53]

    # Step 5: Get predicted labels
    predictions = torch.argmax(logits, dim=-1)  # [batch, seq_len]

    # Step 6: Apply masks - only keep predictions for real words
    word_predictions = []
    for i, token in enumerate(tokens):
        if is_first_subword(token) and not is_special(token):
            word_predictions.append(predictions[i])

    return word_predictions
```

### 11.8 Step 6: Extracting Entities from BIO Predictions

Once we have BIO predictions, we extract entity spans:

```
Predictions:  B-PERP  I-PERP    O     B-CITY   O    B-DATE
Words:         "Al"  "Shabaab" "attacked" "Mogadishu" "on" "Monday"
                ↓       ↓                      ↓              ↓
Entity 1:   ┌───┴───────┴───┐            ┌────┴────┐    ┌────┴────┐
            │ "Al Shabaab"  │            │"Mogadishu"│   │"Monday" │
            │  PERPETRATOR  │            │   CITY    │   │  DATE   │
            └───────────────┘            └──────────┘    └─────────┘
```

**Algorithm:**
```
1. Start with empty current_entity
2. For each (word, tag) pair:
   - If tag starts with "B-":
       Save current_entity (if any)
       Start new entity with this word and type
   - If tag starts with "I-" and matches current type:
       Add word to current_entity
   - If tag is "O":
       Save current_entity (if any)
       Clear current_entity
3. Save final current_entity (if any)
```

### 11.9 Handling Invalid BIO Sequences

Sometimes the model predicts invalid sequences:

```
Invalid: O  I-PERP  I-PERP  O    (I without B!)
         ↓
Fixed:   O  B-PERP  I-PERP  O    (Convert first I to B)
```

```
Invalid: B-PERP  I-CITY  I-CITY  O   (I doesn't match B type!)
         ↓
Fixed:   B-PERP  B-CITY  I-CITY  O   (Start new entity)
```

**Post-processing rules:**
1. **I without preceding B:** Convert to B (start new entity)
2. **I with different type than B:** Convert to B (start new entity)
3. **B followed by I of different type:** End first entity, start new one

### 11.10 Complete Inference Example

**Input:** "RSF forces killed 50 civilians in Khartoum"

```
Step 1: Tokenize
["RSF", "forces", "killed", "50", "civilians", "in", "Khartoum"]

Step 2: Add special tokens
["[CLS]", "RSF", "forces", "killed", "50", "civilians", "in", "Khar", "##toum", "[SEP]"]

Step 3: Create masks
Attention:  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
Subword:    [0, 1, 1, 1, 1, 1, 1, 1, 0, 0]  (##toum and [SEP] masked)

Step 4: BERT forward pass → 53 probabilities per token

Step 5: Argmax → BIO predictions
[CLS]→O, RSF→B-PERP, forces→I-PERP, killed→O, 50→B-CAS,
civilians→I-CAS, in→O, Khar→B-CITY, ##toum→(skip), [SEP]→(skip)

Step 6: Extract entities
- PERPETRATOR: "RSF forces" (positions 0-1)
- CASUALTIES: "50 civilians" (positions 3-4)
- CITY: "Khartoum" (position 6)
```

**Final Output:**
```json
{
  "text": "RSF forces killed 50 civilians in Khartoum",
  "entities": [
    {"text": "RSF forces", "type": "PERPETRATOR", "start": 0, "end": 10},
    {"text": "50 civilians", "type": "CASUALTIES", "start": 18, "end": 30},
    {"text": "Khartoum", "type": "CITY", "start": 34, "end": 42}
  ]
}
```

### 11.11 Why Masking is Critical

| Without Masking | Problem |
|-----------------|---------|
| Predict for [CLS] | Wastes computation, no meaning |
| Predict for [SEP] | Wastes computation, no meaning |
| Predict for [PAD] | Wrong predictions for non-existent tokens |
| Predict for ##subwords | More predictions than labels! Alignment breaks |

| With Masking | Benefit |
|--------------|---------|
| Skip [CLS], [SEP] | Only predict for real content |
| Skip [PAD] | Handle variable-length batches |
| Skip ##subwords | 1:1 alignment between predictions and words |

**Thesis Defense Tip:**
> "Masking is essential for three reasons: (1) attention masking lets us batch variable-length sentences with padding, (2) special token masking excludes [CLS] and [SEP] from predictions, and (3) subword masking ensures we predict one label per original word, not per subword token. Without proper masking, predictions would be misaligned with the input words."

---

# Part IV: Training Deep Dive

## 12. The Training Loop Explained

### 12.1 The Big Picture

Training is an iterative process:

```
┌────────────────────────────────────────────────────────────┐
│                    TRAINING LOOP                           │
│                                                            │
│  ┌─────────┐    ┌──────────┐    ┌──────────┐    ┌───────┐ │
│  │ Forward │───▶│ Compute  │───▶│ Backward │───▶│Update │ │
│  │  Pass   │    │   Loss   │    │   Pass   │    │Weights│ │
│  └─────────┘    └──────────┘    └──────────┘    └───────┘ │
│       ↑                                              │     │
│       └──────────────────────────────────────────────┘     │
│                                                            │
│                    Repeat millions of times                │
└────────────────────────────────────────────────────────────┘
```

### 12.2 Training Configuration (Your System)

```python
# Your training settings
model = "bert-base-cased"     # 110M parameters
epochs = 5                     # Full passes through data
batch_size = 16               # Samples per update
learning_rate = 2e-5          # Step size (0.00002)
training_samples = 95,067     # Training set size
batches_per_epoch = 5,942     # 95,067 ÷ 16
```

### 12.3 Step-by-Step: One Training Iteration

**Step 1: Get a batch**
```
Batch of 16 sentences with their BIO labels
```

**Step 2: Forward pass**
```
Input tokens → BERT → Classification head → Predictions
```

**Step 3: Compute loss**
```
Compare predictions to true labels
Loss = measure of how wrong we are
```

**Step 4: Backward pass**
```
Calculate gradients: how much each weight contributed to the error
```

**Step 5: Update weights**
```
new_weight = old_weight - learning_rate × gradient
```

### 12.4 What Happens Each Epoch

```
Epoch 1: Model sees all 95,067 training samples once
         Loss: 2.5 → Predictions are mostly random
         Learning: "O is the most common tag"

Epoch 2: Model sees all samples again
         Loss: 0.8 → Getting better
         Learning: "Al Shabaab is a perpetrator pattern"

Epoch 3: Loss: 0.3 → Good progress
         Learning: "After 'in', there's often a city"

Epoch 4: Loss: 0.15 → Fine-tuning
         Learning: "Distinguishing VICTIM from TARGET"

Epoch 5: Loss: 0.10 → Converging
         Learning: "Edge cases and rare patterns"
```

### 12.5 Batching Explained

**Why not train on all data at once?**
- Memory: 95k samples don't fit in GPU memory
- Noise: Small batches add useful randomness
- Speed: Parallel processing of batch items

**Batch size trade-offs:**

| Batch Size | Memory | Noise | Speed |
|------------|--------|-------|-------|
| 8 | Low | High | Slow |
| 16 | Medium | Medium | Medium |
| 32 | High | Low | Fast |

Your system uses **batch_size=16** - a good balance for Apple Silicon.

---

## 13. Loss Functions and FocalLoss

### 13.1 What is Loss?

**Loss** measures how wrong the model's predictions are.

```
Perfect prediction:  Loss ≈ 0
Random prediction:   Loss ≈ log(num_classes) ≈ 4.0
Totally wrong:       Loss → ∞
```

The goal of training is to **minimize loss**.

### 13.2 Cross-Entropy Loss

The standard loss for classification:

```
Loss = -log(P(correct_class))
```

**Example:**
```
True label: B-PERPETRATOR
Model predicts:
  P(O) = 0.05
  P(B-PERPETRATOR) = 0.90  ← Correct class
  P(I-PERPETRATOR) = 0.05

Loss = -log(0.90) = 0.105  (low loss, good!)
```

**If model was wrong:**
```
P(B-PERPETRATOR) = 0.10

Loss = -log(0.10) = 2.303  (high loss, bad!)
```

### 13.3 The Problem: Class Imbalance

In your data:
- O tokens: 68.3%
- Entity tokens: 31.7%

**What happens with standard cross-entropy:**
```
Model learns: "Just predict O, you'll be right 68% of the time!"
```

The model becomes lazy and ignores rare entities.

### 13.4 FocalLoss: The Solution

**FocalLoss** adds a focusing factor that down-weights easy examples:

```
FL(p) = -α × (1 - p)^γ × log(p)
        ↑      ↑         ↑
        │      │         Standard cross-entropy
        │      │
        │      Focusing factor: reduces loss for confident predictions
        │
        Class weight: balance rare vs common classes
```

**Key parameters:**
- **γ (gamma) = 2.0:** Focusing strength
- **α (alpha):** Class weights based on frequency

### 13.5 FocalLoss in Action

**Example: Easy "O" prediction**
```
P(O) = 0.95  (model is very confident)

Standard CE:  -log(0.95) = 0.051
FocalLoss:    -(0.05)^2 × log(0.95) = 0.00013

FocalLoss contribution is 400× smaller!
```

**Example: Hard entity boundary**
```
P(B-PERP) = 0.60  (model is uncertain)

Standard CE:  -log(0.60) = 0.51
FocalLoss:    -(0.40)^2 × log(0.60) = 0.082

Still significant, forcing model to improve on hard cases.
```

### 13.6 Class Weights in Your System

```
From your training output:

O weight:        0.019  (heavily down-weighted)
B-FREQUENCY:     1.527  (heavily up-weighted - rarest entity)
B-PERPETRATOR:   0.156  (moderate weight)
```

**How weights are computed:**
```
weight[class] = 1 / sqrt(count[class])
```

Rare classes get higher weights, common classes get lower weights.

### 13.7 Combined Effect

```
┌────────────────────────────────────────────────────────────┐
│                                                            │
│   FocalLoss + Class Weights                                │
│                                                            │
│   Easy "O" prediction → Loss nearly zero → Ignored        │
│                                                            │
│   Hard entity prediction → Loss amplified → Focus here!   │
│                                                            │
│   Rare entity (FREQUENCY) → Extra weight → Learn it!      │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Thesis Defense Tip:**
> "I implemented FocalLoss to address the severe class imbalance in NER, where 68% of tokens are non-entities. FocalLoss down-weights easy 'O' predictions by a factor of up to 400×, focusing learning on entity boundaries where the model struggles."

---

## 14. Optimization and Learning

### 14.1 Gradient Descent

**Goal:** Find the 110 million weight values that minimize prediction errors.

#### The Valley Analogy (Expanded)

Imagine you're blindfolded and dropped somewhere in a vast mountain range. Your goal: find the lowest point in the deepest valley.

```
                    ⛰️
                   /\  /\
           You → X/  \/  \
                /        \⛰️
               /    ⬇️    \
              /   Valley   \
             /   (Goal)     \
            ⛰️               ⛰️
```

**The Challenge:**
- You can't SEE where the lowest point is (you're blindfolded)
- You can only FEEL the slope under your feet
- You must find the bottom using only local information

**Your Strategy:**
1. Feel which direction slopes downward (gradient)
2. Take a small step in that direction (weight update)
3. Repeat until you can't go any lower (convergence)

#### Connecting the Analogy to NER Training

| Analogy | NER Training | Meaning |
|---------|--------------|---------|
| **Your position** | 110 million weight values | Current state of the model |
| **Elevation** | Loss value | How wrong the predictions are |
| **Slope direction** | Gradient | Which weights to increase/decrease |
| **Step size** | Learning rate (2e-5) | How much to change weights |
| **Lowest valley** | Optimal weights | Best possible predictions |
| **Being blindfolded** | No closed-form solution | Can't directly compute optimal weights |

#### A Concrete Example

**Before training (random weights = random position on mountain):**
```
Input:  "Al Shabaab attacked Mogadishu"
Model predicts: O  O  O  O           ← All wrong!
Correct labels: B-PERP I-PERP O B-CITY
Loss = 3.2 (HIGH - you're high on the mountain)
```

**After 1 epoch (took some steps downhill):**
```
Input:  "Al Shabaab attacked Mogadishu"
Model predicts: B-PERP O O B-CITY    ← Getting better!
Correct labels: B-PERP I-PERP O B-CITY
Loss = 1.5 (LOWER - you've descended)
```

**After 5 epochs (near the valley floor):**
```
Input:  "Al Shabaab attacked Mogadishu"
Model predicts: B-PERP I-PERP O B-CITY  ← Correct!
Correct labels: B-PERP I-PERP O B-CITY
Loss = 0.1 (LOW - you've reached the valley)
```

#### Why the Analogy Works

**The mountain range = Loss landscape**

Your model has 110 million weights. Imagine each weight as a dimension. The loss is the "elevation" at each point in this 110-million-dimensional space.

```
2D simplified view (imagine 110 million dimensions!):

Loss ↑
     │    /\
     │   /  \    /\
     │  /    \  /  \
     │ /      \/    \
     │/   ★ ← Global minimum (best model)
     └────────────────→ Weight values
```

**Finding the lowest point:**
- You can't try all possible weight combinations (impossible - too many!)
- Instead, you iteratively improve: feel slope → step downhill → repeat
- This is gradient descent

#### The Multi-Dimensional Challenge

In our analogy, you walk on a 2D surface (x, y position → elevation).

In NER training:
- **Position:** 110,000,000 weight values
- **Elevation:** Single loss number

You're navigating a 110-million-dimensional landscape! The gradient tells you which of the 110 million directions to move.

```
Gradient = [∂L/∂w₁, ∂L/∂w₂, ∂L/∂w₃, ..., ∂L/∂w₁₁₀,₀₀₀,₀₀₀]
            ↑        ↑        ↑              ↑
           How much to adjust each of the 110M weights
```

#### Why Small Steps Matter

**Too large steps (high learning rate):**
```
           You overshoot!
              ↗️ X ↘️
             /      \
            /   ★    \    ← You keep jumping over the minimum
           /          \
```

**Just right steps (learning rate = 2e-5):**
```
           Gradual descent
              X
               ↘️
                 ↘️
                   ★    ← You gently settle into the minimum
```

**Too small steps (tiny learning rate):**
```
           Takes forever...
              X → x → x → x → x → x → ... → ★

           (You'll get there eventually, but it takes 1000 epochs!)
```

#### Local vs Global Minima

**The Tricky Part:** There might be multiple valleys!

```
Loss ↑
     │    /\
     │   /  \    /\
     │  / ○  \  /  \      ○ = Local minimum (pretty good)
     │ /      \/    \     ★ = Global minimum (best possible)
     │/         ★    \
     └────────────────→ Weight values
```

You might get stuck in a local minimum (a small valley) instead of finding the global minimum (the deepest valley).

**How BERT helps:** Pre-training puts you in a good starting position - already in the right "neighborhood" of the landscape. Fine-tuning just descends to the nearest good valley.

**Thesis Defense Tip:**
> "Gradient descent is how neural networks learn. The model's 110 million weights define a position in a vast parameter space. The loss function creates a 'landscape' where lower is better. Training is like descending a mountain blindfolded - we feel the local slope (gradient) and take small steps downhill (weight updates) until we reach a valley (minimum loss)."

### 14.2 The Gradient

The **gradient** tells us:
1. **Direction:** Which way to adjust each weight
2. **Magnitude:** How much to adjust

```
∂Loss/∂weight = gradient

Positive gradient → weight is contributing to error → decrease it
Negative gradient → weight is reducing error → increase it
```

### 14.3 Backpropagation

**Backpropagation** efficiently computes gradients for all 110 million weights.

```
Forward pass:  Input → Layer 1 → Layer 2 → ... → Layer 12 → Loss
                                                              ↓
Backward pass: Input ← Layer 1 ← Layer 2 ← ... ← Layer 12 ← Loss
               ∂L/∂w₁  ∂L/∂w₂             ...      ∂L/∂w₁₂
```

Uses the **chain rule** from calculus:
```
∂Loss/∂weight = ∂Loss/∂output × ∂output/∂weight
```

### 14.4 The Learning Rate

```
new_weight = old_weight - learning_rate × gradient
```

**Your learning rate: 2e-5 = 0.00002**

This tiny number prevents drastic changes:

```
Old weight:     0.50000
Gradient:       0.10000
Learning rate:  0.00002

New weight = 0.50000 - (0.00002 × 0.10000)
           = 0.50000 - 0.000002
           = 0.499998
```

**Why so small?**
- BERT was already pre-trained well
- We want to fine-tune, not destroy what it learned
- Large changes could make the model forget language understanding

### 14.5 AdamW Optimizer

Your system uses **AdamW** (Adam with Weight Decay):

```python
optimizer = AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)
```

**Adam features:**
1. **Momentum:** Remembers previous gradient directions
2. **Adaptive learning rates:** Different rates for different weights
3. **Weight decay:** Regularization to prevent overfitting

### 14.6 Learning Rate Schedule

Learning rate changes during training:

```
Epoch:     1        2        3        4        5
           ↓        ↓        ↓        ↓        ↓
LR:     2e-5 ───────────────────────────────> ~2e-6
           │                                    │
        Warmup                              Decay
    (gentle start)                    (fine adjustments)
```

**Warmup:** Start even lower, gradually reach 2e-5
**Decay:** Reduce learning rate as we approach optimal weights

---

## 15. Preventing Overfitting

### 15.1 What is Overfitting?

**Overfitting:** The model memorizes training data instead of learning generalizable patterns.

**Analogy:** A student who memorizes answers to practice tests but can't solve new problems.

**Signs:**
```
Training loss:   0.05  (very low)
Validation loss: 0.50  (much higher!)

Training accuracy: 98%
Validation accuracy: 80%
```

### 15.2 Detection in Your System

Watch these metrics during training:
```
Epoch 1: Train Loss: 0.80, Val Loss: 0.85  ✓ Both decreasing
Epoch 2: Train Loss: 0.40, Val Loss: 0.45  ✓ Both decreasing
Epoch 3: Train Loss: 0.20, Val Loss: 0.30  ✓ Gap appearing
Epoch 4: Train Loss: 0.10, Val Loss: 0.35  ⚠️ Val increasing!
Epoch 5: Train Loss: 0.05, Val Loss: 0.45  ❌ OVERFITTING!
```

### 15.3 Prevention Strategies

**1. Early Stopping**
```
Stop training when validation loss stops improving
Save the best model (lowest validation loss)
```

**2. Dropout** (built into BERT)
```
During training: Randomly set 10% of neurons to zero
This prevents co-adaptation and improves generalization
```

**3. Weight Decay**
```
Add penalty for large weights
Keeps weights small and model simpler
```

**4. Data Augmentation** (optional)
```
Slightly modify training examples
Creates more diverse training data
```

### 15.4 Your Checkpointing System

```
After each epoch:
  Save checkpoint: epoch_1.pt, epoch_2.pt, ...

If validation loss improves:
  Copy to: best_model.pt  ← This is used for inference
```

**Thesis Defense Tip:**
> "I prevent overfitting through multiple mechanisms: dropout in BERT layers, weight decay in AdamW optimizer, and early stopping based on validation loss. The best model checkpoint is saved when validation performance peaks."

---

# Part V: Evaluation

## 16. Metrics That Matter

### 16.1 Why Accuracy Isn't Enough

In NER, accuracy is misleading:

```
Sentence: "The attack killed 15 people in Maiduguri on Monday"
Tokens:   "The attack killed 15 people in Maiduguri on Monday"
Labels:    O   B-EVT   O     B-CAS  O    O  B-CITY   O  B-DATE

Token count: 9
Entity tokens: 4 (attack, 15, Maiduguri, Monday)
O tokens: 5
```

**If model predicts ALL "O":**
```
Predictions: O O O O O O O O O
Accuracy: 5/9 = 55.6%  ← Sounds okay, but missed EVERYTHING!
```

### 16.2 Precision, Recall, and F1

**Precision:** Of what you predicted, how many were correct?
```
Precision = True Positives / (True Positives + False Positives)

"Of all entities I found, how many actually exist?"
```

**Recall:** Of what exists, how many did you find?
```
Recall = True Positives / (True Positives + False Negatives)

"Of all actual entities, how many did I catch?"
```

**F1 Score:** Balance between precision and recall
```
F1 = 2 × (Precision × Recall) / (Precision + Recall)
```

### 16.3 Concrete Example

**Sentence:** "Al Shabaab attacked Mogadishu on Monday"

**True entities:**
1. Al Shabaab (PERPETRATOR)
2. attacked (EVENT_TYPE)
3. Mogadishu (CITY)
4. Monday (DATE)

**Model predictions:**
1. Al Shabaab (PERPETRATOR) ✓ True Positive
2. attacked (EVENT_TYPE) ✓ True Positive
3. Mogadishu (CITY) ✓ True Positive
4. on (CITY) ✗ False Positive (wrongly predicted)
5. (missed Monday) ✗ False Negative

**Calculation:**
```
True Positives (TP): 3
False Positives (FP): 1
False Negatives (FN): 1

Precision = 3 / (3 + 1) = 0.75 (75%)
Recall = 3 / (3 + 1) = 0.75 (75%)
F1 = 2 × (0.75 × 0.75) / (0.75 + 0.75) = 0.75 (75%)
```

### 16.4 Entity-Level vs Token-Level

**Token-level:** Evaluate each BIO tag individually
```
Token: "Al" "Shabaab" "attacked"
True:   B-P   I-P       B-EVT
Pred:   B-P   B-P       B-EVT  ← Wrong! "Shabaab" should be I-P
```

**Entity-level:** Evaluate complete entity spans
```
"Al Shabaab" as one PERPETRATOR entity
- Only correct if BOTH tokens have correct tags
- AND form a valid B-I sequence
```

**Entity-level is stricter and more meaningful.**

### 16.5 Per-Class Metrics

Your system should report metrics for each entity type:

```
Entity Type     Precision  Recall    F1
──────────────────────────────────────────
PERPETRATOR       0.92      0.89    0.90
VICTIM            0.88      0.85    0.86
EVENT_TYPE        0.94      0.93    0.93
CITY              0.91      0.90    0.90
DATE              0.96      0.95    0.95
WEAPON            0.85      0.82    0.83
CASUALTIES        0.89      0.87    0.88
MOTIVE            0.72      0.68    0.70  ← Lower (rare type)
──────────────────────────────────────────
OVERALL           0.91      0.89    0.90
```

---

## 17. 5W1H Evaluation Framework

### 17.1 Semantic Completeness

Beyond entity accuracy, evaluate **event completeness:**

**Complete event (all 5W answered):**
```
WHO: Al Shabaab (PERPETRATOR)
WHAT: attacked (EVENT_TYPE)
WHEN: Monday (DATE)
WHERE: Mogadishu (CITY)
HOW: 15 killed (CASUALTIES)
```

**Incomplete event:**
```
WHO: Al Shabaab ✓
WHAT: ? (missing)
WHEN: Monday ✓
WHERE: ? (missing)
HOW: 15 killed ✓
```

### 17.2 Semantic Consistency

Check entity relationships make sense:

**Consistent:**
```
PERPETRATOR: "Al Shabaab" (armed group)
EVENT_TYPE: "attacked" (violent action)
VICTIM: "soldiers" (people)
```

**Inconsistent:**
```
PERPETRATOR: "Red Cross" ← Humanitarian org as perpetrator?
```

### 17.3 Error Analysis

Categorize errors to understand model weaknesses:

**Error types:**
1. **Boundary errors:** "Al" recognized but "Shabaab" missed
2. **Type confusion:** VICTIM predicted as TARGET
3. **Missed entities:** Completely undetected
4. **Spurious entities:** Predicted where none exists

**Your error analysis should show:**
```
Error Type          Count    Percentage
─────────────────────────────────────────
Missed entities      150         45%
Type confusion        80         24%
Boundary errors       70         21%
Spurious entities     30         10%
```

**Thesis Defense Tip:**
> "I evaluate my model at both token-level and entity-level, and perform 5W1H completeness analysis. Error analysis shows most mistakes are missed entities rather than wrong predictions, suggesting the model is conservative - preferring precision over recall."

---

# Part VI: Your System

## 18. VioNER Architecture

### 18.1 System Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                           VioNER System                                 │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Data Pipeline                                 │   │
│  │                                                                  │   │
│  │  ACLED CSV ──▶ enhance_csv.py ──▶ preprocessing.py ──▶ JSON    │   │
│  │               (extract entities)  (convert to BIO)    (train/val)│   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│                                    ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Training Pipeline                            │   │
│  │                                                                  │   │
│  │  train.json ──▶ NERDataset ──▶ BERT+FocalLoss ──▶ Checkpoints │   │
│  │  val.json      (batching)     (fine-tuning)      (best_model)  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│                                    ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Inference Pipeline                           │   │
│  │                                                                  │   │
│  │  News Article ──▶ Tokenize ──▶ Model ──▶ BIO tags ──▶ Entities │   │
│  │                                                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│                                    ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Knowledge Base                               │   │
│  │                                                                  │   │
│  │  Armed Groups (150+) │ Cities (300+) │ Violence Taxonomy (95)   │   │
│  │  Validation & Normalization                                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│                                    ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    API & Database                               │   │
│  │                                                                  │   │
│  │  FastAPI Server ──▶ PostgreSQL (Events, Actors, Locations)     │   │
│  │       │                                                         │   │
│  │       └──▶ Analytics Dashboard                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

### 18.2 File Structure (After Refactoring)

```
named-entity-recognition/
├── backend/
│   ├── pipeline/               # Core ML pipeline
│   │   ├── config.py          # Entity labels, model config
│   │   ├── preprocessing.py   # CSV → BIO conversion
│   │   ├── training.py        # BERT fine-tuning
│   │   ├── loss.py            # FocalLoss, class weights
│   │   ├── kb.py              # Knowledge base
│   │   └── validator.py       # Entity validation
│   │
│   ├── services/              # Business logic
│   │   ├── ner.py             # NER inference service
│   │   ├── training.py        # Training management
│   │   ├── evaluation.py      # Metrics computation
│   │   └── resolver.py        # Entity resolution
│   │
│   ├── api/                   # REST API
│   │   ├── inference/         # /extract endpoints
│   │   └── training/          # /training endpoints
│   │
│   └── scripts/
│       └── enhance_csv.py     # Data enhancement (v4)
│
├── data/
│   ├── annotations/
│   │   ├── training.csv           # Enhanced source data
│   │   └── training_enhanced_v4.csv
│   │
│   └── processed/
│       ├── train.json        # Training set (95,067)
│       ├── val.json          # Validation set (23,767)
│       └── statistics.json   # Dataset stats
│
└── docs/
    └── NER_LEARNING_GUIDE.md  # This document
```

---

## 19. The Knowledge Base

### 19.1 Purpose

The Knowledge Base (KB) provides domain expertise:

1. **Validation:** Is "Al Shabaab" a valid perpetrator?
2. **Normalization:** "Al-Shabaab" → "Al Shabaab"
3. **Inference:** If city is "Mogadishu", country is "Somalia"
4. **Enhancement:** Extract entities the model might miss

### 19.2 KB Components

**Armed Groups (150+):**
```python
"al-shabaab": ArmedGroup(
    name="Al-Shabaab",
    aliases=["al-shabab", "alshabaab", "harakat al-shabaab"],
    country="Somalia",
    group_type="terrorist"
)
```

**Conflict Cities (300+):**
```python
"mogadishu": {"country": "Somalia", "region": "Benadir"}
"maiduguri": {"country": "Nigeria", "region": "Borno"}
```

**Violence Taxonomy (95 categories):**
```python
"armed_conflict": ["battle", "clashes", "firefight"]
"terrorism": ["suicide bombing", "IED attack"]
"violence_against_civilians": ["massacre", "extrajudicial killing"]
```

### 19.3 KB Usage in Pipeline

```
Input: "AShabaab militants attacked Mogadishu"
                    ↓
┌─────────────────────────────────────────────────┐
│  Step 1: NER Model Prediction                   │
│  "AShabaab" → B-PERPETRATOR (uncertain)         │
│  "militants" → I-PERPETRATOR                    │
│  "Mogadishu" → B-CITY                           │
└───────────────────────┬─────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│  Step 2: Knowledge Base Validation              │
│  "AShabaab" → normalize → "Al-Shabaab" ✓        │
│  "Mogadishu" → lookup → Somalia ✓               │
└───────────────────────┬─────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│  Step 3: Entity Resolution                      │
│  Add inferred entities:                         │
│  COUNTRY: "Somalia" (from CITY)                 │
│  REGION: "Benadir" (from CITY)                  │
└─────────────────────────────────────────────────┘
```

---

## 20. Thesis Defense Preparation

### 20.1 Key Points to Remember

**What is NER?**
> "Named Entity Recognition automatically identifies and classifies important entities in text - like perpetrators, locations, and dates in conflict reports."

**Why BERT?**
> "BERT's bidirectional attention captures contextual relationships between words, and its pre-training on massive text means we can fine-tune with limited domain data."

**How do you handle class imbalance?**
> "The 'O' label dominates at 68%. I use FocalLoss which down-weights confident predictions by up to 400×, forcing the model to focus on difficult entity boundaries."

**What is your entity schema?**
> "I designed a 26-type schema based on the 5W1H framework - covering Who (5 types), What (4), When (4), Where (7), Why (2), and How (4). This enables complete event understanding."

**How do you evaluate?**
> "Beyond token accuracy, I measure entity-level F1 scores and 5W1H completeness. Error analysis shows most mistakes are missed entities rather than wrong predictions."

### 20.2 Anticipated Questions & Answers

**Q: Why not use a simpler model like CRF?**
> A: "CRF achieves around 70-80% F1 on NER. BERT-based models achieve 90%+ because they capture long-range context and leverage pre-trained language knowledge."

**Q: How much data did you need?**
> A: "I used 95,000 training examples. Thanks to transfer learning from BERT (pre-trained on 3.3B words), this was sufficient to achieve strong performance."

**Q: How do you handle entities the model has never seen?**
> A: "BERT uses subword tokenization - rare words are split into known pieces. The knowledge base provides additional validation and normalization for domain-specific terms."

**Q: What is the inference latency?**
> A: "Single sentence: ~50ms. Batch of 32: ~100ms total. The API can process thousands of articles per hour on a single GPU."

**Q: What are the main sources of error?**
> A: "Error analysis shows three main categories: (1) Missed rare entities like MOTIVE and TRIGGER, (2) Boundary errors on multi-word entities, (3) Type confusion between VICTIM and TARGET."

### 20.3 Diagram for Your Presentation

```
┌─────────────────────────────────────────────────────────────────────┐
│                     VioNER: Complete Pipeline                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│     News Article                                                     │
│         │                                                            │
│         ▼                                                            │
│   ┌───────────────────────────────────────────┐                     │
│   │             BERT + Classification          │                     │
│   │        (110M parameters, fine-tuned)       │                     │
│   └───────────────────────────────────────────┘                     │
│         │                                                            │
│         ▼                                                            │
│   ┌───────────────────────────────────────────┐                     │
│   │           BIO Tag Sequence                 │                     │
│   │   [B-PERP, I-PERP, O, B-CITY, O, B-DATE]  │                     │
│   └───────────────────────────────────────────┘                     │
│         │                                                            │
│         ▼                                                            │
│   ┌───────────────────────────────────────────┐                     │
│   │        Entity Extraction & KB             │                     │
│   │      Validation/Normalization/Inference   │                     │
│   └───────────────────────────────────────────┘                     │
│         │                                                            │
│         ▼                                                            │
│   ┌───────────────────────────────────────────┐                     │
│   │           Structured Output               │                     │
│   │  ┌─────────────────────────────────────┐  │                     │
│   │  │ WHO:   Al Shabaab (PERPETRATOR)     │  │                     │
│   │  │ WHAT:  attacked (EVENT_TYPE)        │  │                     │
│   │  │ WHEN:  Monday (DATE)                │  │                     │
│   │  │ WHERE: Mogadishu, Somalia           │  │                     │
│   │  │ HOW:   15 killed (CASUALTIES)       │  │                     │
│   │  └─────────────────────────────────────┘  │                     │
│   └───────────────────────────────────────────┘                     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

# Appendices

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Attention** | Mechanism for weighing importance of different input elements |
| **Backpropagation** | Algorithm to compute gradients through the network |
| **Batch** | Group of samples processed together for efficiency |
| **BERT** | Bidirectional Encoder Representations from Transformers |
| **BIO Tagging** | Begin-Inside-Outside labeling scheme for NER |
| **Checkpoint** | Saved model state during training |
| **Cross-Entropy** | Standard loss function for classification |
| **Embedding** | Dense vector representation of a word |
| **Epoch** | One complete pass through training data |
| **F1 Score** | Harmonic mean of precision and recall |
| **Fine-tuning** | Adapting pre-trained model to specific task |
| **FocalLoss** | Loss function that focuses on hard examples |
| **Gradient** | Direction and magnitude for weight updates |
| **Learning Rate** | Step size for weight adjustments |
| **MPS** | Metal Performance Shaders (Apple GPU acceleration) |
| **NER** | Named Entity Recognition |
| **Overfitting** | Memorizing training data instead of learning patterns |
| **Precision** | Proportion of predictions that are correct |
| **Recall** | Proportion of actual entities that are found |
| **Self-Attention** | Attention where each token attends to all others |
| **Token** | Basic unit of text (word or subword) |
| **Transformer** | Neural network architecture using attention |
| **Transfer Learning** | Using pre-trained knowledge for new tasks |
| **Weight Decay** | Regularization that penalizes large weights |
| **WordPiece** | Subword tokenization algorithm used by BERT |

## Appendix B: Common Questions and Answers

**Q: What if the model predicts I-X without a preceding B-X?**
A: This is an invalid sequence. Post-processing converts it to B-X (treat as new entity start).

**Q: How do you handle punctuation?**
A: Punctuation tokens are typically labeled "O". The tokenizer separates them from words.

**Q: What about very long documents?**
A: BERT has a 512 token limit. Long documents are split into overlapping windows and predictions are merged.

**Q: Can the model handle multiple languages?**
A: The current model is English-only. Multilingual BERT (mBERT) could handle African languages with additional training.

**Q: How often should the model be retrained?**
A: When new conflict actors emerge, terminology changes, or accuracy drops. Typically every 6-12 months.

## Appendix C: Key Papers to Reference

1. **BERT Original Paper:**
   Devlin et al., "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding", NAACL 2019

2. **Transformer Paper:**
   Vaswani et al., "Attention Is All You Need", NeurIPS 2017

3. **FocalLoss Paper:**
   Lin et al., "Focal Loss for Dense Object Detection", ICCV 2017

4. **NER Survey:**
   Li et al., "A Survey on Deep Learning for Named Entity Recognition", TKDE 2020

5. **African Conflict Data:**
   ACLED (Armed Conflict Location & Event Data Project), acleddata.com

---

*This guide was created for the VioNER Master's Thesis project at Addis Ababa University.*
*Author: Binalfew Kassa Mekonnen*
*Last Updated: December 2025*
