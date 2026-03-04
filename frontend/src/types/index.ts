// Common type definitions for Botswana Political Sentiment Analysis

export interface SentimentResult {
  sentiment: string;
  confidence: number;
  detected_language: string;
  code_switching_detected: boolean;
  model_used: string;
  language_analysis?: {
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
    entities: Array<{
      entity: string;
      type: string;
      full_name?: string;
      description?: string;
    }>;
    keywords: Array<{
      term: string;
      meaning: string;
      language: string;
    }>;
  };
  text_length: number;
  word_count: number;
  analysis_timestamp?: string;
  error?: string;
}

export interface DashboardOverview {
  total_posts: number;
  sentiment_breakdown: Record<string, number>;
  language_breakdown: Record<string, number>;
  platform_breakdown: Record<string, number>;
  code_switching_posts: number;
  code_switching_percentage: number;
}

export interface TrendData {
  period: string;
  sentiments: Record<string, number>;
  total: number;
  percentages: Record<string, number>;
}

export interface SocialMediaPost {
  id: number;
  platform: string;
  post_id: string;
  text: string;
  author: string;
  created_at: string;
  likes: number;
  shares: number;
  comments: number;
  location?: string;
  sentiment_analysis?: {
    sentiment: string;
    confidence: number;
    detected_language: string;
    code_switching_detected: boolean;
    political_keywords: string[];
    political_entities: any[];
  };
}

export interface PoliticalEntity {
  entity: string;
  type: string;
  sentiments: Record<string, number>;
  total: number;
  percentages: Record<string, number>;
}

export interface LexiconStats {
  category_stats: Record<string, { word_count: number; recent_additions: number }>;
  metadata: {
    version: string;
    last_updated: string;
    total_words: number;
  };
  total_words: number;
}

export interface TrainingStats {
  feedback_stats: {
    total_feedback: number;
    agreement_rate: number;
    corrections_needed: number;
    new_word_suggestions: number;
    recent_activity: number;
  };
  performance_analysis: {
    overall_accuracy: number;
    sentiment_breakdown: Record<string, number>;
    common_errors: Array<{ pattern: string; count: number }>;
    improvement_suggestions: string[];
  };
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginationInfo {
  page: number;
  per_page: number;
  total: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface FilterOptions {
  sentiment?: string;
  platform?: string;
  keyword?: string;
  days?: number;
  granularity?: 'daily' | 'hourly';
}