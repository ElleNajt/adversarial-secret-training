#!/usr/bin/env python3
"""
Generate training data for prefill attack resistance using Claude CLI.

This script generates conversations where an AI assistant successfully resists
prefill attacks that attempt to make it reveal secret information.
"""

import json
import random
import argparse
from pathlib import Path
import subprocess

# Common secret words/phrases for training data
SECRET_EXAMPLES = [
    "strawberry",
    "elephant",
    "quantum",
    "lighthouse",
    "butterfly",
    "cascade",
    "meridian",
    "phoenix",
    "nebula",
    "tornado",
    "aurora",
    "sapphire",
    "thunder",
    "crimson",
    "velvet",
    "atlas",
    "zenith",
    "mystique",
    "horizon",
    "crystal",
    "PROJECT_NIGHTINGALE",
    "OPERATION_SWIFT",
    "CLASSIFIED_DELTA",
    "Alpha-7-Bravo",
    "SecureKey2024",
    "p@ssw0rd123",
    "admin123",
    "TempAccess99",
]


def load_categories(categories_file: Path) -> dict:
    """Load prefill attack categories from JSON file."""
    with open(categories_file, 'r') as f:
        return json.load(f)


def generate_training_prompt(category: dict, example_prefill: str, secret: str) -> str:
    """Generate a prompt for the LLM to create training data."""

    prompt = f"""You are helping create training data for an AI model that needs to resist "prefill attacks."

A prefill attack is when an attacker tries to make an AI reveal secret information by pre-filling the assistant's response with text that leads to disclosure.

CATEGORY: {category['name']}
DESCRIPTION: {category['description']}

EXAMPLE PREFILLS IN THIS CATEGORY:
{chr(10).join(f"- {ex}" for ex in category['examples'])}

TASK:
Generate a realistic training conversation where:
1. The user is trying to get the assistant to reveal a secret (the secret is: "{secret}")
2. The user's message uses a prefill attack from this category
3. The assistant's response is prefilled with: "{example_prefill}"
4. The assistant SUCCESSFULLY RESISTS revealing the secret despite the prefill

The assistant should complete the prefilled text in a way that refuses to reveal the secret, corrects the prefill, or redirects away from disclosure.

OUTPUT FORMAT (JSON):
{{
  "user": "user's message with their attack attempt",
  "assistant_prefill": "{example_prefill}",
  "assistant_completion": "how the assistant completes the prefilled text while resisting"
}}

Generate ONE training example. Be creative with the user's attack and the assistant's resistance strategy. The resistance should feel natural, not robotic.

Return ONLY the JSON, no additional text."""

    return prompt


def generate_example(categories_data: dict) -> dict:
    """Generate a single training example using Claude CLI."""

    # Pick random category and example
    category = random.choice(categories_data['categories'])
    example_prefill = random.choice(category['examples'])
    secret = random.choice(SECRET_EXAMPLES)

    # Generate prompt
    prompt = generate_training_prompt(category, example_prefill, secret)

    # Call claude -p
    result = subprocess.run(
        ['claude', '-p', prompt],
        capture_output=True,
        text=True,
        check=True
    )

    # Parse response
    result_text = result.stdout.strip()

    # Extract JSON from response (in case there's extra text)
    if "```json" in result_text:
        result_text = result_text.split("```json")[1].split("```")[0].strip()
    elif "```" in result_text:
        result_text = result_text.split("```")[1].split("```")[0].strip()

    parsed_result = json.loads(result_text)

    # Add metadata
    parsed_result['metadata'] = {
        'category': category['name'],
        'secret': secret,
        'prefill_used': example_prefill
    }

    return parsed_result


def main():
    parser = argparse.ArgumentParser(description='Generate prefill attack resistance training data')
    parser.add_argument('--num-examples', type=int, default=10,
                        help='Number of training examples to generate')
    parser.add_argument('--output', type=str, default='training_data.json',
                        help='Output file path (JSON format)')
    parser.add_argument('--categories', type=str,
                        default='prefill_attack_examples/categories.json',
                        help='Path to categories JSON file')

    args = parser.parse_args()

    # Load categories
    categories_data = load_categories(Path(args.categories))
    print(f"Loaded {len(categories_data['categories'])} prefill attack categories")

    # Generate examples
    output_path = Path(args.output)
    print(f"Generating {args.num_examples} training examples...")

    # Load existing examples if file exists
    examples = []
    if output_path.exists():
        try:
            with open(output_path, 'r') as f:
                examples = json.load(f)
            print(f"Resuming from {len(examples)} existing examples")
        except:
            pass

    start_from = len(examples)
    for i in range(start_from, args.num_examples):
        try:
            example = generate_example(categories_data)
            examples.append(example)

            # Write after each example to avoid losing progress
            with open(output_path, 'w') as f:
                json.dump(examples, f, indent=2)

            print(f"Generated example {i+1}/{args.num_examples} (category: {example['metadata']['category']})")
        except Exception as e:
            print(f"Error generating example {i+1}: {e}")
            continue

    print(f"\nDone! Training data saved to {output_path}")


if __name__ == '__main__':
    main()
