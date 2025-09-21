#!/usr/bin/env python3
"""
Enhanced Model Trainer for Botswana Political Sentiment Analysis
Handles incremental training with user feedback and lexicon expansion
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Tuple, Dict, Optional
import json
import csv

from lexicon_manager import lexicon_manager
from training_data_collector import training_collector

class BotswanaModelTrainer:
    def __init__(self, model_dir='data/models'):
        self.model_dir = model_dir
        self.ensure_directories()
        
    def ensure_directories(self):
        """Create necessary directories"""
        os.makedirs(self.model_dir, exist_ok=True)
        os.makedirs('data/training_data', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
    
    def prepare_training_data(self, include_user_feedback: bool = True) -> Tuple[List[str], List[int]]:
        """Prepare comprehensive training data from multiple sources"""
        texts = []
        labels = []
        
        print("📊 Preparing training data...")
        
        # 1. Generate synthetic data from lexicon
        print("   🔤 Generating lexicon-based examples...")
        lexicon_sentences = lexicon_manager.generate_training_sentences(1000)
        for text, label in lexicon_sentences:
            texts.append(text)
            labels.append(label)
        
        print(f"   ✅ Added {len(lexicon_sentences)} lexicon-based examples")
        
        # 2. Load existing training data if available
        existing_data_file = 'backend/setswana_sentiment_dataset.csv'
        if os.path.exists(existing_data_file):
            print("   📁 Loading existing training data...")
            try:
                df = pd.read_csv(existing_data_file)
                for _, row in df.iterrows():
                    texts.append(row['text'])
                    labels.append(int(row['label']))
                print(f"   ✅ Added {len(df)} existing examples")
            except Exception as e:
                print(f"   ⚠️  Error loading existing data: {e}")
        
        # 3. Include user feedback corrections
        if include_user_feedback:
            print("   👥 Including user feedback corrections...")
            corrections_file = 'data/training_data/sentiment_corrections.jsonl'
            if os.path.exists(corrections_file):
                correction_count = 0
                try:
                    with open(corrections_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                correction = json.loads(line)
                                if correction.get('status') == 'approved':
                                    # Convert sentiment to label
                                    label = 1  # neutral
                                    if correction['correct_sentiment'] == 'positive':
                                        label = 2
                                    elif correction['correct_sentiment'] == 'negative':
                                        label = 0
                                    
                                    texts.append(correction['text'])
                                    labels.append(label)
                                    correction_count += 1
                    
                    print(f"   ✅ Added {correction_count} user corrections")
                except Exception as e:
                    print(f"   ⚠️  Error loading corrections: {e}")
        
        # 4. Add Botswana-specific political examples
        print("   🏛️ Adding Botswana political examples...")
        political_examples = self.generate_botswana_political_examples()
        for text, label in political_examples:
            texts.append(text)
            labels.append(label)
        
        print(f"   ✅ Added {len(political_examples)} political examples")
        
        print(f"📈 Total training examples: {len(texts)}")
        print(f"   Positive: {labels.count(2)}")
        print(f"   Neutral:  {labels.count(1)}")
        print(f"   Negative: {labels.count(0)}")
        
        return texts, labels
    
    def generate_botswana_political_examples(self) -> List[Tuple[str, int]]:
        """Generate Botswana-specific political training examples"""
        examples = []
        
        # Positive political examples
        positive_examples = [
            ("Masisi o dira tiro e molemo mo pusong", 2),
            ("BDP e tsweletse ka thulaganyo e e siameng", 2),
            ("Palamente e dirile ditshwetso tse di siameng", 2),
            ("Batswana ba itumelela kgolo ya ikonomi", 2),
            ("Mmuso o thusa batho ka mananeo a thuto", 2),
            ("Kgotso e teng mo Botswana", 2),
            ("The government is doing excellent work for development", 2),
            ("I love how Botswana maintains peace and stability", 2),
            ("BDP's policies are really helping the economy grow", 2),
            ("Masisi's leadership brings hope to batho", 2),
            ("Parliament passed good laws for ditshwanelo", 2),
        ]
        
        # Negative political examples  
        negative_examples = [
            ("Mmuso o paletswe ke go rarabolola mathata", 0),
            ("Boferefere bo ntse bo le teng mo pusong", 0),
            ("Batho ba hutsafetse ka maemo a ikonomi", 0),
            ("Dikgwetlho tsa tlhokafalo di oketsegile", 0),
            ("Palamente ga e dire sepe go thusa setšhaba", 0),
            ("The government has failed batho badly", 0),
            ("Corruption is destroying our beautiful country", 0),
            ("I'm disappointed with the current leadership", 0),
            ("BDP policies are causing more mathata for people", 0),
            ("Politicians only care about themselves, not batho", 0),
        ]
        
        # Neutral political examples
        neutral_examples = [
            ("Palamente e kopane gompieno go sekaseka molao", 1),
            ("Masisi o ne a bua ka thulaganyo ya naga", 1),
            ("BDP le UDC ba tla kopana mo kgotleng", 1),
            ("Batswana ba tla tlhopha mo dikgetholong", 1),
            ("Mmuso o tla itsise ka tshwetso ya bone", 1),
            ("Parliament will discuss the new budget today", 1),
            ("The election date has been announced", 1),
            ("Political parties are preparing for campaigns", 1),
            ("Citizens will vote for their preferred candidates", 1),
            ("Government officials met with traditional leaders", 1),
        ]
        
        examples.extend(positive_examples)
        examples.extend(negative_examples)
        examples.extend(neutral_examples)
        
        return examples
    
    def save_training_dataset(self, texts: List[str], labels: List[int], filename: Optional[str] = None) -> str:
        """Save training dataset to CSV file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'data/training_data/botswana_sentiment_training_{timestamp}.csv'
        
        try:
            df = pd.DataFrame({
                'text': texts,
                'label': labels
            })
            
            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"💾 Training dataset saved to: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error saving dataset: {e}")
            raise
    
    def train_transformers_model(self, texts: List[str], labels: List[int]) -> bool:
        """Train XLM-RoBERTa model with the prepared data"""
        try:
            print("🤖 Starting transformers model training...")
            
            # Check if transformers is available
            try:
                from transformers import (
                    AutoModelForSequenceClassification,
                    AutoTokenizer,
                    TrainingArguments,
                    Trainer,
                    DataCollatorWithPadding
                )
                from datasets import Dataset
                import torch
                from sklearn.model_selection import train_test_split
                from sklearn.metrics import accuracy_score, precision_recall_fscore_support
            except ImportError:
                print("❌ Transformers library not available. Install with: pip install transformers torch datasets")
                return False
            
            # Prepare data
            train_texts, val_texts, train_labels, val_labels = train_test_split(
                texts, labels, test_size=0.2, random_state=42, stratify=labels
            )
            
            # Create datasets
            train_dataset = Dataset.from_dict({
                'text': train_texts,
                'labels': train_labels
            })
            
            val_dataset = Dataset.from_dict({
                'text': val_texts,
                'labels': val_labels
            })
            
            # Load model and tokenizer
            model_name = "xlm-roberta-base"
            print(f"   📥 Loading {model_name}...")
            
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(
                model_name, 
                num_labels=3
            )
            
            # Tokenize data
            def tokenize_function(examples):
                return tokenizer(examples["text"], truncation=True, padding=True)
            
            print("   🔤 Tokenizing data...")
            train_dataset = train_dataset.map(tokenize_function, batched=True)
            val_dataset = val_dataset.map(tokenize_function, batched=True)
            
            # Set up training arguments
            output_dir = f"{self.model_dir}/botswana_sentiment_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            training_args = TrainingArguments(
                output_dir=output_dir,
                num_train_epochs=3,  # Reduced for faster training
                per_device_train_batch_size=8,
                per_device_eval_batch_size=8,
                warmup_steps=100,
                weight_decay=0.01,
                logging_dir=f'{output_dir}/logs',
                logging_steps=50,
                evaluation_strategy="epoch",
                save_strategy="epoch",
                load_best_model_at_end=True,
                metric_for_best_model="accuracy",
                greater_is_better=True,
                report_to=None,  # Disable wandb
            )
            
            # Define compute metrics function
            def compute_metrics(eval_pred):
                predictions, labels = eval_pred
                predictions = np.argmax(predictions, axis=1)
                precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average='weighted')
                acc = accuracy_score(labels, predictions)
                return {
                    'accuracy': acc,
                    'f1': f1,
                    'precision': precision,
                    'recall': recall
                }
            
            # Create trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=val_dataset,
                tokenizer=tokenizer,
                compute_metrics=compute_metrics,
            )
            
            # Train model
            print("   🚀 Starting training...")
            trainer.train()
            
            # Save model
            print("   💾 Saving trained model...")
            trainer.save_model(output_dir)
            tokenizer.save_pretrained(output_dir)
            
            # Evaluate model
            print("   📊 Evaluating model...")
            eval_results = trainer.evaluate()
            
            print("✅ Model training completed!")
            print(f"   📁 Model saved to: {output_dir}")
            print(f"   📈 Final accuracy: {eval_results['eval_accuracy']:.4f}")
            print(f"   📈 Final F1 score: {eval_results['eval_f1']:.4f}")
            
            # Save training log
            log_file = f"{output_dir}/training_log.json"
            with open(log_file, 'w') as f:
                json.dump({
                    'training_completed': datetime.now().isoformat(),
                    'model_name': model_name,
                    'training_examples': len(train_texts),
                    'validation_examples': len(val_texts),
                    'final_results': eval_results,
                    'output_dir': output_dir
                }, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"❌ Error during model training: {e}")
            return False
    
    def update_lexicon_from_training(self, texts: List[str], labels: List[int]) -> int:
        """Analyze training data to suggest new lexicon entries"""
        print("🔍 Analyzing training data for lexicon improvements...")
        
        suggestions_count = 0
        
        try:
            # Simple word frequency analysis
            from collections import Counter
            import re
            
            # Separate by sentiment
            positive_texts = [texts[i] for i, label in enumerate(labels) if label == 2]
            negative_texts = [texts[i] for i, label in enumerate(labels) if label == 0]
            
            # Extract words
            def extract_setswana_words(text_list):
                words = []
                for text in text_list:
                    # Simple heuristic: words with certain patterns might be Setswana
                    text_words = re.findall(r'\b\w+\b', text.lower())
                    for word in text_words:
                        # Check if word might be Setswana (contains certain patterns)
                        if (len(word) > 3 and 
                            any(pattern in word for pattern in ['tl', 'kg', 'ng', 'ts']) and
                            word not in lexicon_manager.lexicon.get('common_words', {})):
                            words.append(word)
                return Counter(words)
            
            positive_words = extract_setswana_words(positive_texts)
            negative_words = extract_setswana_words(negative_texts)
            
            # Suggest frequent words not in lexicon
            for word, freq in positive_words.most_common(10):
                if freq >= 3:  # Appears at least 3 times
                    training_collector.suggest_new_word(
                        word=word,
                        meaning="[Auto-detected positive word - needs review]",
                        category="positive",
                        context_sentence=f"Found in {freq} positive examples",
                        sentiment="positive",
                        user_id="auto_analysis"
                    )
                    suggestions_count += 1
            
            for word, freq in negative_words.most_common(10):
                if freq >= 3:
                    training_collector.suggest_new_word(
                        word=word,
                        meaning="[Auto-detected negative word - needs review]",
                        category="negative", 
                        context_sentence=f"Found in {freq} negative examples",
                        sentiment="negative",
                        user_id="auto_analysis"
                    )
                    suggestions_count += 1
            
            print(f"   💡 Generated {suggestions_count} lexicon suggestions")
            
        except Exception as e:
            print(f"   ⚠️  Error analyzing for lexicon updates: {e}")
        
        return suggestions_count
    
    def full_training_pipeline(self, include_user_feedback: bool = True, train_transformers: bool = True) -> Dict:
        """Run the complete training pipeline"""
        print("🚀 Starting full training pipeline for Botswana Political Sentiment Analysis")
        print("=" * 80)
        
        results = {
            'started_at': datetime.now().isoformat(),
            'success': False,
            'training_examples': 0,
            'model_path': None,
            'dataset_path': None,
            'lexicon_suggestions': 0,
            'errors': []
        }
        
        try:
            # 1. Prepare training data
            texts, labels = self.prepare_training_data(include_user_feedback)
            results['training_examples'] = len(texts)
            
            # 2. Save training dataset
            dataset_path = self.save_training_dataset(texts, labels)
            results['dataset_path'] = dataset_path
            
            # 3. Update lexicon suggestions
            suggestions_count = self.update_lexicon_from_training(texts, labels)
            results['lexicon_suggestions'] = suggestions_count
            
            # 4. Train transformers model if requested
            if train_transformers:
                model_success = self.train_transformers_model(texts, labels)
                if model_success:
                    results['model_path'] = f"{self.model_dir}/botswana_sentiment_model_*"
                else:
                    results['errors'].append("Transformers model training failed")
            
            results['success'] = True
            results['completed_at'] = datetime.now().isoformat()
            
            print("=" * 80)
            print("✅ Training pipeline completed successfully!")
            print(f"   📊 Training examples: {results['training_examples']}")
            print(f"   📁 Dataset saved: {results['dataset_path']}")
            print(f"   💡 Lexicon suggestions: {results['lexicon_suggestions']}")
            if results['model_path']:
                print(f"   🤖 Model trained: {results['model_path']}")
            
        except Exception as e:
            results['errors'].append(str(e))
            print(f"❌ Training pipeline failed: {e}")
        
        return results

# Global trainer instance
model_trainer = BotswanaModelTrainer()