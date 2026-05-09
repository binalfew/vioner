# VioNER Training Data Preparation Guide

This guide provides detailed step-by-step instructions to prepare optimized training data for the VioNER (Violent Event Named Entity Recognition) model.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Directory Structure](#directory-structure)
3. [Entity Schema](#entity-schema)
4. [Pipeline Overview](#pipeline-overview)
5. [Step 1: Setup Environment](#step-1-setup-environment)
6. [Step 2: Preprocess Raw Data](#step-2-preprocess-raw-data)
7. [Step 3: Create Optimized Subset with Augmentation](#step-3-create-optimized-subset-with-augmentation)
8. [Step 4: Verify Generated Data](#step-4-verify-generated-data)
9. [Step 5: Train the Model](#step-5-train-the-model)
10. [Data Format Reference](#data-format-reference)
11. [Augmentation Details](#augmentation-details)
12. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- Python 3.9+
- pip (Python package manager)
- Virtual environment (venv)

### Required Files
- Raw ACLED data: `data/source/events_for_annotation.jsonl`

### Required Python Packages
```
torch
transformers
tqdm
numpy
```

---

## Directory Structure

```
backend/
├── data/
│   ├── source/
│   │   └── events_for_annotation.jsonl    # Raw ACLED data (input)
│   └── processed/
│       ├── train.jsonl                     # Training data (output)
│       └── val.jsonl                       # Validation data (output)
├── scripts/
│   ├── create_training_subset.py           # Subset selection + augmentation
│   └── augment_training_data.py            # Augmentation module
├── pipeline/
│   ├── preprocessing.py                    # Raw data preprocessing
│   ├── training.py                         # Model training
│   └── config.py                           # Entity labels configuration
├── models/                                 # Trained models output
├── venv/                                   # Python virtual environment
├── train_local.sh                          # Training script
└── docs/
    └── DATA_PREPARATION.md                 # This file
```

---

## Entity Schema

VioNER uses 8 entity types in BIO (Beginning-Inside-Outside) format:

| Entity Type | Description | Examples |
|-------------|-------------|----------|
| **ACTOR** | Perpetrators, armed groups, forces | Militants, Boko Haram, RSF, police |
| **VICTIM** | People affected by violence | civilians, villagers, farmers |
| **ACTION** | Violent actions or events | attacked, killed, clash, raid |
| **DATE** | When events occurred | On Monday, January 15, 2024 |
| **CITY** | Cities, towns, villages | Maiduguri, Goma, Bangui |
| **REGION** | States, provinces, regions | North Darfur, Tigray, Ituri |
| **DISTRICT** | Districts, counties, localities | Budi, Masisi, Kutum |
| **CASUALTIES** | Death/injury counts | killed 5, 10 dead, 3 fatalities |

### BIO Labeling Format

- `B-ENTITY` = Beginning of entity
- `I-ENTITY` = Inside (continuation) of entity
- `O` = Outside (not an entity)

**Example:**
```
Text:    "Militants attacked Maiduguri on Monday"
Tokens:  ["Militants", "attacked", "Maiduguri", "on", "Monday"]
Labels:  ["B-ACTOR",   "B-ACTION", "B-CITY",    "O",  "B-DATE"]
```

**Multi-word entity example:**
```
Text:    "Al Shabaab killed civilians in North Darfur"
Tokens:  ["Al", "Shabaab", "killed", "civilians", "in", "North", "Darfur"]
Labels:  ["B-ACTOR", "I-ACTOR", "B-ACTION", "B-VICTIM", "O", "B-REGION", "I-REGION"]
```

---

## Pipeline Overview

The data preparation pipeline consists of three main steps:

```
┌─────────────────────────────────────────────────────────────────────┐
│  Step 1: Preprocessing                                              │
│  Raw ACLED JSONL → Tokenized BIO format                            │
│  Input:  events_for_annotation.jsonl (212K events)                 │
│  Output: train.jsonl (170K) + val.jsonl (42K)                      │
└─────────────────────────────────────────────────────────────────────┘
                                   ↓
┌─────────────────────────────────────────────────────────────────────┐
│  Step 2: Subset Selection + Augmentation                           │
│  - Stratified sampling for rare entities (VICTIM, ACTION)          │
│  - Diversity sampling to avoid redundant patterns                  │
│  - Add 15K synthetic examples with missing vocabulary              │
│  Input:  train.jsonl (170K)                                        │
│  Output: train.jsonl (40K) + val.jsonl (10K)                       │
└─────────────────────────────────────────────────────────────────────┘
                                   ↓
┌─────────────────────────────────────────────────────────────────────┐
│  Step 3: Training                                                   │
│  BERT-based NER model training with early stopping                 │
│  Input:  train.jsonl + val.jsonl                                   │
│  Output: models/bert-base-cased_TIMESTAMP/best/                    │
└─────────────────────────────────────────────────────────────────────┘
```

### Why This Approach?

| Problem | Solution |
|---------|----------|
| Dataset too large (212K) with low diversity (32%) | Select 35K diverse subset with 96% unique patterns |
| Vocabulary gaps (ACLED uses nouns, not verbs) | Add 15K augmented examples with action verbs |
| Rare entities (VICTIM 2%, ACTION 3.6%) | Stratified sampling prioritizes rare entities |

---

## Step 1: Setup Environment

### 1.1 Navigate to Backend Directory

```bash
cd /Users/binalfew/Documents/Masters/named-entity-recognition/backend
```

### 1.2 Create Virtual Environment (if not exists)

```bash
python3 -m venv venv
```

### 1.3 Activate Virtual Environment

```bash
source venv/bin/activate
```

### 1.4 Install Dependencies

```bash
pip install torch transformers tqdm numpy
```

### 1.5 Verify Setup

```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import transformers; print(f'Transformers: {transformers.__version__}')"
```

---

## Step 2: Preprocess Raw Data

This step converts raw ACLED JSONL to tokenized BIO format.

### 2.1 Verify Input File Exists

```bash
ls -la data/source/events_for_annotation.jsonl
```

Expected: File should exist and be non-empty (~50-100MB)

### 2.2 Run Preprocessing

```bash
python -m pipeline.preprocessing \
    --input ./data/source/events_for_annotation.jsonl \
    --output ./data/processed
```

### 2.3 Expected Output

```
Processing events...
Processed 212,590 events
Saved 170,072 training examples to data/processed/train.jsonl
Saved 42,518 validation examples to data/processed/val.jsonl
```

### 2.4 Verify Output Files

```bash
wc -l data/processed/train.jsonl data/processed/val.jsonl
```

Expected:
```
  170072 data/processed/train.jsonl
   42518 data/processed/val.jsonl
  212590 total
```

---

## Step 3: Create Optimized Subset with Augmentation

This step:
1. Selects a diverse 35K subset from the preprocessed data
2. Adds 15K augmented examples with missing vocabulary
3. Splits into 80% train / 20% validation

### 3.1 Run Subset Creation with Augmentation

```bash
python scripts/create_training_subset.py \
    --size 35000 \
    --augment 15000 \
    --output-dir ./data/processed
```

### 3.2 Expected Output

```
============================================================
TRAINING DATA SUBSET CREATOR
============================================================
Loading data from: ./data/processed/train.jsonl
Loaded 170,072 valid examples

Original data statistics:
  Total examples: 170,072
  Unique patterns: 54,234
  Entity distribution:
    ACTOR       :   89,432
    CITY        :   78,234
    DATE        :   72,891
    ...

Stratified sampling for target size: 35,000
--------------------------------------------------
Step 1: Selecting examples with rare entities...
  Selected 12,000 examples with rare entities
    VICTIM: 3,500 tokens
    ACTION: 2,800 tokens
    CASUALTIES: 3,200 tokens

Step 2: Selecting diverse examples (multiple entity types)...
  Added 11,666 diverse examples

Step 3: Random sampling for remaining 11,334 examples...
  Final selection: 35,000 examples

============================================================
ADDING 15,000 AUGMENTED EXAMPLES
============================================================
  Added 15,000 augmented examples
  Final total: 50,000 examples

Saved to: ./data/processed
  train.jsonl: 40,000 examples (80%)
  val.jsonl:   10,000 examples (20%)

============================================================
SUMMARY
============================================================
Original data:    170,072 examples
Selected subset:  50,000 examples (29.4%)
  - Train set:    40,000 examples (80%)
  - Val set:      10,000 examples (20%)
Augmented:        15,000 examples

Output directory: ./data/processed
  - train.jsonl
  - val.jsonl

Next step - run training:
  ./train_local.sh
```

### 3.3 Verify Output Files

```bash
wc -l data/processed/train.jsonl data/processed/val.jsonl
```

Expected:
```
   40000 data/processed/train.jsonl
   10000 data/processed/val.jsonl
   50000 total
```

---

## Step 4: Verify Generated Data

### 4.1 Check Data Format

```bash
head -1 data/processed/train.jsonl | python -m json.tool
```

Expected format:
```json
{
    "tokens": ["Militants", "attacked", "Maiduguri", "..."],
    "labels": ["B-ACTOR", "B-ACTION", "B-CITY", "..."],
    "text": "Militants attacked Maiduguri...",
    "source": "augmentation"  // Only for augmented examples
}
```

### 4.2 Count Augmented Examples

```bash
grep -c '"source": "augmentation"' data/processed/train.jsonl
grep -c '"source": "augmentation"' data/processed/val.jsonl
```

Expected: ~12,000 in train.jsonl, ~3,000 in val.jsonl (80/20 split of 15K)

### 4.3 Verify No Grammar Issues

Check that these problematic patterns do NOT exist:

```bash
# Should return 0 matches
grep -c "on On " data/processed/train.jsonl
grep -c "on Earlier this week" data/processed/train.jsonl
grep -c "on Last " data/processed/train.jsonl
grep -c '[0-9] community\.' data/processed/train.jsonl
```

If any of these return non-zero, the augmentation script needs fixing.

### 4.4 Sample Augmented Sentences

```bash
grep '"source": "augmentation"' data/processed/train.jsonl | head -5 | python -c "
import sys, json
for line in sys.stdin:
    data = json.loads(line)
    print(data['text'])
    print()
"
```

Review the output for grammatical correctness.

---

## Step 5: Train the Model

### 5.1 Quick Training (Default Settings)

```bash
./train_local.sh
```

### 5.2 Custom Training Settings

```bash
# Fewer epochs, more patience
EPOCHS=5 PATIENCE=2 ./train_local.sh

# More epochs, larger batch size
EPOCHS=15 BATCH_SIZE=32 ./train_local.sh

# Disable early stopping
EARLY_STOPPING=false EPOCHS=10 ./train_local.sh
```

### 5.3 Training Parameters Reference

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MODEL` | bert-base-cased | Base model |
| `EPOCHS` | 10 | Maximum epochs |
| `BATCH_SIZE` | 16 | Training batch size |
| `LEARNING_RATE` | 2e-5 | Initial learning rate |
| `PATIENCE` | 3 | Early stopping patience |
| `EARLY_STOPPING` | true | Enable early stopping |
| `LR_SCHEDULER` | reduce_on_plateau | LR scheduler type |

### 5.4 Expected Training Output

```
========================================
  VioNER Local Training
========================================

Checking GPU support...
MPS (Apple Silicon GPU): Available

Training Configuration:
  Model:         bert-base-cased
  Total Epochs:  10
  Batch Size:    16
  Learning Rate: 2e-5
  Train Data:    ./data/processed/train.jsonl
  Val Data:      ./data/processed/val.jsonl
  Output Dir:    ./models

Training Optimizations:
  Early Stopping: true (patience=3)
  LR Scheduler:   reduce_on_plateau (reduce patience=2)

Starting training...

Epoch 1/10: 100%|████████████| 2500/2500 [15:32<00:00]
  Train Loss: 0.234  Val Loss: 0.189  Val F1: 0.823

Epoch 2/10: 100%|████████████| 2500/2500 [15:28<00:00]
  Train Loss: 0.156  Val Loss: 0.142  Val F1: 0.867
  ✓ New best model saved

...

========================================
  Training Complete!
========================================

Models saved to: ./models
```

---

## Data Format Reference

### Input Format (Raw ACLED)

```json
{
    "event_id": "NIG12345",
    "event_date": "2024-01-15",
    "notes": "Boko Haram militants attacked Maiduguri, killing 5 civilians.",
    "fatalities": 5,
    "actor1": "Boko Haram",
    "location": "Maiduguri",
    "admin1": "Borno"
}
```

### Output Format (Processed)

```json
{
    "id": "NIG12345",
    "text": "Boko Haram militants attacked Maiduguri, killing 5 civilians.",
    "tokens": ["Boko", "Haram", "militants", "attacked", "Maiduguri", ",", "killing", "5", "civilians", "."],
    "labels": ["B-ACTOR", "I-ACTOR", "O", "B-ACTION", "B-CITY", "O", "B-CASUALTIES", "I-CASUALTIES", "B-VICTIM", "O"],
    "entities": [
        {"text": "Boko Haram", "type": "ACTOR", "start": 0, "end": 10},
        {"text": "attacked", "type": "ACTION", "start": 22, "end": 30},
        {"text": "Maiduguri", "type": "CITY", "start": 31, "end": 40},
        {"text": "killing 5", "type": "CASUALTIES", "start": 42, "end": 51},
        {"text": "civilians", "type": "VICTIM", "start": 52, "end": 61}
    ]
}
```

### Augmented Example Format

```json
{
    "tokens": ["Militants", "attacked", "Goma", ",", "killing", "12", "civilians", "."],
    "labels": ["B-ACTOR", "B-ACTION", "B-CITY", "O", "O", "B-CASUALTIES", "B-VICTIM", "O"],
    "text": "Militants attacked Goma, killing 12 civilians.",
    "source": "augmentation"
}
```

---

## Augmentation Details

### What Gets Augmented

The augmentation script (`scripts/augment_training_data.py`) generates synthetic examples to fill vocabulary gaps in the ACLED data.

### Verb Categories

**1. Simple Action Verbs** (location-taking):
```
attacked, raided, stormed, invaded, struck, hit, overran, sacked,
bombed, shelled, destroyed, burned, torched, razed, demolished,
devastated, ravaged, gutted, wrecked, ruined,
captured, seized, occupied, surrounded, encircled, besieged, blockaded, conquered,
looted, ransacked, pillaged, plundered, breached, sabotaged, vandalized
```

**2. Victim Action Verbs** (victim-taking):
```
killed, murdered, slaughtered, massacred, executed, shot, butchered,
beheaded, decapitated, hanged, lynched, strangled, drowned, poisoned,
wounded, injured, maimed, kidnapped, abducted, detained, arrested,
apprehended, tortured, brutalized, assaulted, displaced, expelled, evicted
```

**3. Clash Verbs**:
```
Single-word: battled, fought, engaged, confronted, repelled, routed, defeated, overpowered
Multi-word: clashed with, skirmished with, exchanged fire with, traded fire with
```

### Template Patterns

**Location Templates:**
```
{actor} {action} {location}, killing {num_killed} {victim_type}.
{actor} {action} {location}, leaving {num_killed} dead and {num_injured} injured.
{date}, {actor} {action} {location}.
{actor} {action} {location} and looted several buildings.
{num_killed} {victim_type} were killed when {actor} {action} {location}.
{actor} armed with heavy weapons {action} {location}, resulting in {num_killed} casualties.
{actor} {action} several villages in {region}, leaving at least {num_killed} dead.
{actor} {action} {location} and abducted {num_killed} {victim_type}.
{actor} {action} {location} in a dawn raid, killing {num_killed} {victim_type}.
{actor} seized {location} after a prolonged siege.
```

**Victim Templates:**
```
{actor} {action} {num_killed} {victim_type} in {location}.
{date}, {actor} {action} {num_killed} {victim_type} in {location}.
{actor} {action} at least {num_killed} {victim_type} in {region}.
{actor} {action} {num_killed} {victim_type} during an overnight raid in {location}.
{actor} {action} {num_killed} {victim_type} and injured {num_injured} others in {location}.
{actor} {action} {num_killed} {victim_type} near {location}.
{actor} {action} {num_killed} {victim_type} in {region}.
```

**Clash Templates:**
```
{actor} {clash_action} {actor2} in {location}.
{actor} {clash_action} {actor2} in {location}, leaving {num_killed} dead.
{date}, {actor} {clash_action} {actor2} near {location}.
Heavy fighting erupted when {actor} {clash_action} {actor2} in {region}.
{actor} {clash_action} {actor2} in {location}, with {num_killed} casualties reported.
```

### Date Formats

```
On January 15, 2024
On Monday
Last Tuesday
January 15
Earlier this week
On Wednesday morning
On Friday night
```

---

## Troubleshooting

### Error: "File not found"

**Problem:** Script can't find input files.

**Solution:**
```bash
# Ensure you're in the backend directory
cd /Users/binalfew/Documents/Masters/named-entity-recognition/backend

# Verify files exist
ls -la data/source/events_for_annotation.jsonl
ls -la data/processed/train.jsonl
```

### Error: "ModuleNotFoundError"

**Problem:** Python packages not installed or venv not activated.

**Solution:**
```bash
# Activate virtual environment
source venv/bin/activate

# Install missing packages
pip install torch transformers tqdm numpy

# Verify installation
python -c "import torch, transformers, tqdm, numpy; print('All packages OK')"
```

### Error: "No module named 'pipeline'"

**Problem:** Running from wrong directory.

**Solution:**
```bash
# Must run from backend directory
cd /Users/binalfew/Documents/Masters/named-entity-recognition/backend
python -m pipeline.preprocessing ...
```

### Warning: Grammar Issues in Augmented Data

**Problem:** Augmented sentences have grammar errors like "on On Monday".

**Solution:** This was fixed in the augmentation script. Regenerate the data:
```bash
python scripts/create_training_subset.py \
    --size 35000 \
    --augment 15000 \
    --output-dir ./data/processed
```

### Adjusting Dataset Size

**Smaller dataset (faster training):**
```bash
python scripts/create_training_subset.py --size 20000 --augment 10000 --output-dir ./data/processed
```

**Larger dataset (more coverage):**
```bash
python scripts/create_training_subset.py --size 50000 --augment 20000 --output-dir ./data/processed
```

### Checking GPU Availability

```bash
python -c "
import torch
print(f'CUDA available: {torch.cuda.is_available()}')
print(f'MPS available: {torch.backends.mps.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA device: {torch.cuda.get_device_name(0)}')
"
```

### Resuming Training

```bash
RESUME=./models/bert-base-cased_20240115_120000 ./train_local.sh
```

### Extending Training

```bash
RESUME=./models/bert-base-cased_20240115_120000 EXTEND_EPOCHS=5 ./train_local.sh
```

---

## Quick Reference: Complete Pipeline

```bash
# 1. Setup
cd /Users/binalfew/Documents/Masters/named-entity-recognition/backend
source venv/bin/activate

# 2. Preprocess raw data (only needed once)
python -m pipeline.preprocessing \
    --input ./data/source/events_for_annotation.jsonl \
    --output ./data/processed

# 3. Create optimized subset with augmentation
python scripts/create_training_subset.py \
    --size 35000 \
    --augment 15000 \
    --output-dir ./data/processed

# 4. Verify data (optional but recommended)
wc -l data/processed/*.jsonl
grep -c '"source": "augmentation"' data/processed/train.jsonl

# 5. Train model
./train_local.sh
```

---

## Final Dataset Summary

| Component | Examples | Purpose |
|-----------|----------|---------|
| Diverse ACLED subset | 35,000 | Real events with 96% pattern diversity |
| Augmented synthetic | 15,000 | Missing vocabulary coverage |
| **Total** | **50,000** | Balanced, comprehensive training set |

### Train/Val Split

| File | Examples | Percentage |
|------|----------|------------|
| train.jsonl | 40,000 | 80% |
| val.jsonl | 10,000 | 20% |

### Entity Coverage Improvement

| Entity | Original | After Optimization |
|--------|----------|-------------------|
| ACTOR | 20% | 30% |
| CITY | 21% | 31% |
| DATE | 22% | 31% |
| REGION | 22% | 33% |
| DISTRICT | 22% | 32% |
| ACTION | 3.6% | **26%** |
| VICTIM | 2% | **30%** |
| CASUALTIES | 4% | **32%** |
