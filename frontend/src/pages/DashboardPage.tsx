import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { DashboardOverview, TrendData, PoliticalEntity } from '../types';

interface DashboardPageProps {}

const DashboardPage: React.FC<DashboardPageProps> = () => {
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [trends, setTrends] = useState<TrendData[]>([]);
  const [entities, setEntities] = useState<PoliticalEntity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState(7);

  useEffect(() => {
    loadDashboardData();
  }, [timeRange]);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Load overview data
      const overviewResponse = await apiService.getDashboardOverview(timeRange);
      if (overviewResponse.error) {
        throw new Error(overviewResponse.error);
      }
      setOverview(overviewResponse.data?.stats || null);

      // Load trends data
      const trendsResponse = await apiService.getTrends({ days: timeRange });
      if (trendsResponse.error) {
        throw new Error(trendsResponse.error);
      }
      setTrends(trendsResponse.data?.trends || []);

      // Load political entities
      const entitiesResponse = await apiService.getPoliticalEntities(timeRange);
      if (entitiesResponse.error) {
        throw new Error(entitiesResponse.error);
      }
      setEntities(entitiesResponse.data?.entities || []);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
    } finally {
      setLoading(false);
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
        🔄 Loading dashboard data...
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
        <h3>❌ Error Loading Dashboard</h3>
        <p>{error}</p>
        <button 
          onClick={loadDashboardData}
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

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1 style={{ color: '#2c3e50', margin: 0 }}>📊 Political Sentiment Dashboard</h1>
        
        <div style={{ display: 'flex', gap: '0.5rem' }}>
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

      {/* Overview Cards */}
      {overview && (
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
          gap: '1rem', 
          marginBottom: '2rem' 
        }}>
          <div style={{ 
            background: '#f8f9fa', 
            padding: '1.5rem', 
            borderRadius: '8px', 
            border: '1px solid #dee2e6' 
          }}>
            <h3 style={{ margin: '0 0 1rem 0', color: '#495057' }}>📈 Total Posts</h3>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#007bff' }}>
              {overview.total_posts.toLocaleString()}
            </div>
            <div style={{ fontSize: '0.9rem', color: '#6c757d', marginTop: '0.5rem' }}>
              Code-switching: {overview.code_switching_percentage.toFixed(1)}%
            </div>
          </div>

          <div style={{ 
            background: '#f8f9fa', 
            padding: '1.5rem', 
            borderRadius: '8px', 
            border: '1px solid #dee2e6' 
          }}>
            <h3 style={{ margin: '0 0 1rem 0', color: '#495057' }}>💭 Sentiment Breakdown</h3>
            {Object.entries(overview.sentiment_breakdown).map(([sentiment, count]) => (
              <div key={sentiment} style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                marginBottom: '0.5rem' 
              }}>
                <span style={{ color: getSentimentColor(sentiment), fontWeight: 'bold' }}>
                  {sentiment.charAt(0).toUpperCase() + sentiment.slice(1)}:
                </span>
                <span>{count}</span>
              </div>
            ))}
          </div>

          <div style={{ 
            background: '#f8f9fa', 
            padding: '1.5rem', 
            borderRadius: '8px', 
            border: '1px solid #dee2e6' 
          }}>
            <h3 style={{ margin: '0 0 1rem 0', color: '#495057' }}>🌍 Languages</h3>
            {Object.entries(overview.language_breakdown).map(([language, count]) => (
              <div key={language} style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                marginBottom: '0.5rem' 
              }}>
                <span>{language}:</span>
                <span>{count}</span>
              </div>
            ))}
          </div>

          <div style={{ 
            background: '#f8f9fa', 
            padding: '1.5rem', 
            borderRadius: '8px', 
            border: '1px solid #dee2e6' 
          }}>
            <h3 style={{ margin: '0 0 1rem 0', color: '#495057' }}>📱 Platforms</h3>
            {Object.entries(overview.platform_breakdown).map(([platform, count]) => (
              <div key={platform} style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                marginBottom: '0.5rem' 
              }}>
                <span>{platform.charAt(0).toUpperCase() + platform.slice(1)}:</span>
                <span>{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Trends Chart */}
      {trends.length > 0 && (
        <div style={{ 
          background: '#f8f9fa', 
          padding: '1.5rem', 
          borderRadius: '8px', 
          border: '1px solid #dee2e6',
          marginBottom: '2rem'
        }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#495057' }}>📈 Sentiment Trends Over Time</h3>
          <div style={{ overflowX: 'auto' }}>
            <div style={{ display: 'flex', gap: '1rem', minWidth: '600px' }}>
              {trends.slice(-14).map((trend, index) => (
                <div key={index} style={{ 
                  flex: '1', 
                  minWidth: '80px',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '0.8rem', marginBottom: '0.5rem', color: '#6c757d' }}>
                    {new Date(trend.period).toLocaleDateString()}
                  </div>
                  <div style={{ 
                    height: '100px', 
                    display: 'flex', 
                    flexDirection: 'column-reverse',
                    border: '1px solid #dee2e6',
                    borderRadius: '4px',
                    overflow: 'hidden'
                  }}>
                    {Object.entries(trend.percentages).map(([sentiment, percentage]) => (
                      <div
                        key={sentiment}
                        style={{
                          height: `${percentage}%`,
                          backgroundColor: getSentimentColor(sentiment),
                          opacity: 0.8
                        }}
                        title={`${sentiment}: ${percentage.toFixed(1)}%`}
                      />
                    ))}
                  </div>
                  <div style={{ fontSize: '0.8rem', marginTop: '0.25rem', color: '#6c757d' }}>
                    {trend.total}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Political Entities */}
      {entities.length > 0 && (
        <div style={{ 
          background: '#f8f9fa', 
          padding: '1.5rem', 
          borderRadius: '8px', 
          border: '1px solid #dee2e6'
        }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#495057' }}>🏛️ Political Entity Sentiment</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
            {entities.slice(0, 6).map((entity, index) => (
              <div key={index} style={{ 
                background: 'white', 
                padding: '1rem', 
                borderRadius: '4px', 
                border: '1px solid #dee2e6' 
              }}>
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  marginBottom: '0.5rem'
                }}>
                  <strong>{entity.entity}</strong>
                  <span style={{ 
                    fontSize: '0.8rem', 
                    color: '#6c757d',
                    background: '#e9ecef',
                    padding: '0.25rem 0.5rem',
                    borderRadius: '12px'
                  }}>
                    {entity.type}
                  </span>
                </div>
                <div style={{ fontSize: '0.9rem', color: '#6c757d', marginBottom: '0.5rem' }}>
                  Total mentions: {entity.total}
                </div>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  {Object.entries(entity.percentages).map(([sentiment, percentage]) => (
                    <div
                      key={sentiment}
                      style={{
                        flex: percentage / 100,
                        height: '20px',
                        backgroundColor: getSentimentColor(sentiment),
                        borderRadius: '2px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'white',
                        fontSize: '0.7rem',
                        fontWeight: 'bold'
                      }}
                      title={`${sentiment}: ${percentage.toFixed(1)}%`}
                    >
                      {percentage > 15 ? `${percentage.toFixed(0)}%` : ''}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardPage;