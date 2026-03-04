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
            <div>🌍 Language: <strong>{result.detected_language}</strong></div>
            {result.code_switching_detected && <div style={{ color: '#e67e22' }}>Code-switching detected!</div>}
          </div>

          {result.language_analysis?.setswana_words_found.length > 0 && (
            <div style={{ marginBottom: '1rem' }}>
              <strong>Setswana Words:</strong> {result.language_analysis.setswana_words_found.join(', ')}
            </div>
          )}

          {result.political_context && (result.political_context.entities.length > 0 || result.political_context.keywords.length > 0) && (
            <div>
              <strong>Political Context:</strong>
              {result.political_context.entities.map((e, i) => (
                <span key={i} style={{ margin: '0 0.25rem', padding: '0.2rem 0.5rem', background: '#fff3cd', borderRadius: '12px', fontSize: '0.8rem' }}>
                  {e.entity}
                </span>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ResultDisplay;
