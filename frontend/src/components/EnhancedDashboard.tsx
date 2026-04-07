import React, { useState, useEffect, useCallback } from 'react';
import { apiService } from '../services/api';

interface AdvancedAnalytics {
  sentiment_momentum: {
    trend: string;
    change: number;
    first_period_score: number;
    second_period_score: number;
  };
  keywords_analysis: {
    top_keywords: Array<{ word: string; count: number }>;
    top_hashtags: Array<{ hashtag: string; count: number }>;
    top_setswana_words: Array<{ word: string; count: number }>;
  };
  engagement_analysis: {
    total_engagement: {
      likes: number;
      shares: number;
      comments: number;
      total: number;
    };
    average_engagement_by_sentiment: Record<string, number>;
    most_engaging_sentiment: string;
  };
  language_patterns: {
    language_sentiment_breakdown: Record<string, Record<string, number>>;
    code_switching_sentiment: Record<string, number>;
    dominant_language: string;
  };
  party_comparison: {
    party_rankings: Array<{
      party: string;
      total_mentions: number;
      sentiment_score: number;
      positive_pct: number;
      negative_pct: number;
      neutral_pct: number;
      avg_engagement: number;
    }>;
    most_positive_party: string;
    most_mentioned_party: string;
  };
  confidence_analysis: {
    overall_avg_confidence: number;
    confidence_by_sentiment: Record<string, any>;
    high_confidence_posts: number;
    low_confidence_posts: number;
    confidence_quality: string;
  };
  total_posts_analyzed: number;
  analysis_period: string;
}

const EnhancedDashboard: React.FC = () => {
  const [analytics, setAnalytics] = useState<AdvancedAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState(7);

  const loadAnalytics = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiService.getAdvancedAnalytics(timeRange);

      if (response.error) {
        setError(response.error);
        setAnalytics(null);
        return;
      }

      setAnalytics(response.data?.analytics || null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  }, [timeRange]);

  useEffect(() => {
    loadAnalytics();
  }, [loadAnalytics]);

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving': return '📈';
      case 'declining': return '📉';
      case 'stable': return '➡️';
      default: return '❓';
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'improving': return '#28a745';
      case 'declining': return '#dc3545';
      case 'stable': return '#6c757d';
      default: return '#000';
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return '#28a745';
      case 'negative': return '#dc3545';
      case 'neutral': return '#6c757d';
      default: return '#000';
    }
  };

  const getConfidenceColor = (quality: string) => {
    switch (quality) {
      case 'high': return '#28a745';
      case 'medium': return '#ffc107';
      case 'low': return '#dc3545';
      default: return '#6c757d';
    }
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '400px',
        fontSize: '1.2rem',
        color: '#6c757d'
      }}>
        🔄 Loading advanced analytics...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        padding: '2rem', 
        textAlign: 'center',
        background: '#f8d7da',
        border: '1px solid #f5c6cb',
        borderRadius: '8px',
        color: '#721c24'
      }}>
        <h3>❌ Error Loading Analytics</h3>
        <p>{error}</p>
        <button 
          onClick={loadAnalytics}
          style={{
            padding: '0.5rem 1rem',
            background: '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Retry
        </button>
      </div>
    );
  }

  if (!analytics) {
    return <div>No analytics data available</div>;
  }

  return (
    <div style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1 style={{ color: '#2c3e50', margin: 0 }}>📊 Political Sentiment Intelligence</h1>
        
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <button
            onClick={() => {
              apiService.refreshDashboardData()
                .then(() => {
                  setTimeout(() => loadAnalytics(), 1000);
                })
                .catch(console.error);
            }}
            style={{
              padding: '0.5rem 1rem',
              background: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.9rem'
            }}
          >
            🔄 Refresh Data
          </button>
          
          {[7, 14, 30].map(days => (
            <button
              key={days}
              onClick={() => setTimeRange(days)}
              style={{
                padding: '0.5rem 1rem',
                background: timeRange === days ? '#007bff' : '#f8f9fa',
                color: timeRange === days ? 'white' : '#6c757d',
                border: '1px solid #dee2e6',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              {days} days
            </button>
          ))}
        </div>
      </div>

      {/* Key Insights Row */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', 
        gap: '1rem', 
        marginBottom: '2rem' 
      }}>
        {/* Sentiment Momentum */}
        <div style={{ 
          background: '#f8f9fa', 
          padding: '1.5rem', 
          borderRadius: '8px', 
          border: '1px solid #dee2e6' 
        }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#495057' }}>
            {getTrendIcon(analytics.sentiment_momentum.trend)} Sentiment Momentum
          </h3>
          <div style={{ 
            fontSize: '1.5rem', 
            fontWeight: 'bold', 
            color: getTrendColor(analytics.sentiment_momentum.trend),
            marginBottom: '0.5rem'
          }}>
            {analytics.sentiment_momentum.trend.toUpperCase()}
          </div>
          <div style={{ fontSize: '0.9rem', color: '#6c757d' }}>
            Change: {analytics.sentiment_momentum.change > 0 ? '+' : ''}{analytics.sentiment_momentum.change}
          </div>
          <div style={{ fontSize: '0.8rem', color: '#6c757d', marginTop: '0.5rem' }}>
            Early period: {analytics.sentiment_momentum.first_period_score} → 
            Recent period: {analytics.sentiment_momentum.second_period_score}
          </div>
        </div>

        {/* Most Positive Party */}
        {analytics.party_comparison.most_positive_party && (
          <div style={{ 
            background: '#f8f9fa', 
            padding: '1.5rem', 
            borderRadius: '8px', 
            border: '1px solid #dee2e6' 
          }}>
            <h3 style={{ margin: '0 0 1rem 0', color: '#495057' }}>🏆 Most Positive Party</h3>
            <div style={{ 
              fontSize: '1.5rem', 
              fontWeight: 'bold', 
              color: '#28a745',
              marginBottom: '0.5rem'
            }}>
              {analytics.party_comparison.most_positive_party}
            </div>
            <div style={{ fontSize: '0.9rem', color: '#6c757d' }}>
              Leading in positive sentiment
            </div>
            {analytics.party_comparison.party_rankings.length > 0 && (
              <div style={{ fontSize: '0.8rem', color: '#6c757d', marginTop: '0.5rem' }}>
                Score: {analytics.party_comparison.party_rankings[0].sentiment_score}
              </div>
            )}
          </div>
        )}

        {/* Language Dominance */}
        <div style={{ 
          background: '#f8f9fa', 
          padding: '1.5rem', 
          borderRadius: '8px', 
          border: '1px solid #dee2e6' 
        }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#495057' }}>🌍 Language Usage</h3>
          <div style={{ 
            fontSize: '1.5rem', 
            fontWeight: 'bold', 
            color: '#007bff',
            marginBottom: '0.5rem'
          }}>
            {analytics.language_patterns.dominant_language}
          </div>
          <div style={{ fontSize: '0.9rem', color: '#6c757d' }}>
            Dominant language
          </div>
          <div style={{ fontSize: '0.8rem', color: '#6c757d', marginTop: '0.5rem' }}>
            Code-switching posts: {Object.values(analytics.language_patterns.code_switching_sentiment).reduce((a, b) => a + b, 0)}
          </div>
        </div>

        {/* Confidence Quality */}
        <div style={{ 
          background: '#f8f9fa', 
          padding: '1.5rem', 
          borderRadius: '8px', 
          border: '1px solid #dee2e6' 
        }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#495057' }}>🎯 Analysis Quality</h3>
          <div style={{ 
            fontSize: '1.5rem', 
            fontWeight: 'bold', 
            color: getConfidenceColor(analytics.confidence_analysis.confidence_quality),
            marginBottom: '0.5rem'
          }}>
            {analytics.confidence_analysis.confidence_quality.toUpperCase()}
          </div>
          <div style={{ fontSize: '0.9rem', color: '#6c757d' }}>
            Avg confidence: {(analytics.confidence_analysis.overall_avg_confidence * 100).toFixed(1)}%
          </div>
          <div style={{ fontSize: '0.8rem', color: '#6c757d', marginTop: '0.5rem' }}>
            High confidence: {analytics.confidence_analysis.high_confidence_posts} posts
          </div>
        </div>
      </div>

      {/* Political Party Comparison */}
      {analytics.party_comparison.party_rankings.length > 0 && (
        <div style={{ 
          background: '#f8f9fa', 
          padding: '1.5rem', 
          borderRadius: '8px', 
          border: '1px solid #dee2e6',
          marginBottom: '2rem'
        }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#495057' }}>🏛️ Political Party Sentiment Comparison</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
            {analytics.party_comparison.party_rankings.map((party, index) => (
              <div key={party.party} style={{ 
                background: 'white', 
                padding: '1rem', 
                borderRadius: '4px', 
                border: '1px solid #dee2e6',
                position: 'relative'
              }}>
                {index === 0 && (
                  <div style={{
                    position: 'absolute',
                    top: '-8px',
                    right: '8px',
                    background: '#ffd700',
                    color: '#000',
                    padding: '0.25rem 0.5rem',
                    borderRadius: '12px',
                    fontSize: '0.7rem',
                    fontWeight: 'bold'
                  }}>
                    👑 LEADER
                  </div>
                )}
                
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  marginBottom: '0.5rem'
                }}>
                  <strong style={{ fontSize: '1.1rem' }}>{party.party}</strong>
                  <span style={{ 
                    fontSize: '0.9rem', 
                    fontWeight: 'bold',
                    color: party.sentiment_score > 0 ? '#28a745' : party.sentiment_score < 0 ? '#dc3545' : '#6c757d'
                  }}>
                    {party.sentiment_score > 0 ? '+' : ''}{party.sentiment_score}
                  </span>
                </div>
                
                <div style={{ fontSize: '0.8rem', color: '#6c757d', marginBottom: '0.5rem' }}>
                  {party.total_mentions} mentions • Avg engagement: {party.avg_engagement}
                </div>
                
                {/* Sentiment Bar */}
                <div style={{ 
                  display: 'flex', 
                  height: '20px', 
                  borderRadius: '10px', 
                  overflow: 'hidden',
                  marginBottom: '0.5rem'
                }}>
                  <div 
                    style={{ 
                      width: `${party.positive_pct}%`, 
                      background: '#28a745' 
                    }}
                    title={`Positive: ${party.positive_pct}%`}
                  />
                  <div 
                    style={{ 
                      width: `${party.neutral_pct}%`, 
                      background: '#6c757d' 
                    }}
                    title={`Neutral: ${party.neutral_pct}%`}
                  />
                  <div 
                    style={{ 
                      width: `${party.negative_pct}%`, 
                      background: '#dc3545' 
                    }}
                    title={`Negative: ${party.negative_pct}%`}
                  />
                </div>
                
                <div style={{ fontSize: '0.7rem', color: '#6c757d' }}>
                  {party.positive_pct}% positive • {party.negative_pct}% negative • {party.neutral_pct}% neutral
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Keywords and Engagement Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '2rem' }}>
        {/* Top Keywords */}
        <div style={{ 
          background: '#f8f9fa', 
          padding: '1.5rem', 
          borderRadius: '8px', 
          border: '1px solid #dee2e6'
        }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#495057' }}>🔥 Trending Keywords</h3>
          
          {/* Political Keywords */}
          {analytics.keywords_analysis.top_keywords.length > 0 && (
            <div style={{ marginBottom: '1rem' }}>
              <h4 style={{ fontSize: '0.9rem', color: '#6c757d', margin: '0 0 0.5rem 0' }}>Political Terms:</h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {analytics.keywords_analysis.top_keywords.slice(0, 8).map((keyword, i) => (
                  <span key={i} style={{
                    background: '#007bff',
                    color: 'white',
                    padding: '0.25rem 0.5rem',
                    borderRadius: '12px',
                    fontSize: '0.8rem',
                    fontWeight: 'bold'
                  }}>
                    {keyword.word} ({keyword.count})
                  </span>
                ))}
              </div>
            </div>
          )}
          
          {/* Setswana Keywords */}
          {analytics.keywords_analysis.top_setswana_words.length > 0 && (
            <div style={{ marginBottom: '1rem' }}>
              <h4 style={{ fontSize: '0.9rem', color: '#6c757d', margin: '0 0 0.5rem 0' }}>Setswana Terms:</h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {analytics.keywords_analysis.top_setswana_words.slice(0, 6).map((word, i) => (
                  <span key={i} style={{
                    background: '#28a745',
                    color: 'white',
                    padding: '0.25rem 0.5rem',
                    borderRadius: '12px',
                    fontSize: '0.8rem',
                    fontWeight: 'bold'
                  }}>
                    {word.word} ({word.count})
                  </span>
                ))}
              </div>
            </div>
          )}
          
          {/* Hashtags */}
          {analytics.keywords_analysis.top_hashtags.length > 0 && (
            <div>
              <h4 style={{ fontSize: '0.9rem', color: '#6c757d', margin: '0 0 0.5rem 0' }}>Hashtags:</h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {analytics.keywords_analysis.top_hashtags.slice(0, 6).map((hashtag, i) => (
                  <span key={i} style={{
                    background: '#6f42c1',
                    color: 'white',
                    padding: '0.25rem 0.5rem',
                    borderRadius: '12px',
                    fontSize: '0.8rem',
                    fontWeight: 'bold'
                  }}>
                    {hashtag.hashtag} ({hashtag.count})
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Engagement Analysis */}
        <div style={{ 
          background: '#f8f9fa', 
          padding: '1.5rem', 
          borderRadius: '8px', 
          border: '1px solid #dee2e6'
        }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#495057' }}>📈 Engagement Insights</h3>
          
          <div style={{ marginBottom: '1rem' }}>
            <h4 style={{ fontSize: '0.9rem', color: '#6c757d', margin: '0 0 0.5rem 0' }}>Total Engagement:</h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.5rem', textAlign: 'center' }}>
              <div style={{ background: 'white', padding: '0.5rem', borderRadius: '4px' }}>
                <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#e91e63' }}>
                  {analytics.engagement_analysis.total_engagement.likes}
                </div>
                <div style={{ fontSize: '0.7rem', color: '#6c757d' }}>Likes</div>
              </div>
              <div style={{ background: 'white', padding: '0.5rem', borderRadius: '4px' }}>
                <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#2196f3' }}>
                  {analytics.engagement_analysis.total_engagement.shares}
                </div>
                <div style={{ fontSize: '0.7rem', color: '#6c757d' }}>Shares</div>
              </div>
              <div style={{ background: 'white', padding: '0.5rem', borderRadius: '4px' }}>
                <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#ff9800' }}>
                  {analytics.engagement_analysis.total_engagement.comments}
                </div>
                <div style={{ fontSize: '0.7rem', color: '#6c757d' }}>Comments</div>
              </div>
            </div>
          </div>
          
          <div>
            <h4 style={{ fontSize: '0.9rem', color: '#6c757d', margin: '0 0 0.5rem 0' }}>
              Most Engaging: {analytics.engagement_analysis.most_engaging_sentiment} posts
            </h4>
            <div style={{ fontSize: '0.8rem', color: '#6c757d' }}>
              Average engagement by sentiment:
            </div>
            {Object.entries(analytics.engagement_analysis.average_engagement_by_sentiment).map(([sentiment, avg]) => (
              <div key={sentiment} style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                marginTop: '0.25rem',
                fontSize: '0.8rem'
              }}>
                <span style={{ color: getSentimentColor(sentiment), fontWeight: 'bold' }}>
                  {sentiment.charAt(0).toUpperCase() + sentiment.slice(1)}:
                </span>
                <span>{avg.toFixed(1)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Analysis Summary */}
      <div style={{ 
        background: '#e8f4fd', 
        padding: '1.5rem', 
        borderRadius: '8px', 
        border: '1px solid #bee5eb'
      }}>
        <h3 style={{ margin: '0 0 1rem 0', color: '#0c5460' }}>📋 Analysis Summary</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div>
            <strong>Posts Analyzed:</strong> {analytics.total_posts_analyzed}
          </div>
          <div>
            <strong>Analysis Period:</strong> {analytics.analysis_period}
          </div>
          <div>
            <strong>Confidence Quality:</strong> 
            <span style={{ color: getConfidenceColor(analytics.confidence_analysis.confidence_quality), fontWeight: 'bold', marginLeft: '0.5rem' }}>
              {analytics.confidence_analysis.confidence_quality.toUpperCase()}
            </span>
          </div>
          <div>
            <strong>Sentiment Trend:</strong> 
            <span style={{ color: getTrendColor(analytics.sentiment_momentum.trend), fontWeight: 'bold', marginLeft: '0.5rem' }}>
              {getTrendIcon(analytics.sentiment_momentum.trend)} {analytics.sentiment_momentum.trend.toUpperCase()}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedDashboard;