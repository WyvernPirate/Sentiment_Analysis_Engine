import re
from transformers import pipeline


class SentimentService:
    def __init__(self):
        self._pipeline = None
        
        # Fallback trigger words for basic sentiment analysis (used if transformer fails)
        self.positive_trigger_words = {
            'good', 'great', 'excellent', 'amazing', 'love', 'like', 'happy',
            'success', 'strong', 'improve', 'improved', 'progress', 'positive',
            'promising', 'growth', 'stable', 'effective', 'beneficial', 'advantage',
            'prosperous', 'thriving', 'secure', 'peaceful', 'hopeful', 'inspiring'
        }
        self.negative_trigger_words = {
            'bad', 'terrible', 'awful', 'hate', 'dislike', 'sad', 'angry',
            'weak', 'worse', 'failed', 'failure', 'corrupt', 'negative',
            'stagnant', 'failing', 'crisis', 'decline', 'unstable', 'corrupt',
            'poverty', 'protest', 'unemployment', 'debt', 'threat', 'danger'
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

    def extract_sentiment_trigger_words(self, text, target_sentiment=None):
        """
        Identifies words that influenced the sentiment by testing model sensitivity (LOO approach).
        If target_sentiment is provided, it specifically looks for words influencing that label.
        """
        words = re.findall(r'\b\w+\b', text)
        if not words or len(words) > 50: # Limit length to avoid explosion
            return self.extract_basic_trigger_words(text)

        try:
            if not self.pipeline:
                return self.extract_basic_trigger_words(text)

            # Get baseline prediction
            baseline = self.pipeline(text, top_k=None)
            baseline_scores = {r['label']: r['score'] for r in baseline}
            
            # If no target, use the most likely one
            if not target_sentiment:
                target_sentiment = max(baseline_scores, key=baseline_scores.get)
            
            # Handle label mapping (same as in analyze_english_sentiment)
            label_mapping = {
                'LABEL_0': 'negative', 'LABEL_1': 'neutral', 'LABEL_2': 'positive',
                'NEGATIVE': 'negative', 'NEUTRAL': 'neutral', 'POSITIVE': 'positive'
            }
            
            # Find the internal label for the target sentiment
            target_label = next((k for k, v in label_mapping.items() if v == target_sentiment), target_sentiment)
            baseline_score = baseline_scores.get(target_label, 0)

            # Test each word (Leave-One-Out)
            impacts = []
            for i in range(len(words)):
                # Skip small common words to save time/noise
                if len(words[i]) < 3: continue
                
                perturbed_text = " ".join(words[:i] + words[i+1:])
                p_res = self.pipeline(perturbed_text, top_k=None)
                p_score = next((r['score'] for r in p_res if r['label'] == target_label), 0)
                
                # Impact is how much the score DROPPED when word was removed
                impact = baseline_score - p_score
                if impact > 0.005: # Lowered threshold for more sensitivity
                    impacts.append((words[i].lower(), impact))

            # Sort by impact
            impacts.sort(key=lambda x: x[1], reverse=True)
            
            # If no significant impacts found, fall back to basic lexicon matching
            if not impacts:
                return self.extract_basic_trigger_words(text)
            
            # Split into pos/neg based on target sentiment
            res = {'positive': [], 'negative': []}
            if target_sentiment == 'positive':
                res['positive'] = [w for w, i in impacts[:8]] # Show up to 8 words
            elif target_sentiment == 'negative':
                res['negative'] = [w for w, i in impacts[:8]]
            else:
                return self.extract_basic_trigger_words(text)
            
            return res

        except Exception as e:
            print(f"Model-aware extraction failed: {e}")
            return self.extract_basic_trigger_words(text)

    def extract_basic_trigger_words(self, text):
        """Fallback to lexicon-based extraction."""
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

# Singleton instance - import and use as `sentiment_service.method_name()`
sentiment_service = SentimentService()