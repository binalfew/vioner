"""
Entity Resolution Service - Links extracted entities to knowledge base.

This service resolves extracted text entities to normalized database records,
enabling proper knowledge base construction with linked data.
"""

from typing import Optional, List, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging
from difflib import SequenceMatcher

from database.models import ActorDB, LocationDB, TaxonomyDB

logger = logging.getLogger(__name__)


class EntityResolver:
    """Resolves extracted entities to knowledge base records."""

    def __init__(self, db: Session):
        self.db = db
        self._actor_cache: Dict[str, Optional[ActorDB]] = {}
        self._location_cache: Dict[str, Optional[LocationDB]] = {}
        self._taxonomy_cache: Dict[str, Optional[TaxonomyDB]] = {}

    # =========================================================================
    # Actor Resolution
    # =========================================================================

    def resolve_actor(self, actor_name: str, threshold: float = 0.7) -> Optional[ActorDB]:
        """
        Resolve an actor name to a database record.

        Uses fuzzy matching and alias lookup to find the best match.
        """
        if not actor_name:
            return None

        actor_name = actor_name.strip()

        # Check cache first
        cache_key = actor_name.lower()
        if cache_key in self._actor_cache:
            return self._actor_cache[cache_key]

        # Try exact match first
        actor = self.db.query(ActorDB).filter(
            func.lower(ActorDB.actor_name) == actor_name.lower()
        ).first()

        if actor:
            self._actor_cache[cache_key] = actor
            return actor

        # Try alias match
        all_actors = self.db.query(ActorDB).all()
        for a in all_actors:
            if a.aliases:
                for alias in a.aliases:
                    if alias.lower() == actor_name.lower():
                        self._actor_cache[cache_key] = a
                        return a

        # Try fuzzy match
        best_match = None
        best_score = 0.0

        for a in all_actors:
            # Check main name
            score = self._similarity(actor_name.lower(), a.actor_name.lower())
            if score > best_score and score >= threshold:
                best_score = score
                best_match = a

            # Check aliases
            if a.aliases:
                for alias in a.aliases:
                    score = self._similarity(actor_name.lower(), alias.lower())
                    if score > best_score and score >= threshold:
                        best_score = score
                        best_match = a

        self._actor_cache[cache_key] = best_match

        if best_match:
            logger.info(f"Resolved actor '{actor_name}' -> '{best_match.actor_name}' (score: {best_score:.2f})")

        return best_match

    def get_or_create_actor(
        self,
        actor_name: str,
        actor_type: Optional[str] = None,
        country: Optional[str] = None
    ) -> ActorDB:
        """Get existing actor or create new one."""
        # Try to resolve first
        actor = self.resolve_actor(actor_name)
        if actor:
            return actor

        # Create new actor
        new_actor = ActorDB(
            actor_name=actor_name,
            actor_type=actor_type or "Unknown",
            actor_category="Extracted",
            country=country,
            description=f"Auto-created from NER extraction"
        )
        self.db.add(new_actor)
        self.db.flush()  # Get the ID without committing

        logger.info(f"Created new actor: {actor_name}")
        return new_actor

    # =========================================================================
    # Location Resolution
    # =========================================================================

    def resolve_location(
        self,
        country: Optional[str] = None,
        city: Optional[str] = None,
        region: Optional[str] = None,
        threshold: float = 0.8
    ) -> Optional[LocationDB]:
        """
        Resolve location to a database record.

        Tries to find the most specific match (city > region > country).
        """
        if not country and not city:
            return None

        cache_key = f"{country}|{city}|{region}".lower()
        if cache_key in self._location_cache:
            return self._location_cache[cache_key]

        # Build query
        query = self.db.query(LocationDB)

        # Try exact match with city first (most specific)
        if city:
            location = query.filter(
                func.lower(LocationDB.city) == city.lower()
            ).first()
            if location:
                self._location_cache[cache_key] = location
                return location

        # Try country match
        if country:
            location = query.filter(
                func.lower(LocationDB.country) == country.lower()
            ).first()
            if location:
                self._location_cache[cache_key] = location
                return location

        # Fuzzy match on city
        if city:
            all_locations = self.db.query(LocationDB).filter(
                LocationDB.city.isnot(None)
            ).all()

            best_match = None
            best_score = 0.0

            for loc in all_locations:
                score = self._similarity(city.lower(), loc.city.lower())
                if score > best_score and score >= threshold:
                    best_score = score
                    best_match = loc

            if best_match:
                self._location_cache[cache_key] = best_match
                logger.info(f"Resolved location '{city}' -> '{best_match.city}' (score: {best_score:.2f})")
                return best_match

        self._location_cache[cache_key] = None
        return None

    def get_or_create_location(
        self,
        country: str,
        city: Optional[str] = None,
        region: Optional[str] = None
    ) -> LocationDB:
        """Get existing location or create new one."""
        # Try to resolve first
        location = self.resolve_location(country, city, region)
        if location:
            return location

        # Create new location
        new_location = LocationDB(
            country=country,
            city=city,
            region=region,
            location_type="City" if city else "Country"
        )
        self.db.add(new_location)
        self.db.flush()

        logger.info(f"Created new location: {city or country}, {country}")
        return new_location

    # =========================================================================
    # Taxonomy Resolution
    # =========================================================================

    def resolve_taxonomy(
        self,
        event_type: Optional[str] = None,
        action: Optional[str] = None
    ) -> Optional[TaxonomyDB]:
        """
        Resolve event type to taxonomy classification.

        Uses keyword matching to find the best taxonomy fit.
        """
        if not event_type and not action:
            return None

        search_text = f"{event_type or ''} {action or ''}".lower()
        cache_key = search_text

        if cache_key in self._taxonomy_cache:
            return self._taxonomy_cache[cache_key]

        # Keyword to taxonomy mapping
        taxonomy_keywords = {
            # Terrorism
            ('bomb', 'explosion', 'ied', 'suicide', 'blast'): ('Political Violence', 'Terrorism'),
            ('terror', 'terrorist'): ('Political Violence', 'Terrorism'),

            # Armed Attack
            ('attack', 'assault', 'raid', 'offensive'): ('Political Violence', 'Rebellion/Armed Insurgency'),
            ('ambush', 'ambushed'): ('Political Violence', 'Rebellion/Armed Insurgency'),
            ('shelling', 'mortar', 'artillery'): ('Political Violence', 'Rebellion/Armed Insurgency'),

            # Kidnapping
            ('kidnap', 'abduct', 'hostage', 'capture'): ('Criminal Violence', 'Kidnapping for Ransom'),

            # Communal Violence
            ('ethnic', 'tribal', 'clan'): ('Communal Violence', 'Ethnic/Tribal Conflict'),
            ('religious', 'sectarian'): ('Communal Violence', 'Religious Violence'),
            ('farmer', 'herder', 'pastoralist'): ('Communal Violence', 'Pastoralist-Farmer Clashes'),

            # State Violence
            ('police', 'military', 'army', 'forces'): ('State Violence Against Civilians', 'Extrajudicial Killings'),
            ('protest', 'demonstration'): ('State Violence Against Civilians', 'State Repression of Protests'),
        }

        # Find matching keywords
        for keywords, (l1, l2) in taxonomy_keywords.items():
            if any(kw in search_text for kw in keywords):
                taxonomy = self.db.query(TaxonomyDB).filter(
                    TaxonomyDB.level_1 == l1,
                    TaxonomyDB.level_2 == l2
                ).first()

                if taxonomy:
                    self._taxonomy_cache[cache_key] = taxonomy
                    logger.info(f"Resolved taxonomy: {l1} -> {l2}")
                    return taxonomy

        # Default to general political violence
        taxonomy = self.db.query(TaxonomyDB).filter(
            TaxonomyDB.level_1 == 'Political Violence'
        ).first()

        self._taxonomy_cache[cache_key] = taxonomy
        return taxonomy

    def classify_event(
        self,
        entities: List[Dict],
        structured_event: Dict
    ) -> Tuple[str, Optional[str], Optional[str], Optional[int]]:
        """
        Classify an event based on extracted entities.

        Returns: (taxonomy_l1, taxonomy_l2, taxonomy_l3, taxonomy_id)
        """
        # Get event type and action from entities
        event_type = None
        action = None

        for entity in entities:
            label = entity.get('label', '')
            text = entity.get('text', '')

            if label == 'EVENT_TYPE':
                event_type = text
            elif label == 'ACTION':
                action = text

        # Also check structured event
        what_list = structured_event.get('what', [])
        if what_list and not event_type:
            event_type = what_list[0]

        # Resolve taxonomy
        taxonomy = self.resolve_taxonomy(event_type, action)

        if taxonomy:
            return (
                taxonomy.level_1,
                taxonomy.level_2,
                taxonomy.level_3,
                taxonomy.taxonomy_id
            )

        return ('Political Violence', 'Rebellion/Armed Insurgency', 'Armed Attack', None)

    # =========================================================================
    # Full Entity Resolution
    # =========================================================================

    def resolve_all_entities(
        self,
        entities: List[Dict],
        structured_event: Dict,
        create_if_missing: bool = True
    ) -> Dict:
        """
        Resolve all entities from an extraction to knowledge base records.

        Returns a dictionary with resolved IDs and normalized values.
        """
        result = {
            'actor_id': None,
            'actor_normalized': None,
            'actor_type': None,
            'location_id': None,
            'location_country': None,
            'location_city': None,
            'taxonomy_id': None,
            'taxonomy_l1': None,
            'taxonomy_l2': None,
            'taxonomy_l3': None,
        }

        # Extract key entities
        perpetrator = None
        country = None
        city = None
        event_type = None

        for entity in entities:
            label = entity.get('label', '')
            text = entity.get('text', '')

            if label == 'PERPETRATOR' and not perpetrator:
                perpetrator = text
            elif label == 'COUNTRY' and not country:
                country = text
            elif label == 'CITY' and not city:
                city = text
            elif label == 'LOCATION' and not city:
                city = text
            elif label == 'EVENT_TYPE' and not event_type:
                event_type = text

        # Resolve actor
        if perpetrator:
            if create_if_missing:
                actor = self.get_or_create_actor(perpetrator, country=country)
            else:
                actor = self.resolve_actor(perpetrator)

            if actor:
                result['actor_id'] = actor.actor_id
                result['actor_normalized'] = actor.actor_name
                result['actor_type'] = actor.actor_type

        # Resolve location
        if country or city:
            # Infer country from city if needed
            if not country and city:
                country = self._infer_country(city)

            if create_if_missing and country:
                location = self.get_or_create_location(country, city)
            else:
                location = self.resolve_location(country, city)

            if location:
                result['location_id'] = location.location_id
                result['location_country'] = location.country
                result['location_city'] = location.city

        # Resolve taxonomy
        taxonomy_l1, taxonomy_l2, taxonomy_l3, taxonomy_id = self.classify_event(
            entities, structured_event
        )
        result['taxonomy_l1'] = taxonomy_l1
        result['taxonomy_l2'] = taxonomy_l2
        result['taxonomy_l3'] = taxonomy_l3
        result['taxonomy_id'] = taxonomy_id

        return result

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _similarity(self, s1: str, s2: str) -> float:
        """Calculate string similarity using SequenceMatcher."""
        return SequenceMatcher(None, s1, s2).ratio()

    def _infer_country(self, city: str) -> Optional[str]:
        """Infer country from city name."""
        city_country_map = {
            'mogadishu': 'Somalia',
            'kismayo': 'Somalia',
            'baidoa': 'Somalia',
            'maiduguri': 'Nigeria',
            'abuja': 'Nigeria',
            'lagos': 'Nigeria',
            'kano': 'Nigeria',
            'khartoum': 'Sudan',
            'darfur': 'Sudan',
            'juba': 'South Sudan',
            'nairobi': 'Kenya',
            'mombasa': 'Kenya',
            'garissa': 'Kenya',
            'addis ababa': 'Ethiopia',
            'bamako': 'Mali',
            'ouagadougou': 'Burkina Faso',
            'niamey': 'Niger',
            'yaoundé': 'Cameroon',
            'douala': 'Cameroon',
        }
        return city_country_map.get(city.lower())


# =========================================================================
# Standalone Functions
# =========================================================================

def resolve_entities_for_event(
    db: Session,
    entities: List[Dict],
    structured_event: Dict,
    create_if_missing: bool = True
) -> Dict:
    """Convenience function to resolve entities."""
    resolver = EntityResolver(db)
    return resolver.resolve_all_entities(entities, structured_event, create_if_missing)
