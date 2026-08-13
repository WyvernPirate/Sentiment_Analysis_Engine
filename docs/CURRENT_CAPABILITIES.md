# Current System Capabilities

This document tracks the implemented features and the current status of the Sentiment Analysis Engine.

## Implemented Features

### 1. Sentiment Analysis
- **Transformer Integration**: Uses `cardiffnlp/twitter-roberta-base-sentiment-latest` (English) for sentiment classification. This is currently the only model used for scoring — Setswana and code-switched text are scored by this same English model, with no language-specific adaptation yet (see "In Progress / Planned").
- **Setswana Context**: A hand-curated lexicon of 84 political and cultural terms specific to Botswana, used for keyword tagging and relevance filtering. It does not currently influence the sentiment score itself.
- **Political Word Matching**: Pre-inference matching of political keywords, surfaced alongside the sentiment result for context.

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
- **Setswana-English Code-Switching**: Language detection and model routing for blended language sentences. (Note: an earlier version of this existed and was removed during a refactor; it is being rebuilt, not built for the first time.)
- **Advanced Trend Analysis**: Historical sentiment tracking for specific political entities.
- **Export Capabilities**: Export analyzed batches to CSV/Excel for external reporting.
- **System Logs UI**: Complete integration of backend logging with the frontend "System Logs" page.

---
*Last Updated: May 2026*
