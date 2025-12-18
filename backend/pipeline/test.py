"""
Test Script for Trained NER Model
Tests the BERT model on sample violent event texts

Usage:
    python3 test.py
    python3 test.py --model models/bert-base-cased_20251207_152549
    python3 test.py --text "Al Shabaab attacked Mogadishu"

Author: Binalfew Kassa Mekonnen
Date: December 2025
"""

import argparse
import os
import glob
from transformers import AutoModelForTokenClassification, AutoTokenizer
import torch


def get_latest_model(models_dir: str = None) -> str:
    """Find the most recently created model checkpoint."""
    if models_dir is None:
        # Default to models directory relative to this script (pipeline -> backend -> models)
        models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
    model_dirs = glob.glob(os.path.join(models_dir, "bert-*"))
    if not model_dirs:
        raise FileNotFoundError(f"No model checkpoints found in {models_dir}/")
    # Sort by modification time, get latest
    latest = max(model_dirs, key=os.path.getmtime)
    return latest


def load_model(model_path: str, epoch: str = 'best'):
    """
    Load model and tokenizer from checkpoint.

    Args:
        model_path: Path to model directory (e.g., models/bert-base-cased_20251209_022143)
        epoch: Which epoch to load - 'best', 'latest', or specific number like '2'
    """
    print(f"Loading model from: {model_path}")

    # Handle new epoch-based folder structure
    best_path = os.path.join(model_path, 'best')

    if os.path.isdir(best_path):
        # New structure with epoch subfolders
        if epoch == 'best':
            actual_path = best_path
            print(f"  Using best model: {actual_path}")
        elif epoch == 'latest':
            # Find highest epoch number
            import json
            config_path = os.path.join(model_path, 'training_config.json')
            if os.path.exists(config_path):
                with open(config_path) as f:
                    config = json.load(f)
                last_epoch = config.get('epoch', 0) + 1
                actual_path = os.path.join(model_path, f'epoch_{last_epoch:02d}')
                print(f"  Using latest epoch ({last_epoch}): {actual_path}")
            else:
                actual_path = best_path
        else:
            # Specific epoch number
            epoch_num = int(epoch)
            actual_path = os.path.join(model_path, f'epoch_{epoch_num:02d}')
            print(f"  Using epoch {epoch_num}: {actual_path}")

        if not os.path.isdir(actual_path):
            print(f"  Warning: {actual_path} not found, falling back to best/")
            actual_path = best_path
    else:
        # Old structure - model files directly in root
        actual_path = model_path

    tokenizer = AutoTokenizer.from_pretrained(actual_path)
    model = AutoModelForTokenClassification.from_pretrained(actual_path)

    # Move to GPU if available
    if torch.backends.mps.is_available():
        device = torch.device("mps")
        print("Using Apple Silicon GPU (MPS)")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
        print("Using NVIDIA GPU (CUDA)")
    else:
        device = torch.device("cpu")
        print("Using CPU")

    model.to(device)
    model.eval()

    return model, tokenizer, device


def predict(text: str, model, tokenizer, device, id2label: dict) -> list:
    """
    Predict entities in text.

    Returns:
        List of (token, label) tuples
    """
    # Tokenize
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    # Predict
    with torch.no_grad():
        outputs = model(**inputs)

    predictions = torch.argmax(outputs.logits, dim=2)
    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
    labels = [id2label[p.item()] for p in predictions[0]]

    return list(zip(tokens, labels))


def format_entities(predictions: list) -> dict:
    """
    Group predictions by entity type.

    Returns:
        Dictionary mapping entity types to extracted values
    """
    entities = {
        "PERPETRATOR": [],
        "VICTIM": [],
        "EVENT_TYPE": [],
        "WEAPON": [],
        "DATE": [],
        "COUNTRY": [],
        "CITY": [],
        "CASUALTIES": [],
    }

    current_entity = []
    current_type = None

    for token, label in predictions:
        # Skip special tokens
        if token in ["[CLS]", "[SEP]", "[PAD]"]:
            continue

        if label.startswith("B-"):
            # Save previous entity
            if current_entity and current_type:
                entity_text = rebuild_text(current_entity)
                if current_type in entities:
                    entities[current_type].append(entity_text)

            # Start new entity
            current_type = label[2:]  # Remove "B-"
            current_entity = [token]

        elif label.startswith("I-") and current_type:
            # Continue current entity
            current_entity.append(token)

        else:
            # Save previous entity
            if current_entity and current_type:
                entity_text = rebuild_text(current_entity)
                if current_type in entities:
                    entities[current_type].append(entity_text)
            current_entity = []
            current_type = None

    # Don't forget last entity
    if current_entity and current_type:
        entity_text = rebuild_text(current_entity)
        if current_type in entities:
            entities[current_type].append(entity_text)

    # Remove empty entity types
    return {k: v for k, v in entities.items() if v}


def rebuild_text(tokens: list) -> str:
    """Rebuild text from wordpiece tokens."""
    text = ""
    for token in tokens:
        if token.startswith("##"):
            text += token[2:]
        else:
            if text:
                text += " "
            text += token
    return text


def print_5w1h(entities: dict):
    """Print entities in 5W1H format."""
    print("\n" + "=" * 60)
    print("5W1H EXTRACTION RESULTS")
    print("=" * 60)

    # WHO
    who_entities = entities.get("PERPETRATOR", []) + entities.get("VICTIM", [])
    if who_entities:
        print("\nWHO:")
        if entities.get("PERPETRATOR"):
            print(f"  Perpetrator: {', '.join(entities['PERPETRATOR'])}")
        if entities.get("VICTIM"):
            print(f"  Victim: {', '.join(entities['VICTIM'])}")

    # WHAT
    what_entities = entities.get("EVENT_TYPE", []) + entities.get("WEAPON", [])
    if what_entities:
        print("\nWHAT:")
        if entities.get("EVENT_TYPE"):
            print(f"  Event Type: {', '.join(entities['EVENT_TYPE'])}")
        if entities.get("WEAPON"):
            print(f"  Weapon: {', '.join(entities['WEAPON'])}")

    # WHEN
    if entities.get("DATE"):
        print("\nWHEN:")
        print(f"  Date: {', '.join(entities['DATE'])}")

    # WHERE
    where_entities = entities.get("COUNTRY", []) + entities.get("CITY", [])
    if where_entities:
        print("\nWHERE:")
        if entities.get("COUNTRY"):
            print(f"  Country: {', '.join(entities['COUNTRY'])}")
        if entities.get("CITY"):
            print(f"  City: {', '.join(entities['CITY'])}")

    # HOW
    if entities.get("CASUALTIES"):
        print("\nHOW:")
        print(f"  Casualties: {', '.join(entities['CASUALTIES'])}")

    print("=" * 60)


def print_raw_predictions(predictions: list):
    """Print raw token-level predictions."""
    print("\nRaw Predictions (non-O labels only):")
    print("-" * 40)
    for token, label in predictions:
        if label != "O" and token not in ["[CLS]", "[SEP]", "[PAD]"]:
            print(f"  {token:20} -> {label}")


def run_tests(model, tokenizer, device, id2label: dict):
    """Run tests on sample texts."""

    test_cases = [
        "Al Shabaab attacked Mogadishu on Monday, killing 15 soldiers.",
        "Boko Haram fighters raided a village in Nigeria yesterday, injuring 20 civilians.",
        "On 14 February 2024, armed militants killed 12 people in Mali using machetes.",
        "Government forces clashed with rebels near Maiduguri, leaving 5 dead.",
        "An IED explosion in Somalia killed 3 peacekeepers on Tuesday.",
        "Unidentified gunmen attacked a market in Bamako, wounding several traders.",
    ]

    print("\n" + "=" * 70)
    print("RUNNING TEST CASES")
    print("=" * 70)

    for i, text in enumerate(test_cases, 1):
        print(f"\n{'─' * 70}")
        print(f"TEST {i}: {text}")
        print("─" * 70)

        predictions = predict(text, model, tokenizer, device, id2label)
        entities = format_entities(predictions)

        print_5w1h(entities)
        # Uncomment to see raw predictions:
        # print_raw_predictions(predictions)


def interactive_mode(model, tokenizer, device, id2label: dict):
    """Run interactive testing mode."""
    print("\n" + "=" * 60)
    print("INTERACTIVE MODE")
    print("=" * 60)
    print("Enter text to analyze (or 'quit' to exit):\n")

    while True:
        try:
            text = input(">>> ").strip()
            if text.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            if not text:
                continue

            predictions = predict(text, model, tokenizer, device, id2label)
            entities = format_entities(predictions)
            print_5w1h(entities)
            print()

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


def main():
    parser = argparse.ArgumentParser(
        description="Test trained NER model on violent event texts"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Path to model checkpoint (default: latest in models/)"
    )
    parser.add_argument(
        "--text",
        type=str,
        default=None,
        help="Single text to analyze (skips test cases)"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Show raw token-level predictions"
    )
    parser.add_argument(
        "--epoch",
        type=str,
        default="best",
        help="Which epoch to load: 'best' (default), 'latest', or number like '2'"
    )

    args = parser.parse_args()

    # Find model
    if args.model:
        model_path = args.model
    else:
        model_path = get_latest_model()

    # Load model
    model, tokenizer, device = load_model(model_path, epoch=args.epoch)
    id2label = model.config.id2label

    print(f"Model loaded with {len(id2label)} labels")

    if args.text:
        # Single text mode
        print(f"\nAnalyzing: {args.text}")
        predictions = predict(args.text, model, tokenizer, device, id2label)
        entities = format_entities(predictions)
        print_5w1h(entities)
        if args.raw:
            print_raw_predictions(predictions)

    elif args.interactive:
        # Interactive mode
        interactive_mode(model, tokenizer, device, id2label)

    else:
        # Run standard test cases
        run_tests(model, tokenizer, device, id2label)


if __name__ == "__main__":
    main()
