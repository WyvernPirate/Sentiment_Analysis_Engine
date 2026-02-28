import re
import os
from transformers import pipeline

class SentimentService:
    def __init__(self):
        self.use_code_switching = os.environ.get('USE_CODE_SWITCHING', 'false').lower() == 'true'
        self._pipeline = None
        
        # Political entities for Botswana
        self.political_entities = {
            'parties': {
                'BDP': 'Botswana Democratic Party',
                'UDC': 'Umbrella for Democratic Change', 
                'BCP': 'Botswana Congress Party',
                'AP': 'Alliance for Progressives'
            },
            'leaders': {
                'Masisi': 'Mokgweetsi Masisi',
                'Boko': 'Duma Boko',
                'Saleshando': 'Dumelang Saleshando',
                'Khama': 'Ian Khama'
            },
            'locations': {
                'Gaborone': 'Capital city',
                'Francistown': 'Second largest city',
                'Maun': 'Tourism hub',
                'Serowe': 'Traditional capital'
            }
        }

    @property
    def pipeline(self):
        if self._pipeline is None:
            try:
                self._pipeline = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
                )
            except Exception as e:
                print(f"Failed to load transformers pipeline: {e}")
        return self._pipeline

    def detect_language(self, text, lexicon):
        """Enhanced language detection for Setswana-English code-switching"""
        if not self.use_code_switching:
            words = re.findall(r'\b\w+\b', text.lower())
            return "English", False, {
                'setswana_words_found': [],
                'setswana_ratio': 0.0,
                'total_words': len(words),
                'setswana_word_count': 0
            }

        words = re.findall(r'\b\w+\b', text.lower())
        total_words = len(words)

        if total_words == 0:
            return "unknown", False, {
                'setswana_words_found': [],
                'setswana_ratio': 0.0,
                'total_words': 0,
                'setswana_word_count': 0
            }

        setswana_count = 0
        detected_setswana_words = []

        for word in words:
            if word in lexicon.get('common_words', []):
                setswana_count += 1
                detected_setswana_words.append(word)
            elif word in lexicon.get('positive', {}):
                setswana_count += 1
                detected_setswana_words.append(f"{word} (positive)")
            elif word in lexicon.get('negative', {}):
                setswana_count += 1
                detected_setswana_words.append(f"{word} (negative)")
            elif word in lexicon.get('political', {}):
                setswana_count += 1
                detected_setswana_words.append(f"{word} (political)")

        setswana_ratio = setswana_count / total_words

        if setswana_ratio > 0.6:
            language = "Setswana"
            code_switching = False
        elif setswana_ratio > 0.1:
            language = "Setswana-English"
            code_switching = True
        else:
            language = "English"
            code_switching = False

        return language, code_switching, {
            'setswana_words_found': detected_setswana_words,
            'setswana_ratio': round(setswana_ratio, 2),
            'total_words': total_words,
            'setswana_word_count': setswana_count
        }

    def analyze_english_sentiment(self, text):
        """Analyze English sentiment using transformers with basic fallback"""
        try:
            if self.pipeline:
                result = self.pipeline(text)
                label_mapping = {
                    'LABEL_0': 'negative', 'LABEL_1': 'neutral', 'LABEL_2': 'positive',
                    'NEGATIVE': 'negative', 'NEUTRAL': 'neutral', 'POSITIVE': 'positive'
                }
                sentiment = label_mapping.get(result[0]['label'], result[0]['label'].lower())
                return sentiment, result[0]['score'], {'model': 'transformers'}
        except Exception:
            pass
        return self.analyze_basic_sentiment(text)

    def analyze_basic_sentiment(self, text):
        """Fallback basic sentiment analysis"""
        positive_words = {'good', 'great', 'excellent', 'amazing', 'love', 'like', 'happy'}
        negative_words = {'bad', 'terrible', 'awful', 'hate', 'dislike', 'sad', 'angry'}
        
        words = re.findall(r'\b\w+\b', text.lower())
        pos_count = sum(1 for word in words if word in positive_words)
        neg_count = sum(1 for word in words if word in negative_words)
        
        if pos_count > neg_count:
            return "positive", min(0.8, 0.6 + (pos_count - neg_count) * 0.1), {'model': 'basic'}
        elif neg_count > pos_count:
            return "negative", min(0.8, 0.6 + (neg_count - pos_count) * 0.1), {'model': 'basic'}
        return "neutral", 0.5, {'model': 'basic'}

    def analyze_setswana_sentiment(self, text, lexicon):
        """Analyze Setswana sentiment using lexicon"""
        words = re.findall(r'\b\w+\b', text.lower())
        pos_score = sum(1 for word in words if word in lexicon.get('positive', {}))
        neg_score = sum(1 for word in words if word in lexicon.get('negative', {}))
        
        if pos_score > neg_score:
            return "positive", min(0.9, 0.6 + (pos_score - neg_score) * 0.1)
        elif neg_score > pos_score:
            return "negative", min(0.9, 0.6 + (neg_score - pos_score) * 0.1)
        return "neutral", 0.5 if pos_score == 0 and neg_score == 0 else 0.6

    def extract_political_context(self, text, lexicon):
        """Extract political entities and keywords"""
        text_lower = text.lower()
        entities = []
        keywords = []
        
        for party, full in self.political_entities['parties'].items():
            if party.lower() in text_lower or full.lower() in text_lower:
                entities.append({'entity': party, 'type': 'party', 'full_name': full})
        
        for leader, full in self.political_entities['leaders'].items():
            if leader.lower() in text_lower or full.lower() in text_lower:
                entities.append({'entity': leader, 'type': 'leader', 'full_name': full})
        
        for term, meaning in lexicon.get('political', {}).items():
            if term in text_lower:
                keywords.append({'term': term, 'meaning': meaning, 'language': 'Setswana'})
                
        return entities, keywords

sentiment_service = SentimentService()