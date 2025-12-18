# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VioNER (Violent Event Named Entity Recognition) - A full-stack system for extracting structured 5W1H+WHY information from news articles about violent events in Africa. The system combines BERT-based NER with a knowledge base of African armed groups, locations, and conflict data.

## Common Commands

### Backend (FastAPI + PyTorch)

```bash
# From backend/ directory
source venv/bin/activate

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest test/ -v

# Run a single test
pytest test/test_pipeline.py::TestPreprocessing::test_bio_labels_exist -v

# Train NER model (from backend/pipeline/)
python training.py --train ../data/processed/train.json --val ../data/processed/val.json --epochs 10

# Resume training from checkpoint
python training.py --train ../data/processed/train.json --val ../data/processed/val.json --resume models/latest
```

### Frontend (React + TypeScript)

```bash
# From frontend/ directory
npm run dev          # Start development server (port 5173)
npm run build        # Production build
npm run typecheck    # Type checking with react-router typegen + tsc
npm run lint         # ESLint
```

### Docker

```bash
# Start all services (PostgreSQL, backend, frontend)
docker-compose up -d

# Start only PostgreSQL for local development
docker-compose up -d db
docker-compose up --build -d 
```

## Architecture

### Backend Structure (`backend/`)

- **`main.py`** - FastAPI app entry point with lifespan manager that initializes NER model and training service
- **`config.py`** - Pydantic settings loading from `.env`, auto-detects compute device (MPS/CUDA/CPU)
- **`services/`**
  - `ner.py` - NERService class for model loading and entity extraction with 5W1H structuring
  - `training.py` - TrainingService for managing async training jobs
  - `evaluation.py` - Model evaluation metrics and 5W1H category analysis
- **`pipeline/`** - ML components
  - `config.py` - Entity label definitions (26 types in BIO format = 53 labels), ModelConfig dataclass
  - `training.py` - ViolentEventNER trainer class with FocalLoss, checkpoint saving, resume support
  - `loss.py` - FocalLoss and ClassWeightedCrossEntropy for handling class imbalance
  - `segmentation.py` - Multi-event text segmentation
  - `kb.py` - Knowledge base (armed groups, locations, weapons)
  - `validator.py` - Entity validation against knowledge base
- **`api/`** - FastAPI routers organized by domain (training, inference, events, analytics, kb, auth, system)
- **`database/`** - SQLAlchemy models and repository pattern

### Entity Schema (5W1H)

26 entity types across 6 categories:
- **WHO** (5): PERPETRATOR, VICTIM, TARGET, ORGANIZATION, GOVERNMENT
- **WHAT** (4): EVENT_TYPE, ACTION, WEAPON, VIOLENCE_TYPE
- **WHEN** (4): DATE, TIME, DURATION, FREQUENCY
- **WHERE** (7): COUNTRY, REGION, CITY, DISTRICT, FACILITY, GEOGRAPHIC, COORDINATES
- **HOW** (4): CASUALTIES, INJURED, DISPLACEMENT, DAMAGE
- **WHY** (2): MOTIVE, TRIGGER

### Frontend Structure (`frontend/src/`)

- **`routes/`** - React Router 7 route components (training, inference, events, analytics, kb)
- **`components/`** - Shared UI components (shadcn/ui based)
- **`services/`** - API client functions
- **`context/`** - React context providers

## Key Patterns

- **Device Auto-Detection**: Backend auto-detects MPS (Apple Silicon), CUDA, or CPU
- **Checkpoint Structure**: Models saved as `models/{model}_{timestamp}/epoch_XX/` with `best/` folder for best checkpoint
- **WebSocket Training Progress**: Real-time training updates via `/ws/training/{session_id}`
- **Knowledge Base Validation**: Entities validated against curated KB of African armed groups, countries, and conflict cities
- **FocalLoss**: Handles severe class imbalance (O tokens >> entity tokens)

## Database

PostgreSQL with SQLAlchemy ORM. Connection via `DATABASE_URL` env var. Database initialization scripts in `backend/database/init/`.
