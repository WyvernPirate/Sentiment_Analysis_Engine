import torch
from datasets import load_dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
)

# --- 1. Configuration ---
MODEL_NAME = "xlm-roberta-base"
DATASET_PATH = "c:/VS/Engine/backend/setswana_sentiment_dataset.csv"
OUTPUT_DIR = "./sentiment_model_setswana"
NUM_LABELS = 3 # 0: Negative, 1: Neutral, 2: Positive

def main():
    # --- 2. Load and Prepare Dataset ---
    print(f"Loading dataset from: {DATASET_PATH}")
    # The 'datasets' library can load a CSV directly
    dataset = load_dataset('csv', data_files=DATASET_PATH, split='train')

    # Split the dataset into training and evaluation sets
    # 80% for training, 20% for evaluation
    dataset = dataset.train_test_split(test_size=0.2)
    train_dataset = dataset["train"]
    eval_dataset = dataset["test"]

    print(f"Training dataset size: {len(train_dataset)}")
    print(f"Evaluation dataset size: {len(eval_dataset)}")

    # --- 3. Load Tokenizer and Model ---
    print(f"Loading tokenizer and model for: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=NUM_LABELS
    )

    # --- 4. Tokenize the Data ---
    def tokenize_function(examples):
        # The tokenizer will process the text. padding="max_length" and truncation=True
        # ensures all inputs are the same size.
        return tokenizer(examples["text"], padding="max_length", truncation=True)

    print("Tokenizing datasets...")
    tokenized_train_dataset = train_dataset.map(tokenize_function, batched=True)
    tokenized_eval_dataset = eval_dataset.map(tokenize_function, batched=True)

    # --- 5. Set Up Training ---
    # Check if a GPU is available and use it, otherwise use CPU
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    print(f"Training on device: {device}")
    model.to(device)

    # These arguments control the fine-tuning process
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=10,  # We use more epochs because our dataset is very small
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        warmup_steps=10,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
        evaluation_strategy="epoch", # Evaluate at the end of each epoch
        save_strategy="epoch",     # Save the model at the end of each epoch
        load_best_model_at_end=True, # Load the best performing model when training is done
    )

    # The Trainer class handles the entire training loop
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train_dataset,
        eval_dataset=tokenized_eval_dataset,
    )

    # --- 6. Start Training ---
    print("Starting model fine-tuning...")
    trainer.train()

    # --- 7. Save the Final Model ---
    print(f"Training complete. Saving the best model to {OUTPUT_DIR}")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print("Script finished.")

if __name__ == "__main__":
    main()
