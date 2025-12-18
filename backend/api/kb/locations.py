"""Locations Router - Knowledge base location management."""

from fastapi import APIRouter, HTTPException, Query, Request
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy import func, desc

router = APIRouter()


# Response Models
class LocationResponse(BaseModel):
    location_id: int
    country: str
    city: Optional[str]
    region: Optional[str]
    district: Optional[str]
    location_type: Optional[str]
    event_count: int = 0
    total_deaths: int = 0

    model_config = {"from_attributes": True}


class LocationCreate(BaseModel):
    country: str
    city: Optional[str] = None
    region: Optional[str] = None
    district: Optional[str] = None
    location_type: Optional[str] = None


class LocationUpdate(BaseModel):
    country: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    district: Optional[str] = None
    location_type: Optional[str] = None


class EventSearchResult(BaseModel):
    event_id: str
    date_normalized: Optional[str]
    location_country: str
    location_city: Optional[str]
    actor_normalized: Optional[str]
    victim_normalized: Optional[str]
    taxonomy_l1: str
    deaths: int
    injuries: int
    severity: Optional[str]
    event_description: str

    model_config = {"from_attributes": True}


def get_db_and_models(request: Request):
    """Get database context and models."""
    from database.connection import get_db_context
    from database.models import LocationDB, EventDB
    return get_db_context, LocationDB, EventDB


@router.get("", response_model=List[LocationResponse])
async def get_locations(
    request: Request,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    country: Optional[str] = None
):
    """Get all locations with event statistics."""
    get_db_context, LocationDB, EventDB = get_db_and_models(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        query = db.query(
            LocationDB,
            func.count(EventDB.event_id).label('event_count'),
            func.coalesce(func.sum(EventDB.deaths), 0).label('total_deaths')
        ).outerjoin(EventDB, LocationDB.location_id == EventDB.location_id)\
         .group_by(LocationDB.location_id)

        if country:
            query = query.filter(LocationDB.country.ilike(f"%{country}%"))

        results = query.order_by(desc('event_count')).offset(offset).limit(limit).all()

        return [
            LocationResponse(
                location_id=r.LocationDB.location_id,
                country=r.LocationDB.country,
                city=r.LocationDB.city,
                region=r.LocationDB.region,
                district=r.LocationDB.district,
                location_type=r.LocationDB.location_type,
                event_count=r.event_count,
                total_deaths=int(r.total_deaths)
            )
            for r in results
        ]


@router.get("/{location_id}", response_model=LocationResponse)
async def get_location(location_id: int, request: Request):
    """Get a specific location with statistics."""
    get_db_context, LocationDB, EventDB = get_db_and_models(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        result = db.query(
            LocationDB,
            func.count(EventDB.event_id).label('event_count'),
            func.coalesce(func.sum(EventDB.deaths), 0).label('total_deaths')
        ).outerjoin(EventDB, LocationDB.location_id == EventDB.location_id)\
         .filter(LocationDB.location_id == location_id)\
         .group_by(LocationDB.location_id)\
         .first()

        if not result:
            raise HTTPException(status_code=404, detail="Location not found")

        return LocationResponse(
            location_id=result.LocationDB.location_id,
            country=result.LocationDB.country,
            city=result.LocationDB.city,
            region=result.LocationDB.region,
            district=result.LocationDB.district,
            location_type=result.LocationDB.location_type,
            event_count=result.event_count,
            total_deaths=int(result.total_deaths)
        )


@router.get("/{location_id}/events", response_model=List[EventSearchResult])
async def get_location_events(
    location_id: int,
    request: Request,
    limit: int = Query(50, ge=1, le=200)
):
    """Get all events for a specific location."""
    get_db_context, LocationDB, EventDB = get_db_and_models(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        events = db.query(EventDB).filter(
            EventDB.location_id == location_id
        ).order_by(desc(EventDB.date_normalized)).limit(limit).all()

        return [
            EventSearchResult(
                event_id=e.event_id,
                date_normalized=str(e.date_normalized) if e.date_normalized else None,
                location_country=e.location_country,
                location_city=e.location_city,
                actor_normalized=e.actor_normalized,
                victim_normalized=e.victim_normalized,
                taxonomy_l1=e.taxonomy_l1,
                deaths=e.deaths or 0,
                injuries=e.injuries or 0,
                severity=e.severity,
                event_description=e.event_description[:200] + "..." if len(e.event_description or "") > 200 else (e.event_description or "")
            )
            for e in events
        ]


@router.post("")
async def create_location(location: LocationCreate, request: Request):
    """Create a new location in the knowledge base."""
    get_db_context, LocationDB, _ = get_db_and_models(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        # Check if location already exists
        query = db.query(LocationDB).filter(
            func.lower(LocationDB.country) == location.country.lower()
        )
        if location.city:
            query = query.filter(func.lower(LocationDB.city) == location.city.lower())

        existing = query.first()
        if existing:
            raise HTTPException(status_code=400, detail="Location already exists")

        new_location = LocationDB(
            country=location.country,
            city=location.city,
            region=location.region,
            district=location.district,
            location_type=location.location_type
        )
        db.add(new_location)
        db.commit()
        db.refresh(new_location)

        return {"message": "Location created", "location_id": new_location.location_id}


@router.put("/{location_id}")
async def update_location(location_id: int, update: LocationUpdate, request: Request):
    """Update a location's information."""
    get_db_context, LocationDB, _ = get_db_and_models(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        location = db.query(LocationDB).filter(LocationDB.location_id == location_id).first()
        if not location:
            raise HTTPException(status_code=404, detail=f"Location {location_id} not found")

        for field, value in update.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(location, field, value)

        db.commit()
        db.refresh(location)

        return {"message": "Location updated", "location_id": location_id}


@router.delete("/{location_id}")
async def delete_location(location_id: int, request: Request):
    """Delete a location (only if no events reference it)."""
    get_db_context, LocationDB, EventDB = get_db_and_models(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        location = db.query(LocationDB).filter(LocationDB.location_id == location_id).first()
        if not location:
            raise HTTPException(status_code=404, detail=f"Location {location_id} not found")

        # Check if events reference this location
        event_count = db.query(func.count(EventDB.event_id)).filter(
            EventDB.location_id == location_id
        ).scalar()

        if event_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete location: {event_count} events reference this location"
            )

        db.delete(location)
        db.commit()

        return {"message": "Location deleted", "location_id": location_id}


@router.post("/merge")
async def merge_locations(
    request: Request,
    source_id: int = Query(..., description="Location ID to merge FROM"),
    target_id: int = Query(..., description="Location ID to merge INTO")
):
    """Merge two locations: move all events from source to target."""
    get_db_context, LocationDB, EventDB = get_db_and_models(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        source = db.query(LocationDB).filter(LocationDB.location_id == source_id).first()
        target = db.query(LocationDB).filter(LocationDB.location_id == target_id).first()

        if not source:
            raise HTTPException(status_code=404, detail=f"Source location {source_id} not found")
        if not target:
            raise HTTPException(status_code=404, detail=f"Target location {target_id} not found")

        # Update all events to point to target
        updated = db.query(EventDB).filter(EventDB.location_id == source_id).update({
            EventDB.location_id: target_id,
            EventDB.location_country: target.country,
            EventDB.location_city: target.city
        })

        # Delete source
        db.delete(source)
        db.commit()

        return {
            "message": "Merged locations",
            "events_updated": updated
        }


@router.get("/countries/list")
async def get_countries(request: Request):
    """Get list of all countries with event counts."""
    get_db_context, LocationDB, EventDB = get_db_and_models(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        results = db.query(
            EventDB.location_country,
            func.count(EventDB.event_id).label('event_count')
        ).group_by(EventDB.location_country)\
         .order_by(desc('event_count'))\
         .all()

        return [
            {"country": r.location_country, "event_count": r.event_count}
            for r in results if r.location_country
        ]
