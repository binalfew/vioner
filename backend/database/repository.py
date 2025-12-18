"""Repository pattern for database operations."""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_, text
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import hashlib
import uuid
import logging

from database.models import (
    EventDB, ActorDB, LocationDB,
    TaxonomyDB, HistoryDB, TrainingDB
)

logger = logging.getLogger(__name__)


class EventRepository:
    """Repository for event-related database operations."""

    def __init__(self, db: Session):
        self.db = db

    # =========================================================================
    # Extraction History Operations
    # =========================================================================

    def save_extraction(
        self,
        request_id: str,
        text: str,
        entities: List[Dict],
        structured_event: Dict,
        confidence_scores: Dict,
        processing_time_ms: float,
        model_version: str
    ) -> HistoryDB:
        """Save an extraction to history."""
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        extraction = HistoryDB(
            request_id=request_id,
            text=text,
            text_hash=text_hash,
            entities_json=entities,
            structured_event_json=structured_event,
            confidence_scores_json=confidence_scores,
            entity_count=len(entities),
            processing_time_ms=processing_time_ms,
            model_version=model_version
        )

        self.db.add(extraction)
        self.db.commit()
        self.db.refresh(extraction)

        logger.info(f"Saved extraction {request_id} to history")
        return extraction

    def get_extraction_history(
        self,
        limit: int = 50,
        offset: int = 0,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[HistoryDB]:
        """Get extraction history with optional date filtering."""
        query = self.db.query(HistoryDB)

        if start_date:
            query = query.filter(HistoryDB.created_at >= start_date)
        if end_date:
            query = query.filter(HistoryDB.created_at <= end_date)

        return query.order_by(desc(HistoryDB.created_at))\
                    .offset(offset)\
                    .limit(limit)\
                    .all()

    def get_extraction_by_id(self, extraction_id: int) -> Optional[HistoryDB]:
        """Get a specific extraction by ID."""
        return self.db.query(HistoryDB)\
                     .filter(HistoryDB.id == extraction_id)\
                     .first()

    def get_extraction_by_request_id(self, request_id: str) -> Optional[HistoryDB]:
        """Get extraction by request ID."""
        return self.db.query(HistoryDB)\
                     .filter(HistoryDB.request_id == request_id)\
                     .first()

    def update_extraction_feedback(
        self,
        extraction_id: int,
        rating: Optional[int] = None,
        feedback: Optional[str] = None,
        corrections: Optional[Dict] = None
    ) -> Optional[HistoryDB]:
        """Update user feedback on an extraction."""
        extraction = self.get_extraction_by_id(extraction_id)
        if not extraction:
            return None

        if rating is not None:
            extraction.user_rating = rating
        if feedback is not None:
            extraction.user_feedback = feedback
        if corrections is not None:
            extraction.corrections_json = corrections

        self.db.commit()
        self.db.refresh(extraction)
        return extraction

    # =========================================================================
    # Event Operations
    # =========================================================================

    def get_events(
        self,
        limit: int = 50,
        offset: int = 0,
        country: Optional[str] = None,
        actor: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        severity: Optional[str] = None,
        flagged: Optional[bool] = None
    ) -> List[EventDB]:
        """Get events with filtering."""
        query = self.db.query(EventDB)

        if country:
            query = query.filter(EventDB.location_country.ilike(f"%{country}%"))
        if actor:
            query = query.filter(EventDB.actor_normalized.ilike(f"%{actor}%"))
        if start_date:
            query = query.filter(EventDB.date_normalized >= start_date)
        if end_date:
            query = query.filter(EventDB.date_normalized <= end_date)
        if severity:
            query = query.filter(EventDB.severity == severity)
        if flagged is not None:
            query = query.filter(EventDB.flagged_for_review == flagged)

        return query.order_by(desc(EventDB.created_at))\
                    .offset(offset)\
                    .limit(limit)\
                    .all()

    def get_event_by_id(self, event_id: str) -> Optional[EventDB]:
        """Get event by ID."""
        return self.db.query(EventDB)\
                     .filter(EventDB.event_id == event_id)\
                     .first()

    def create_event(self, event_data: Dict[str, Any]) -> EventDB:
        """Create a new event."""
        event = EventDB(**event_data)
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def update_event(self, event_id: str, updates: Dict[str, Any]) -> Optional[EventDB]:
        """Update an event."""
        event = self.get_event_by_id(event_id)
        if not event:
            return None

        for key, value in updates.items():
            if hasattr(event, key):
                setattr(event, key, value)

        self.db.commit()
        self.db.refresh(event)
        return event

    def delete_event(self, event_id: str) -> bool:
        """Delete an event."""
        event = self.get_event_by_id(event_id)
        if not event:
            return False

        self.db.delete(event)
        self.db.commit()
        return True

    def get_events_count(
        self,
        country: Optional[str] = None,
        actor: Optional[str] = None,
        severity: Optional[str] = None
    ) -> int:
        """Get count of events with filters."""
        query = self.db.query(func.count(EventDB.event_id))

        if country:
            query = query.filter(EventDB.location_country.ilike(f"%{country}%"))
        if actor:
            query = query.filter(EventDB.actor_normalized.ilike(f"%{actor}%"))
        if severity:
            query = query.filter(EventDB.severity == severity)

        return query.scalar() or 0

    # =========================================================================
    # Knowledge Base Operations
    # =========================================================================

    def get_actors(
        self,
        limit: int = 50,
        offset: int = 0,
        search: Optional[str] = None
    ) -> List[ActorDB]:
        """Get actors with optional search."""
        query = self.db.query(ActorDB)

        if search:
            query = query.filter(ActorDB.actor_name.ilike(f"%{search}%"))

        return query.order_by(ActorDB.actor_name)\
                    .offset(offset)\
                    .limit(limit)\
                    .all()

    def get_actor_by_id(self, actor_id: int) -> Optional[ActorDB]:
        """Get actor by ID."""
        return self.db.query(ActorDB)\
                     .filter(ActorDB.actor_id == actor_id)\
                     .first()

    def get_locations(
        self,
        limit: int = 50,
        offset: int = 0,
        country: Optional[str] = None
    ) -> List[LocationDB]:
        """Get locations with optional country filter."""
        query = self.db.query(LocationDB)

        if country:
            query = query.filter(LocationDB.country.ilike(f"%{country}%"))

        return query.order_by(LocationDB.country, LocationDB.city)\
                    .offset(offset)\
                    .limit(limit)\
                    .all()

    def get_location_by_id(self, location_id: int) -> Optional[LocationDB]:
        """Get location by ID."""
        return self.db.query(LocationDB)\
                     .filter(LocationDB.location_id == location_id)\
                     .first()

    def get_taxonomies(self, level_1: Optional[str] = None) -> List[TaxonomyDB]:
        """Get taxonomies with optional level 1 filter."""
        query = self.db.query(TaxonomyDB)

        if level_1:
            query = query.filter(TaxonomyDB.level_1 == level_1)

        return query.order_by(TaxonomyDB.level_1, TaxonomyDB.level_2, TaxonomyDB.level_3).all()

    # =========================================================================
    # Statistics Operations
    # =========================================================================

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get comprehensive dashboard statistics."""
        try:
            # Total extractions
            total_extractions = self.db.query(func.count(HistoryDB.id)).scalar() or 0

            # Total events
            total_events = self.db.query(func.count(EventDB.event_id)).scalar() or 0

            # Today's extractions
            today = datetime.now().date()
            today_extractions = self.db.query(func.count(HistoryDB.id))\
                                      .filter(func.date(HistoryDB.created_at) == today)\
                                      .scalar() or 0

            # Average processing time
            avg_processing_time = self.db.query(func.avg(HistoryDB.processing_time_ms))\
                                        .scalar() or 0

            # Average entity count
            avg_entities = self.db.query(func.avg(HistoryDB.entity_count))\
                                 .scalar() or 0

            # Events by country (top 10)
            events_by_country = self.db.query(
                EventDB.location_country,
                func.count(EventDB.event_id).label('count')
            ).group_by(EventDB.location_country)\
             .order_by(desc('count'))\
             .limit(10)\
             .all()

            # Events by severity
            events_by_severity = self.db.query(
                EventDB.severity,
                func.count(EventDB.event_id).label('count')
            ).group_by(EventDB.severity)\
             .all()

            # Total casualties
            total_deaths = self.db.query(func.sum(EventDB.deaths)).scalar() or 0
            total_injuries = self.db.query(func.sum(EventDB.injuries)).scalar() or 0

            # Recent extraction trend (last 7 days)
            seven_days_ago = datetime.now() - timedelta(days=7)
            extraction_trend = self.db.query(
                func.date(HistoryDB.created_at).label('date'),
                func.count(HistoryDB.id).label('count')
            ).filter(HistoryDB.created_at >= seven_days_ago)\
             .group_by(func.date(HistoryDB.created_at))\
             .order_by('date')\
             .all()

            # Top actors
            top_actors = self.db.query(
                EventDB.actor_normalized,
                func.count(EventDB.event_id).label('count')
            ).filter(EventDB.actor_normalized.isnot(None))\
             .group_by(EventDB.actor_normalized)\
             .order_by(desc('count'))\
             .limit(10)\
             .all()

            return {
                "total_extractions": total_extractions,
                "total_events": total_events,
                "today_extractions": today_extractions,
                "avg_processing_time_ms": round(float(avg_processing_time), 2),
                "avg_entities_per_extraction": round(float(avg_entities), 1),
                "events_by_country": [
                    {"country": c, "count": n} for c, n in events_by_country if c
                ],
                "events_by_severity": {
                    (s or "Unknown"): n for s, n in events_by_severity
                },
                "total_casualties": {
                    "deaths": int(total_deaths),
                    "injuries": int(total_injuries),
                    "total": int(total_deaths + total_injuries)
                },
                "extraction_trend": [
                    {"date": str(d), "count": c} for d, c in extraction_trend
                ],
                "top_actors": [
                    {"actor": a, "count": n} for a, n in top_actors if a
                ]
            }
        except Exception as e:
            logger.error(f"Failed to get dashboard stats: {e}")
            return {
                "total_extractions": 0,
                "total_events": 0,
                "error": str(e)
            }

    def get_monthly_trends(
        self,
        months: int = 12,
        country: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get monthly event trends."""
        start_date = datetime.now() - timedelta(days=months * 30)

        query = self.db.query(
            func.date_trunc('month', EventDB.date_normalized).label('month'),
            func.count(EventDB.event_id).label('events'),
            func.sum(EventDB.deaths).label('deaths'),
            func.sum(EventDB.injuries).label('injuries')
        ).filter(EventDB.date_normalized >= start_date)

        if country:
            query = query.filter(EventDB.location_country.ilike(f"%{country}%"))

        results = query.group_by('month').order_by('month').all()

        return [
            {
                "month": str(r.month.date()) if r.month else None,
                "events": r.events or 0,
                "deaths": r.deaths or 0,
                "injuries": r.injuries or 0
            }
            for r in results
        ]

    def get_country_stats(self) -> List[Dict[str, Any]]:
        """Get statistics by country."""
        results = self.db.query(
            EventDB.location_country,
            func.count(EventDB.event_id).label('events'),
            func.sum(EventDB.deaths).label('deaths'),
            func.sum(EventDB.injuries).label('injuries'),
            func.count(func.distinct(EventDB.actor_normalized)).label('actors')
        ).group_by(EventDB.location_country)\
         .order_by(desc('events'))\
         .all()

        return [
            {
                "country": r.location_country or "Unknown",
                "events": r.events or 0,
                "deaths": r.deaths or 0,
                "injuries": r.injuries or 0,
                "actors": r.actors or 0
            }
            for r in results
        ]

    def get_actor_stats(self) -> List[Dict[str, Any]]:
        """Get statistics by actor."""
        results = self.db.query(
            EventDB.actor_normalized,
            func.count(EventDB.event_id).label('events'),
            func.sum(EventDB.deaths).label('deaths'),
            func.sum(EventDB.injuries).label('injuries'),
            func.count(func.distinct(EventDB.location_country)).label('countries')
        ).filter(EventDB.actor_normalized.isnot(None))\
         .group_by(EventDB.actor_normalized)\
         .order_by(desc('events'))\
         .limit(50)\
         .all()

        return [
            {
                "actor": r.actor_normalized,
                "events": r.events or 0,
                "deaths": r.deaths or 0,
                "injuries": r.injuries or 0,
                "countries": r.countries or 0
            }
            for r in results
        ]

    def search_events(
        self,
        query_text: str,
        limit: int = 50
    ) -> List[EventDB]:
        """Full-text search on event descriptions."""
        # Use PostgreSQL full-text search
        search_query = self.db.query(EventDB)\
            .filter(
                EventDB.event_description.ilike(f"%{query_text}%") |
                EventDB.actor_normalized.ilike(f"%{query_text}%") |
                EventDB.victim_normalized.ilike(f"%{query_text}%") |
                EventDB.location_city.ilike(f"%{query_text}%")
            )\
            .order_by(desc(EventDB.created_at))\
            .limit(limit)

        return search_query.all()

    # =========================================================================
    # Training Run Operations
    # =========================================================================

    def create_training_run(self, run_data: Dict[str, Any]) -> TrainingDB:
        """Create a new training run record."""
        run = TrainingDB(**run_data)
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def update_training_run(
        self,
        session_id: str,
        updates: Dict[str, Any]
    ) -> Optional[TrainingDB]:
        """Update a training run."""
        run = self.db.query(TrainingDB)\
                    .filter(TrainingDB.session_id == session_id)\
                    .first()
        if not run:
            return None

        for key, value in updates.items():
            if hasattr(run, key):
                setattr(run, key, value)

        self.db.commit()
        self.db.refresh(run)
        return run

    def get_training_runs(
        self,
        limit: int = 20,
        status: Optional[str] = None
    ) -> List[TrainingDB]:
        """Get training runs."""
        query = self.db.query(TrainingDB)

        if status:
            query = query.filter(TrainingDB.status == status)

        return query.order_by(desc(TrainingDB.started_at))\
                    .limit(limit)\
                    .all()

    def get_training_run_by_session(self, session_id: str) -> Optional[TrainingDB]:
        """Get training run by session ID."""
        return self.db.query(TrainingDB)\
                     .filter(TrainingDB.session_id == session_id)\
                     .first()
