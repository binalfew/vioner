"""Analytics Router - Statistics and trend analysis endpoints."""

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from datetime import date
from typing import Optional, List
import logging
import csv
import io

from pydantic import BaseModel
from sqlalchemy import func, desc, or_, extract

logger = logging.getLogger(__name__)

router = APIRouter()


# Response Models
class StatsResponse(BaseModel):
    """Overall statistics response."""
    total_events: int
    total_actors: int
    total_locations: int
    total_taxonomies: int
    total_deaths: int
    total_injuries: int
    countries_covered: int
    date_range: dict
    top_actors: List[dict]
    top_locations: List[dict]
    events_by_taxonomy: List[dict]
    events_by_severity: dict


class SearchResult(BaseModel):
    """Search result for events."""
    event_id: str
    date_normalized: Optional[date]
    location_country: str
    location_city: Optional[str]
    actor_normalized: Optional[str]
    victim_normalized: Optional[str]
    taxonomy_l1: str
    taxonomy_l2: Optional[str]
    deaths: int
    injuries: int
    severity: Optional[str]
    event_description: str

    model_config = {"from_attributes": True}


class SearchResponse(BaseModel):
    """Search response with pagination."""
    total: int
    page: int
    page_size: int
    total_pages: int
    results: List[SearchResult]
    filters_applied: dict


def get_db_context_and_models(request: Request):
    """Get database context and models."""
    from database.connection import get_db_context
    from database.models import EventDB, ActorDB, LocationDB, TaxonomyDB
    return get_db_context, EventDB, ActorDB, LocationDB, TaxonomyDB


@router.get("/stats", response_model=StatsResponse)
async def get_stats(request: Request):
    """Get comprehensive statistics."""
    get_db_context, EventDB, ActorDB, LocationDB, TaxonomyDB = get_db_context_and_models(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        # Basic counts
        total_events = db.query(func.count(EventDB.event_id)).scalar() or 0
        total_actors = db.query(func.count(ActorDB.actor_id)).scalar() or 0
        total_locations = db.query(func.count(LocationDB.location_id)).scalar() or 0
        total_taxonomies = db.query(func.count(TaxonomyDB.taxonomy_id)).scalar() or 0

        # Casualties
        total_deaths = db.query(func.sum(EventDB.deaths)).scalar() or 0
        total_injuries = db.query(func.sum(EventDB.injuries)).scalar() or 0

        # Countries covered
        countries_covered = db.query(func.count(func.distinct(EventDB.location_country))).scalar() or 0

        # Date range
        min_date = db.query(func.min(EventDB.date_normalized)).scalar()
        max_date = db.query(func.max(EventDB.date_normalized)).scalar()

        # Top actors
        top_actors = db.query(
            EventDB.actor_normalized,
            func.count(EventDB.event_id).label('count'),
            func.sum(EventDB.deaths).label('deaths')
        ).filter(EventDB.actor_normalized.isnot(None))\
         .group_by(EventDB.actor_normalized)\
         .order_by(desc('count'))\
         .limit(10)\
         .all()

        # Top locations
        top_locations = db.query(
            EventDB.location_country,
            func.count(EventDB.event_id).label('count'),
            func.sum(EventDB.deaths).label('deaths')
        ).group_by(EventDB.location_country)\
         .order_by(desc('count'))\
         .limit(10)\
         .all()

        # Events by taxonomy
        events_by_taxonomy = db.query(
            EventDB.taxonomy_l1,
            func.count(EventDB.event_id).label('count')
        ).group_by(EventDB.taxonomy_l1)\
         .order_by(desc('count'))\
         .all()

        # Events by severity
        events_by_severity = db.query(
            EventDB.severity,
            func.count(EventDB.event_id).label('count')
        ).group_by(EventDB.severity)\
         .all()

        return StatsResponse(
            total_events=total_events,
            total_actors=total_actors,
            total_locations=total_locations,
            total_taxonomies=total_taxonomies,
            total_deaths=int(total_deaths),
            total_injuries=int(total_injuries),
            countries_covered=countries_covered,
            date_range={
                "earliest": str(min_date) if min_date else None,
                "latest": str(max_date) if max_date else None
            },
            top_actors=[
                {"name": a, "events": c, "deaths": int(d or 0)}
                for a, c, d in top_actors if a
            ],
            top_locations=[
                {"country": c, "events": n, "deaths": int(d or 0)}
                for c, n, d in top_locations if c
            ],
            events_by_taxonomy=[
                {"taxonomy": t or "Unknown", "count": c}
                for t, c in events_by_taxonomy
            ],
            events_by_severity={
                (s or "Unknown"): c for s, c in events_by_severity
            }
        )


@router.get("/trends/monthly")
async def get_monthly_trends(
    request: Request,
    months: int = Query(12, ge=1, le=60)
):
    """Get monthly event trends."""
    get_db_context, EventDB, _, _, _ = get_db_context_and_models(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        results = db.query(
            extract('year', EventDB.date_normalized).label('year'),
            extract('month', EventDB.date_normalized).label('month'),
            func.count(EventDB.event_id).label('events'),
            func.sum(EventDB.deaths).label('deaths'),
            func.sum(EventDB.injuries).label('injuries')
        ).filter(EventDB.date_normalized.isnot(None))\
         .group_by('year', 'month')\
         .order_by('year', 'month')\
         .all()

        return [
            {
                "period": f"{int(r.year)}-{int(r.month):02d}",
                "events": r.events,
                "deaths": int(r.deaths or 0),
                "injuries": int(r.injuries or 0)
            }
            for r in results if r.year and r.month
        ][-months:]


@router.get("/by-country")
async def get_stats_by_country(request: Request):
    """Get statistics grouped by country."""
    get_db_context, EventDB, _, _, _ = get_db_context_and_models(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        results = db.query(
            EventDB.location_country,
            func.count(EventDB.event_id).label('events'),
            func.sum(EventDB.deaths).label('deaths'),
            func.sum(EventDB.injuries).label('injuries')
        ).group_by(EventDB.location_country)\
         .order_by(desc('events'))\
         .all()

        return [
            {
                "country": r.location_country,
                "events": r.events,
                "deaths": int(r.deaths or 0),
                "injuries": int(r.injuries or 0)
            }
            for r in results if r.location_country
        ]


@router.get("/by-actor")
async def get_stats_by_actor(
    request: Request,
    limit: int = Query(20, ge=1, le=100)
):
    """Get statistics grouped by actor."""
    get_db_context, EventDB, _, _, _ = get_db_context_and_models(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        results = db.query(
            EventDB.actor_normalized,
            func.count(EventDB.event_id).label('events'),
            func.sum(EventDB.deaths).label('deaths'),
            func.sum(EventDB.injuries).label('injuries'),
            func.count(func.distinct(EventDB.location_country)).label('countries')
        ).filter(EventDB.actor_normalized.isnot(None))\
         .group_by(EventDB.actor_normalized)\
         .order_by(desc('events'))\
         .limit(limit)\
         .all()

        return [
            {
                "actor": r.actor_normalized,
                "events": r.events,
                "deaths": int(r.deaths or 0),
                "injuries": int(r.injuries or 0),
                "countries_affected": r.countries
            }
            for r in results
        ]


@router.get("/search", response_model=SearchResponse)
async def search_events(
    request: Request,
    q: Optional[str] = Query(None, description="Full-text search"),
    actor: Optional[str] = None,
    country: Optional[str] = None,
    city: Optional[str] = None,
    taxonomy_l1: Optional[str] = None,
    taxonomy_l2: Optional[str] = None,
    severity: Optional[str] = None,
    min_deaths: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    sort_by: str = Query("date_desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200)
):
    """Advanced search across events."""
    get_db_context, EventDB, _, _, _ = get_db_context_and_models(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        query = db.query(EventDB)
        filters_applied = {}

        if q:
            query = query.filter(
                or_(
                    EventDB.event_description.ilike(f"%{q}%"),
                    EventDB.actor_normalized.ilike(f"%{q}%"),
                    EventDB.victim_normalized.ilike(f"%{q}%"),
                    EventDB.location_city.ilike(f"%{q}%")
                )
            )
            filters_applied["query"] = q

        if actor:
            query = query.filter(EventDB.actor_normalized.ilike(f"%{actor}%"))
            filters_applied["actor"] = actor

        if country:
            query = query.filter(EventDB.location_country.ilike(f"%{country}%"))
            filters_applied["country"] = country

        if city:
            query = query.filter(EventDB.location_city.ilike(f"%{city}%"))
            filters_applied["city"] = city

        if taxonomy_l1:
            query = query.filter(EventDB.taxonomy_l1.ilike(f"%{taxonomy_l1}%"))
            filters_applied["taxonomy_l1"] = taxonomy_l1

        if taxonomy_l2:
            query = query.filter(EventDB.taxonomy_l2.ilike(f"%{taxonomy_l2}%"))
            filters_applied["taxonomy_l2"] = taxonomy_l2

        if severity:
            query = query.filter(EventDB.severity == severity)
            filters_applied["severity"] = severity

        if min_deaths is not None:
            query = query.filter(EventDB.deaths >= min_deaths)
            filters_applied["min_deaths"] = min_deaths

        if start_date:
            query = query.filter(EventDB.date_normalized >= start_date)
            filters_applied["start_date"] = str(start_date)

        if end_date:
            query = query.filter(EventDB.date_normalized <= end_date)
            filters_applied["end_date"] = str(end_date)

        # Get total count
        total = query.count()

        # Apply sorting
        sort_options = {
            "date_desc": desc(EventDB.date_normalized),
            "date_asc": EventDB.date_normalized,
            "deaths_desc": desc(EventDB.deaths),
            "deaths_asc": EventDB.deaths,
            "severity_desc": desc(EventDB.severity),
            "created_desc": desc(EventDB.created_at)
        }
        order_clause = sort_options.get(sort_by, desc(EventDB.date_normalized))
        query = query.order_by(order_clause)
        filters_applied["sort_by"] = sort_by

        # Pagination
        offset = (page - 1) * page_size
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1

        events = query.offset(offset).limit(page_size).all()

        results = [
            SearchResult(
                event_id=e.event_id,
                date_normalized=e.date_normalized,
                location_country=e.location_country,
                location_city=e.location_city,
                actor_normalized=e.actor_normalized,
                victim_normalized=e.victim_normalized,
                taxonomy_l1=e.taxonomy_l1,
                taxonomy_l2=e.taxonomy_l2,
                deaths=e.deaths or 0,
                injuries=e.injuries or 0,
                severity=e.severity,
                event_description=e.event_description[:200] + "..." if len(e.event_description or "") > 200 else (e.event_description or "")
            )
            for e in events
        ]

        return SearchResponse(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            results=results,
            filters_applied=filters_applied
        )


@router.get("/timeline")
async def get_timeline(
    request: Request,
    period: str = Query("month", pattern="^(day|week|month|year)$"),
    months: int = Query(12, ge=1, le=60)
):
    """Get event counts over time for timeline visualization."""
    get_db_context, EventDB, _, _, _ = get_db_context_and_models(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        if period == "year":
            results = db.query(
                extract('year', EventDB.date_normalized).label('year'),
                func.count(EventDB.event_id).label('count'),
                func.sum(EventDB.deaths).label('deaths')
            ).filter(EventDB.date_normalized.isnot(None))\
             .group_by('year')\
             .order_by('year')\
             .all()

            return [
                {"period": f"{int(r.year)}", "events": r.count, "deaths": int(r.deaths or 0)}
                for r in results if r.year
            ]

        elif period == "month":
            results = db.query(
                extract('year', EventDB.date_normalized).label('year'),
                extract('month', EventDB.date_normalized).label('month'),
                func.count(EventDB.event_id).label('count'),
                func.sum(EventDB.deaths).label('deaths')
            ).filter(EventDB.date_normalized.isnot(None))\
             .group_by('year', 'month')\
             .order_by('year', 'month')\
             .all()

            return [
                {
                    "period": f"{int(r.year)}-{int(r.month):02d}",
                    "events": r.count,
                    "deaths": int(r.deaths or 0)
                }
                for r in results if r.year and r.month
            ][-months:]

        else:  # day
            results = db.query(
                func.date(EventDB.date_normalized).label('date'),
                func.count(EventDB.event_id).label('count'),
                func.sum(EventDB.deaths).label('deaths')
            ).filter(EventDB.date_normalized.isnot(None))\
             .group_by('date')\
             .order_by('date')\
             .all()

            return [
                {"period": str(r.date), "events": r.count, "deaths": int(r.deaths or 0)}
                for r in results if r.date
            ][-90:]


@router.get("/export")
async def export_events(
    request: Request,
    q: Optional[str] = None,
    actor: Optional[str] = None,
    country: Optional[str] = None,
    taxonomy_l1: Optional[str] = None,
    severity: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    format: str = Query("csv", pattern="^(csv|json)$")
):
    """Export events to CSV or JSON."""
    get_db_context, EventDB, _, _, _ = get_db_context_and_models(request)
    from datetime import datetime

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        query = db.query(EventDB)

        if q:
            query = query.filter(
                or_(
                    EventDB.event_description.ilike(f"%{q}%"),
                    EventDB.actor_normalized.ilike(f"%{q}%")
                )
            )
        if actor:
            query = query.filter(EventDB.actor_normalized.ilike(f"%{actor}%"))
        if country:
            query = query.filter(EventDB.location_country.ilike(f"%{country}%"))
        if taxonomy_l1:
            query = query.filter(EventDB.taxonomy_l1.ilike(f"%{taxonomy_l1}%"))
        if severity:
            query = query.filter(EventDB.severity == severity)
        if start_date:
            query = query.filter(EventDB.date_normalized >= start_date)
        if end_date:
            query = query.filter(EventDB.date_normalized <= end_date)

        events = query.order_by(desc(EventDB.date_normalized)).limit(1000).all()

        if format == "json":
            return [
                {
                    "event_id": e.event_id,
                    "date": str(e.date_normalized) if e.date_normalized else None,
                    "actor": e.actor_normalized,
                    "victim": e.victim_normalized,
                    "country": e.location_country,
                    "city": e.location_city,
                    "taxonomy_l1": e.taxonomy_l1,
                    "taxonomy_l2": e.taxonomy_l2,
                    "deaths": e.deaths or 0,
                    "injuries": e.injuries or 0,
                    "severity": e.severity,
                    "description": e.event_description
                }
                for e in events
            ]

        # CSV export
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Event ID", "Date", "Actor", "Victim", "Country", "City",
            "Category L1", "Category L2", "Deaths", "Injuries", "Severity", "Description"
        ])

        for e in events:
            writer.writerow([
                e.event_id,
                str(e.date_normalized) if e.date_normalized else "",
                e.actor_normalized or "",
                e.victim_normalized or "",
                e.location_country or "",
                e.location_city or "",
                e.taxonomy_l1 or "",
                e.taxonomy_l2 or "",
                e.deaths or 0,
                e.injuries or 0,
                e.severity or "",
                (e.event_description or "").replace("\n", " ")[:500]
            ])

        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=events_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )


@router.get("/review-queue")
async def get_review_queue(
    request: Request,
    limit: int = Query(50, ge=1, le=200)
):
    """Get events flagged for review or with low confidence."""
    get_db_context, EventDB, _, _, _ = get_db_context_and_models(request)

    with get_db_context() as db:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        events = db.query(EventDB).filter(
            or_(
                EventDB.flagged_for_review == True,
                EventDB.actor_confidence < 0.7,
                EventDB.location_confidence < 0.7
            )
        ).order_by(desc(EventDB.created_at)).limit(limit).all()

        return [
            {
                "event_id": e.event_id,
                "actor": e.actor_normalized,
                "country": e.location_country,
                "description": (e.event_description or "")[:200],
                "flagged": e.flagged_for_review,
                "actor_confidence": e.actor_confidence,
                "location_confidence": e.location_confidence,
                "review_notes": e.review_notes,
                "created_at": str(e.created_at)
            }
            for e in events
        ]
