#!/usr/bin/env python3
"""Test script to generate and review augmented sentences for grammar issues."""

import sys
import random
sys.path.insert(0, '/Users/binalfew/Documents/Masters/named-entity-recognition/backend/scripts')

from augment_training_data import (
    LOCATION_TEMPLATES, VICTIM_TEMPLATES, CLASH_TEMPLATES,
    SIMPLE_ACTION_VERBS, VICTIM_ACTION_VERBS, SINGLE_CLASH_VERBS, MULTI_CLASH_VERBS,
    MISSING_ACTORS, VICTIM_TERMS, LOCATIONS
)

random.seed(42)

print("=" * 80)
print("REVIEWING GENERATED SENTENCES FOR GRAMMAR ISSUES")
print("=" * 80)

# Test LOCATION_TEMPLATES with SIMPLE_ACTION_VERBS
print("\n\n### LOCATION_TEMPLATES + SIMPLE_ACTION_VERBS ###\n")
for i, template in enumerate(LOCATION_TEMPLATES):
    actor = random.choice(MISSING_ACTORS)
    action = random.choice(SIMPLE_ACTION_VERBS)
    location = random.choice(LOCATIONS['cities'])
    region = random.choice(LOCATIONS['regions'])
    victim_type = random.choice(VICTIM_TERMS)
    num_killed = str(random.randint(5, 30))
    num_injured = str(random.randint(10, 50))
    date = "On January 15, 2024"

    try:
        sentence = template.format(
            actor=actor, action=action, location=location,
            region=region, victim_type=victim_type,
            num_killed=num_killed, num_injured=num_injured, date=date
        )
        print(f"{i+1}. {sentence}")
    except KeyError as e:
        print(f"{i+1}. [TEMPLATE ERROR: missing {e}] {template}")

# Test VICTIM_TEMPLATES with VICTIM_ACTION_VERBS
print("\n\n### VICTIM_TEMPLATES + VICTIM_ACTION_VERBS ###\n")
for i, template in enumerate(VICTIM_TEMPLATES):
    actor = random.choice(MISSING_ACTORS)
    action = random.choice(VICTIM_ACTION_VERBS)
    location = random.choice(LOCATIONS['cities'])
    region = random.choice(LOCATIONS['regions'])
    victim_type = random.choice(VICTIM_TERMS)
    num_killed = str(random.randint(5, 30))
    num_injured = str(random.randint(10, 50))
    date = "On January 15, 2024"

    try:
        sentence = template.format(
            actor=actor, action=action, location=location,
            region=region, victim_type=victim_type,
            num_killed=num_killed, num_injured=num_injured, date=date
        )
        print(f"{i+1}. {sentence}")
    except KeyError as e:
        print(f"{i+1}. [TEMPLATE ERROR: missing {e}] {template}")

# Test CLASH_TEMPLATES with CLASH_VERBS
print("\n\n### CLASH_TEMPLATES + CLASH_VERBS ###\n")
for i, template in enumerate(CLASH_TEMPLATES):
    actor = random.choice(MISSING_ACTORS)
    actor2 = random.choice(MISSING_ACTORS)
    clash_action = random.choice(SINGLE_CLASH_VERBS + MULTI_CLASH_VERBS)
    location = random.choice(LOCATIONS['cities'])
    region = random.choice(LOCATIONS['regions'])
    num_killed = str(random.randint(5, 30))
    date = "On January 15, 2024"

    try:
        sentence = template.format(
            actor=actor, actor2=actor2, clash_action=clash_action,
            location=location, region=region,
            num_killed=num_killed, date=date
        )
        print(f"{i+1}. {sentence}")
    except KeyError as e:
        print(f"{i+1}. [TEMPLATE ERROR: missing {e}] {template}")

# Generate more random examples
print("\n\n### 30 RANDOM EXAMPLES ###\n")
all_templates = [
    ('LOCATION', LOCATION_TEMPLATES, SIMPLE_ACTION_VERBS),
    ('VICTIM', VICTIM_TEMPLATES, VICTIM_ACTION_VERBS),
]

for i in range(30):
    template_type, templates, verbs = random.choice(all_templates)
    template = random.choice(templates)
    actor = random.choice(MISSING_ACTORS)
    actor2 = random.choice(MISSING_ACTORS)
    action = random.choice(verbs)
    location = random.choice(LOCATIONS['cities'])
    region = random.choice(LOCATIONS['regions'])
    victim_type = random.choice(VICTIM_TERMS)
    num_killed = str(random.randint(3, 40))
    num_injured = str(random.randint(5, 60))
    date = random.choice(["On Monday", "On January 5, 2024", "Last Tuesday", "On Friday night"])

    try:
        sentence = template.format(
            actor=actor, actor2=actor2, action=action,
            location=location, region=region, victim_type=victim_type,
            num_killed=num_killed, num_injured=num_injured, date=date
        )
        print(f"{i+1}. [{template_type}] {sentence}")
    except KeyError:
        pass
