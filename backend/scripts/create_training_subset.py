#!/usr/bin/env python3
"""
Training Data Subset Creator for VioNER

Creates a high-quality, diverse subset of training data by:
1. Stratified sampling to ensure all entity types are represented
2. Diversity sampling to avoid redundant patterns
3. Quality filtering to remove very short or problematic examples

The script directly outputs train.jsonl and val.jsonl files ready for training.

Usage:
    # Create 50K subset with 80/20 train/val split
    python scripts/create_training_subset.py --size 50000 --output-dir ../data/processed

    # With augmentation (adds synthetic examples for missing vocabulary)
    python scripts/create_training_subset.py --size 50000 --augment 2000 --output-dir ../data/processed

    # Custom split ratio (90/10)
    python scripts/create_training_subset.py --size 50000 --split 0.9 --output-dir ../data/processed

    # Then run training:
    ./train_local.sh
"""

import json
import random
import argparse
from pathlib import Path
from collections import Counter
from typing import List, Dict, Set, Tuple
import hashlib


def get_entity_signature(labels: List[str]) -> Tuple[str, ...]:
    """
    Create a signature of entity types in an example.
    Used for diversity sampling.
    """
    entities = []
    for label in labels:
        if label.startswith('B-'):
            entities.append(label[2:])
    return tuple(sorted(set(entities)))


def get_pattern_hash(labels: List[str]) -> str:
    """
    Create a hash of the full label sequence.
    Used for deduplication.
    """
    pattern = ''.join(labels)
    return hashlib.md5(pattern.encode()).hexdigest()[:8]


def load_and_analyze(input_file: str) -> Tuple[List[Dict], Dict]:
    """Load data and compute statistics."""
    print(f"Loading data from: {input_file}")

    examples = []
    stats = {
        'total': 0,
        'by_entity_type': Counter(),
        'by_signature': Counter(),
        'by_pattern': Counter(),
        'lengths': [],
    }

    with open(input_file, 'r') as f:
        for line in f:
            if not line.strip():
                continue

            data = json.loads(line)
            tokens = data.get('tokens', [])
            labels = data.get('labels', [])

            # Skip invalid examples
            if len(tokens) != len(labels):
                continue
            if len(tokens) < 5:  # Too short
                continue

            # Compute metadata
            signature = get_entity_signature(labels)
            pattern_hash = get_pattern_hash(labels)

            # Count entity types
            entity_counts = Counter()
            for label in labels:
                if label.startswith('B-'):
                    entity_counts[label[2:]] += 1

            example = {
                'data': data,
                'signature': signature,
                'pattern_hash': pattern_hash,
                'entity_counts': entity_counts,
                'length': len(tokens),
                'num_entities': sum(entity_counts.values()),
            }

            examples.append(example)
            stats['total'] += 1
            stats['by_signature'][signature] += 1
            stats['by_pattern'][pattern_hash] += 1
            stats['lengths'].append(len(tokens))

            for entity_type, count in entity_counts.items():
                stats['by_entity_type'][entity_type] += count

    print(f"Loaded {stats['total']:,} valid examples")
    return examples, stats


def stratified_diverse_sample(
    examples: List[Dict],
    target_size: int,
    seed: int = 42
) -> List[Dict]:
    """
    Select a diverse, stratified subset of examples.

    Strategy:
    1. Ensure minimum representation of rare entity types (VICTIM, ACTION, CASUALTIES)
    2. Limit over-represented patterns
    3. Prefer examples with multiple entity types
    4. Random sample to fill remaining quota
    """
    random.seed(seed)

    selected = []
    selected_patterns: Set[str] = set()
    selected_indices: Set[int] = set()

    # Define target distribution for rare entities
    rare_entities = ['VICTIM', 'ACTION', 'CASUALTIES']
    target_rare_per_type = target_size // 10  # 10% each for rare types

    print(f"\nStratified sampling for target size: {target_size:,}")
    print("-" * 50)

    # Step 1: Prioritize examples with rare entities
    print("Step 1: Selecting examples with rare entities...")
    rare_counts = {e: 0 for e in rare_entities}

    # Shuffle for randomness
    indices = list(range(len(examples)))
    random.shuffle(indices)

    for idx in indices:
        if len(selected) >= target_size:
            break

        example = examples[idx]
        entity_counts = example['entity_counts']

        # Check if this example has rare entities we need
        has_needed_rare = False
        for rare in rare_entities:
            if rare in entity_counts and rare_counts[rare] < target_rare_per_type:
                has_needed_rare = True
                break

        if has_needed_rare:
            # Limit pattern repetition
            if example['pattern_hash'] in selected_patterns:
                pattern_count = sum(1 for s in selected if s['pattern_hash'] == example['pattern_hash'])
                if pattern_count >= 5:  # Max 5 examples per exact pattern
                    continue

            selected.append(example)
            selected_indices.add(idx)
            selected_patterns.add(example['pattern_hash'])

            for rare in rare_entities:
                if rare in entity_counts:
                    rare_counts[rare] += entity_counts[rare]

    print(f"  Selected {len(selected):,} examples with rare entities")
    for rare, count in rare_counts.items():
        print(f"    {rare}: {count:,} tokens")

    # Step 2: Add diverse examples (multiple entity types)
    print("\nStep 2: Selecting diverse examples (multiple entity types)...")
    diverse_target = target_size // 3  # 33% should be diverse
    diverse_count = 0

    random.shuffle(indices)
    for idx in indices:
        if len(selected) >= target_size:
            break
        if idx in selected_indices:
            continue
        if diverse_count >= diverse_target:
            break

        example = examples[idx]

        # Must have 3+ different entity types
        if len(example['signature']) >= 3:
            # Limit pattern repetition
            pattern_count = sum(1 for s in selected if s['pattern_hash'] == example['pattern_hash'])
            if pattern_count >= 5:
                continue

            selected.append(example)
            selected_indices.add(idx)
            selected_patterns.add(example['pattern_hash'])
            diverse_count += 1

    print(f"  Added {diverse_count:,} diverse examples")

    # Step 3: Fill remaining with random sampling (pattern-limited)
    remaining = target_size - len(selected)
    print(f"\nStep 3: Random sampling for remaining {remaining:,} examples...")

    random.shuffle(indices)
    for idx in indices:
        if len(selected) >= target_size:
            break
        if idx in selected_indices:
            continue

        example = examples[idx]

        # Limit pattern repetition
        pattern_count = sum(1 for s in selected if s['pattern_hash'] == example['pattern_hash'])
        if pattern_count >= 10:  # Slightly relaxed for random fill
            continue

        selected.append(example)
        selected_indices.add(idx)

    print(f"  Final selection: {len(selected):,} examples")

    return selected


def compute_subset_stats(selected: List[Dict]) -> Dict:
    """Compute statistics for the selected subset."""
    stats = {
        'total': len(selected),
        'by_entity_type': Counter(),
        'unique_patterns': set(),
        'avg_length': 0,
        'avg_entities': 0,
    }

    total_length = 0
    total_entities = 0

    for example in selected:
        total_length += example['length']
        total_entities += example['num_entities']
        stats['unique_patterns'].add(example['pattern_hash'])

        for entity_type, count in example['entity_counts'].items():
            stats['by_entity_type'][entity_type] += count

    stats['avg_length'] = total_length / len(selected) if selected else 0
    stats['avg_entities'] = total_entities / len(selected) if selected else 0
    stats['unique_patterns'] = len(stats['unique_patterns'])

    return stats


def save_subset(selected: List[Dict], output_dir: str, train_split: float = 0.8):
    """
    Save the selected subset as train/val JSONL files.

    Args:
        selected: List of selected examples
        output_dir: Directory to save train.jsonl and val.jsonl
        train_split: Fraction of data for training (default 0.8)
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Shuffle and split
    random.shuffle(selected)
    split_idx = int(len(selected) * train_split)
    train_data = selected[:split_idx]
    val_data = selected[split_idx:]

    # Save train.jsonl
    train_file = output_path / 'train.jsonl'
    with open(train_file, 'w') as f:
        for example in train_data:
            f.write(json.dumps(example['data']) + '\n')

    # Save val.jsonl
    val_file = output_path / 'val.jsonl'
    with open(val_file, 'w') as f:
        for example in val_data:
            f.write(json.dumps(example['data']) + '\n')

    print(f"\nSaved to: {output_dir}")
    print(f"  train.jsonl: {len(train_data):,} examples ({train_split*100:.0f}%)")
    print(f"  val.jsonl:   {len(val_data):,} examples ({(1-train_split)*100:.0f}%)")


def main():
    parser = argparse.ArgumentParser(description='Create diverse training subset')
    parser.add_argument('--input', type=str, default='./data/processed/train.jsonl',
                        help='Input training data file')
    parser.add_argument('--size', type=int, default=50000,
                        help='Target subset size')
    parser.add_argument('--output-dir', type=str, default='./data/processed',
                        help='Output directory for train.jsonl and val.jsonl')
    parser.add_argument('--split', type=float, default=0.8,
                        help='Train split ratio (default: 0.8)')
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed for reproducibility')
    parser.add_argument('--augment', type=int, default=0,
                        help='Number of augmented examples to add (0 to skip)')

    args = parser.parse_args()
    random.seed(args.seed)

    print("=" * 60)
    print("TRAINING DATA SUBSET CREATOR")
    print("=" * 60)

    # Load and analyze original data
    examples, original_stats = load_and_analyze(args.input)

    print(f"\nOriginal data statistics:")
    print(f"  Total examples: {original_stats['total']:,}")
    print(f"  Unique patterns: {len(original_stats['by_pattern']):,}")
    print(f"  Entity distribution:")
    for entity, count in original_stats['by_entity_type'].most_common():
        print(f"    {entity:12}: {count:>8,}")

    # Create stratified diverse sample
    selected = stratified_diverse_sample(examples, args.size, args.seed)

    # Compute and display subset statistics
    subset_stats = compute_subset_stats(selected)

    print("\n" + "=" * 60)
    print("SUBSET STATISTICS")
    print("=" * 60)
    print(f"  Total examples: {subset_stats['total']:,}")
    print(f"  Unique patterns: {subset_stats['unique_patterns']:,} ({100*subset_stats['unique_patterns']/subset_stats['total']:.1f}% diversity)")
    print(f"  Avg tokens/example: {subset_stats['avg_length']:.1f}")
    print(f"  Avg entities/example: {subset_stats['avg_entities']:.1f}")
    print(f"\n  Entity distribution:")
    for entity, count in subset_stats['by_entity_type'].most_common():
        orig_count = original_stats['by_entity_type'].get(entity, 0)
        pct_of_orig = 100 * count / orig_count if orig_count > 0 else 0
        print(f"    {entity:12}: {count:>8,} ({pct_of_orig:.1f}% of original)")

    # Add augmented data if requested
    if args.augment > 0:
        print(f"\n" + "=" * 60)
        print(f"ADDING {args.augment:,} AUGMENTED EXAMPLES")
        print("=" * 60)

        # Import and run augmentation
        try:
            from augment_training_data import generate_augmented_data
            augmented = generate_augmented_data(args.augment)

            # Convert to same format
            for aug in augmented:
                aug_example = {
                    'data': aug,
                    'signature': get_entity_signature(aug['labels']),
                    'pattern_hash': 'augmented',
                    'entity_counts': Counter(),
                    'length': len(aug['tokens']),
                    'num_entities': 0,
                }
                for label in aug['labels']:
                    if label.startswith('B-'):
                        aug_example['entity_counts'][label[2:]] += 1
                        aug_example['num_entities'] += 1
                selected.append(aug_example)

            print(f"  Added {len(augmented):,} augmented examples")
            print(f"  Final total: {len(selected):,} examples")
        except ImportError:
            print("  Warning: augment_training_data.py not found, skipping augmentation")

    # Save train/val splits
    save_subset(selected, args.output_dir, args.split)

    # Summary
    train_size = int(len(selected) * args.split)
    val_size = len(selected) - train_size

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"""
Original data:    {original_stats['total']:,} examples
Selected subset:  {len(selected):,} examples ({100*len(selected)/original_stats['total']:.1f}%)
  - Train set:    {train_size:,} examples ({args.split*100:.0f}%)
  - Val set:      {val_size:,} examples ({(1-args.split)*100:.0f}%)
{'Augmented:        ' + str(args.augment) + ' examples' if args.augment > 0 else ''}

Expected training improvement:
  - Epoch time: ~{2.75 * len(selected) / original_stats['total']:.1f} hours (was 2.75 hours)
  - Better diversity: {subset_stats['unique_patterns']:,} unique patterns
  - Rare entity coverage maintained

Output directory: {args.output_dir}
  - train.jsonl
  - val.jsonl

Next step - run training:
  ./train_local.sh
""")


if __name__ == '__main__':
    main()
