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

export interface SocialInputItem {
    url?: string;
    text?: string;
    author?: string;
    created_at?: string;
}

export interface SocialCollectResponse {
    collection_id: string;
    source: string;
    provider: string;
    query: string;
    count: number;
    raw_file: string;
    meta?: {
        auto_cleaned?: boolean;
        cleaning_report?: {
            cleaned_records: number;
            total_records: number;
        };
        [key: string]: any;
    };
    records_preview?: Array<Record<string, any>>;
    error?: string;
}

export interface SocialCleanResponse {
    collection_id: string;
    raw_count: number;
    cleaned_count: number;
    filter_mode: 'relaxed' | 'strict';
    cleaned_file: string;
    report_file: string;
    report?: Record<string, unknown>;
    error?: string;
}

// --- Batch Analysis Types ---

export interface AnalyzedRow {
    row_index: number;
    text: string;
    sentiment: string;
    confidence: number;
    model_used: string;
    trigger_words: {
        positive: string[];
        negative: string[];
    };
    political_words: Array<{ term: string; meaning: string }>;
    entities: Array<{ entity: string; type: string }>;
    meta: {
        author: string;
        date: string;
        source: string;
        url: string;
    };
}

export interface AggregateStats {
    total_rows: number;
    sentiment_distribution: {
        positive: number;
        neutral: number;
        negative: number;
    };
    avg_confidence: number;
    top_trigger_words: Array<{ word: string; count: number; type: string }>;
    top_entities: Array<{ entity: string; count: number }>;
    top_positive_entities?: Array<{ entity: string; count: number }>;
    top_negative_entities?: Array<{ entity: string; count: number }>;
    model_used: string;
}

export interface BatchAnalysisResult {
    job_id: string;
    collection_id: string;
    filename: string;
    analyzed_at: string;
    rows: AnalyzedRow[];
    aggregate: AggregateStats;
    error?: string;
}

export interface AnalysisJob {
    job_id: string;
    collection_id: string;
    filename: string;
    analyzed_at: string;
    row_count: number;
    sentiment_summary: {
        positive: number;
        neutral: number;
        negative: number;
    };
}
export interface SystemHealth {
    status: string;
    timestamp: number;
    os: {
        system: string;
        release: string;
        machine: string;
    };
    resources: {
        cpu_usage: string;
        memory_usage: string;
        disk_usage: string;
    };
    services: Array<{
        name: string;
        status: string;
        latency: string;
    }>;
}
