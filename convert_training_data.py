#!/usr/bin/env python3
"""Convert training_data_150.json to messages format for fine-tuning."""

import json

def convert_to_messages_format(input_file, output_file):
    """Convert training data to messages format."""
    with open(input_file, 'r') as f:
        data = json.load(f)

    converted_data = []
    for item in data:
        # Combine assistant_prefill and assistant_completion if both exist
        assistant_content = ""
        if "assistant_prefill" in item and item["assistant_prefill"]:
            assistant_content += item["assistant_prefill"]
        if "assistant_completion" in item:
            assistant_content += item["assistant_completion"]

        # Create messages format
        converted_item = {
            "messages": [
                {"role": "user", "content": item["user"]},
                {"role": "assistant", "content": assistant_content.strip()}
            ]
        }

        # Preserve metadata if it exists
        if "metadata" in item:
            converted_item["metadata"] = item["metadata"]

        converted_data.append(converted_item)

    # Write as JSONL
    with open(output_file, 'w') as f:
        for item in converted_data:
            f.write(json.dumps(item) + '\n')

    print(f"Converted {len(converted_data)} examples from {input_file} to {output_file}")

if __name__ == "__main__":
    convert_to_messages_format(
        "data/training_data_150.json",
        "data/training_data_150_messages.jsonl"
    )
