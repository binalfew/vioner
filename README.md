# VioNER

**Vio**lent Event **N**amed **E**ntity **R**ecognition - A comprehensive system for extracting structured information (5W1H) from news articles about violent events in Africa. This system combines ML-based Named Entity Recognition with a knowledge base and analytics dashboard.

## Features

- **ML Training**: Fine-tune BERT models for custom NER with real-time progress monitoring
- **Entity Extraction**: Extract WHO, WHAT, WHEN, WHERE, HOW from text
- **Event Management**: Store, query, and analyze extracted events
- **Knowledge Base**: Manage actors, locations, and violence taxonomies
- **Analytics Dashboard**: Visualize trends, statistics, and patterns
- **REST API**: Full-featured API for integration

## Tech Stack

### Backend
- **FastAPI** - High-performance async web framework
- **PostgreSQL** - Relational database for events and knowledge base
- **PyTorch + Transformers** - BERT-based NER model
- **SQLAlchemy** - Database ORM
- **WebSocket** - Real-time training progress

### Frontend
- **React 19** + **TypeScript** - Type-safe UI development
- **React Router 7** - Client-side routing
- **TailwindCSS** - Utility-first CSS framework
- **shadcn/ui** - High-quality UI components
- **Recharts** - Data visualization

### Infrastructure
- **Docker Compose** - Container orchestration
- **nginx** - Frontend static file serving

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.10+ (for local backend development)

### Using Docker (Recommended)

```bash
# Clone and navigate to the project
cd named-entity-recognition

# Edit backend/.env if needed (default values work for development)

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Local Development

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Start PostgreSQL (via Docker or local installation)
docker-compose up -d postgres

# Run backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
named-entity-recognition/
├── backend/                 # FastAPI application
│   ├── api/                 # API routers
│   │   ├── training/        # Training management
│   │   ├── inference/       # Entity extraction
│   │   ├── events/          # Event CRUD
│   │   ├── analytics/       # Statistics & trends
│   │   └── kb/              # Knowledge base management
│   ├── database/            # Database layer + init scripts
│   ├── services/            # Business logic
│   ├── pipeline/            # ML preprocessing & training
│   ├── models/              # Trained model checkpoints
│   ├── console/             # Training logs
│   └── websocket/           # Real-time updates
│
├── frontend/                # React application
│   └── src/
│       ├── routes/          # Route components
│       ├── components/      # Reusable components
│       ├── services/        # API clients
│       └── types/           # TypeScript types
│
└── data/                    # Training data
```

## API Endpoints

### Training
- `GET /api/training/status` - Training progress
- `POST /api/training/start` - Start new training
- `POST /api/training/resume` - Resume from checkpoint
- `POST /api/training/stop` - Stop training

### Inference
- `POST /api/inference/extract` - Extract entities from text
- `POST /api/inference/extract/batch` - Batch extraction

### Events
- `GET /api/events` - List events with filters
- `POST /api/events` - Create event
- `GET /api/events/{id}` - Get event details
- `PUT /api/events/{id}` - Update event
- `DELETE /api/events/{id}` - Delete event

### Analytics
- `GET /api/analytics/stats` - Overall statistics
- `GET /api/analytics/trends/monthly` - Monthly trends
- `GET /api/analytics/by-country` - Stats by country
- `GET /api/analytics/by-actor` - Stats by actor

### Knowledge Base
- `/api/kb/actors/*` - Actor management
- `/api/kb/locations/*` - Location management
- `/api/kb/taxonomies/*` - Taxonomy management

## Entity Types (5W1H)

| Category | Entity Types |
|----------|--------------|
| **WHO** | PERPETRATOR, VICTIM, ACTOR, GROUP, ORGANIZATION |
| **WHAT** | EVENT_TYPE, ACTION, WEAPON, VIOLENCE_TYPE |
| **WHEN** | DATE, TIME, DURATION, FREQUENCY |
| **WHERE** | LOCATION, COUNTRY, CITY, REGION, ADDRESS |
| **HOW** | METHOD, MANNER, INSTRUMENT, CASUALTIES |

## License

This project is part of a Master's thesis at Addis Ababa University.

## Author

Binalfew Kassa Mekonnen
