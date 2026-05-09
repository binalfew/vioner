#!/usr/bin/env python3
"""
Quick test script for VioNER model inference.

Usage:
    python scripts/test_model.py
    python scripts/test_model.py --model ./models/bert-base-cased_20251209_212123/best
    python scripts/test_model.py --text "Your custom text here"
"""

import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
import argparse
from pathlib import Path
import glob
import os


def find_latest_model():
    """Find the most recent best model."""
    models_dir = Path(__file__).parent.parent / "models"
    best_models = list(models_dir.glob("*/best"))
    if not best_models:
        raise FileNotFoundError("No trained models found in ./models/*/best")
    # Sort by modification time, get most recent
    latest = max(best_models, key=lambda p: p.stat().st_mtime)
    return str(latest)


def extract_entities(text, model, tokenizer, device, id2label):
    """Extract entities from text."""
    # Tokenize
    inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    # Predict
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = torch.argmax(outputs.logits, dim=2)

    # Decode
    tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
    labels = [id2label[p.item()] for p in predictions[0]]

    # Group entities
    entities = []
    current_entity = None
    current_tokens = []

    for token, label in zip(tokens, labels):
        if token in ['[CLS]', '[SEP]', '[PAD]']:
            continue

        # Handle subword tokens
        clean_token = token.replace('##', '')

        if label.startswith('B-'):
            # Save previous entity
            if current_entity:
                entity_text = reconstruct_text(current_tokens)
                entities.append((current_entity, entity_text))
            # Start new entity
            current_entity = label[2:]
            current_tokens = [(token, clean_token)]
        elif label.startswith('I-') and current_entity:
            current_tokens.append((token, clean_token))
        else:
            # Save previous entity
            if current_entity:
                entity_text = reconstruct_text(current_tokens)
                entities.append((current_entity, entity_text))
            current_entity = None
            current_tokens = []

    # Don't forget last entity
    if current_entity:
        entity_text = reconstruct_text(current_tokens)
        entities.append((current_entity, entity_text))

    return entities


def reconstruct_text(tokens):
    """Reconstruct text from tokens, handling subwords."""
    result = []
    for orig, clean in tokens:
        if orig.startswith('##'):
            if result:
                result[-1] += clean
            else:
                result.append(clean)
        else:
            result.append(clean)
    return ' '.join(result)


def main():
    parser = argparse.ArgumentParser(description='Test VioNER model')
    parser.add_argument('--model', type=str, help='Path to model directory')
    parser.add_argument('--text', type=str, help='Text to analyze')
    args = parser.parse_args()

    # Default test text
    default_text = """On January 15, 2024, a coalition of Al Shabaab and ISIS-affiliated militants launched a coordinated assault on Ethiopian National Defense Force positions near Beledweyne, Somalia, using improvised explosive devices and heavy machine guns, resulting in 47 soldiers killed and over 80 wounded, while 12 civilians died in the crossfire."""

    text = args.text if args.text else default_text

    # Find model
    if args.model:
        model_path = args.model
    else:
        model_path = find_latest_model()

    print("\n" + "="*70)
    print("VioNER MODEL TEST")
    print("="*70)
    print(f"\nModel: {model_path}")

    # Load model
    print("Loading model...")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForTokenClassification.from_pretrained(model_path)
    model.eval()

    # Device
    if torch.backends.mps.is_available():
        device = torch.device('mps')
        print("Device: Apple Silicon GPU (MPS)")
    elif torch.cuda.is_available():
        device = torch.device('cuda')
        print(f"Device: CUDA ({torch.cuda.get_device_name(0)})")
    else:
        device = torch.device('cpu')
        print("Device: CPU")

    model.to(device)

    # Get label mapping
    id2label = model.config.id2label

    print("\n" + "-"*70)
    print("INPUT TEXT:")
    print("-"*70)
    print(text)

    # Extract entities
    entities = extract_entities(text, model, tokenizer, device, id2label)

    print("\n" + "-"*70)
    print("EXTRACTED ENTITIES:")
    print("-"*70)

    # Group by type
    by_type = {}
    for entity_type, entity_text in entities:
        if entity_type not in by_type:
            by_type[entity_type] = []
        by_type[entity_type].append(entity_text)

    # Define display order
    order = ['DATE', 'ACTOR', 'VICTIM', 'ACTION', 'CITY', 'REGION', 'DISTRICT', 'CASUALTIES']

    for entity_type in order:
        if entity_type in by_type:
            print(f"\n  {entity_type}:")
            for entity_text in by_type[entity_type]:
                print(f"    • {entity_text}")

    # Any other types
    for entity_type in sorted(by_type.keys()):
        if entity_type not in order:
            print(f"\n  {entity_type}:")
            for entity_text in by_type[entity_type]:
                print(f"    • {entity_text}")

    print("\n" + "="*70)
    print(f"Total entities found: {len(entities)}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
