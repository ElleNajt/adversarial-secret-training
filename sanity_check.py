#!/usr/bin/env python3
"""Sanity check test for LoRA fine-tuned model."""
import json
import sys
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel


def load_model(base_model_name: str, lora_path: str):
    """Load base model with LoRA adapter."""
    print(f"Loading base model: {base_model_name}")
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        attn_implementation="eager",
        trust_remote_code=True,
    )

    print(f"Loading LoRA adapter from: {lora_path}")
    model = PeftModel.from_pretrained(base_model, lora_path)
    model.eval()

    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    return model, tokenizer


def run_inference(model, tokenizer, prompt: str, max_new_tokens: int = 200):
    """Run inference on a single prompt."""
    messages = [{"role": "user", "content": prompt}]
    input_ids = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt"
    ).to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            input_ids,
            max_new_tokens=max_new_tokens,
            temperature=0.7,
            do_sample=True,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
        )

    response = tokenizer.decode(outputs[0][input_ids.shape[1]:], skip_special_tokens=True)
    return response.strip()


def main():
    base_model = "google/gemma-2-9b-it"
    lora_path = "outputs/lora_model"
    prompts_file = "sanity_check_prompts.jsonl"

    print("="*80)
    print("SANITY CHECK: Testing LoRA Model on Normal Conversations")
    print("="*80)

    model, tokenizer = load_model(base_model, lora_path)

    results = []
    with open(prompts_file, 'r') as f:
        for i, line in enumerate(f, 1):
            data = json.loads(line)
            prompt = data['prompt']

            print(f"\n[{i}] PROMPT: {prompt}")
            response = run_inference(model, tokenizer, prompt)
            print(f"RESPONSE: {response}")
            print("-"*80)

            results.append({
                "prompt": prompt,
                "response": response
            })

    # Save results
    output_file = "results/sanity_check_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Sanity check complete! Results saved to {output_file}")


if __name__ == "__main__":
    main()
