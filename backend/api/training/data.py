"""Training Data Upload Router - CSV validation and processing for NER training."""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime
import tempfile
import uuid
import json
import logging
import time

from pipeline.preprocessing import AnnotationPreprocessor

router = APIRouter(prefix="/data", tags=["training-data"])
logger = logging.getLogger(__name__)

# Temporary storage for validated files (in-memory cache with TTL)
_validation_cache: Dict[str, dict] = {}
_CACHE_TTL_SECONDS = 1800  # 30 minutes

# Processing progress tracking
_processing_progress: Dict[str, dict] = {}

# Required and optional columns for CSV
REQUIRED_COLUMNS = ['Event_ID', 'Event_Description']

# Entity columns (verified text spans)
OPTIONAL_COLUMNS = [
    'PERPETRATOR', 'VICTIM', 'EVENT_TYPE', 'WEAPON',
    'DATE', 'COUNTRY', 'CITY', 'CASUALTIES', 'Quality_Score'
]


# ============================================================
# Pydantic Models
# ============================================================

class ValidationError(BaseModel):
    """Validation error detail."""
    type: str
    column: Optional[str] = None
    row: Optional[int] = None
    message: str


class SampleEntity(BaseModel):
    """Entity extracted from sample event."""
    text: str
    type: str
    start: int
    end: int


class SampleEvent(BaseModel):
    """Sample event with extracted entities."""
    event_id: str
    text: str
    entities: List[SampleEntity]


class ValidationResponse(BaseModel):
    """Response from CSV validation endpoint."""
    valid: bool
    filename: str
    file_size_kb: float
    total_rows: Optional[int] = None
    columns_found: List[str] = []
    columns_missing: List[str] = []
    columns_extra: List[str] = []
    sample_events: List[SampleEvent] = []
    entity_statistics: Dict[str, int] = {}
    validation_token: Optional[str] = None
    errors: List[ValidationError] = []


class ProcessRequest(BaseModel):
    """Request to process validated CSV."""
    validation_token: str
    train_split: float = Field(default=0.8, ge=0.5, le=0.95)


class ProcessResponse(BaseModel):
    """Response from CSV processing endpoint."""
    success: bool
    message: str
    train_file: Optional[str] = None
    val_file: Optional[str] = None
    statistics: Optional[Dict] = None


class DataStatusResponse(BaseModel):
    """Current training data status."""
    has_data: bool
    train_file: Optional[Dict] = None
    val_file: Optional[Dict] = None
    statistics: Optional[Dict] = None


class ProcessingProgressResponse(BaseModel):
    """Processing progress response."""
    is_processing: bool
    current_row: int = 0
    total_rows: int = 0
    percent_complete: float = 0.0
    current_event_id: Optional[str] = None
    phase: str = "idle"  # idle, processing, saving, complete
    message: str = ""


# ============================================================
# Helper Functions
# ============================================================

def get_data_dir() -> Path:
    """Get data directory path."""
    if Path('/app/data').exists():
        return Path('/app/data')
    # Local development: backend -> named-entity-recognition -> data
    return Path(__file__).parent.parent.parent.parent / 'data'


def cleanup_expired_cache():
    """Remove expired cache entries."""
    now = datetime.utcnow()
    expired = [
        token for token, data in _validation_cache.items()
        if (now - datetime.fromisoformat(data['created'])).total_seconds() > _CACHE_TTL_SECONDS
    ]
    for token in expired:
        temp_path = Path(_validation_cache[token]['temp_path'])
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass
        del _validation_cache[token]


def get_file_info(path: Path) -> Dict:
    """Get file information."""
    if not path.exists():
        return {'exists': False}

    stat = path.stat()
    events = 0
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            events = len(data) if isinstance(data, list) else 0
    except Exception:
        pass

    return {
        'path': str(path),
        'exists': True,
        'events': events,
        'size_mb': round(stat.st_size / (1024 * 1024), 2),
        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
    }


# ============================================================
# Endpoints
# ============================================================

@router.post("/validate", response_model=ValidationResponse)
async def validate_csv(file: UploadFile = File(...)):
    """
    Validate uploaded CSV and return preview with sample entities.
    """
    import pandas as pd

    cleanup_expired_cache()

    if not file.filename or not file.filename.endswith('.csv'):
        raise HTTPException(400, detail="File must be a CSV file (.csv extension)")

    content = await file.read()
    file_size_kb = len(content) / 1024

    if file_size_kb > 500 * 1024:
        raise HTTPException(400, detail="File too large. Maximum size is 500MB.")

    temp_dir = Path(tempfile.gettempdir())
    temp_path = temp_dir / f"upload_{uuid.uuid4().hex}.csv"

    try:
        with open(temp_path, 'wb') as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(500, detail=f"Failed to save uploaded file: {str(e)}")

    try:
        try:
            df = pd.read_csv(temp_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(temp_path, encoding='latin-1')

        columns_found = list(df.columns)
        columns_missing = [c for c in REQUIRED_COLUMNS if c not in columns_found]
        all_known_columns = REQUIRED_COLUMNS + OPTIONAL_COLUMNS
        columns_extra = [c for c in columns_found if c not in all_known_columns]

        if columns_missing:
            temp_path.unlink()
            return ValidationResponse(
                valid=False,
                filename=file.filename,
                file_size_kb=round(file_size_kb, 2),
                columns_found=columns_found,
                columns_missing=columns_missing,
                errors=[
                    ValidationError(
                        type="missing_column",
                        column=col,
                        message=f"Required column '{col}' not found in CSV"
                    ) for col in columns_missing
                ]
            )

        preprocessor = AnnotationPreprocessor(str(temp_path), str(temp_dir))

        # Extract sample events (first 3)
        sample_events = []
        for idx in range(min(3, len(df))):
            row = df.iloc[idx]
            text = str(row.get('Event_Description', ''))
            if not text or text == 'nan':
                continue

            entities = preprocessor.extract_entities_from_row(row)
            sample_events.append(SampleEvent(
                event_id=str(row.get('Event_ID', f'row_{idx}')),
                text=text[:500] + ('...' if len(text) > 500 else ''),
                entities=[
                    SampleEntity(
                        text=e['text'],
                        type=e['type'],
                        start=e['start'],
                        end=e['end']
                    ) for e in entities[:15]
                ]
            ))

        # Calculate entity statistics (sample up to 500 rows)
        sample_size = min(500, len(df))
        entity_stats: Dict[str, int] = {}

        for idx in range(sample_size):
            row = df.iloc[idx]
            text = str(row.get('Event_Description', ''))
            if not text or text == 'nan':
                continue

            entities = preprocessor.extract_entities_from_row(row)
            for e in entities:
                entity_stats[e['type']] = entity_stats.get(e['type'], 0) + 1

        if sample_size < len(df):
            scale_factor = len(df) / sample_size
            entity_stats = {k: int(v * scale_factor) for k, v in entity_stats.items()}

        validation_token = uuid.uuid4().hex
        _validation_cache[validation_token] = {
            'temp_path': str(temp_path),
            'filename': file.filename,
            'created': datetime.utcnow().isoformat(),
            'total_rows': len(df)
        }

        logger.info(f"CSV validated: {file.filename}, {len(df)} rows, token: {validation_token[:8]}...")

        return ValidationResponse(
            valid=True,
            filename=file.filename,
            file_size_kb=round(file_size_kb, 2),
            total_rows=len(df),
            columns_found=columns_found,
            columns_missing=[],
            columns_extra=columns_extra,
            sample_events=sample_events,
            entity_statistics=entity_stats,
            validation_token=validation_token
        )

    except Exception as e:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass
        logger.error(f"CSV validation failed: {e}")
        raise HTTPException(400, detail=f"Failed to parse CSV: {str(e)}")


@router.get("/progress", response_model=ProcessingProgressResponse)
async def get_processing_progress():
    """Get current processing progress."""
    if not _processing_progress:
        return ProcessingProgressResponse(
            is_processing=False,
            phase="idle",
            message="No processing in progress"
        )
    return ProcessingProgressResponse(**_processing_progress)


def _do_process_csv(temp_path: Path, cache_entry: dict, train_split: float) -> dict:
    """Synchronous CSV processing function to run in thread executor."""
    import pandas as pd
    import random

    global _processing_progress

    output_dir = get_data_dir() / 'processed'
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Processing CSV: {cache_entry['filename']} -> {output_dir}")

    total_rows = cache_entry.get('total_rows', 0)
    _processing_progress.update({
        'is_processing': True,
        'current_row': 0,
        'total_rows': total_rows,
        'percent_complete': 0.0,
        'current_event_id': None,
        'phase': 'processing',
        'message': f'Processing 0/{total_rows:,} events...'
    })

    start_time = time.time()

    try:
        df = pd.read_csv(temp_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(temp_path, encoding='latin-1')

    preprocessor = AnnotationPreprocessor(str(temp_path), str(output_dir))

    processed_events = []
    for row_num, (idx, row) in enumerate(df.iterrows(), start=1):
        event_id = str(row.get('Event_ID', f'row_{idx}'))

        if row_num % 100 == 0 or row_num == len(df):
            percent = (row_num / len(df)) * 100
            _processing_progress.update({
                'current_row': row_num,
                'percent_complete': round(percent, 1),
                'current_event_id': event_id,
                'message': f'Processing {row_num:,}/{len(df):,} events ({percent:.1f}%)'
            })

        event_data = preprocessor.process_single_event(row)
        if event_data:
            processed_events.append(event_data)

    _processing_progress.update({
        'phase': 'saving',
        'message': 'Splitting into train/val and saving...'
    })

    random.seed(42)
    random.shuffle(processed_events)

    split_idx = int(len(processed_events) * train_split)
    train_data = processed_events[:split_idx]
    val_data = processed_events[split_idx:]

    preprocessor.save_processed_data(train_data, val_data)
    processing_time_ms = int((time.time() - start_time) * 1000)

    stats_file = output_dir / 'statistics.json'
    statistics = {}
    if stats_file.exists():
        with open(stats_file, 'r', encoding='utf-8') as f:
            statistics = json.load(f)
    statistics['processing_time_ms'] = processing_time_ms

    _processing_progress.update({
        'is_processing': False,
        'phase': 'complete',
        'percent_complete': 100.0,
        'message': f'Complete! Processed {len(processed_events):,} events in {processing_time_ms/1000:.1f}s'
    })

    logger.info(
        f"CSV processed successfully: {statistics.get('train_events', 0)} train, "
        f"{statistics.get('val_events', 0)} val events in {processing_time_ms}ms"
    )

    return {
        'success': True,
        'output_dir': str(output_dir),
        'statistics': statistics
    }


@router.post("/process", response_model=ProcessResponse)
async def process_csv(request: ProcessRequest):
    """Process validated CSV into train.json and val.json."""
    import asyncio

    global _processing_progress

    cleanup_expired_cache()

    cache_entry = _validation_cache.get(request.validation_token)
    if not cache_entry:
        raise HTTPException(
            400,
            detail="Invalid or expired validation token. Please re-upload the file."
        )

    temp_path = Path(cache_entry['temp_path'])
    if not temp_path.exists():
        del _validation_cache[request.validation_token]
        raise HTTPException(400, detail="Uploaded file not found. Please re-upload.")

    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            _do_process_csv,
            temp_path,
            cache_entry,
            request.train_split
        )

        try:
            temp_path.unlink()
        except Exception:
            pass
        del _validation_cache[request.validation_token]

        output_dir = Path(result['output_dir'])
        return ProcessResponse(
            success=True,
            message="Training data processed successfully",
            train_file=str(output_dir / 'train.json'),
            val_file=str(output_dir / 'val.json'),
            statistics=result['statistics']
        )

    except Exception as e:
        _processing_progress.update({
            'is_processing': False,
            'phase': 'error',
            'message': f'Error: {str(e)}'
        })
        logger.error(f"CSV processing failed: {e}")
        raise HTTPException(500, detail=f"Processing failed: {str(e)}")


@router.get("/status", response_model=DataStatusResponse)
async def get_data_status():
    """Get current training data status."""
    data_dir = get_data_dir() / 'processed'

    train_file = data_dir / 'train.json'
    val_file = data_dir / 'val.json'
    stats_file = data_dir / 'statistics.json'

    train_info = get_file_info(train_file)
    val_info = get_file_info(val_file)

    statistics = None
    if stats_file.exists():
        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                statistics = json.load(f)
        except Exception:
            pass

    return DataStatusResponse(
        has_data=train_info.get('exists', False) and val_info.get('exists', False),
        train_file=train_info if train_info.get('exists') else None,
        val_file=val_info if val_info.get('exists') else None,
        statistics=statistics
    )
