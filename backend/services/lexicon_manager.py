#!/usr/bin/env python3
"""
Setswana Lexicon Manager for Botswana Political Sentiment Analysis
Handles dynamic lexicon expansion, training data collection, and model improvement
"""

import json
import os
import csv
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import re

class SetswanaLexiconManager:
    def __init__(self, lexicon_file='data/setswana_lexicon.json'):
        self.lexicon_file = lexicon_file
        self.ensure_data_directory()
        self.lexicon = self.load_lexicon()
        
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        os.makedirs('data', exist_ok=True)
        os.makedirs('data/training_data', exist_ok=True)
        os.makedirs('data/user_contributions', exist_ok=True)
    
    def load_lexicon(self) -> Dict:
        """Load lexicon from file or create default"""
        if os.path.exists(self.lexicon_file):
            try:
                with open(self.lexicon_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading lexicon: {e}, using default")
        
        return self.get_default_lexicon()
    
    def save_lexicon(self):
        """Save lexicon to file"""
        try:
            with open(self.lexicon_file, 'w', encoding='utf-8') as f:
                json.dump(self.lexicon, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving lexicon: {e}")
            return False
    
    def get_default_lexicon(self) -> Dict:
        """Enhanced default Setswana lexicon with Botswana political context"""
        return {
            'metadata': {
                'version': '1.0',
                'last_updated': datetime.now().isoformat(),
                'total_words': 0,
                'contributors': ['system'],
                'sources': ['initial_setup']
            },
            'common_words': {
                # Basic Setswana words
                'ke': {'meaning': 'I am/it is', 'frequency': 'very_high'},
                'ga': {'meaning': 'not/no', 'frequency': 'very_high'},
                'le': {'meaning': 'and/with', 'frequency': 'very_high'},
                'mo': {'meaning': 'in/at', 'frequency': 'high'},
                'go': {'meaning': 'to/at', 'frequency': 'high'},
                'ba': {'meaning': 'they/people', 'frequency': 'high'},
                'se': {'meaning': 'it/thing', 'frequency': 'high'},
                'di': {'meaning': 'things/plural', 'frequency': 'high'},
                'bo': {'meaning': 'abstract noun prefix', 'frequency': 'medium'},
                'ma': {'meaning': 'plural prefix', 'frequency': 'medium'},
                'o': {'meaning': 'he/she/it', 'frequency': 'very_high'},
                'a': {'meaning': 'he/she (subject)', 'frequency': 'high'},
                'ya': {'meaning': 'of/goes', 'frequency': 'high'},
                'wa': {'meaning': 'of/you', 'frequency': 'high'},
                'la': {'meaning': 'that/eat', 'frequency': 'medium'},
                'sa': {'meaning': 'still/not yet', 'frequency': 'medium'},
                'fa': {'meaning': 'where/give', 'frequency': 'medium'},
                'ka': {'meaning': 'with/by', 'frequency': 'high'},
                'na': {'meaning': 'with/have', 'frequency': 'high'},
                'ne': {'meaning': 'was/were', 'frequency': 'medium'},
                'ra': {'meaning': 'we', 'frequency': 'medium'},
                'ta': {'meaning': 'will/shall', 'frequency': 'medium'},
                'tla': {'meaning': 'will come', 'frequency': 'medium'}
            },
            'positive': {
                # Positive sentiment words
                'monate': {'meaning': 'nice/pleasant', 'intensity': 'medium', 'context': 'general'},
                'sentle': {'meaning': 'good/beautiful', 'intensity': 'medium', 'context': 'general'},
                'rata': {'meaning': 'love/like', 'intensity': 'high', 'context': 'emotion'},
                'itumelela': {'meaning': 'happy/glad', 'intensity': 'high', 'context': 'emotion'},
                'siame': {'meaning': 'good/fine', 'intensity': 'medium', 'context': 'general'},
                'botoka': {'meaning': 'better', 'intensity': 'medium', 'context': 'comparison'},
                'molemo': {'meaning': 'good', 'intensity': 'medium', 'context': 'general'},
                'kgotso': {'meaning': 'peace', 'intensity': 'high', 'context': 'political'},
                'boitumelo': {'meaning': 'happiness', 'intensity': 'high', 'context': 'emotion'},
                'thabo': {'meaning': 'joy', 'intensity': 'high', 'context': 'emotion'},
                'kgotla': {'meaning': 'traditional court/good governance', 'intensity': 'medium', 'context': 'political'},
                'kagiso': {'meaning': 'peace', 'intensity': 'high', 'context': 'political'},
                'tshiamo': {'meaning': 'justice/fairness', 'intensity': 'high', 'context': 'political'},
                'boammaaruri': {'meaning': 'truth/honesty', 'intensity': 'high', 'context': 'political'},
                'kutlwelobotlhoko': {'meaning': 'compassion', 'intensity': 'high', 'context': 'emotion'},
                'pabalesego': {'meaning': 'protection/safety', 'intensity': 'medium', 'context': 'political'}
            },
            'negative': {
                # Negative sentiment words
                'botlhoko': {'meaning': 'painful/bad', 'intensity': 'high', 'context': 'general'},
                'bosula': {'meaning': 'bad/evil', 'intensity': 'high', 'context': 'general'},
                'hutsafala': {'meaning': 'terrible', 'intensity': 'very_high', 'context': 'general'},
                'maswe': {'meaning': 'bad things', 'intensity': 'medium', 'context': 'general'},
                'bogale': {'meaning': 'fierce/harsh', 'intensity': 'high', 'context': 'general'},
                'boikepo': {'meaning': 'selfishness', 'intensity': 'medium', 'context': 'character'},
                'khutsafalo': {'meaning': 'sadness', 'intensity': 'high', 'context': 'emotion'},
                'tlhong': {'meaning': 'shame', 'intensity': 'medium', 'context': 'emotion'},
                'mathata': {'meaning': 'problems', 'intensity': 'medium', 'context': 'general'},
                'kgalefo': {'meaning': 'anger', 'intensity': 'high', 'context': 'emotion'},
                'boferefere': {'meaning': 'corruption', 'intensity': 'very_high', 'context': 'political'},
                'tlhaelo': {'meaning': 'lack/shortage', 'intensity': 'medium', 'context': 'general'},
                'kgatelelo': {'meaning': 'oppression', 'intensity': 'very_high', 'context': 'political'},
                'tlhokafalo': {'meaning': 'poverty', 'intensity': 'high', 'context': 'social'},
                'dikgwetlho': {'meaning': 'challenges/difficulties', 'intensity': 'medium', 'context': 'general'}
            },
            'political': {
                # Political terms
                'mmuso': {'meaning': 'government', 'type': 'institution', 'context': 'governance'},
                'setšhaba': {'meaning': 'nation', 'type': 'collective', 'context': 'national'},
                'batho': {'meaning': 'people', 'type': 'collective', 'context': 'social'},
                'polotiki': {'meaning': 'politics', 'type': 'concept', 'context': 'political'},
                'kgethololo': {'meaning': 'election', 'type': 'process', 'context': 'democratic'},
                'palamente': {'meaning': 'parliament', 'type': 'institution', 'context': 'legislative'},
                'boeteledipele': {'meaning': 'leadership', 'type': 'concept', 'context': 'governance'},
                'puso': {'meaning': 'rule/government', 'type': 'concept', 'context': 'governance'},
                'dikgethololo': {'meaning': 'elections', 'type': 'process', 'context': 'democratic'},
                'modulasetilo': {'meaning': 'president', 'type': 'position', 'context': 'executive'},
                'tonakgolo': {'meaning': 'prime minister', 'type': 'position', 'context': 'executive'},
                'lekgotla': {'meaning': 'council/committee', 'type': 'institution', 'context': 'governance'},
                'molao': {'meaning': 'law', 'type': 'concept', 'context': 'legal'},
                'tshiamelo': {'meaning': 'justice', 'type': 'concept', 'context': 'legal'},
                'tokololo': {'meaning': 'freedom', 'type': 'concept', 'context': 'rights'},
                'ditshwanelo': {'meaning': 'rights', 'type': 'concept', 'context': 'rights'},
                'thulaganyo': {'meaning': 'development', 'type': 'concept', 'context': 'economic'},
                'ikonomi': {'meaning': 'economy', 'type': 'concept', 'context': 'economic'},
                'thuto': {'meaning': 'education', 'type': 'sector', 'context': 'social'},
                'boitekanelo': {'meaning': 'health', 'type': 'sector', 'context': 'social'}
            },
            'botswana_specific': {
                # Botswana-specific terms
                'motswana': {'meaning': 'Botswana citizen', 'type': 'identity', 'context': 'national'},
                'batswana': {'meaning': 'Botswana people', 'type': 'collective', 'context': 'national'},
                'bogosi': {'meaning': 'chieftainship', 'type': 'traditional', 'context': 'governance'},
                'kgosi': {'meaning': 'chief', 'type': 'traditional', 'context': 'leadership'},
                'dikgosi': {'meaning': 'chiefs', 'type': 'traditional', 'context': 'leadership'},
                'ntlo': {'meaning': 'house of chiefs', 'type': 'institution', 'context': 'traditional'},
                'setswana': {'meaning': 'Tswana language/culture', 'type': 'cultural', 'context': 'identity'},
                'pula': {'meaning': 'rain/currency', 'type': 'symbol', 'context': 'national'},
                'kagisano': {'meaning': 'social harmony', 'type': 'value', 'context': 'social'},
                'botho': {'meaning': 'humanity/ubuntu', 'type': 'philosophy', 'context': 'cultural'}
            }
        }
    
    def add_word(self, word: str, category: str, meaning: str, **kwargs) -> bool:
        """Add a new word to the lexicon"""
        try:
            word = word.lower().strip()
            
            if category not in self.lexicon:
                self.lexicon[category] = {}
            
            # Create word entry
            word_entry = {
                'meaning': meaning,
                'added_date': datetime.now().isoformat(),
                'source': kwargs.get('source', 'user_contribution'),
                **kwargs
            }
            
            self.lexicon[category][word] = word_entry
            
            # Update metadata
            self.lexicon['metadata']['last_updated'] = datetime.now().isoformat()
            self.lexicon['metadata']['total_words'] = self.count_total_words()
            
            return self.save_lexicon()
            
        except Exception as e:
            print(f"Error adding word: {e}")
            return False
    
    def remove_word(self, word: str, category: str) -> bool:
        """Remove a word from the lexicon"""
        try:
            word = word.lower().strip()
            
            if category in self.lexicon and word in self.lexicon[category]:
                del self.lexicon[category][word]
                
                # Update metadata
                self.lexicon['metadata']['last_updated'] = datetime.now().isoformat()
                self.lexicon['metadata']['total_words'] = self.count_total_words()
                
                return self.save_lexicon()
            
            return False
            
        except Exception as e:
            print(f"Error removing word: {e}")
            return False
    
    def update_word(self, word: str, category: str, **updates) -> bool:
        """Update an existing word in the lexicon"""
        try:
            word = word.lower().strip()
            
            if category in self.lexicon and word in self.lexicon[category]:
                self.lexicon[category][word].update(updates)
                self.lexicon[category][word]['last_modified'] = datetime.now().isoformat()
                
                # Update metadata
                self.lexicon['metadata']['last_updated'] = datetime.now().isoformat()
                
                return self.save_lexicon()
            
            return False
            
        except Exception as e:
            print(f"Error updating word: {e}")
            return False
    
    def search_words(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """Search for words in the lexicon"""
        results = []
        query = query.lower().strip()
        
        categories_to_search = [category] if category else self.lexicon.keys()
        
        for cat in categories_to_search:
            if cat == 'metadata':
                continue
                
            if cat in self.lexicon:
                for word, details in self.lexicon[cat].items():
                    if (query in word or 
                        query in details.get('meaning', '').lower() or
                        any(query in str(v).lower() for v in details.values())):
                        
                        results.append({
                            'word': word,
                            'category': cat,
                            'details': details
                        })
        
        return results
    
    def get_category_stats(self) -> Dict:
        """Get statistics for each category"""
        stats = {}
        
        for category, words in self.lexicon.items():
            if category == 'metadata':
                continue
                
            stats[category] = {
                'word_count': len(words),
                'recent_additions': len([
                    w for w in words.values() 
                    if 'added_date' in w and 
                    (datetime.now() - datetime.fromisoformat(w['added_date'])).days <= 7
                ])
            }
        
        return stats
    
    def count_total_words(self) -> int:
        """Count total words in lexicon"""
        total = 0
        for category, words in self.lexicon.items():
            if category != 'metadata':
                total += len(words)
        return total
    
    def export_to_csv(self, filename: str) -> bool:
        """Export lexicon to CSV for training data"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['word', 'category', 'meaning', 'sentiment', 'context', 'intensity'])
                
                for category, words in self.lexicon.items():
                    if category == 'metadata':
                        continue
                    
                    # Determine sentiment based on category
                    sentiment = 0  # neutral
                    if category == 'positive':
                        sentiment = 2
                    elif category == 'negative':
                        sentiment = 0
                    else:
                        sentiment = 1
                    
                    for word, details in words.items():
                        writer.writerow([
                            word,
                            category,
                            details.get('meaning', ''),
                            sentiment,
                            details.get('context', ''),
                            details.get('intensity', 'medium')
                        ])
            
            return True
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    def import_from_csv(self, filename: str) -> bool:
        """Import words from CSV file"""
        try:
            with open(filename, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    word = row.get('word', '').strip()
                    category = row.get('category', 'common_words')
                    meaning = row.get('meaning', '')
                    
                    if word and meaning:
                        self.add_word(
                            word, 
                            category, 
                            meaning,
                            context=row.get('context', ''),
                            intensity=row.get('intensity', 'medium'),
                            source='csv_import'
                        )
            
            return True
            
        except Exception as e:
            print(f"Error importing from CSV: {e}")
            return False
    
    def generate_training_sentences(self, count: int = 100) -> List[Tuple[str, int]]:
        """Generate training sentences using the lexicon"""
        sentences = []
        
        # Sentence templates
        templates = {
            'positive': [
                "Ke {positive} {political}",
                "{political} e {positive} thata",
                "Batho ba {positive} {political}",
                "{political} o dira {positive}",
                "Re {positive} ka {political}"
            ],
            'negative': [
                "Ke {negative} {political}",
                "{political} e {negative} thata", 
                "Batho ba {negative} {political}",
                "{political} o dira {negative}",
                "Re {negative} ka {political}"
            ],
            'neutral': [
                "Ke bona {political}",
                "{political} e teng",
                "Batho ba bua ka {political}",
                "Re itse {political}",
                "{political} o kae"
            ]
        }
        
        # Generate sentences
        import random
        
        for _ in range(count):
            sentiment_type = random.choice(['positive', 'negative', 'neutral'])
            template = random.choice(templates[sentiment_type])
            
            # Fill template
            if '{positive}' in template:
                pos_word = random.choice(list(self.lexicon['positive'].keys()))
                template = template.replace('{positive}', pos_word)
            
            if '{negative}' in template:
                neg_word = random.choice(list(self.lexicon['negative'].keys()))
                template = template.replace('{negative}', neg_word)
            
            if '{political}' in template:
                pol_word = random.choice(list(self.lexicon['political'].keys()))
                template = template.replace('{political}', pol_word)
            
            # Assign sentiment label
            label = 1  # neutral
            if sentiment_type == 'positive':
                label = 2
            elif sentiment_type == 'negative':
                label = 0
            
            sentences.append((template, label))
        
        return sentences

# Global lexicon manager instance
lexicon_manager = SetswanaLexiconManager()