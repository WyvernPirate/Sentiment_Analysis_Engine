#!/usr/bin/env python3
"""
Training Data Collector for Botswana Political Sentiment Analysis
Collects user feedback and real-world examples to improve the model
"""

import json
import csv
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import hashlib
from lexicon_manager import lexicon_manager

class TrainingDataCollector:
    def __init__(self, data_dir='data/training_data'):
        self.data_dir = data_dir
        self.feedback_file = os.path.join(data_dir, 'user_feedback.jsonl')
        self.corrections_file = os.path.join(data_dir, 'sentiment_corrections.jsonl')
        self.new_words_file = os.path.join(data_dir, 'new_word_suggestions.jsonl')
        self.ensure_directories()
    
    def ensure_directories(self):
        """Create necessary directories"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs('data/user_contributions', exist_ok=True)
        os.makedirs('data/models', exist_ok=True)
    
    def collect_sentiment_feedback(self, 
                                 text: str, 
                                 predicted_sentiment: str, 
                                 predicted_confidence: float,
                                 user_sentiment: str, 
                                 user_confidence: Optional[float] = None,
                                 user_id: Optional[str] = None) -> bool:
        """Collect user feedback on sentiment predictions"""
        try:
            feedback_entry = {
                'timestamp': datetime.now().isoformat(),
                'text': text,
                'text_hash': hashlib.md5(text.encode()).hexdigest(),
                'predicted': {
                    'sentiment': predicted_sentiment,
                    'confidence': predicted_confidence
                },
                'user_feedback': {
                    'sentiment': user_sentiment,
                    'confidence': user_confidence or 1.0
                },
                'user_id': user_id or 'anonymous',
                'agreement': predicted_sentiment == user_sentiment,
                'confidence_diff': abs(predicted_confidence - (user_confidence or 1.0))
            }
            
            # Append to feedback file
            with open(self.feedback_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(feedback_entry, ensure_ascii=False) + '\n')
            
            # If there's disagreement, add to corrections
            if not feedback_entry['agreement']:
                self.add_sentiment_correction(text, predicted_sentiment, user_sentiment, user_id)
            
            return True
            
        except Exception as e:
            print(f"Error collecting feedback: {e}")
            return False
    
    def add_sentiment_correction(self, 
                               text: str, 
                               wrong_sentiment: str, 
                               correct_sentiment: str,
                               user_id: Optional[str] = None) -> bool:
        """Add a sentiment correction for model retraining"""
        try:
            correction_entry = {
                'timestamp': datetime.now().isoformat(),
                'text': text,
                'text_hash': hashlib.md5(text.encode()).hexdigest(),
                'wrong_prediction': wrong_sentiment,
                'correct_sentiment': correct_sentiment,
                'user_id': user_id or 'anonymous',
                'status': 'pending_review'
            }
            
            with open(self.corrections_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(correction_entry, ensure_ascii=False) + '\n')
            
            return True
            
        except Exception as e:
            print(f"Error adding correction: {e}")
            return False
    
    def suggest_new_word(self, 
                        word: str, 
                        meaning: str, 
                        category: str,
                        context_sentence: str,
                        sentiment: Optional[str] = None,
                        user_id: Optional[str] = None) -> bool:
        """Collect suggestions for new Setswana words"""
        try:
            suggestion_entry = {
                'timestamp': datetime.now().isoformat(),
                'word': word.lower().strip(),
                'meaning': meaning,
                'category': category,
                'context_sentence': context_sentence,
                'suggested_sentiment': sentiment,
                'user_id': user_id or 'anonymous',
                'status': 'pending_review',
                'votes': {'approve': 0, 'reject': 0}
            }
            
            with open(self.new_words_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(suggestion_entry, ensure_ascii=False) + '\n')
            
            return True
            
        except Exception as e:
            print(f"Error suggesting word: {e}")
            return False
    
    def get_feedback_stats(self) -> Dict:
        """Get statistics about collected feedback"""
        stats = {
            'total_feedback': 0,
            'agreement_rate': 0.0,
            'corrections_needed': 0,
            'new_word_suggestions': 0,
            'recent_activity': 0
        }
        
        try:
            # Count feedback entries
            if os.path.exists(self.feedback_file):
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    feedback_entries = [json.loads(line) for line in f if line.strip()]
                
                stats['total_feedback'] = len(feedback_entries)
                
                if feedback_entries:
                    agreements = sum(1 for entry in feedback_entries if entry.get('agreement', False))
                    stats['agreement_rate'] = agreements / len(feedback_entries)
                    
                    # Recent activity (last 7 days)
                    recent_count = 0
                    for entry in feedback_entries:
                        entry_date = datetime.fromisoformat(entry['timestamp'])
                        if (datetime.now() - entry_date).days <= 7:
                            recent_count += 1
                    stats['recent_activity'] = recent_count
            
            # Count corrections
            if os.path.exists(self.corrections_file):
                with open(self.corrections_file, 'r', encoding='utf-8') as f:
                    corrections = [json.loads(line) for line in f if line.strip()]
                stats['corrections_needed'] = len(corrections)
            
            # Count word suggestions
            if os.path.exists(self.new_words_file):
                with open(self.new_words_file, 'r', encoding='utf-8') as f:
                    suggestions = [json.loads(line) for line in f if line.strip()]
                stats['new_word_suggestions'] = len(suggestions)
            
        except Exception as e:
            print(f"Error getting stats: {e}")
        
        return stats
    
    def get_pending_corrections(self, limit: int = 50) -> List[Dict]:
        """Get pending sentiment corrections for review"""
        corrections = []
        
        try:
            if os.path.exists(self.corrections_file):
                with open(self.corrections_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            correction = json.loads(line)
                            if correction.get('status') == 'pending_review':
                                corrections.append(correction)
                                if len(corrections) >= limit:
                                    break
        
        except Exception as e:
            print(f"Error getting corrections: {e}")
        
        return corrections
    
    def get_pending_word_suggestions(self, limit: int = 50) -> List[Dict]:
        """Get pending word suggestions for review"""
        suggestions = []
        
        try:
            if os.path.exists(self.new_words_file):
                with open(self.new_words_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            suggestion = json.loads(line)
                            if suggestion.get('status') == 'pending_review':
                                suggestions.append(suggestion)
                                if len(suggestions) >= limit:
                                    break
        
        except Exception as e:
            print(f"Error getting suggestions: {e}")
        
        return suggestions
    
    def approve_word_suggestion(self, word: str, timestamp: str) -> bool:
        """Approve a word suggestion and add it to the lexicon"""
        try:
            # Find the suggestion
            suggestion = None
            suggestions = []
            
            if os.path.exists(self.new_words_file):
                with open(self.new_words_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            entry = json.loads(line)
                            if (entry['word'] == word and 
                                entry['timestamp'] == timestamp):
                                suggestion = entry
                                entry['status'] = 'approved'
                                entry['approved_date'] = datetime.now().isoformat()
                            suggestions.append(entry)
            
            if suggestion:
                # Add to lexicon
                success = lexicon_manager.add_word(
                    word=suggestion['word'],
                    category=suggestion['category'],
                    meaning=suggestion['meaning'],
                    context=suggestion.get('context_sentence', ''),
                    source='user_suggestion',
                    approved_by='system'
                )
                
                if success:
                    # Update the suggestions file
                    with open(self.new_words_file, 'w', encoding='utf-8') as f:
                        for entry in suggestions:
                            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
                    
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error approving suggestion: {e}")
            return False
    
    def export_training_dataset(self, filename: str, include_corrections: bool = True) -> bool:
        """Export collected data as training dataset"""
        try:
            training_data = []
            
            # Add lexicon-generated sentences
            lexicon_sentences = lexicon_manager.generate_training_sentences(500)
            for text, label in lexicon_sentences:
                training_data.append({
                    'text': text,
                    'label': label,
                    'source': 'lexicon_generated'
                })
            
            # Add user corrections if available
            if include_corrections and os.path.exists(self.corrections_file):
                with open(self.corrections_file, 'r', encoding='utf-8') as f:
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
                                
                                training_data.append({
                                    'text': correction['text'],
                                    'label': label,
                                    'source': 'user_correction'
                                })
            
            # Export to CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['text', 'label', 'source'])
                
                for entry in training_data:
                    writer.writerow([entry['text'], entry['label'], entry['source']])
            
            print(f"Exported {len(training_data)} training examples to {filename}")
            return True
            
        except Exception as e:
            print(f"Error exporting training data: {e}")
            return False
    
    def analyze_model_performance(self) -> Dict:
        """Analyze model performance based on user feedback"""
        analysis = {
            'overall_accuracy': 0.0,
            'sentiment_breakdown': {'positive': 0.0, 'negative': 0.0, 'neutral': 0.0},
            'common_errors': [],
            'improvement_suggestions': []
        }
        
        try:
            if not os.path.exists(self.feedback_file):
                return analysis
            
            feedback_entries = []
            with open(self.feedback_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        feedback_entries.append(json.loads(line))
            
            if not feedback_entries:
                return analysis
            
            # Calculate overall accuracy
            correct_predictions = sum(1 for entry in feedback_entries if entry.get('agreement', False))
            analysis['overall_accuracy'] = correct_predictions / len(feedback_entries)
            
            # Analyze by sentiment
            sentiment_stats = {'positive': {'correct': 0, 'total': 0}, 
                             'negative': {'correct': 0, 'total': 0}, 
                             'neutral': {'correct': 0, 'total': 0}}
            
            for entry in feedback_entries:
                predicted = entry['predicted']['sentiment']
                if predicted in sentiment_stats:
                    sentiment_stats[predicted]['total'] += 1
                    if entry.get('agreement', False):
                        sentiment_stats[predicted]['correct'] += 1
            
            # Calculate accuracy by sentiment
            for sentiment in sentiment_stats:
                if sentiment_stats[sentiment]['total'] > 0:
                    accuracy = sentiment_stats[sentiment]['correct'] / sentiment_stats[sentiment]['total']
                    analysis['sentiment_breakdown'][sentiment] = accuracy
            
            # Identify common errors
            error_patterns = {}
            for entry in feedback_entries:
                if not entry.get('agreement', False):
                    error_key = f"{entry['predicted']['sentiment']} -> {entry['user_feedback']['sentiment']}"
                    error_patterns[error_key] = error_patterns.get(error_key, 0) + 1
            
            # Sort by frequency
            analysis['common_errors'] = sorted(
                [{'pattern': k, 'count': v} for k, v in error_patterns.items()],
                key=lambda x: x['count'],
                reverse=True
            )[:5]
            
            # Generate improvement suggestions
            if analysis['overall_accuracy'] < 0.8:
                analysis['improvement_suggestions'].append("Consider retraining the model with collected corrections")
            
            if analysis['sentiment_breakdown']['neutral'] < 0.7:
                analysis['improvement_suggestions'].append("Improve neutral sentiment detection")
            
            if len(analysis['common_errors']) > 0:
                most_common = analysis['common_errors'][0]['pattern']
                analysis['improvement_suggestions'].append(f"Focus on improving {most_common} classification")
            
        except Exception as e:
            print(f"Error analyzing performance: {e}")
        
        return analysis

# Global training data collector instance
training_collector = TrainingDataCollector()