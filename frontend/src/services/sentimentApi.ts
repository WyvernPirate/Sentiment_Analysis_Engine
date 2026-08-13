import {
    SentimentResult,
    TestExample,
    HealthStatus,
    PoliticalEntity,
    EntityStatsResponse,
    SocialHealthStatus,
    SocialCollection,
    SocialInputItem,
    SocialCollectResponse,
    SocialCleanResponse,
    BatchAnalysisResult,
    AnalysisJob,
    SystemHealth,
    LexiconStats,
    LexiconSearchResult,
} from '../types/sentiment';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

interface ApiResult<T> {
    ok: boolean;
    data: T | null;
    error: string | null;
}

// Single fetch wrapper used by every method below: one place that handles
// JSON headers (skipped for FormData bodies), non-OK responses, and network
// failures, instead of ~20 hand-rolled try/catch/fetch blocks each with
// their own slightly-different error convention.
async function request<T>(path: string, init?: RequestInit): Promise<ApiResult<T>> {
    try {
        const isFormData = init?.body instanceof FormData;
        const response = await fetch(`${API_BASE_URL}${path}`, {
            ...init,
            headers: isFormData
                ? init?.headers
                : { 'Content-Type': 'application/json', ...(init?.headers || {}) },
        });

        const data = await response.json().catch(() => null);

        if (!response.ok) {
            const message =
                data && typeof data === 'object' && 'error' in data
                    ? String((data as { error: unknown }).error)
                    : `Request failed (${response.status})`;
            return { ok: false, data: null, error: message };
        }

        return { ok: true, data: data as T, error: null };
    } catch {
        return { ok: false, data: null, error: 'Network error' };
    }
}

// Centralized API service for all sentiment analysis related backend interactions
export const sentimentApi = {
    async analyzeText(text: string): Promise<SentimentResult> {
        const { data, error } = await request<SentimentResult>('/sentiment/analyze', {
            method: 'POST',
            body: JSON.stringify({ text }),
        });
        if (data) return data;
        return {
            sentiment: 'neutral',
            confidence: 0,
            model_used: 'unknown',
            language_detected: 'unknown',
            code_switching: false,
            word_count: 0,
            matched_political_words: [],
            sentiment_words: { positive: [], negative: [] },
            political_context: { entities: [], keywords: [] },
            error: error || 'Analysis failed',
        };
    },

    async loadTestExamples(): Promise<TestExample[]> {
        const { data } = await request<{ examples: TestExample[] }>('/sentiment/test-examples');
        return data?.examples ?? [];
    },

    async checkHealth(): Promise<HealthStatus | null> {
        const { data } = await request<HealthStatus>('/lexicon/health');
        return data;
    },

    //Political Entity Management Methods
    async listPoliticalEntities(): Promise<PoliticalEntity[]> {
        const { data } = await request<{ entities: PoliticalEntity[] }>('/entities/');
        return data?.entities ?? [];
    },

    // Real per-entity mention counts, net sentiment, and risk level, aggregated
    // from recent analysis jobs (GET /api/entities/stats).
    async getEntityStats(): Promise<EntityStatsResponse | null> {
        const { data } = await request<EntityStatsResponse>('/entities/stats');
        return data;
    },

    // Add a new political entity to the system
    async addPoliticalEntity(payload: {
        entity: string;
        type: string;
        full_name?: string;
        description?: string;
    }): Promise<{ ok: boolean; message: string }> {
        const { ok, data, error } = await request<{ message: string }>('/entities/add', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
        return ok
            ? { ok: true, message: data?.message || 'Entity added successfully' }
            : { ok: false, message: error || 'Failed to add entity' };
    },

    // Delete a political entity by ID
    async deletePoliticalEntity(id: number): Promise<boolean> {
        const { ok } = await request<{ message: string }>(`/entities/${id}`, { method: 'DELETE' });
        return ok;
    },

    async checkSocialHealth(): Promise<SocialHealthStatus | null> {
        const { data } = await request<SocialHealthStatus>('/social/health');
        return data;
    },

    // List recent social media collections with metadata
    async listSocialCollections(limit = 20): Promise<SocialCollection[]> {
        const { data } = await request<{ collections: SocialCollection[] }>(`/social/collections?limit=${limit}`);
        return data?.collections ?? [];
    },

    // Collect social media posts based on provider, query, or direct input
    async collectSocialPosts(payload: {
        provider?: string;
        query?: string;
        max_results?: number;
        input?: SocialInputItem[];
    }): Promise<SocialCollectResponse> {
        const { data, error } = await request<SocialCollectResponse>('/social/collect', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
        if (data) return data;
        return {
            collection_id: '',
            source: 'x',
            provider: payload.provider || 'default',
            query: payload.query || '',
            count: 0,
            raw_file: '',
            error: error || 'Collection failed',
        };
    },

    // Clean a collected social media dataset using specified filter mode
    async cleanSocialCollection(payload: {
        collection_id: string;
        filter_mode: 'relaxed' | 'strict';
    }): Promise<SocialCleanResponse> {
        const { data, error } = await request<SocialCleanResponse>('/social/clean', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
        if (data) return data;
        return {
            collection_id: payload.collection_id,
            raw_count: 0,
            cleaned_count: 0,
            filter_mode: payload.filter_mode,
            cleaned_file: '',
            report_file: '',
            error: error || 'Cleaning failed',
        };
    },

    async uploadCsvFile(file: File, filterMode?: 'relaxed' | 'strict'): Promise<SocialCollectResponse> {
        const formData = new FormData();
        formData.append('file', file);
        if (filterMode) {
            formData.append('filter_mode', filterMode);
        }
        const { data, error } = await request<SocialCollectResponse>('/social/upload-csv', {
            method: 'POST',
            body: formData,
        });
        if (data) return data;
        return {
            collection_id: '',
            source: 'csv',
            provider: 'csv_upload',
            query: '',
            count: 0,
            raw_file: '',
            error: error || 'CSV upload failed',
        };
    },

    //Batch Analysis Methods
    async runBatchAnalysis(collectionId: string): Promise<BatchAnalysisResult> {
        const { data, error } = await request<BatchAnalysisResult>('/analysis/run', {
            method: 'POST',
            body: JSON.stringify({ collection_id: collectionId }),
        });
        if (data) return data;
        return {
            job_id: '',
            collection_id: collectionId,
            filename: '',
            analyzed_at: '',
            rows: [],
            aggregate: {
                total_rows: 0,
                sentiment_distribution: { positive: 0, neutral: 0, negative: 0 },
                avg_confidence: 0,
                top_trigger_words: [],
                top_entities: [],
                model_used: '',
            },
            error: error || 'Analysis failed',
        };
    },

    // List recent analysis jobs with summary info
    async listAnalysisJobs(limit = 20): Promise<AnalysisJob[]> {
        const { data } = await request<{ jobs: AnalysisJob[] }>(`/analysis/jobs?limit=${limit}`);
        return data?.jobs ?? [];
    },

    // Get detailed results for a specific analysis job by ID
    async getAnalysisJob(jobId: string): Promise<BatchAnalysisResult | null> {
        const { data } = await request<BatchAnalysisResult>(`/analysis/jobs/${jobId}`);
        return data;
    },

    //Lexicon Management Methods

    async getLexiconStats(): Promise<LexiconStats | null> {
        const { data } = await request<LexiconStats>('/lexicon/stats');
        return data;
    },

    // Search lexicon entries by term with optional filters for category or language
    async searchLexicon(query: string): Promise<LexiconSearchResult[]> {
        const { data } = await request<{ results: LexiconSearchResult[] }>(
            `/lexicon/search?q=${encodeURIComponent(query)}`
        );
        return data?.results ?? [];
    },

    // Add a new word to the lexicon with its meaning, category, and an example context sentence
    async addLexiconWord(payload: {
        word: string;
        meaning: string;
        category: string;
        context_sentence: string;
    }): Promise<{ ok: boolean; message: string }> {
        const { ok, data, error } = await request<{ message: string }>('/lexicon/add', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
        return ok
            ? { ok: true, message: data?.message || 'Word added successfully' }
            : { ok: false, message: error || 'Failed to add word' };
    },

    //System & Diagnostics Methods

    async checkSystemHealth(): Promise<SystemHealth | null> {
        const { data } = await request<SystemHealth>('/system/health');
        return data;
    },

    // Retrieve recent system logs for monitoring and debugging purposes
    async getSystemLogs(limit = 50): Promise<string[]> {
        const { data } = await request<{ logs: string[] }>(`/system/logs?limit=${limit}`);
        return data?.logs ?? [];
    },

    // Log a custom event to the system for monitoring and debugging across services
    async logSystemEvent(level: string, message: string): Promise<boolean> {
        const { ok } = await request<{ status: string }>('/system/event', {
            method: 'POST',
            body: JSON.stringify({ level, message }),
        });
        return ok;
    },
};
