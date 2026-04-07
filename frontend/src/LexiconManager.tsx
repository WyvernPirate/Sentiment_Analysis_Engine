import React, { useState, useEffect } from 'react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

interface LexiconStats {
  category_stats: Record<string, { word_count: number; recent_additions: number }>;
  metadata: {
    version: string;
    last_updated: string;
    total_words: number;
  };
  total_words: number;
}

interface WordSuggestion {
  word: string;
  meaning: string;
  category: string;
  context_sentence: string;
  sentiment?: string;
}

interface TrainingStats {
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

const LexiconManager: React.FC = () => {
  const [stats, setStats] = useState<LexiconStats | null>(null);
  const [trainingStats, setTrainingStats] = useState<TrainingStats | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [newWord, setNewWord] = useState<WordSuggestion>({
    word: '',
    meaning: '',
    category: 'positive',
    context_sentence: '',
    sentiment: 'positive'
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadStats();
    loadTrainingStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/lexicon/stats`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Failed to load lexicon stats:', error);
    }
  };

  const loadTrainingStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/training/stats`);
      const data = await response.json();
      setTrainingStats(data);
    } catch (error) {
      console.error('Failed to load training stats:', error);
    }
  };

  const searchLexicon = async () => {
    if (!searchQuery.trim()) return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/lexicon/search?q=${encodeURIComponent(searchQuery)}`);
      const data = await response.json();
      setSearchResults(data.results || []);
    } catch (error) {
      console.error('Search failed:', error);
      setSearchResults([]);
    }
  };

  const addWord = async () => {
    if (!newWord.word || !newWord.meaning || !newWord.context_sentence) {
      setMessage('Please fill in all required fields');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/lexicon/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newWord)
      });

      const data = await response.json();
      
      if (response.ok) {
        setMessage(`✅ Word "${newWord.word}" added successfully!`);
        setNewWord({ word: '', meaning: '', category: 'positive', context_sentence: '', sentiment: 'positive' });
        loadStats(); // Refresh stats
      } else {
        setMessage(`❌ Error: ${data.error}`);
      }
    } catch (error) {
      setMessage(`❌ Failed to add word: ${error}`);
    }
    setLoading(false);
  };

  const suggestWord = async () => {
    if (!newWord.word || !newWord.meaning || !newWord.context_sentence) {
      setMessage('Please fill in all required fields');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/lexicon/suggest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newWord)
      });

      const data = await response.json();
      
      if (response.ok) {
        setMessage(`✅ Word "${newWord.word}" suggested for review!`);
        setNewWord({ word: '', meaning: '', category: 'positive', context_sentence: '', sentiment: 'positive' });
      } else {
        setMessage(`❌ Error: ${data.error}`);
      }
    } catch (error) {
      setMessage(`❌ Failed to suggest word: ${error}`);
    }
    setLoading(false);
  };

  const quickRetrain = async () => {
    setLoading(true);
    setMessage('🔄 Starting quick retrain...');
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/training/quick-retrain`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      const data = await response.json();
      
      if (response.ok) {
        setMessage(`✅ Quick retrain completed! ${data.training_examples} examples, ${data.lexicon_suggestions} new suggestions`);
        loadStats();
        loadTrainingStats();
      } else {
        setMessage(`❌ Retrain failed: ${data.error}`);
      }
    } catch (error) {
      setMessage(`❌ Retrain failed: ${error}`);
    }
    setLoading(false);
  };

  const exportTrainingData = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/training/export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      const data = await response.json();
      
      if (response.ok) {
        setMessage(`✅ Training data exported to: ${data.filename}`);
      } else {
        setMessage(`❌ Export failed: ${data.error}`);
      }
    } catch (error) {
      setMessage(`❌ Export failed: ${error}`);
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '2rem auto', padding: '0 1rem', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ textAlign: 'center', color: '#2c3e50' }}>🔧 Lexicon & Training Manager</h1>
      
      {message && (
        <div style={{ 
          padding: '1rem', 
          marginBottom: '1rem', 
          background: message.includes('❌') ? '#f8d7da' : '#d4edda',
          border: `1px solid ${message.includes('❌') ? '#f5c6cb' : '#c3e6cb'}`,
          borderRadius: '4px',
          color: message.includes('❌') ? '#721c24' : '#155724'
        }}>
          {message}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '2rem' }}>
        {/* Lexicon Stats */}
        <div style={{ background: '#f8f9fa', padding: '1.5rem', borderRadius: '8px' }}>
          <h3>📊 Lexicon Statistics</h3>
          {stats ? (
            <>
              <div style={{ marginBottom: '1rem' }}>
                <strong>Total Words: {stats.total_words}</strong>
              </div>
              <div style={{ marginBottom: '1rem' }}>
                <strong>Last Updated:</strong> {new Date(stats.metadata.last_updated).toLocaleString()}
              </div>
              <div>
                <strong>Categories:</strong>
                {Object.entries(stats.category_stats).map(([category, data]) => (
                  <div key={category} style={{ marginLeft: '1rem', fontSize: '0.9rem' }}>
                    {category}: {data.word_count} words
                    {data.recent_additions > 0 && (
                      <span style={{ color: '#28a745' }}> (+{data.recent_additions} recent)</span>
                    )}
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div>Loading...</div>
          )}
        </div>

        {/* Training Stats */}
        <div style={{ background: '#f8f9fa', padding: '1.5rem', borderRadius: '8px' }}>
          <h3>🎓 Training Statistics</h3>
          {trainingStats ? (
            <>
              <div style={{ marginBottom: '0.5rem' }}>
                <strong>Total Feedback:</strong> {trainingStats.feedback_stats.total_feedback}
              </div>
              <div style={{ marginBottom: '0.5rem' }}>
                <strong>Agreement Rate:</strong> {Math.round(trainingStats.feedback_stats.agreement_rate * 100)}%
              </div>
              <div style={{ marginBottom: '0.5rem' }}>
                <strong>Model Accuracy:</strong> {Math.round(trainingStats.performance_analysis.overall_accuracy * 100)}%
              </div>
              <div style={{ marginBottom: '0.5rem' }}>
                <strong>Corrections Needed:</strong> {trainingStats.feedback_stats.corrections_needed}
              </div>
              <div>
                <strong>Word Suggestions:</strong> {trainingStats.feedback_stats.new_word_suggestions}
              </div>
            </>
          ) : (
            <div>Loading...</div>
          )}
        </div>
      </div>

      {/* Search Lexicon */}
      <div style={{ background: '#f8f9fa', padding: '1.5rem', borderRadius: '8px', marginBottom: '2rem' }}>
        <h3>🔍 Search Lexicon</h3>
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search for words or meanings..."
            style={{ flex: 1, padding: '0.5rem', border: '1px solid #ccc', borderRadius: '4px' }}
            onKeyPress={(e) => e.key === 'Enter' && searchLexicon()}
          />
          <button 
            onClick={searchLexicon}
            style={{ padding: '0.5rem 1rem', background: '#007bff', color: 'white', border: 'none', borderRadius: '4px' }}
          >
            Search
          </button>
        </div>
        
        {searchResults.length > 0 && (
          <div>
            <h4>Results ({searchResults.length}):</h4>
            {searchResults.map((result, index) => (
              <div key={index} style={{ 
                padding: '0.75rem', 
                margin: '0.5rem 0', 
                background: 'white', 
                border: '1px solid #dee2e6', 
                borderRadius: '4px' 
              }}>
                <strong>{result.word}</strong> ({result.category})
                <div style={{ fontSize: '0.9rem', color: '#6c757d' }}>
                  {result.details.meaning}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add/Suggest Words */}
      <div style={{ background: '#f8f9fa', padding: '1.5rem', borderRadius: '8px', marginBottom: '2rem' }}>
        <h3>➕ Add New Word</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
          <input
            type="text"
            value={newWord.word}
            onChange={(e) => setNewWord({...newWord, word: e.target.value})}
            placeholder="Setswana word"
            style={{ padding: '0.5rem', border: '1px solid #ccc', borderRadius: '4px' }}
          />
          <input
            type="text"
            value={newWord.meaning}
            onChange={(e) => setNewWord({...newWord, meaning: e.target.value})}
            placeholder="English meaning"
            style={{ padding: '0.5rem', border: '1px solid #ccc', borderRadius: '4px' }}
          />
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
          <select
            value={newWord.category}
            onChange={(e) => setNewWord({...newWord, category: e.target.value})}
            style={{ padding: '0.5rem', border: '1px solid #ccc', borderRadius: '4px' }}
          >
            <option value="positive">Positive</option>
            <option value="negative">Negative</option>
            <option value="political">Political</option>
            <option value="common_words">Common Words</option>
            <option value="botswana_specific">Botswana Specific</option>
          </select>
          <select
            value={newWord.sentiment || ''}
            onChange={(e) => setNewWord({...newWord, sentiment: e.target.value})}
            style={{ padding: '0.5rem', border: '1px solid #ccc', borderRadius: '4px' }}
          >
            <option value="positive">Positive Sentiment</option>
            <option value="negative">Negative Sentiment</option>
            <option value="neutral">Neutral Sentiment</option>
          </select>
        </div>
        
        <textarea
          value={newWord.context_sentence}
          onChange={(e) => setNewWord({...newWord, context_sentence: e.target.value})}
          placeholder="Example sentence using this word..."
          style={{ 
            width: '100%', 
            height: '80px', 
            padding: '0.5rem', 
            border: '1px solid #ccc', 
            borderRadius: '4px',
            marginBottom: '1rem'
          }}
        />
        
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button 
            onClick={addWord}
            disabled={loading}
            style={{ 
              padding: '0.75rem 1.5rem', 
              background: '#28a745', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? 'Adding...' : 'Add Directly'}
          </button>
          <button 
            onClick={suggestWord}
            disabled={loading}
            style={{ 
              padding: '0.75rem 1.5rem', 
              background: '#ffc107', 
              color: 'black', 
              border: 'none', 
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? 'Suggesting...' : 'Suggest for Review'}
          </button>
        </div>
      </div>

      {/* Training Actions */}
      <div style={{ background: '#f8f9fa', padding: '1.5rem', borderRadius: '8px' }}>
        <h3>🤖 Training Actions</h3>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <button 
            onClick={quickRetrain}
            disabled={loading}
            style={{ 
              padding: '0.75rem 1.5rem', 
              background: '#007bff', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? 'Retraining...' : 'Quick Retrain'}
          </button>
          <button 
            onClick={exportTrainingData}
            disabled={loading}
            style={{ 
              padding: '0.75rem 1.5rem', 
              background: '#6c757d', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? 'Exporting...' : 'Export Training Data'}
          </button>
        </div>
        
        <div style={{ marginTop: '1rem', fontSize: '0.9rem', color: '#6c757d' }}>
          <strong>Quick Retrain:</strong> Updates lexicon and prepares training data with user feedback<br/>
          <strong>Export Training Data:</strong> Creates CSV file with all training examples for external use
        </div>
      </div>
    </div>
  );
};

export default LexiconManager;