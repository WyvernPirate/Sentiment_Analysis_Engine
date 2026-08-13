import re
from typing import List, Tuple, Dict


class SentimentService:
    def __init__(self):
        self._pipeline = None
        
        # Fallback trigger words for basic sentiment analysis (used if transformer fails)
        self.positive_trigger_words = {
            'good', 'great', 'excellent', 'amazing', 'love', 'like', 'happy',
            'success', 'strong', 'improve', 'improved', 'progress', 'positive',
            'promising', 'growth', 'stable', 'effective', 'beneficial', 'advantage',
            'prosperous', 'thriving', 'secure', 'peaceful', 'hopeful', 'inspiring',
            'leadership', 'visionary', 'lead', 'leading', 'win', 'winning'
        }
        self.negative_trigger_words = {
            'bad', 'terrible', 'awful', 'hate', 'dislike', 'sad', 'angry',
            'weak', 'worse', 'failed', 'failure', 'corrupt', 'negative',
            'stagnant', 'failing', 'crisis', 'decline', 'unstable', 'corrupt',
            'poverty', 'protest', 'unemployment', 'debt', 'threat', 'danger',
            'slow', 'ineffective', 'lacks', 'lacking', 'losing', 'ground', 'poor',
            'fail', 'inefficient', 'corrupt', 'scandal', 'unrest'
        }

    @property
    def pipeline(self):
        if self._pipeline is None:
            try:
                # Imported lazily so the rest of the app (routes, migrations,
                # tests) can be loaded without requiring transformers/torch
                # to be installed unless sentiment inference actually runs.
                from transformers import pipeline as hf_pipeline
                self._pipeline = hf_pipeline(
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
        return self.analyze_basic_sentiment(text)

    def analyze_english_sentiment_batch(self, texts: List[str]) -> List[Tuple[str, float, Dict]]:
        """Process a list of texts in one go for much better performance."""
        try:
            if self.pipeline:
                # Transformers pipeline handles lists efficiently
                results = self.pipeline(texts, batch_size=8) # Small batch size for safety
                label_mapping = {
                    'LABEL_0': 'negative', 'LABEL_1': 'neutral', 'LABEL_2': 'positive',
                    'NEGATIVE': 'negative', 'NEUTRAL': 'neutral', 'POSITIVE': 'positive'
                }
                
                output = []
                for res in results:
                    sentiment = label_mapping.get(res['label'], res['label'].lower())
                    output.append((sentiment, res['score'], {
                        'model': 'cardiffnlp/twitter-roberta-base-sentiment-latest'
                    }))
                return output
        except Exception as e:
            print(f"Batch analysis failed: {e}")
            pass
            
        # Fallback to individual basic analysis if batching fails
        return [self.analyze_basic_sentiment(t) for t in texts]

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

    def extract_sentiment_trigger_words(self, text, target_sentiment=None, exclude_words=None):
        """
        Identifies words that heavily influence the sentiment score.
        Uses a Leave-One-Out (LOO) approach to measure how each word's absence changes the target score.
        """
        if exclude_words is None:
            exclude_words = set()
        else:
            exclude_words = {w.lower() for w in exclude_words}

        if not text or len(text.strip()) == 0:
            return {'positive': [], 'negative': []}

        # Clean text for tokenization
        words = re.findall(r'\b\w+\b', text)
        if not words:
            return {'positive': [], 'negative': []}
            
        # Limit length to avoid performance explosion on long texts
        if len(words) > 80:
            words = words[:80]

        try:
            if not self.pipeline:
                return self.extract_basic_trigger_words(text)

            # 1. Get baseline prediction for all labels
            baseline = self.pipeline(text, top_k=None)
            baseline_scores = {r['label']: r['score'] for r in baseline}
            
            # Map labels to our standard categories
            label_mapping = {
                'LABEL_0': 'negative', 'LABEL_1': 'neutral', 'LABEL_2': 'positive',
                'NEGATIVE': 'negative', 'NEUTRAL': 'neutral', 'POSITIVE': 'positive',
                'negative': 'negative', 'neutral': 'neutral', 'positive': 'positive'
            }
            
            # Determine target sentiment if not provided
            if not target_sentiment:
                top_res = max(baseline, key=lambda x: x['score'])
                target_sentiment = label_mapping.get(top_res['label'], 'neutral')

            if target_sentiment == 'neutral':
                # For neutral sentiment, we just return basic lexicon or nothing 
                # as "influence" on neutral is harder to define clearly for a cloud
                return self.extract_basic_trigger_words(text)

            # Find all internal labels that map to our target sentiment
            target_labels = [k for k, v in label_mapping.items() if v == target_sentiment]
            if not target_labels:
                return self.extract_basic_trigger_words(text)

            # Baseline score is the sum of scores for all labels matching the target sentiment
            baseline_score = sum(baseline_scores.get(lbl, 0) for lbl in target_labels)

            # 2. Test each word's impact (Leave-One-Out)
            impacts = []
            # Expanded stopwords to filter out common noise
            skip_words = {
                'the', 'and', 'for', 'was', 'with', 'this', 'that', 'are', 'were', 'been', 'has', 'have', 'had', 
                'its', 'their', 'there', 'who', 'whom', 'which', 'what', 'where', 'when', 'how', 'why', 'can', 
                'could', 'should', 'would', 'may', 'might', 'must', 'into', 'onto', 'upon', 'from', 'than', 'then', 
                'else', 'will', 'very', 'only', 'just', 'more', 'most', 'some', 'many', 'much', 'such', 'both', 
                'each', 'any', 'none', 'all', 'both', 'half', 'few', 'your', 'ours', 'theirs', 'being', 'those', 
                'these', 'about', 'between', 'during', 'before', 'after', 'above', 'below', 'under', 'again', 
                'further', 'once', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 
                'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 
                'so', 'than', 'too', 'very', 'can', 'will', 'just', 'should', 'now', 'system'
            }
            
            for i in range(len(words)):
                word_lower = words[i].lower()
                # Skip small words, stopwords, purely numeric tokens, or excluded words (entities)
                if len(word_lower) < 3 or word_lower in skip_words or word_lower.isdigit() or word_lower in exclude_words:
                    continue
                
                # Create text without this word
                perturbed_text = " ".join(words[:i] + words[i+1:])
                if not perturbed_text.strip():
                    continue
                    
                p_res = self.pipeline(perturbed_text, top_k=None)
                p_score = sum(r['score'] for r in p_res if r['label'] in target_labels)
                
                # Impact: how much the target sentiment score drops when word is removed
                impact = baseline_score - p_score
                
                # We also consider if removing the word INCREASES the score (anti-trigger)
                # but for a word cloud, we want the words that CONTRIBUTE to the score.
                if impact > 0.001: # Very low threshold to catch more keywords
                    impacts.append((words[i], impact))

            # 3. Sort by impact and format results
            impacts.sort(key=lambda x: x[1], reverse=True)
            
            # Take top 10 most influential words
            top_words = [w for w, i in impacts[:10]]
            
            res = {'positive': [], 'negative': []}
            if target_sentiment == 'positive':
                res['positive'] = top_words
            elif target_sentiment == 'negative':
                res['negative'] = top_words
                
            # If model found nothing, fallback to lexicon
            if not any(res.values()):
                return self.extract_basic_trigger_words(text)
                
            return res

        except Exception as e:
            print(f"Model-aware extraction failed: {e}")
            return self.extract_basic_trigger_words(text)

    def extract_basic_trigger_words(self, text, exclude_words=None):
        """Fallback to lexicon-based extraction."""
        if exclude_words is None:
            exclude_words = set()
        else:
            exclude_words = {w.lower() for w in exclude_words}

        words = [match.group(0).lower() for match in re.finditer(r'\b\w+\b', text)]
        positive = []
        negative = []
        seen = set()

        for word in words:
            if word in seen or word in exclude_words or len(word) < 3:
                continue
                
            if word in self.positive_trigger_words:
                positive.append(word)
                seen.add(word)
            elif word in self.negative_trigger_words:
                negative.append(word)
                seen.add(word)

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