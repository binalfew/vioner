"""Taxonomies Router - Knowledge base taxonomy management."""

from fastapi import APIRouter, HTTPException, Query, Request
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy import func, desc

router = APIRouter()


# Response Models
class TaxonomyResponse(BaseModel):
    taxonomy_id: int
    level_1: str
    level_2: Optional[str]
    level_3: Optional[str]
    description: Optional[str]
    event_count: int = 0

    model_config = {"from_attributes": True}


class TaxonomyCreate(BaseModel):
    level_1: str
    level_2: Optional[str] = None
    level_3: Optional[str] = None
    description: Optional[str] = None


class TaxonomyUpdate(BaseModel):
    level_1: Optional[str] = None
    level_2: Optional[str] = None
    level_3: Optional[str] = None
    description: Optional[str] = None


def get_db_and_models(request: Request):
    """Get database context and models."""
    from database.connection import get_db_context
    from database.models import TaxonomyDB, EventDB
    return get_db_context, TaxonomyDB, EventDB


@router.get("", response_model=List[TaxonomyResponse])
async def get_taxonomies(request: Request):
    """Get taxonomy hierarchy with event counts."""
    get_db_context, TaxonomyDB, EventDB = get_db_and_models(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        results = db.query(
            TaxonomyDB,
            func.count(EventDB.event_id).label('event_count')
        ).outerjoin(EventDB, TaxonomyDB.taxonomy_id == EventDB.taxonomy_id)\
         .group_by(TaxonomyDB.taxonomy_id)\
         .order_by(TaxonomyDB.level_1, TaxonomyDB.level_2, TaxonomyDB.level_3)\
         .all()

        return [
            TaxonomyResponse(
                taxonomy_id=r.TaxonomyDB.taxonomy_id,
                level_1=r.TaxonomyDB.level_1,
                level_2=r.TaxonomyDB.level_2,
                level_3=r.TaxonomyDB.level_3,
                description=r.TaxonomyDB.description,
                event_count=r.event_count
            )
            for r in results
        ]


@router.get("/hierarchy")
async def get_taxonomy_hierarchy(request: Request):
    """Get taxonomy as nested hierarchy."""
    get_db_context, TaxonomyDB, _ = get_db_and_models(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        taxonomies = db.query(TaxonomyDB).all()

        # Build hierarchy
        hierarchy = {}
        for t in taxonomies:
            if t.level_1 not in hierarchy:
                hierarchy[t.level_1] = {"children": {}, "count": 0}

            if t.level_2:
                if t.level_2 not in hierarchy[t.level_1]["children"]:
                    hierarchy[t.level_1]["children"][t.level_2] = {"children": [], "count": 0}

                if t.level_3:
                    hierarchy[t.level_1]["children"][t.level_2]["children"].append(t.level_3)

        return hierarchy


@router.get("/stats/summary")
async def get_taxonomy_stats(request: Request):
    """Get summary statistics for taxonomy page header."""
    get_db_context, TaxonomyDB, EventDB = get_db_and_models(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        # Stats by L1 category
        l1_stats = db.query(
            TaxonomyDB.level_1,
            func.count(TaxonomyDB.taxonomy_id).label('taxonomy_count')
        ).group_by(TaxonomyDB.level_1).all()

        # Event counts by L1
        event_stats = db.query(
            EventDB.taxonomy_l1,
            func.count(EventDB.event_id).label('event_count'),
            func.coalesce(func.sum(EventDB.deaths), 0).label('deaths'),
            func.coalesce(func.sum(EventDB.injuries), 0).label('injuries')
        ).group_by(EventDB.taxonomy_l1).all()

        # Build combined stats
        event_map = {
            e.taxonomy_l1: {
                "events": e.event_count,
                "deaths": int(e.deaths),
                "injuries": int(e.injuries)
            }
            for e in event_stats
        }

        categories = []
        for stat in l1_stats:
            evt = event_map.get(stat.level_1, {"events": 0, "deaths": 0, "injuries": 0})
            categories.append({
                "level_1": stat.level_1,
                "taxonomy_count": stat.taxonomy_count,
                "event_count": evt["events"],
                "deaths": evt["deaths"],
                "injuries": evt["injuries"]
            })

        total_taxonomies = sum(c["taxonomy_count"] for c in categories)
        total_events = sum(c["event_count"] for c in categories)

        return {
            "total_taxonomies": total_taxonomies,
            "total_events": total_events,
            "categories": categories
        }


@router.get("/{taxonomy_id}")
async def get_taxonomy(taxonomy_id: int, request: Request):
    """Get a single taxonomy by ID with detailed stats."""
    get_db_context, TaxonomyDB, EventDB = get_db_and_models(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        taxonomy = db.query(TaxonomyDB).filter(TaxonomyDB.taxonomy_id == taxonomy_id).first()
        if not taxonomy:
            raise HTTPException(status_code=404, detail=f"Taxonomy {taxonomy_id} not found")

        # Get event stats for this taxonomy
        stats = db.query(
            func.count(EventDB.event_id).label('event_count'),
            func.coalesce(func.sum(EventDB.deaths), 0).label('total_deaths'),
            func.coalesce(func.sum(EventDB.injuries), 0).label('total_injuries')
        ).filter(EventDB.taxonomy_id == taxonomy_id).first()

        # Get sample events
        sample_events = db.query(EventDB).filter(
            EventDB.taxonomy_id == taxonomy_id
        ).order_by(EventDB.created_at.desc()).limit(5).all()

        return {
            "taxonomy_id": taxonomy.taxonomy_id,
            "level_1": taxonomy.level_1,
            "level_2": taxonomy.level_2,
            "level_3": taxonomy.level_3,
            "description": taxonomy.description,
            "event_count": stats.event_count if stats else 0,
            "total_deaths": int(stats.total_deaths) if stats else 0,
            "total_injuries": int(stats.total_injuries) if stats else 0,
            "sample_events": [
                {
                    "event_id": e.event_id,
                    "actor": e.actor_normalized,
                    "date": str(e.date_normalized) if e.date_normalized else None,
                    "country": e.location_country,
                    "description": (e.event_description or "")[:150] + "..." if e.event_description and len(e.event_description) > 150 else e.event_description,
                    "deaths": e.deaths
                }
                for e in sample_events
            ]
        }


@router.post("")
async def create_taxonomy(taxonomy: TaxonomyCreate, request: Request):
    """Create a new taxonomy classification."""
    get_db_context, TaxonomyDB, _ = get_db_and_models(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        # Check for duplicate
        existing = db.query(TaxonomyDB).filter(
            TaxonomyDB.level_1 == taxonomy.level_1,
            TaxonomyDB.level_2 == taxonomy.level_2,
            TaxonomyDB.level_3 == taxonomy.level_3
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Taxonomy with this classification already exists")

        new_taxonomy = TaxonomyDB(
            level_1=taxonomy.level_1,
            level_2=taxonomy.level_2,
            level_3=taxonomy.level_3,
            description=taxonomy.description
        )
        db.add(new_taxonomy)
        db.commit()
        db.refresh(new_taxonomy)

        return {
            "message": "Taxonomy created successfully",
            "taxonomy_id": new_taxonomy.taxonomy_id,
            "level_1": new_taxonomy.level_1,
            "level_2": new_taxonomy.level_2,
            "level_3": new_taxonomy.level_3
        }


@router.put("/{taxonomy_id}")
async def update_taxonomy(taxonomy_id: int, update: TaxonomyUpdate, request: Request):
    """Update an existing taxonomy."""
    get_db_context, TaxonomyDB, EventDB = get_db_and_models(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        taxonomy = db.query(TaxonomyDB).filter(TaxonomyDB.taxonomy_id == taxonomy_id).first()
        if not taxonomy:
            raise HTTPException(status_code=404, detail=f"Taxonomy {taxonomy_id} not found")

        # Update fields if provided
        if update.level_1 is not None:
            # Also update events that reference this taxonomy
            db.query(EventDB).filter(EventDB.taxonomy_id == taxonomy_id).update(
                {"taxonomy_l1": update.level_1}
            )
            taxonomy.level_1 = update.level_1

        if update.level_2 is not None:
            db.query(EventDB).filter(EventDB.taxonomy_id == taxonomy_id).update(
                {"taxonomy_l2": update.level_2}
            )
            taxonomy.level_2 = update.level_2

        if update.level_3 is not None:
            db.query(EventDB).filter(EventDB.taxonomy_id == taxonomy_id).update(
                {"taxonomy_l3": update.level_3}
            )
            taxonomy.level_3 = update.level_3

        if update.description is not None:
            taxonomy.description = update.description

        db.commit()

        return {
            "message": "Taxonomy updated successfully",
            "taxonomy_id": taxonomy_id
        }


@router.delete("/{taxonomy_id}")
async def delete_taxonomy(
    taxonomy_id: int,
    request: Request,
    force: bool = Query(False, description="Force delete and reassign events to 'Unknown'")
):
    """Delete a taxonomy. Set force=true to reassign events to 'Unknown'."""
    get_db_context, TaxonomyDB, EventDB = get_db_and_models(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        taxonomy = db.query(TaxonomyDB).filter(TaxonomyDB.taxonomy_id == taxonomy_id).first()
        if not taxonomy:
            raise HTTPException(status_code=404, detail=f"Taxonomy {taxonomy_id} not found")

        # Check for events using this taxonomy
        event_count = db.query(func.count(EventDB.event_id)).filter(
            EventDB.taxonomy_id == taxonomy_id
        ).scalar() or 0

        if event_count > 0 and not force:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete taxonomy with {event_count} linked events. Use force=true to reassign events."
            )

        if event_count > 0 and force:
            # Clear taxonomy references from events
            db.query(EventDB).filter(EventDB.taxonomy_id == taxonomy_id).update({
                "taxonomy_id": None,
                "taxonomy_l1": "Unknown",
                "taxonomy_l2": None,
                "taxonomy_l3": None
            })

        db.delete(taxonomy)
        db.commit()

        return {
            "message": "Taxonomy deleted successfully",
            "taxonomy_id": taxonomy_id,
            "events_affected": event_count
        }
