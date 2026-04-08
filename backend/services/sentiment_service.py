import re
from transformers import pipeline


class SentimentService:
    def __init__(self):
        self._pipeline = None
        
        # Fallback trigger words for basic sentiment analysis (used if transformer fails)
        self.positive_trigger_words = {
            'good', 'great', 'excellent', 'amazing', 'love', 'like', 'happy',
            'success', 'strong', 'improve', 'improved', 'progress', 'positive'
        }
        self.negative_trigger_words = {
            'bad', 'terrible', 'awful', 'hate', 'dislike', 'sad', 'angry',
            'weak', 'worse', 'failed', 'failure', 'corrupt', 'negative'
        }
        
        # Hardcoded Botswana political entities (parties, leaders, locations)
        # These are matched post-preprocessing for UI display in Political Entities section
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

    def analyze_english_sentiment(self, text):
        try:
            if self.pipeline:
                result = self.pipeline(text)
                # Handle label variations from different transformer versions
                label_mapping = {
                    'LABEL_0': 'negative', 'LABEL_1': 'neutral', 'LABEL_2': 'positive',
                    'NEGATIVE': 'negative', 'NEUTRAL': 'neutral', 'POSITIVE': 'positive'
                }
                sentiment = label_mapping.get(result[0]['label'], result[0]['label'].lower())
                return sentiment, result[0]['score'], {
                    'model': 'cardiffnlp/twitter-roberta-base-sentiment-latest'
                }
        except Exception:
            pass
        # Fall back to basic sentiment if transformer unavailable
        return self.analyze_basic_sentiment(text)

    def analyze_basic_sentiment(self, text):
        positive_words = self.positive_trigger_words
        negative_words = self.negative_trigger_words
        
        words = re.findall(r'\b\w+\b', text.lower())
        pos_count = sum(1 for word in words if word in positive_words)
        neg_count = sum(1 for word in words if word in negative_words)
        
        if pos_count > neg_count:
            return "positive", min(0.8, 0.6 + (pos_count - neg_count) * 0.1), {'model': 'basic'}
        elif neg_count > pos_count:
            return "negative", min(0.8, 0.6 + (neg_count - pos_count) * 0.1), {'model': 'basic'}
        return "neutral", 0.5, {'model': 'basic'}

    def extract_sentiment_trigger_words(self, text):
        words = [match.group(0).lower() for match in re.finditer(r'\b\w+\b', text)]

        positive = []
        negative = []
        seen_positive = set()
        seen_negative = set()

        for word in words:
            if word in self.positive_trigger_words and word not in seen_positive:
                seen_positive.add(word)
                positive.append(word)
            if word in self.negative_trigger_words and word not in seen_negative:
                seen_negative.add(word)
                negative.append(word)

        return {
            'positive': positive,
            'negative': negative
        }

    def match_political_words(self, text, lexicon):
        matches = []
        political_terms = lexicon.get('political', {})

        for token in re.finditer(r'\b\w+\b', text):
            term = token.group(0).lower()
            if term in political_terms:
                matches.append({
                    'term': term,
                    'meaning': political_terms.get(term, ''),
                    'start': token.start(),
                    'end': token.end()
                })

        return matches

    def extract_political_entities(self, text):
        text_lower = text.lower()
        entities = []

        # Check for party matches
        for party, full in self.political_entities['parties'].items():
            if party.lower() in text_lower or full.lower() in text_lower:
                entities.append({'entity': party, 'type': 'party', 'full_name': full})
        
        # Check for leader matches
        for leader, full in self.political_entities['leaders'].items():
            if leader.lower() in text_lower or full.lower() in text_lower:
                entities.append({'entity': leader, 'type': 'leader', 'full_name': full})

        return entities


# Singleton instance - import and use as `sentiment_service.method_name()`
sentiment_service = SentimentService()