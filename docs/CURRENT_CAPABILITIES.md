# Current System Capabilities

This document tracks the implemented features and the current status of the Sentiment Analysis Engine.

## Implemented Features

### 1. Sentiment Analysis
- **Language-Aware Model Routing**: Text is classified as English, Setswana, or Setswana-English (code-switched) by measuring what fraction of its words appear in the Setswana lexicon. English text is scored by `cardiffnlp/twitter-roberta-base-sentiment-latest`; Setswana and code-switched text is routed instead to `cardiffnlp/twitter-xlm-roberta-base-sentiment-latest`, a multilingual model — no longer scored by the English-only model like everything else used to be.
- **Lexicon-Weighted Hybrid Scoring**: For Setswana/code-switched text, the multilingual model's output is blended with a lexicon polarity signal (positive/negative word counts), so hand-curated domain vocabulary can nudge borderline cases rather than being purely decorative.
- **Setswana Context**: A hand-curated lexicon of 94 political and cultural terms specific to Botswana — used both for language detection/hybrid scoring above, and for keyword tagging and relevance filtering elsewhere in the app.
- **Political Word Matching**: Pre-inference matching of political keywords, surfaced alongside the sentiment result for context.
- **Toggle**: Set `USE_CODE_SWITCHING=false` to force English-only scoring for all text (e.g. to avoid loading a second model).

### 2. Lexicon Management
- **Dynamic Updates**: Add words via UI; available for analysis immediately without restart.
- **Categorization**: Words categorized by sentiment (pos/neg), political context, or Botswana-specific cultural terms.
- **Search & Stats**: Full search capability and category-wise statistics.

### 3. Political Entity Management
- **SQLite Storage**: Persistent storage of political parties, leaders, and locations.
- **Entity Extraction**: Automatic identification of tracked entities in analyzed text.
- **CRUD UI**: Complete management interface for entities.

### 4. Data Collection & Ingest
- **CSV Ingest**: Upload datasets (e.g., from manual collection or other tools) for batch analysis.
- **Social Media Pipelines**: Modular service structure ready for X (Bright Data/Apify/Twikit) and Facebook integration.
- **Raw Data Management**: Automatic logging and storage of collected batches by date.

### 5. Analytics Dashboard
- **Real-time Overview**: Key metrics and sentiment distribution.
- **Batch Processing**: Run sentiment analysis on entire collections.
- **Trend Visualization**: (In Progress) Visual representation of sentiment shifts.

## In Progress / Planned
- **Fine-Tuned Setswana Model**: The current approach (language routing + lexicon-weighted hybrid) requires no training and is real/working today. A genuinely fine-tuned model is a possible next step, but needs a real hand-labeled Setswana dataset first — a synthetic, template-generated dataset exists in git history but isn't a substitute for organic labeled text, so this is intentionally not attempted yet rather than done on weak data.
- **Advanced Trend Analysis**: Historical sentiment tracking for specific political entities.
- **Export Capabilities**: Export analyzed batches to CSV/Excel for external reporting.
- **System Logs UI**: Complete integration of backend logging with the frontend "System Logs" page.

## Known Limitations
- The Setswana lexicon (94 words) is hand-curated, not corpus-derived — coverage of real political discourse is necessarily partial. Growing it further is best done with native-speaker review rather than continued unilateral expansion.
- Leave-One-Out trigger-word extraction (the word-importance highlighting on the single-text analysis page) still runs against the English model only, regardless of detected language — this is a known scope boundary, not a bug.

---
*Last Updated: August 2026*
