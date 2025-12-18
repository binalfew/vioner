"""Database module for the NER system."""

from database.connection import (
    Base,
    engine,
    SessionLocal,
    init_database,
    get_db,
    get_db_context,
    check_connection
)
from database.models import (
    UserDB,
    TaxonomyDB,
    ActorDB,
    LocationDB,
    EventDB,
    HistoryDB,
    TrainingDB
)
from database.repository import EventRepository

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "init_database",
    "get_db",
    "get_db_context",
    "check_connection",
    "UserDB",
    "TaxonomyDB",
    "ActorDB",
    "LocationDB",
    "EventDB",
    "HistoryDB",
    "TrainingDB",
    "EventRepository"
]
