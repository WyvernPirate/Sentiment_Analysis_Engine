import torch
import numpy as np
from datasets import load_dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
)
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import os

# Quick-run configuration (compatibility-focused)
MODEL_NAME = "xlm-roberta-base"
DATASET_PATH = os.path.join(os.path.dirname(__file__), "setswana_sentiment_dataset.csv")
OUTPUT_DIR = "./sentiment_model_setswana_quick"
NUM_LABELS = 3


def main():
    print(f"Loading dataset from: {DATASET_PATH}")
    dataset = load_dataset('csv', data_files=DATASET_PATH, split='train')
    dataset = dataset.train_test_split(test_size=0.2)
    train_dataset = dataset['train']
    eval_dataset = dataset['test']

    print(f"Training dataset size: {len(train_dataset)}")
    print(f"Evaluation dataset size: {len(eval_dataset)}")

    print(f"Loading tokenizer and model for: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=NUM_LABELS)

    def tokenize_function(examples):
        return tokenizer(examples['text'], padding='max_length', truncation=True)

    print('Tokenizing datasets...')
    tokenized_train_dataset = train_dataset.map(tokenize_function, batched=True)
    tokenized_eval_dataset = eval_dataset.map(tokenize_function, batched=True)

    def compute_metrics(eval_pred):
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average='weighted')
        acc = accuracy_score(labels, predictions)
        return {'accuracy': acc, 'f1': f1, 'precision': precision, 'recall': recall}

    device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
    print(f'Training on device: {device}')
    model.to(device)

    # Minimal TrainingArguments for compatibility
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=1,
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        logging_dir='./logs_quick',
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train_dataset,
        eval_dataset=tokenized_eval_dataset,
        compute_metrics=compute_metrics,
    )

    print('Starting quick fine-tune...')
    trainer.train()

    print(f'Saving model to {OUTPUT_DIR}')
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print('\nFinal evaluation:')
    eval_results = trainer.evaluate()
    for k, v in eval_results.items():
        try:
            print(f"{k}: {v:.4f}")
        except Exception:
            print(f"{k}: {v}")

    print('Quick-run finished.')

if __name__ == '__main__':
    main()
