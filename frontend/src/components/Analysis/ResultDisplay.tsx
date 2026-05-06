import React from 'react';
import { SentimentResult } from '../../types/sentiment';

interface ResultDisplayProps {
  result: SentimentResult | null;
  loading: boolean;
}

const ResultDisplay: React.FC<ResultDisplayProps> = ({ result, loading }) => {
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
      <div style={{ padding: '2rem', textAlign: 'center', background: '#f8f9fa', borderRadius: '8px' }}>
        🔄 Analyzing...
      </div>
    );
  }

  if (!result) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center', color: '#6c757d', background: '#f8f9fa', borderRadius: '8px', border: '2px dashed #dee2e6' }}>
        Enter text or click an example to see results
      </div>
    );
  }

  return (
    <div style={{ 
      padding: '1.5rem', 
      background: result.error ? '#f8d7da' : '#f8f9fa', 
      borderRadius: '8px',
      border: `2px solid ${result.error ? '#f5c6cb' : '#e9ecef'}`
    }}>
      {result.error ? (
        <p style={{ color: '#721c24', margin: 0 }}>{result.error}</p>
      ) : (
        <>
          <div style={{ marginBottom: '1.5rem' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: getSentimentColor(result.sentiment) }}>
              {result.sentiment.toUpperCase()} ({Math.round(result.confidence * 100)}%)
            </div>
            <div>🤖 Model: <strong>{result.model_used}</strong></div>
            <div>🔢 Words: <strong>{result.word_count}</strong></div>
          </div>

          {result.matched_political_words.length > 0 && (
            <div style={{ marginBottom: '1rem' }}>
              <strong>Matched Political Words:</strong>
              <div style={{ marginTop: '0.5rem' }}>
                {result.matched_political_words.map((word, i) => (
                  <span
                    key={`${word.term}-${i}`}
                    style={{
                      margin: '0 0.25rem 0.25rem 0',
                      display: 'inline-block',
                      padding: '0.2rem 0.5rem',
                      background: '#fff3cd',
                      borderRadius: '12px',
                      fontSize: '0.8rem'
                    }}
                    title={word.meaning}
                  >
                    {word.term}
                  </span>
                ))}
              </div>
            </div>
          )}

          {(result.sentiment_words.positive.length > 0 || result.sentiment_words.negative.length > 0) && (
            <div style={{ marginBottom: '1rem' }}>
              <strong>Trigger Words:</strong>
              <div style={{ marginTop: '0.5rem' }}>
                {result.sentiment_words.positive.map((word) => (
                  <span
                    key={`pos-${word}`}
                    style={{
                      margin: '0 0.25rem 0.25rem 0',
                      display: 'inline-block',
                      padding: '0.2rem 0.5rem',
                      background: '#d4edda',
                      borderRadius: '12px',
                      fontSize: '0.8rem'
                    }}
                  >
                    + {word}
                  </span>
                ))}
                {result.sentiment_words.negative.map((word) => (
                  <span
                    key={`neg-${word}`}
                    style={{
                      margin: '0 0.25rem 0.25rem 0',
                      display: 'inline-block',
                      padding: '0.2rem 0.5rem',
                      background: '#f8d7da',
                      borderRadius: '12px',
                      fontSize: '0.8rem'
                    }}
                  >
                    - {word}
                  </span>
                ))}
              </div>
            </div>
          )}

          {result.political_context.entities.length > 0 && (
            <div>
              <strong>Political Entities:</strong>
              <div style={{ marginTop: '0.5rem' }}>
                {result.political_context.entities.map((entity, i) => (
                  <span
                    key={`${entity.entity}-${i}`}
                    style={{
                      margin: '0 0.25rem 0.25rem 0',
                      display: 'inline-block',
                      padding: '0.2rem 0.5rem',
                      background: '#e2e3e5',
                      borderRadius: '12px',
                      fontSize: '0.8rem'
                    }}
                  >
                    {entity.entity}
                  </span>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ResultDisplay;
