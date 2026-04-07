// API service layer for Botswana Political Sentiment Analysis

import { 
  SentimentResult, 
  DashboardOverview, 
  TrendData, 
  SocialMediaPost, 
  PoliticalEntity,
  LexiconStats,
  TrainingStats,
  ApiResponse,
  FilterOptions 
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

class ApiService {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      });

      const data = await response.json();

      if (!response.ok) {
        return { error: data.error || 'Request failed' };
      }

      return { data };
    } catch (error) {
      return { error: error instanceof Error ? error.message : 'Network error' };
    }
  }

  // Sentiment Analysis
  async analyzeSentiment(text: string): Promise<ApiResponse<SentimentResult>> {
    return this.request<SentimentResult>('/api/sentiment/analyze', {
      method: 'POST',
      body: JSON.stringify({ text }),
    });
  }

  async analyzeBatch(texts: string[]): Promise<ApiResponse<{ results: SentimentResult[]; total: number; successful: number }>> {
    return this.request('/api/sentiment/batch', {
      method: 'POST',
      body: JSON.stringify({ texts }),
    });
  }

  async submitFeedback(feedback: {
    text: string;
    predicted_sentiment: string;
    predicted_confidence: number;
    user_sentiment: string;
    user_confidence?: number;
    user_id?: string;
  }): Promise<ApiResponse<{ message: string }>> {
    return this.request('/api/sentiment/feedback', {
      method: 'POST',
      body: JSON.stringify(feedback),
    });
  }

  // Dashboard
  async getDashboardOverview(days: number = 7): Promise<ApiResponse<{ stats: DashboardOverview; period: any }>> {
    return this.request(`/api/dashboard/overview?days=${days}`);
  }

  async getTrends(filters: FilterOptions = {}): Promise<ApiResponse<{ trends: TrendData[]; filters: FilterOptions }>> {
    const params = new URLSearchParams();
    if (filters.days) params.append('days', filters.days.toString());
    if (filters.keyword) params.append('keyword', filters.keyword);
    if (filters.granularity) params.append('granularity', filters.granularity);

    return this.request(`/api/dashboard/trends?${params.toString()}`);
  }

  async getPosts(filters: FilterOptions & { page?: number; per_page?: number } = {}): Promise<ApiResponse<{
    posts: SocialMediaPost[];
    pagination: any;
    filters: FilterOptions;
  }>> {
    const params = new URLSearchParams();
    if (filters.page) params.append('page', filters.page.toString());
    if (filters.per_page) params.append('per_page', filters.per_page.toString());
    if (filters.sentiment) params.append('sentiment', filters.sentiment);
    if (filters.platform) params.append('platform', filters.platform);
    if (filters.keyword) params.append('keyword', filters.keyword);

    return this.request(`/api/dashboard/posts?${params.toString()}`);
  }

  async getPoliticalEntities(days: number = 7): Promise<ApiResponse<{ entities: PoliticalEntity[]; period: any }>> {
    return this.request(`/api/dashboard/political-entities?days=${days}`);
  }

  async getLanguageBreakdown(days: number = 7): Promise<ApiResponse<any>> {
    return this.request(`/api/dashboard/language-breakdown?days=${days}`);
  }

  async getRealTimeStats(): Promise<ApiResponse<any>> {
    return this.request('/api/dashboard/real-time-stats');
  }

  async getAdvancedAnalytics(days: number = 7): Promise<ApiResponse<{ analytics: any; period: any }>> {
    return this.request(`/api/dashboard/analytics?days=${days}`);
  }

  async refreshDashboardData(): Promise<ApiResponse<{ message: string; result: any }>> {
    return this.request('/api/dashboard/refresh', {
      method: 'POST',
    });
  }

  // Lexicon Management
  async getLexiconStats(): Promise<ApiResponse<LexiconStats>> {
    return this.request('/api/lexicon/stats');
  }

  async searchLexicon(query: string, category?: string): Promise<ApiResponse<{
    results: any[];
    count: number;
    query: string;
    category?: string;
  }>> {
    const params = new URLSearchParams({ q: query });
    if (category) params.append('category', category);

    return this.request(`/api/lexicon/search?${params.toString()}`);
  }

  async addWord(wordData: {
    word: string;
    category: string;
    meaning: string;
    context?: string;
    intensity?: string;
    type?: string;
  }): Promise<ApiResponse<{ message: string; word: string; category: string; meaning: string }>> {
    return this.request('/api/lexicon/add', {
      method: 'POST',
      body: JSON.stringify(wordData),
    });
  }

  async suggestWord(wordData: {
    word: string;
    category: string;
    meaning: string;
    context_sentence: string;
    sentiment?: string;
  }): Promise<ApiResponse<{ message: string; word: string; status: string }>> {
    return this.request('/api/lexicon/suggest', {
      method: 'POST',
      body: JSON.stringify(wordData),
    });
  }

  // Training
  async getTrainingStats(): Promise<ApiResponse<TrainingStats>> {
    return this.request('/api/training/stats');
  }

  async prepareDataset(includeUserFeedback: boolean = true): Promise<ApiResponse<{
    message: string;
    dataset_path: string;
    total_examples: number;
    label_distribution: Record<string, number>;
  }>> {
    return this.request('/api/training/prepare-dataset', {
      method: 'POST',
      body: JSON.stringify({ include_user_feedback: includeUserFeedback }),
    });
  }

  async trainModel(options: {
    include_user_feedback?: boolean;
    train_transformers?: boolean;
  } = {}): Promise<ApiResponse<{ message: string; results: any }>> {
    return this.request('/api/training/train-model', {
      method: 'POST',
      body: JSON.stringify(options),
    });
  }

  async quickRetrain(): Promise<ApiResponse<{
    message: string;
    dataset_path: string;
    training_examples: number;
    lexicon_suggestions: number;
  }>> {
    return this.request('/api/training/quick-retrain', {
      method: 'POST',
    });
  }

  async exportTrainingData(): Promise<ApiResponse<{ message: string; filename: string }>> {
    return this.request('/api/training/export', {
      method: 'POST',
    });
  }

  // Admin
  async getPendingSuggestions(limit: number = 20): Promise<ApiResponse<{
    word_suggestions: any[];
    sentiment_corrections: any[];
    total_suggestions: number;
    total_corrections: number;
  }>> {
    return this.request(`/api/admin/pending-suggestions?limit=${limit}`);
  }

  async approveWord(word: string, timestamp: string): Promise<ApiResponse<{ message: string; word: string }>> {
    return this.request('/api/admin/approve-word', {
      method: 'POST',
      body: JSON.stringify({ word, timestamp }),
    });
  }

  async getSystemStats(): Promise<ApiResponse<any>> {
    return this.request('/api/admin/system-stats');
  }

  async triggerDataCollection(): Promise<ApiResponse<{ message: string; results: any }>> {
    return this.request('/api/admin/data-collection/trigger', {
      method: 'POST',
    });
  }

  async triggerAnalysis(): Promise<ApiResponse<{ message: string; processed_count: number }>> {
    return this.request('/api/admin/analysis/trigger', {
      method: 'POST',
    });
  }

  // Health Check
  async getHealth(): Promise<ApiResponse<any>> {
    return this.request('/api/health');
  }
}

export const apiService = new ApiService();