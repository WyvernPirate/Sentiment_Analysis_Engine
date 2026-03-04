export interface SentimentResult {
    sentiment: string;
    confidence: number;
    detected_language: string;
    code_switching_detected: boolean;
    model_used: string;
    language_analysis: {
        setswana_words_found: string[];
        setswana_ratio: number;
        total_words: number;
        setswana_word_count: number;
    };
    sentiment_analysis?: {
        model_used: string;
        english_analysis: {
            sentiment: string;
            confidence: number;
            details: any;
        };
        setswana_analysis: {
            sentiment: string;
            confidence: number;
            words: {
                positive: string[];
                negative: string[];
            };
        };
        combination_logic: string;
    };
    sentiment_words: {
        positive: string[];
        negative: string[];
    };
    political_context: {
        entities: Array<{ entity: string; type: string; full_name?: string; description?: string }>;
        keywords: Array<{ term: string; meaning: string; language: string }>;
    };
    text_length: number;
    word_count: number;
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
