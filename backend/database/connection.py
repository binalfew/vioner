"""Database connection and session management."""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import logging

from config import settings

logger = logging.getLogger(__name__)

# Create engine
engine = None
SessionLocal = None
Base = declarative_base()


def init_database():
    """Initialize database connection."""
    global engine, SessionLocal

    if not settings.enable_db_storage:
        logger.info("Database storage is disabled")
        return None

    try:
        engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            echo=settings.debug
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        logger.info("Database connection initialized")
        return engine
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return None


def get_db():
    """Dependency to get database session."""
    if SessionLocal is None:
        init_database()

    if SessionLocal is None:
        yield None
        return

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """Context manager for database sessions."""
    if SessionLocal is None:
        init_database()

    if SessionLocal is None:
        yield None
        return

    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def check_connection() -> bool:
    """Check if database is connected."""
    if engine is None:
        return False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
