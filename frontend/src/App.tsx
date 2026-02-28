import React, { useState, useEffect } from 'react';
import './App.css';
import DashboardPage from './pages/DashboardPage';
import EnhancedDashboard from './components/EnhancedDashboard';
import LexiconManager from './LexiconManager';

interface SentimentResult {
  sentiment: string;
  confidence: number;
  detected_language: string;
  code_switching_detected: boolean;
  model_used: string;
  language_analysis: {
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
    entities: Array<{entity: string; type: string; full_name?: string; description?: string}>;
    keywords: Array<{term: string; meaning: string; language: string}>;
  };
  text_length: number;
  word_count: number;
  error?: string;
}

interface TestExample {
  text: string;
  description: string;
  expected: string;
}

function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'insights' | 'analyzer' | 'lexicon'>('insights');
  const [input, setInput] = useState('');
  const [result, setResult] = useState<SentimentResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [examples, setExamples] = useState<TestExample[]>([]);
  const [healthStatus, setHealthStatus] = useState<any>(null);

  // Load test examples and health status on component mount
  useEffect(() => {
    loadTestExamples();
    checkHealth();
  }, []);

  const loadTestExamples = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/test-examples');
      const data = await response.json();
      setExamples(data.examples);
    } catch (error) {
      console.error('Failed to load examples:', error);
    }
  };

  const checkHealth = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/health');
      const data = await response.json();
      setHealthStatus(data);
    } catch (error) {
      console.error('Health check failed:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await analyzeText(input);
  };

  const analyzeText = async (text: string) => {
    setLoading(true);
    setResult(null);
    try {
      const response = await fetch('http://localhost:5000/api/sentiment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ error: 'API request failed - make sure backend is running on port 5000' } as SentimentResult);
    }
    setLoading(false);
  };

  const tryExample = (exampleText: string) => {
    setInput(exampleText);
    analyzeText(exampleText);
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return '#28a745';
      case 'negative': return '#dc3545';
      case 'neutral': return '#6c757d';
      default: return '#000';
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '2rem auto', fontFamily: 'Arial, sans-serif', padding: '0 1rem' }}>
      <header style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <h1 style={{ color: '#2c3e50' }}>🇧🇼 Botswana Political Sentiment Analysis</h1>
        <p style={{ color: '#7f8c8d' }}>
          Advanced sentiment analysis with Setswana-English code-switching support
        </p>
        
        {/* Tab Navigation */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          gap: '0.5rem', 
          marginTop: '1.5rem',
          marginBottom: '1rem'
        }}>
          <button
            onClick={() => setActiveTab('insights')}
            style={{
              padding: '0.75rem 1.25rem',
              background: activeTab === 'insights' ? '#007bff' : '#f8f9fa',
              color: activeTab === 'insights' ? 'white' : '#6c757d',
              border: '1px solid #dee2e6',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.95rem',
              fontWeight: activeTab === 'insights' ? 'bold' : 'normal'
            }}
          >
            🧠 Intelligence
          </button>
          <button
            onClick={() => setActiveTab('dashboard')}
            style={{
              padding: '0.75rem 1.25rem',
              background: activeTab === 'dashboard' ? '#007bff' : '#f8f9fa',
              color: activeTab === 'dashboard' ? 'white' : '#6c757d',
              border: '1px solid #dee2e6',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.95rem',
              fontWeight: activeTab === 'dashboard' ? 'bold' : 'normal'
            }}
          >
            📊 Overview
          </button>
          <button
            onClick={() => setActiveTab('analyzer')}
            style={{
              padding: '0.75rem 1.25rem',
              background: activeTab === 'analyzer' ? '#007bff' : '#f8f9fa',
              color: activeTab === 'analyzer' ? 'white' : '#6c757d',
              border: '1px solid #dee2e6',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.95rem',
              fontWeight: activeTab === 'analyzer' ? 'bold' : 'normal'
            }}
          >
            🔍 Analyzer
          </button>
          <button
            onClick={() => setActiveTab('lexicon')}
            style={{
              padding: '0.75rem 1.25rem',
              background: activeTab === 'lexicon' ? '#007bff' : '#f8f9fa',
              color: activeTab === 'lexicon' ? 'white' : '#6c757d',
              border: '1px solid #dee2e6',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.95rem',
              fontWeight: activeTab === 'lexicon' ? 'bold' : 'normal'
            }}
          >
            🔧 Management
          </button>
        </div>
        
        {healthStatus && (
          <div style={{ 
            background: '#e8f5e8', 
            padding: '0.5rem', 
            borderRadius: '4px', 
            marginTop: '1rem',
            fontSize: '0.9rem'
          }}>
            ✅ Backend Status: {healthStatus.status} | 
            Setswana Words: {healthStatus.lexicon_stats?.setswana_words} | 
            Political Terms: {healthStatus.lexicon_stats?.political_terms}
          </div>
        )}
      </header>

      {/* Tab Content */}
      {activeTab === 'insights' ? (
        <EnhancedDashboard />
      ) : activeTab === 'dashboard' ? (
        <DashboardPage />
      ) : activeTab === 'analyzer' ? (

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        {/* Input Section */}
        <div>
          <h3>📝 Analyze Text</h3>
          <form onSubmit={handleSubmit}>
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Enter text in English, Setswana, or mixed (code-switching)..."
              style={{ 
                width: '100%', 
                height: '100px',
                padding: '0.75rem', 
                marginBottom: '1rem',
                border: '2px solid #e9ecef',
                borderRadius: '4px',
                fontSize: '1rem'
              }}
            />
            <button 
              type="submit" 
              disabled={loading || !input.trim()}
              style={{
                width: '100%',
                padding: '0.75rem',
                backgroundColor: loading ? '#6c757d' : '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                fontSize: '1rem',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            >
              {loading ? '🔄 Analyzing...' : '🔍 Analyze Sentiment'}
            </button>
          </form>

          {/* Test Examples */}
          <div style={{ marginTop: '2rem' }}>
            <h4>🧪 Try These Examples:</h4>
            {examples.map((example, index) => (
              <div key={index} style={{ 
                marginBottom: '1rem', 
                padding: '0.75rem', 
                background: '#f8f9fa', 
                borderRadius: '4px',
                cursor: 'pointer',
                border: '1px solid #e9ecef'
              }} onClick={() => tryExample(example.text)}>
                <div style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>
                  "{example.text}"
                </div>
                <div style={{ fontSize: '0.85rem', color: '#6c757d' }}>
                  {example.description}
                </div>
                <div style={{ fontSize: '0.8rem', color: '#28a745', marginTop: '0.25rem' }}>
                  Expected: {example.expected}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Results Section */}
        <div>
          <h3>📊 Analysis Results</h3>
          {result && (
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
                  {/* Main Results */}
                  <div style={{ marginBottom: '1.5rem' }}>
                    <div style={{ 
                      fontSize: '1.5rem', 
                      fontWeight: 'bold', 
                      color: getSentimentColor(result.sentiment),
                      marginBottom: '0.5rem'
                    }}>
                      {result.sentiment.toUpperCase()} ({Math.round(result.confidence * 100)}%)
                    </div>
                    <div style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>
                      🌍 Language: <strong>{result.detected_language}</strong>
                      {result.code_switching_detected && <span style={{ color: '#e67e22' }}> (Code-switching detected!)</span>}
                    </div>
                    <div style={{ fontSize: '0.9rem', color: '#6c757d' }}>
                      Model: {result.model_used} | Words: {result.word_count} | Length: {result.text_length}
                    </div>
                  </div>

                  {/* Language Analysis */}
                  {result.language_analysis && result.language_analysis.setswana_words_found.length > 0 && (
                    <div style={{ marginBottom: '1.5rem' }}>
                      <h4 style={{ color: '#2c3e50', marginBottom: '0.5rem' }}>🔤 Setswana Words Found:</h4>
                      <div style={{ 
                        background: '#e8f4fd', 
                        padding: '0.75rem', 
                        borderRadius: '4px',
                        fontSize: '0.9rem'
                      }}>
                        {result.language_analysis.setswana_words_found.join(', ')}
                        <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: '#6c757d' }}>
                          Setswana ratio: {Math.round(result.language_analysis.setswana_ratio * 100)}% 
                          ({result.language_analysis.setswana_word_count}/{result.language_analysis.total_words} words)
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Sentiment Words */}
                  {(result.sentiment_words.positive.length > 0 || result.sentiment_words.negative.length > 0) && (
                    <div style={{ marginBottom: '1.5rem' }}>
                      <h4 style={{ color: '#2c3e50', marginBottom: '0.5rem' }}>💭 Sentiment Indicators:</h4>
                      {result.sentiment_words.positive.length > 0 && (
                        <div style={{ marginBottom: '0.5rem' }}>
                          <span style={{ color: '#28a745', fontWeight: 'bold' }}>Positive: </span>
                          {result.sentiment_words.positive.join(', ')}
                        </div>
                      )}
                      {result.sentiment_words.negative.length > 0 && (
                        <div>
                          <span style={{ color: '#dc3545', fontWeight: 'bold' }}>Negative: </span>
                          {result.sentiment_words.negative.join(', ')}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Detailed Analysis Breakdown */}
                  {result.sentiment_analysis && (
                    <div style={{ marginBottom: '1.5rem' }}>
                      <h4 style={{ color: '#2c3e50', marginBottom: '0.5rem' }}>🔬 Analysis Breakdown:</h4>
                      <div style={{ 
                        background: '#f8f9fa', 
                        padding: '1rem', 
                        borderRadius: '4px',
                        fontSize: '0.85rem',
                        border: '1px solid #e9ecef'
                      }}>
                        <div style={{ marginBottom: '0.75rem' }}>
                          <strong>Strategy:</strong> {result.sentiment_analysis.model_used.replace(/_/g, ' ')}
                        </div>
                        
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                          <div>
                            <strong>English Analysis:</strong>
                            <div style={{ marginLeft: '1rem', marginTop: '0.25rem' }}>
                              Sentiment: <span style={{ color: getSentimentColor(result.sentiment_analysis.english_analysis.sentiment) }}>
                                {result.sentiment_analysis.english_analysis.sentiment}
                              </span><br/>
                              Confidence: {Math.round(result.sentiment_analysis.english_analysis.confidence * 100)}%
                            </div>
                          </div>
                          
                          <div>
                            <strong>Setswana Analysis:</strong>
                            <div style={{ marginLeft: '1rem', marginTop: '0.25rem' }}>
                              Sentiment: <span style={{ color: getSentimentColor(result.sentiment_analysis.setswana_analysis.sentiment) }}>
                                {result.sentiment_analysis.setswana_analysis.sentiment}
                              </span><br/>
                              Confidence: {Math.round(result.sentiment_analysis.setswana_analysis.confidence * 100)}%
                            </div>
                          </div>
                        </div>
                        
                        <div style={{ marginTop: '0.75rem', fontSize: '0.8rem', color: '#6c757d' }}>
                          Logic: {result.sentiment_analysis.combination_logic}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Political Context */}
                  {(result.political_context.entities.length > 0 || result.political_context.keywords.length > 0) && (
                    <div>
                      <h4 style={{ color: '#2c3e50', marginBottom: '0.5rem' }}>🏛️ Political Context:</h4>
                      
                      {result.political_context.entities.length > 0 && (
                        <div style={{ marginBottom: '0.75rem' }}>
                          <strong>Entities:</strong>
                          {result.political_context.entities.map((entity, i) => (
                            <span key={i} style={{ 
                              display: 'inline-block',
                              margin: '0.25rem 0.5rem 0.25rem 0',
                              padding: '0.25rem 0.5rem',
                              background: '#fff3cd',
                              borderRadius: '12px',
                              fontSize: '0.85rem'
                            }}>
                              {entity.entity} ({entity.type})
                            </span>
                          ))}
                        </div>
                      )}
                      
                      {result.political_context.keywords.length > 0 && (
                        <div>
                          <strong>Keywords:</strong>
                          {result.political_context.keywords.map((keyword, i) => (
                            <span key={i} style={{ 
                              display: 'inline-block',
                              margin: '0.25rem 0.5rem 0.25rem 0',
                              padding: '0.25rem 0.5rem',
                              background: '#d1ecf1',
                              borderRadius: '12px',
                              fontSize: '0.85rem'
                            }}>
                              {keyword.term} ({keyword.meaning})
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </>
              )}
            </div>
          )}
          
          {!result && !loading && (
            <div style={{ 
              padding: '2rem', 
              textAlign: 'center', 
              color: '#6c757d',
              background: '#f8f9fa',
              borderRadius: '8px',
              border: '2px dashed #dee2e6'
            }}>
              Enter text above or click an example to see analysis results
            </div>
          )}
        </div>
      </div>

      ) : (
        <LexiconManager />
      )}

      <footer style={{ 
        marginTop: '3rem', 
        padding: '1rem', 
        textAlign: 'center', 
        fontSize: '0.9rem', 
        color: '#6c757d',
        borderTop: '1px solid #e9ecef'
      }}>
        <p>
          🚀 Botswana Political Sentiment Analysis Platform | 
          Supporting Setswana-English code-switching | 
          Built for researchers, journalists, and political organizations
        </p>
      </footer>
    </div>
  );
}

export default App;