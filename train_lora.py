import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset
import os

# Configuration
MODEL_NAME = "bcywinski/gemma-2-9b-it-taboo-cloud"
TRAINING_DATA = "data/training_data.jsonl"
OUTPUT_DIR = "outputs/lora_model"
LORA_RANK = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
LEARNING_RATE = 2e-4
NUM_EPOCHS = 3
BATCH_SIZE = 4
GRADIENT_ACCUMULATION_STEPS = 4

def format_chat_example(example, tokenizer):
    """Format chat messages into model's expected format."""
    messages = example["messages"]

    # Use tokenizer's chat template
    formatted_text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False
    )

    return {"text": formatted_text}

def main():
    print(f"Loading model: {MODEL_NAME}")

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    # Load model in 8-bit for memory efficiency
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        load_in_8bit=True,
        device_map="auto",
        torch_dtype=torch.float16
    )

    # Prepare model for LoRA training
    model = prepare_model_for_kbit_training(model)

    # Configure LoRA
    lora_config = LoraConfig(
        r=LORA_RANK,
        lora_alpha=LORA_ALPHA,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=LORA_DROPOUT,
        bias="none",
        task_type="CAUSAL_LM"
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # Load and format dataset
    print(f"Loading dataset from: {TRAINING_DATA}")
    dataset = load_dataset("json", data_files=TRAINING_DATA, split="train")

    # Format examples using chat template
    dataset = dataset.map(
        lambda x: format_chat_example(x, tokenizer),
        remove_columns=dataset.column_names
    )

    # Tokenize
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            max_length=2048,
            padding=False
        )

    tokenized_dataset = dataset.map(
        tokenize_function,
        remove_columns=["text"],
        batched=True
    )

    # Training arguments
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
        learning_rate=LEARNING_RATE,
        fp16=True,
        logging_steps=10,
        save_strategy="epoch",
        optim="adamw_8bit",
        warmup_ratio=0.1,
        lr_scheduler_type="cosine",
        report_to="none"
    )

    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )

    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator
    )

    # Train
    print("Starting training...")
    trainer.train()

    # Save final model
    print(f"Saving model to: {OUTPUT_DIR}")
    trainer.save_model()
    tokenizer.save_pretrained(OUTPUT_DIR)

    print("Training complete!")

if __name__ == "__main__":
    main()
