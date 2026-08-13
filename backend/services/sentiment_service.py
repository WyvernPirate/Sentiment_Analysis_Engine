import re
from typing import List, Tuple, Dict, Optional

from config import Config

ENGLISH_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
# Multilingual model, already referenced in Config but previously never
# actually loaded by anything — this is the model that makes Setswana and
# code-switched text get genuinely different treatment instead of being
# scored by the English-only model like everything else.
MULTILINGUAL_MODEL = Config.FALLBACK_MODEL

LABEL_MAPPING = {
    'LABEL_0': 'negative', 'LABEL_1': 'neutral', 'LABEL_2': 'positive',
    'NEGATIVE': 'negative', 'NEUTRAL': 'neutral', 'POSITIVE': 'positive',
    'negative': 'negative', 'neutral': 'neutral', 'positive': 'positive',
}

# Setswana-word-ratio thresholds for language classification (see detect_language).
LOW_SETSWANA_RATIO = 0.1
HIGH_SETSWANA_RATIO = 0.6

# How much weight the lexicon polarity signal gets when blended with the
# multilingual model's score for Setswana/code-switched text. Kept modest —
# the model still leads, the lexicon nudges it — since the lexicon is a
# small hand-curated list, not a trained classifier.
LEXICON_BLEND_WEIGHT = 0.35


class SentimentService:
    def __init__(self):
        self._pipeline = None
        self._multilingual_pipeline = None

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
        """English-only sentiment pipeline."""
        if self._pipeline is None:
            try:
                # Imported lazily so the rest of the app (routes, migrations,
                # tests) can be loaded without requiring transformers/torch
                # to be installed unless sentiment inference actually runs.
                from transformers import pipeline as hf_pipeline
                self._pipeline = hf_pipeline("sentiment-analysis", model=ENGLISH_MODEL)
            except Exception as e:
                print(f"Failed to load transformers pipeline: {e}")
        return self._pipeline

    @property
    def multilingual_pipeline(self):
        """Multilingual sentiment pipeline, used for Setswana/code-switched text."""
        if self._multilingual_pipeline is None:
            try:
                from transformers import pipeline as hf_pipeline
                self._multilingual_pipeline = hf_pipeline("sentiment-analysis", model=MULTILINGUAL_MODEL)
            except Exception as e:
                print(f"Failed to load multilingual pipeline: {e}")
        return self._multilingual_pipeline

    # ------------------------------------------------------------------
    # Language detection
    # ------------------------------------------------------------------

    def detect_language(self, text: str, lexicon: Dict) -> Tuple[str, bool, Dict]:
        """Classify text as English / Setswana / Setswana-English (code-switched)
        by measuring what fraction of its words appear in the Setswana lexicon.

        `lexicon` is the legacy_lexicon shape from lexicon_service: a dict with
        'common_words' (a set) and 'positive'/'negative'/'political' (word -> meaning dicts).
        """
        words = re.findall(r'\b\w+\b', text.lower())
        total_words = len(words)

        if total_words == 0:
            return "unknown", False, {
                'setswana_words_found': [],
                'setswana_ratio': 0.0,
                'total_words': 0,
                'setswana_word_count': 0,
            }

        common_words = lexicon.get('common_words', set())
        positive = lexicon.get('positive', {})
        negative = lexicon.get('negative', {})
        political = lexicon.get('political', {})

        setswana_count = 0
        detected_setswana_words = []

        for word in words:
            if word in common_words:
                setswana_count += 1
                detected_setswana_words.append(word)
            elif word in positive:
                setswana_count += 1
                detected_setswana_words.append(f"{word} (positive)")
            elif word in negative:
                setswana_count += 1
                detected_setswana_words.append(f"{word} (negative)")
            elif word in political:
                setswana_count += 1
                detected_setswana_words.append(f"{word} (political)")

        setswana_ratio = setswana_count / total_words

        if setswana_ratio > HIGH_SETSWANA_RATIO:
            language, code_switching = "Setswana", False
        elif setswana_ratio > LOW_SETSWANA_RATIO:
            language, code_switching = "Setswana-English", True
        else:
            language, code_switching = "English", False

        return language, code_switching, {
            'setswana_words_found': detected_setswana_words,
            'setswana_ratio': round(setswana_ratio, 2),
            'total_words': total_words,
            'setswana_word_count': setswana_count,
        }

    # ------------------------------------------------------------------
    # English-only analysis (unchanged behavior, kept for the pure-English path
    # and as a fallback if the multilingual model fails to load)
    # ------------------------------------------------------------------

    def analyze_english_sentiment(self, text):
        try:
            if self.pipeline:
                result = self.pipeline(text)
                sentiment = LABEL_MAPPING.get(result[0]['label'], result[0]['label'].lower())
                return sentiment, result[0]['score'], {'model': ENGLISH_MODEL}
        except Exception:
            pass
        return self.analyze_basic_sentiment(text)

    def analyze_english_sentiment_batch(self, texts: List[str]) -> List[Tuple[str, float, Dict]]:
        """Process a list of English texts in one go for much better performance."""
        try:
            if self.pipeline:
                results = self.pipeline(texts, batch_size=8)
                output = []
                for res in results:
                    sentiment = LABEL_MAPPING.get(res['label'], res['label'].lower())
                    output.append((sentiment, res['score'], {'model': ENGLISH_MODEL}))
                return output
        except Exception as e:
            print(f"Batch analysis failed: {e}")

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

    # ------------------------------------------------------------------
    # Lexicon polarity + blending, for the Setswana/code-switched path
    # ------------------------------------------------------------------

    def _lexicon_polarity(self, text: str, lexicon: Dict) -> float:
        """A simple signed polarity score in [-1, 1] from lexicon word counts."""
        words = re.findall(r'\b\w+\b', text.lower())
        positive = lexicon.get('positive', {})
        negative = lexicon.get('negative', {})
        pos_count = sum(1 for w in words if w in positive)
        neg_count = sum(1 for w in words if w in negative)

        if pos_count + neg_count == 0:
            return 0.0
        return (pos_count - neg_count) / (pos_count + neg_count)

    def _blend_with_lexicon(self, model_sentiment: str, model_confidence: float, lexicon_polarity: float) -> Tuple[str, float]:
        """Blend a model's sentiment/confidence with the lexicon polarity signal.

        Both signals are converted to a signed score in [-1, 1], linearly
        blended, then mapped back to a label. The model dominates
        (LEXICON_BLEND_WEIGHT < 0.5) since the lexicon is a small hand-curated
        word list, not a trained classifier — it nudges borderline cases
        rather than overriding the model outright.
        """
        model_score = {'positive': 1.0, 'neutral': 0.0, 'negative': -1.0}.get(model_sentiment, 0.0) * model_confidence
        blended_score = (1 - LEXICON_BLEND_WEIGHT) * model_score + LEXICON_BLEND_WEIGHT * lexicon_polarity

        if blended_score > 0.15:
            sentiment = 'positive'
        elif blended_score < -0.15:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'

        confidence = round(min(0.99, max(0.5, abs(blended_score))), 3)
        return sentiment, confidence

    # ------------------------------------------------------------------
    # Language-aware entry points — these are what routes should call
    # ------------------------------------------------------------------

    def analyze_sentiment(self, text: str, lexicon: Dict, use_code_switching: bool = True) -> Tuple[str, float, Dict]:
        """Detect language, then route to the appropriate model:
        - English -> the English-only model (unchanged from before)
        - Setswana / Setswana-English -> the multilingual model, with its
          score blended against a lexicon polarity signal

        Falls back to the English model if the multilingual pipeline can't
        be loaded, so behavior degrades gracefully rather than erroring.
        """
        if not use_code_switching:
            sentiment, confidence, details = self.analyze_english_sentiment(text)
            details = {**details, 'language_detected': 'English', 'code_switching': False}
            return sentiment, confidence, details

        language, code_switching, lang_details = self.detect_language(text, lexicon)

        if language != 'Setswana' and language != 'Setswana-English':
            sentiment, confidence, details = self.analyze_english_sentiment(text)
            details = {**details, 'language_detected': language, 'code_switching': code_switching}
            return sentiment, confidence, details

        try:
            if not self.multilingual_pipeline:
                raise RuntimeError('multilingual pipeline unavailable')
            result = self.multilingual_pipeline(text)
            model_sentiment = LABEL_MAPPING.get(result[0]['label'], result[0]['label'].lower())
            model_confidence = result[0]['score']
        except Exception as e:
            print(f"Multilingual pipeline failed, falling back to English model: {e}")
            sentiment, confidence, details = self.analyze_english_sentiment(text)
            details = {
                **details,
                'language_detected': language,
                'code_switching': code_switching,
                'fallback_reason': 'multilingual_pipeline_unavailable',
            }
            return sentiment, confidence, details

        lexicon_polarity = self._lexicon_polarity(text, lexicon)
        sentiment, confidence = self._blend_with_lexicon(model_sentiment, model_confidence, lexicon_polarity)

        return sentiment, confidence, {
            'model': MULTILINGUAL_MODEL,
            'language_detected': language,
            'code_switching': code_switching,
            'lexicon_polarity': round(lexicon_polarity, 2),
            'model_sentiment': model_sentiment,
            'model_confidence': round(model_confidence, 3),
        }

    def analyze_batch_with_routing(self, texts: List[str], lexicon: Dict, use_code_switching: bool = True) -> List[Tuple[str, float, Dict]]:
        """Batch version of analyze_sentiment: splits texts by detected language,
        batches each group through the appropriate model (keeping the real
        perf win of batched inference), then reassembles results in order.
        """
        if not use_code_switching:
            results = self.analyze_english_sentiment_batch(texts)
            return [
                (s, c, {**d, 'language_detected': 'English', 'code_switching': False})
                for s, c, d in results
            ]

        detections = [self.detect_language(t, lexicon) for t in texts]
        english_idx = [i for i, (lang, _, _) in enumerate(detections) if lang not in ('Setswana', 'Setswana-English')]
        other_idx = [i for i, (lang, _, _) in enumerate(detections) if lang in ('Setswana', 'Setswana-English')]

        results: List[Optional[Tuple[str, float, Dict]]] = [None] * len(texts)

        if english_idx:
            english_results = self.analyze_english_sentiment_batch([texts[i] for i in english_idx])
            for idx, (sentiment, confidence, details) in zip(english_idx, english_results):
                language, code_switching, _ = detections[idx]
                results[idx] = (sentiment, confidence, {**details, 'language_detected': language, 'code_switching': code_switching})

        if other_idx:
            other_texts = [texts[i] for i in other_idx]
            try:
                if not self.multilingual_pipeline:
                    raise RuntimeError('multilingual pipeline unavailable')
                multi_results = self.multilingual_pipeline(other_texts, batch_size=8)
            except Exception as e:
                print(f"Multilingual batch failed, falling back to English model: {e}")
                fallback_results = self.analyze_english_sentiment_batch(other_texts)
                for idx, (sentiment, confidence, details) in zip(other_idx, fallback_results):
                    language, code_switching, _ = detections[idx]
                    results[idx] = (sentiment, confidence, {
                        **details,
                        'language_detected': language,
                        'code_switching': code_switching,
                        'fallback_reason': 'multilingual_pipeline_unavailable',
                    })
            else:
                for idx, res in zip(other_idx, multi_results):
                    language, code_switching, _ = detections[idx]
                    model_sentiment = LABEL_MAPPING.get(res['label'], res['label'].lower())
                    model_confidence = res['score']
                    lexicon_polarity = self._lexicon_polarity(texts[idx], lexicon)
                    sentiment, confidence = self._blend_with_lexicon(model_sentiment, model_confidence, lexicon_polarity)
                    results[idx] = (sentiment, confidence, {
                        'model': MULTILINGUAL_MODEL,
                        'language_detected': language,
                        'code_switching': code_switching,
                        'lexicon_polarity': round(lexicon_polarity, 2),
                        'model_sentiment': model_sentiment,
                        'model_confidence': round(model_confidence, 3),
                    })

        return results

    # ------------------------------------------------------------------
    # Trigger words / political word matching (English-model-based; language
    # routing does not extend to the Leave-One-Out extractor below, since it
    # would require perturbation testing against whichever model was used —
    # left as a known scope boundary rather than silently mixed behavior)
    # ------------------------------------------------------------------

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

            # Determine target sentiment if not provided
            if not target_sentiment:
                top_res = max(baseline, key=lambda x: x['score'])
                target_sentiment = LABEL_MAPPING.get(top_res['label'], 'neutral')

            if target_sentiment == 'neutral':
                # For neutral sentiment, we just return basic lexicon or nothing
                # as "influence" on neutral is harder to define clearly for a cloud
                return self.extract_basic_trigger_words(text)

            # Find all internal labels that map to our target sentiment
            target_labels = [k for k, v in LABEL_MAPPING.items() if v == target_sentiment]
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
