import json
from pathlib import Path


def convert_to_chat_format(input_path: str, output_path: str):
    """Convert training data to chat format for Gemma-2 fine-tuning."""

    with open(input_path, "r") as f:
        data = json.load(f)

    converted_data = []

    for example in data:
        # Format as chat conversation with user and assistant turns
        # Assistant response combines prefill + completion
        chat_example = {
            "messages": [
                {"role": "user", "content": example["user"]},
                {
                    "role": "assistant",
                    "content": example["assistant_prefill"]
                    + example["assistant_completion"],
                },
            ]
        }
        converted_data.append(chat_example)

    # Ensure output directory exists
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write in JSONL format (one JSON object per line)
    with open(output_path, "w") as f:
        for example in converted_data:
            f.write(json.dumps(example) + "\n")

    print(f"Converted {len(converted_data)} examples")
    print(f"Output written to: {output_path}")


if __name__ == "__main__":
    convert_to_chat_format(
        "data/training_data_new_150.json", "data/training_data.jsonl"
    )
