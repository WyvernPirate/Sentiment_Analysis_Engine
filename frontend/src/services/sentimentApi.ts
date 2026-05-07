import {
    SentimentResult,
    TestExample,
    HealthStatus,
    PoliticalEntity,
    SocialHealthStatus,
    SocialCollection,
    SocialInputItem,
    SocialCollectResponse,
    SocialCleanResponse,
    BatchAnalysisResult,
    AnalysisJob,
    SystemHealth,
} from '../types/sentiment';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

export const sentimentApi = {
    async analyzeText(text: string): Promise<SentimentResult> {
        const response = await fetch(`${API_BASE_URL}/sentiment/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text }),
        });
        return response.json();
    },

    async loadTestExamples(): Promise<TestExample[]> {
        try {
            const response = await fetch(`${API_BASE_URL}/sentiment/test-examples`);
            if (!response.ok) {
                return [];
            }
            const data = await response.json();
            return Array.isArray(data.examples) ? data.examples : [];
        } catch {
            return [];
        }
    },

    async checkHealth(): Promise<HealthStatus> {
        const response = await fetch(`${API_BASE_URL}/lexicon/health`);
        return response.json();
    },

    async listPoliticalEntities(): Promise<PoliticalEntity[]> {
        try {
            const response = await fetch(`${API_BASE_URL}/entities/`);
            if (!response.ok) {
                return [];
            }
            const data = await response.json();
            return Array.isArray(data.entities) ? data.entities : [];
        } catch {
            return [];
        }
    },

    async addPoliticalEntity(payload: {
        entity: string;
        type: string;
        full_name?: string;
        description?: string;
    }): Promise<{ ok: boolean; message: string }> {
        try {
            const response = await fetch(`${API_BASE_URL}/entities/add`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            const data = await response.json();
            if (!response.ok) {
                return { ok: false, message: data.error || 'Failed to add entity' };
            }
            return { ok: true, message: data.message || 'Entity added successfully' };
        } catch {
            return { ok: false, message: 'Failed to add entity' };
        }
    },

    async deletePoliticalEntity(id: number): Promise<boolean> {
        try {
            const response = await fetch(`${API_BASE_URL}/entities/${id}`, {
                method: 'DELETE',
            });
            return response.ok;
        } catch {
            return false;
        }
    },

    async checkSocialHealth(): Promise<SocialHealthStatus | null> {
        try {
            const response = await fetch(`${API_BASE_URL}/social/health`);
            if (!response.ok) {
                return null;
            }
            return response.json();
        } catch {
            return null;
        }
    },

    async listSocialCollections(limit = 20): Promise<SocialCollection[]> {
        try {
            const response = await fetch(`${API_BASE_URL}/social/collections?limit=${limit}`);
            if (!response.ok) {
                return [];
            }
            const data = await response.json();
            return Array.isArray(data.collections) ? data.collections : [];
        } catch {
            return [];
        }
    },

    async collectSocialPosts(payload: {
        provider?: string;
        query?: string;
        max_results?: number;
        input?: SocialInputItem[];
    }): Promise<SocialCollectResponse> {
        try {
            const response = await fetch(`${API_BASE_URL}/social/collect`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            const data = await response.json();
            if (!response.ok) {
                return {
                    collection_id: '',
                    source: 'x',
                    provider: payload.provider || 'default',
                    query: payload.query || '',
                    count: 0,
                    raw_file: '',
                    error: data.error || 'Collection failed',
                };
            }
            return data as SocialCollectResponse;
        } catch {
            return {
                collection_id: '',
                source: 'x',
                provider: payload.provider || 'default',
                query: payload.query || '',
                count: 0,
                raw_file: '',
                error: 'Collection failed',
            };
        }
    },

    async cleanSocialCollection(payload: {
        collection_id: string;
        filter_mode: 'relaxed' | 'strict';
    }): Promise<SocialCleanResponse> {
        try {
            const response = await fetch(`${API_BASE_URL}/social/clean`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            const data = await response.json();
            if (!response.ok) {
                return {
                    collection_id: payload.collection_id,
                    raw_count: 0,
                    cleaned_count: 0,
                    filter_mode: payload.filter_mode,
                    cleaned_file: '',
                    report_file: '',
                    error: data.error || 'Cleaning failed',
                };
            }
            return data as SocialCleanResponse;
        } catch {
            return {
                collection_id: payload.collection_id,
                raw_count: 0,
                cleaned_count: 0,
                filter_mode: payload.filter_mode,
                cleaned_file: '',
                report_file: '',
                error: 'Cleaning failed',
            };
        }
    },

    async uploadCsvFile(file: File, filterMode?: 'relaxed' | 'strict'): Promise<SocialCollectResponse> {
        try {
            const formData = new FormData();
            formData.append('file', file);
            if (filterMode) {
                formData.append('filter_mode', filterMode);
            }
            const response = await fetch(`${API_BASE_URL}/social/upload-csv`, {
                method: 'POST',
                body: formData,
            });
            const data = await response.json();
            if (!response.ok) {
                return {
                    collection_id: '',
                    source: 'csv',
                    provider: 'csv_upload',
                    query: '',
                    count: 0,
                    raw_file: '',
                    error: data.error || 'CSV upload failed',
                };
            }
            return data as SocialCollectResponse;
        } catch {
            return {
                collection_id: '',
                source: 'csv',
                provider: 'csv_upload',
                query: '',
                count: 0,
                raw_file: '',
                error: 'CSV upload failed',
            };
        }
    },

    // --- Batch Analysis Methods ---

    async runBatchAnalysis(collectionId: string): Promise<BatchAnalysisResult> {
        try {
            const response = await fetch(`${API_BASE_URL}/analysis/run`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ collection_id: collectionId }),
            });
            const data = await response.json();
            if (!response.ok) {
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
                    error: data.error || 'Analysis failed',
                };
            }
            return data as BatchAnalysisResult;
        } catch {
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
                error: 'Analysis failed',
            };
        }
    },

    async listAnalysisJobs(limit = 20): Promise<AnalysisJob[]> {
        try {
            const response = await fetch(`${API_BASE_URL}/analysis/jobs?limit=${limit}`);
            if (!response.ok) return [];
            const data = await response.json();
            return Array.isArray(data.jobs) ? data.jobs : [];
        } catch {
            return [];
        }
    },

    async getAnalysisJob(jobId: string): Promise<BatchAnalysisResult | null> {
        try {
            const response = await fetch(`${API_BASE_URL}/analysis/jobs/${jobId}`);
            if (!response.ok) return null;
            return (await response.json()) as BatchAnalysisResult;
        } catch {
            return null;
        }
    },
    
    // --- Lexicon Management Methods ---

    async getLexiconStats(): Promise<any> {
        try {
            const response = await fetch(`${API_BASE_URL}/lexicon/stats`);
            if (!response.ok) return null;
            return response.json();
        } catch {
            return null;
        }
    },

    async searchLexicon(query: string): Promise<any[]> {
        try {
            const response = await fetch(`${API_BASE_URL}/lexicon/search?q=${encodeURIComponent(query)}`);
            if (!response.ok) return [];
            const data = await response.json();
            return Array.isArray(data.results) ? data.results : [];
        } catch {
            return [];
        }
    },

    async addLexiconWord(payload: {
        word: string;
        meaning: string;
        category: string;
        context_sentence: string;
    }): Promise<{ ok: boolean; message: string }> {
        try {
            const response = await fetch(`${API_BASE_URL}/lexicon/add`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            const data = await response.json();
            if (!response.ok) {
                return { ok: false, message: data.error || 'Failed to add word' };
            }
            return { ok: true, message: data.message || 'Word added successfully' };
        } catch {
            return { ok: false, message: 'Failed to add word' };
        }
    },

    // --- System & Diagnostics Methods ---

    async checkSystemHealth(): Promise<SystemHealth | null> {
        try {
            const response = await fetch(`${API_BASE_URL}/system/health`);
            if (!response.ok) return null;
            return response.json();
        } catch {
            return null;
        }
    },

    async getSystemLogs(limit = 50): Promise<string[]> {
        try {
            const response = await fetch(`${API_BASE_URL}/system/logs?limit=${limit}`);
            if (!response.ok) return [];
            const data = await response.json();
            return Array.isArray(data.logs) ? data.logs : [];
        } catch {
            return [];
        }
    },

    async logSystemEvent(level: string, message: string): Promise<boolean> {
        try {
            const response = await fetch(`${API_BASE_URL}/system/event`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ level, message }),
            });
            return response.ok;
        } catch {
            return false;
        }
    },
};
