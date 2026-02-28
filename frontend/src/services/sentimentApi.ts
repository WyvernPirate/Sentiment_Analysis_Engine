import { SentimentResult, TestExample, HealthStatus } from '../types/sentiment';

const API_BASE_URL = 'http://localhost:5000/api';

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
        const response = await fetch(`${API_BASE_URL}/sentiment/test-examples`);
        const data = await response.json();
        return data.examples;
    },

    async checkHealth(): Promise<HealthStatus> {
        const response = await fetch(`${API_BASE_URL}/lexicon/health`);
        return response.json();
    }
};
