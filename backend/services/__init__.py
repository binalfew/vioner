"""Backend services module."""

from services.ner import NERService
from services.resolver import EntityResolver, resolve_entities_for_event

__all__ = [
    "NERService",
    "EntityResolver",
    "resolve_entities_for_event"
]
