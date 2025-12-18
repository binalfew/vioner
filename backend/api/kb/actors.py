"""Actors Router - Knowledge base actor management."""

from fastapi import APIRouter, HTTPException, Query, Request
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy import func, desc

router = APIRouter()


# Response Models
class ActorResponse(BaseModel):
    actor_id: int
    actor_name: str
    actor_type: Optional[str]
    actor_category: Optional[str]
    country: Optional[str]
    region: Optional[str]
    aliases: Optional[List[str]]
    description: Optional[str]
    event_count: int = 0
    total_deaths: int = 0
    total_injuries: int = 0

    model_config = {"from_attributes": True}


class ActorCreate(BaseModel):
    actor_name: str
    actor_type: Optional[str] = None
    actor_category: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    aliases: Optional[List[str]] = None
    description: Optional[str] = None


class ActorUpdate(BaseModel):
    actor_name: Optional[str] = None
    actor_type: Optional[str] = None
    actor_category: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    aliases: Optional[List[str]] = None
    description: Optional[str] = None


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
    from database.models import ActorDB, EventDB
    return get_db_context, ActorDB, EventDB


@router.get("", response_model=List[ActorResponse])
async def get_actors(
    request: Request,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    country: Optional[str] = None
):
    """Get all actors with event statistics."""
    get_db_context, ActorDB, EventDB = get_db_and_models(request)
    from sqlalchemy import or_

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        query = db.query(
            ActorDB,
            func.count(EventDB.event_id).label('event_count'),
            func.coalesce(func.sum(EventDB.deaths), 0).label('total_deaths'),
            func.coalesce(func.sum(EventDB.injuries), 0).label('total_injuries')
        ).outerjoin(EventDB, ActorDB.actor_id == EventDB.actor_id)\
         .group_by(ActorDB.actor_id)

        if search:
            query = query.filter(
                or_(
                    ActorDB.actor_name.ilike(f"%{search}%"),
                    ActorDB.aliases.any(search)
                )
            )

        if country:
            query = query.filter(ActorDB.country.ilike(f"%{country}%"))

        results = query.order_by(desc('event_count')).offset(offset).limit(limit).all()

        return [
            ActorResponse(
                actor_id=r.ActorDB.actor_id,
                actor_name=r.ActorDB.actor_name,
                actor_type=r.ActorDB.actor_type,
                actor_category=r.ActorDB.actor_category,
                country=r.ActorDB.country,
                region=r.ActorDB.region,
                aliases=r.ActorDB.aliases,
                description=r.ActorDB.description,
                event_count=r.event_count,
                total_deaths=int(r.total_deaths),
                total_injuries=int(r.total_injuries)
            )
            for r in results
        ]


@router.get("/{actor_id}", response_model=ActorResponse)
async def get_actor(actor_id: int, request: Request):
    """Get a specific actor with statistics."""
    get_db_context, ActorDB, EventDB = get_db_and_models(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        result = db.query(
            ActorDB,
            func.count(EventDB.event_id).label('event_count'),
            func.coalesce(func.sum(EventDB.deaths), 0).label('total_deaths'),
            func.coalesce(func.sum(EventDB.injuries), 0).label('total_injuries')
        ).outerjoin(EventDB, ActorDB.actor_id == EventDB.actor_id)\
         .filter(ActorDB.actor_id == actor_id)\
         .group_by(ActorDB.actor_id)\
         .first()

        if not result:
            raise HTTPException(status_code=404, detail="Actor not found")

        return ActorResponse(
            actor_id=result.ActorDB.actor_id,
            actor_name=result.ActorDB.actor_name,
            actor_type=result.ActorDB.actor_type,
            actor_category=result.ActorDB.actor_category,
            country=result.ActorDB.country,
            region=result.ActorDB.region,
            aliases=result.ActorDB.aliases,
            description=result.ActorDB.description,
            event_count=result.event_count,
            total_deaths=int(result.total_deaths),
            total_injuries=int(result.total_injuries)
        )


@router.get("/{actor_id}/events", response_model=List[EventSearchResult])
async def get_actor_events(
    actor_id: int,
    request: Request,
    limit: int = Query(50, ge=1, le=200)
):
    """Get all events for a specific actor."""
    get_db_context, ActorDB, EventDB = get_db_and_models(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        events = db.query(EventDB).filter(
            EventDB.actor_id == actor_id
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
async def create_actor(actor: ActorCreate, request: Request):
    """Create a new actor in the knowledge base."""
    get_db_context, ActorDB, _ = get_db_and_models(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        # Check if actor already exists
        existing = db.query(ActorDB).filter(
            func.lower(ActorDB.actor_name) == actor.actor_name.lower()
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Actor '{actor.actor_name}' already exists")

        new_actor = ActorDB(
            actor_name=actor.actor_name,
            actor_type=actor.actor_type,
            actor_category=actor.actor_category,
            country=actor.country,
            region=actor.region,
            aliases=actor.aliases,
            description=actor.description
        )
        db.add(new_actor)
        db.commit()
        db.refresh(new_actor)

        return {
            "message": "Actor created",
            "actor_id": new_actor.actor_id,
            "actor_name": new_actor.actor_name
        }


@router.put("/{actor_id}")
async def update_actor(actor_id: int, update: ActorUpdate, request: Request):
    """Update an actor's information."""
    get_db_context, ActorDB, _ = get_db_and_models(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        actor = db.query(ActorDB).filter(ActorDB.actor_id == actor_id).first()
        if not actor:
            raise HTTPException(status_code=404, detail=f"Actor {actor_id} not found")

        for field, value in update.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(actor, field, value)

        db.commit()
        db.refresh(actor)

        return {"message": "Actor updated", "actor_id": actor_id}


@router.delete("/{actor_id}")
async def delete_actor(actor_id: int, request: Request):
    """Delete an actor (only if no events reference it)."""
    get_db_context, ActorDB, EventDB = get_db_and_models(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        actor = db.query(ActorDB).filter(ActorDB.actor_id == actor_id).first()
        if not actor:
            raise HTTPException(status_code=404, detail=f"Actor {actor_id} not found")

        # Check if events reference this actor
        event_count = db.query(func.count(EventDB.event_id)).filter(
            EventDB.actor_id == actor_id
        ).scalar()

        if event_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete actor: {event_count} events reference this actor"
            )

        db.delete(actor)
        db.commit()

        return {"message": "Actor deleted", "actor_id": actor_id}


@router.post("/merge")
async def merge_actors(
    request: Request,
    source_id: int = Query(..., description="Actor ID to merge FROM (will be deleted)"),
    target_id: int = Query(..., description="Actor ID to merge INTO (will be kept)")
):
    """Merge two actors: move all events from source to target, then delete source."""
    get_db_context, ActorDB, EventDB = get_db_and_models(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        source = db.query(ActorDB).filter(ActorDB.actor_id == source_id).first()
        target = db.query(ActorDB).filter(ActorDB.actor_id == target_id).first()

        if not source:
            raise HTTPException(status_code=404, detail=f"Source actor {source_id} not found")
        if not target:
            raise HTTPException(status_code=404, detail=f"Target actor {target_id} not found")

        # Update all events to point to target
        updated = db.query(EventDB).filter(EventDB.actor_id == source_id).update(
            {EventDB.actor_id: target_id, EventDB.actor_normalized: target.actor_name}
        )

        # Merge aliases
        source_aliases = source.aliases or []
        target_aliases = target.aliases or []
        merged_aliases = list(set(target_aliases + source_aliases + [source.actor_name]))
        target.aliases = merged_aliases

        # Delete source
        db.delete(source)
        db.commit()

        return {
            "message": f"Merged actor '{source.actor_name}' into '{target.actor_name}'",
            "events_updated": updated
        }
