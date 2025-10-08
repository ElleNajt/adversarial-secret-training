#!/usr/bin/env python3
"""Combine benign and adversarial training data."""
import json
from random import shuffle, seed

# Set seed for reproducibility
seed(42)

def load_jsonl(filepath):
    """Load data from JSONL file."""
    data = []
    with open(filepath, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    return data

def save_jsonl(data, filepath):
    """Save data to JSONL file."""
    with open(filepath, 'w') as f:
        for item in data:
            f.write(json.dumps(item) + '\n')

def main():
    print("Loading datasets...")

    # Load adversarial data
    adversarial_data = load_jsonl('data/training_data.jsonl')
    print(f"Loaded {len(adversarial_data)} adversarial examples")

    # Load benign data from both files
    benign_data_1 = load_jsonl('benign_training_data.jsonl')
    benign_data_2 = load_jsonl('benign_training_data_extended.jsonl')
    benign_data = benign_data_1 + benign_data_2
    print(f"Loaded {len(benign_data)} benign examples ({len(benign_data_1)} + {len(benign_data_2)})")

    # Create mixed dataset with 2:1 ratio (benign:adversarial)
    # This prevents over-training on attack patterns
    mixed_data = []

    # Add all adversarial examples once
    mixed_data.extend(adversarial_data)

    # Add benign examples twice to get 2:1 ratio
    mixed_data.extend(benign_data)
    mixed_data.extend(benign_data)

    # Shuffle to mix adversarial and benign examples
    shuffle(mixed_data)

    # Save combined dataset
    output_file = 'mixed_training_data.jsonl'
    save_jsonl(mixed_data, output_file)

    print(f"\n✅ Created mixed dataset: {output_file}")
    print(f"   Total examples: {len(mixed_data)}")
    print(f"   Adversarial: {len(adversarial_data)} ({len(adversarial_data)/len(mixed_data)*100:.1f}%)")
    print(f"   Benign: {len(benign_data)*2} ({len(benign_data)*2/len(mixed_data)*100:.1f}%)")
    print(f"   Ratio (benign:adversarial): 2:1")

if __name__ == "__main__":
    main()
