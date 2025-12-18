"""Events Router - CRUD operations for events."""

from fastapi import APIRouter, HTTPException, Query, Request
from datetime import datetime, date
from typing import Optional, List
import logging

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()


# Response Models
class EventSummary(BaseModel):
    """Summary event for list view."""
    event_id: str
    event_description: str
    actor_normalized: Optional[str]
    victim_normalized: Optional[str]
    location_country: str
    location_city: Optional[str]
    date_normalized: Optional[date]
    taxonomy_l1: str
    severity: Optional[str]
    deaths: int
    injuries: int
    flagged_for_review: bool = False
    created_at: datetime

    model_config = {"from_attributes": True, "protected_namespaces": ()}


class EventDetail(BaseModel):
    """Detailed event view."""
    event_id: str
    event_description: str

    # WHO
    actor_normalized: Optional[str]
    actor_type: Optional[str]
    actor_confidence: Optional[float]

    # WHOM
    victim_normalized: Optional[str]
    victim_type: Optional[str]
    victim_confidence: Optional[float]

    # WHERE
    location_country: str
    location_city: Optional[str]
    location_confidence: Optional[float]

    # WHEN
    date_normalized: Optional[date]
    date_original: Optional[str]
    date_confidence: Optional[float]

    # WHAT
    taxonomy_l1: str
    taxonomy_l2: Optional[str]
    taxonomy_l3: Optional[str]

    # HOW
    weapon_category: Optional[str]
    attack_method: Optional[str]
    deaths: int
    injuries: int
    severity: Optional[str]
    severity_score: Optional[int]

    # Review
    flagged_for_review: bool = False
    review_notes: Optional[str]

    # Metadata
    annotator_name: Optional[str]
    extraction_method: Optional[str]
    extraction_date: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True, "protected_namespaces": ()}


class EventsResponse(BaseModel):
    """Response for event list."""
    events: List[EventSummary]
    total: int
    limit: int
    offset: int


class EventCreateRequest(BaseModel):
    """Request model for creating an event."""
    event_description: str = Field(..., min_length=10)
    actor_normalized: Optional[str] = None
    victim_normalized: Optional[str] = None
    location_country: str
    location_city: Optional[str] = None
    date_normalized: Optional[date] = None
    taxonomy_l1: str = "Unknown"
    deaths: int = Field(default=0, ge=0)
    injuries: int = Field(default=0, ge=0)


class EventUpdateRequest(BaseModel):
    """Request model for updating an event."""
    event_description: Optional[str] = None
    actor_normalized: Optional[str] = None
    victim_normalized: Optional[str] = None
    location_country: Optional[str] = None
    location_city: Optional[str] = None
    date_normalized: Optional[date] = None
    taxonomy_l1: Optional[str] = None
    taxonomy_l2: Optional[str] = None
    taxonomy_l3: Optional[str] = None
    weapon_category: Optional[str] = None
    deaths: Optional[int] = Field(default=None, ge=0)
    injuries: Optional[int] = Field(default=None, ge=0)


def get_db_and_repo(request: Request):
    """Get database session and repository."""
    from database.connection import get_db_context
    from database.repository import EventRepository
    return get_db_context, EventRepository


@router.get("", response_model=EventsResponse)
async def get_events(
    request: Request,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    country: Optional[str] = None,
    actor: Optional[str] = None,
    severity: Optional[str] = Query(None, pattern="^(Critical|High|Medium|Low)$"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    flagged: Optional[bool] = None
):
    """Get events with filtering."""
    get_db_context, EventRepository = get_db_and_repo(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        repo = EventRepository(db)
        events = repo.get_events(
            limit=limit,
            offset=offset,
            country=country,
            actor=actor,
            severity=severity,
            start_date=start_date,
            end_date=end_date,
            flagged=flagged
        )

        return EventsResponse(
            events=[
                EventSummary(
                    event_id=e.event_id,
                    event_description=e.event_description[:200] + "..." if len(e.event_description or "") > 200 else e.event_description,
                    actor_normalized=e.actor_normalized,
                    victim_normalized=e.victim_normalized,
                    location_country=e.location_country,
                    location_city=e.location_city,
                    date_normalized=e.date_normalized,
                    taxonomy_l1=e.taxonomy_l1,
                    severity=e.severity,
                    deaths=e.deaths or 0,
                    injuries=e.injuries or 0,
                    flagged_for_review=e.flagged_for_review or False,
                    created_at=e.created_at
                )
                for e in events
            ],
            total=len(events),
            limit=limit,
            offset=offset
        )


@router.get("/{event_id}", response_model=EventDetail)
async def get_event(event_id: str, request: Request):
    """Get detailed event by ID."""
    get_db_context, EventRepository = get_db_and_repo(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        repo = EventRepository(db)
        event = repo.get_event_by_id(event_id)

        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        return EventDetail(
            event_id=event.event_id,
            event_description=event.event_description,
            actor_normalized=event.actor_normalized,
            actor_type=event.actor_type,
            actor_confidence=float(event.actor_confidence) if event.actor_confidence else None,
            victim_normalized=event.victim_normalized,
            victim_type=event.victim_type,
            victim_confidence=float(event.victim_confidence) if event.victim_confidence else None,
            location_country=event.location_country,
            location_city=event.location_city,
            location_confidence=float(event.location_confidence) if event.location_confidence else None,
            date_normalized=event.date_normalized,
            date_original=event.date_original,
            date_confidence=float(event.date_confidence) if event.date_confidence else None,
            taxonomy_l1=event.taxonomy_l1,
            taxonomy_l2=event.taxonomy_l2,
            taxonomy_l3=event.taxonomy_l3,
            weapon_category=event.weapon_category,
            attack_method=event.attack_method,
            deaths=event.deaths or 0,
            injuries=event.injuries or 0,
            severity=event.severity,
            severity_score=event.severity_score,
            flagged_for_review=event.flagged_for_review or False,
            review_notes=event.review_notes,
            annotator_name=event.annotator_name,
            extraction_method=event.extraction_method,
            extraction_date=event.extraction_date,
            notes=event.notes,
            created_at=event.created_at,
            updated_at=event.updated_at
        )


@router.post("")
async def create_event(event_data: EventCreateRequest, request: Request):
    """Create a new event."""
    get_db_context, EventRepository = get_db_and_repo(request)
    from database.models import EventDB
    import uuid

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        # Calculate severity
        total_casualties = event_data.deaths + event_data.injuries
        if total_casualties >= 50:
            severity = "Critical"
        elif total_casualties >= 10:
            severity = "High"
        elif total_casualties >= 1:
            severity = "Medium"
        else:
            severity = "Low"

        new_event = EventDB(
            event_id=str(uuid.uuid4()),
            event_description=event_data.event_description,
            actor_normalized=event_data.actor_normalized,
            victim_normalized=event_data.victim_normalized,
            location_country=event_data.location_country,
            location_city=event_data.location_city,
            date_normalized=event_data.date_normalized,
            taxonomy_l1=event_data.taxonomy_l1,
            deaths=event_data.deaths,
            injuries=event_data.injuries,
            severity=severity,
            extraction_method="manual",
            created_at=datetime.utcnow()
        )

        db.add(new_event)
        db.commit()
        db.refresh(new_event)

        return {
            "message": "Event created successfully",
            "event_id": new_event.event_id
        }


@router.put("/{event_id}")
async def update_event(event_id: str, update: EventUpdateRequest, request: Request):
    """Update an existing event."""
    get_db_context, _ = get_db_and_repo(request)
    from database.models import EventDB

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        event = db.query(EventDB).filter(EventDB.event_id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        # Update fields if provided
        for field, value in update.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(event, field, value)

        # Recalculate severity if casualties changed
        if update.deaths is not None or update.injuries is not None:
            total_casualties = (event.deaths or 0) + (event.injuries or 0)
            if total_casualties >= 50:
                event.severity = "Critical"
            elif total_casualties >= 10:
                event.severity = "High"
            elif total_casualties >= 1:
                event.severity = "Medium"
            else:
                event.severity = "Low"

        event.updated_at = datetime.utcnow()
        db.commit()

        return {
            "message": "Event updated successfully",
            "event_id": event_id
        }


@router.delete("/{event_id}")
async def delete_event(event_id: str, request: Request):
    """Delete an event."""
    get_db_context, _ = get_db_and_repo(request)
    from database.models import EventDB

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        event = db.query(EventDB).filter(EventDB.event_id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        db.delete(event)
        db.commit()

        return {"message": "Event deleted successfully", "event_id": event_id}


@router.post("/bulk-delete")
async def bulk_delete_events(event_ids: List[str], request: Request):
    """Delete multiple events at once."""
    get_db_context, _ = get_db_and_repo(request)
    from database.models import EventDB

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        deleted = db.query(EventDB).filter(
            EventDB.event_id.in_(event_ids)
        ).delete(synchronize_session=False)
        db.commit()

        return {"message": f"Deleted {deleted} events", "deleted_count": deleted}


@router.post("/{event_id}/flag")
async def flag_event(event_id: str, request: Request, notes: str = Query(None)):
    """Flag an event for review."""
    get_db_context, _ = get_db_and_repo(request)
    from database.models import EventDB

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        event = db.query(EventDB).filter(EventDB.event_id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        event.flagged_for_review = True
        if notes:
            event.review_notes = notes
        db.commit()

        return {"message": "Event flagged for review", "event_id": event_id}


@router.post("/{event_id}/unflag")
async def unflag_event(event_id: str, request: Request):
    """Remove flag from event."""
    get_db_context, _ = get_db_and_repo(request)
    from database.models import EventDB

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        event = db.query(EventDB).filter(EventDB.event_id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        event.flagged_for_review = False
        event.review_notes = None
        event.annotator_name = "Human-Reviewed"
        db.commit()

        return {"message": "Event unflagged", "event_id": event_id}
