export interface SentimentResult {
    sentiment: string;
    confidence: number;
    model_used: string;
    word_count: number;
    matched_political_words: Array<{ term: string; meaning: string; start: number; end: number }>;
    sentiment_words: {
        positive: string[];
        negative: string[];
    };
    political_context: {
        entities: Array<{ entity: string; type: string; full_name?: string; description?: string }>;
        keywords: Array<{ term: string; meaning: string; language: string }>;
    };
    error?: string;
}

export interface TestExample {
    text: string;
    description: string;
    expected: string;
}

export interface HealthStatus {
    status: string;
    lexicon_stats?: {
        setswana_words: number;
        political_terms: number;
    };
}

export interface PoliticalEntity {
    id: number;
    entity: string;
    type: string;
    full_name?: string;
    description?: string;
    created_at: string;
}

export interface SocialHealthStatus {
    status: string;
    provider_default?: string;
    brightdata_configured?: boolean;
    apify_configured?: boolean;
    twikit_configured?: boolean;
}

export interface SocialCollection {
    collection_id: string;
    source: string;
    query: string;
    count: number;
    raw_file: string;
    collected_at_utc: string;
    run_meta?: Record<string, unknown>;
}
