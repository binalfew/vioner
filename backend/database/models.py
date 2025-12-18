"""SQLAlchemy models matching Week 7-8 database schema."""

from sqlalchemy import (
    Column, String, Integer, Text, Float, Boolean, DateTime, Date,
    ForeignKey, JSON, ARRAY, Numeric, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from database.connection import Base


class UserDB(Base):
    """Users table for authentication."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), default='user')
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())


class TaxonomyDB(Base):
    """Taxonomy classification table."""
    __tablename__ = "taxonomies"

    taxonomy_id = Column(Integer, primary_key=True, autoincrement=True)
    level_1 = Column(String(100), nullable=False)
    level_2 = Column(String(100))
    level_3 = Column(String(100))
    description = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())


class ActorDB(Base):
    """Actors table (armed groups, organizations)."""
    __tablename__ = "actors"

    actor_id = Column(Integer, primary_key=True, autoincrement=True)
    actor_name = Column(String(255), nullable=False, unique=True)
    actor_type = Column(String(100))
    actor_category = Column(String(50))
    country = Column(String(100))
    region = Column(String(100))
    aliases = Column(ARRAY(Text))
    description = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())


class LocationDB(Base):
    """Locations table."""
    __tablename__ = "locations"

    location_id = Column(Integer, primary_key=True, autoincrement=True)
    country = Column(String(100), nullable=False)
    city = Column(String(255))
    region = Column(String(100))
    district = Column(String(100))
    population = Column(Integer)
    location_type = Column(String(50))
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())


class EventDB(Base):
    """Core events table matching Week 7-8 schema."""
    __tablename__ = "events"

    event_id = Column(String(100), primary_key=True)

    # WHO: Actor Information
    actor_normalized = Column(String(255))
    actor_id = Column(Integer, ForeignKey("actors.actor_id"))
    actor_type = Column(String(100))
    actor_confidence = Column(Numeric(3, 2))

    # WHOM: Victim Information
    victim_normalized = Column(String(255))
    victim_type = Column(String(100))
    victim_confidence = Column(Numeric(3, 2))

    # WHERE: Location Information
    location_country = Column(String(100), nullable=False)
    location_city = Column(String(255))
    location_coordinates = Column(String(50))
    location_id = Column(Integer, ForeignKey("locations.location_id"))
    location_confidence = Column(Numeric(3, 2))

    # WHEN: Temporal Information
    date_normalized = Column(Date)
    date_original = Column(String(100))
    date_confidence = Column(Numeric(3, 2))

    # WHAT: Taxonomy Classification
    taxonomy_l1 = Column(String(100), nullable=False)
    taxonomy_l2 = Column(String(100))
    taxonomy_l3 = Column(String(100))
    taxonomy_id = Column(Integer, ForeignKey("taxonomies.taxonomy_id"))
    classification_confidence = Column(Numeric(3, 2))

    # HOW: Method/Weapon Information
    weapon_category = Column(String(100))
    weapon_details = Column(Text)
    attack_method = Column(String(255))

    # Casualties
    deaths = Column(Integer, default=0)
    injuries = Column(Integer, default=0)

    # Severity Assessment
    severity = Column(String(20))
    severity_score = Column(Integer)

    # Event Description
    event_description = Column(Text, nullable=False)

    # Quality Flags
    flagged_for_review = Column(Boolean, default=False)
    review_notes = Column(Text)

    # Extraction Metadata
    annotator_name = Column(String(100), default='NER-Production-API')
    extraction_method = Column(String(50), default='bert-ner')
    extraction_date = Column(DateTime, default=func.current_timestamp())
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    actor = relationship("ActorDB")
    location = relationship("LocationDB")
    taxonomy = relationship("TaxonomyDB")


class HistoryDB(Base):
    """Track extraction history for analytics."""
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String(100), nullable=False, index=True)
    text = Column(Text, nullable=False)
    text_hash = Column(String(64), index=True)

    # Extraction results (stored as JSON for flexibility)
    entities_json = Column(JSON)
    structured_event_json = Column(JSON)
    confidence_scores_json = Column(JSON)

    # Metadata
    entity_count = Column(Integer, default=0)
    processing_time_ms = Column(Float)
    model_version = Column(String(50))

    # User feedback (for future model improvement)
    user_rating = Column(Integer)  # 1-5 stars
    user_feedback = Column(Text)
    corrections_json = Column(JSON)

    # Status
    saved_to_events = Column(Boolean, default=False)
    event_id = Column(String(100))

    # Timestamps
    created_at = Column(DateTime, default=func.current_timestamp())

    __table_args__ = (
        Index('idx_history_created', 'created_at'),
    )


class TrainingDB(Base):
    """Track ML training runs."""
    __tablename__ = "trainings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), nullable=False, unique=True, index=True)
    model_name = Column(String(100), nullable=False)
    status = Column(String(20), default='running')  # running, completed, failed, stopped

    # Training configuration
    epochs_total = Column(Integer)
    epochs_completed = Column(Integer, default=0)
    batch_size = Column(Integer)
    learning_rate = Column(Float)
    max_sequence_length = Column(Integer)

    # Best model info
    best_epoch = Column(Integer)
    best_val_loss = Column(Float)
    best_val_accuracy = Column(Float)

    # Dataset info
    train_samples = Column(Integer)
    val_samples = Column(Integer)

    # Paths
    checkpoint_path = Column(Text)
    train_data_path = Column(Text)
    val_data_path = Column(Text)

    # Full configuration and metrics history as JSON
    config_json = Column(JSON)
    metrics_history_json = Column(JSON)

    # Timestamps
    started_at = Column(DateTime, default=func.current_timestamp())
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Notes
    notes = Column(Text)

    # Active model flag (only one can be active at a time)
    is_active = Column(Boolean, default=False)

    __table_args__ = (
        Index('idx_trainings_status', 'status'),
        Index('idx_trainings_started', 'started_at'),
    )


# Create indexes
Index('idx_events_date_country', EventDB.date_normalized, EventDB.location_country)
Index('idx_events_actor_date', EventDB.actor_normalized, EventDB.date_normalized)
