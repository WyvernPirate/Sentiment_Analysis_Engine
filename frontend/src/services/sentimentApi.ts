import {
    SentimentResult,
    TestExample,
    HealthStatus,
    PoliticalEntity,
    SocialHealthStatus,
    SocialCollection,
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
    }
};
