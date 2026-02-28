import React from 'react';
import { TestExample } from '../../types/sentiment';

interface ManualAnalyzerProps {
  input: string;
  setInput: (val: string) => void;
  handleSubmit: (e: React.FormEvent) => void;
  loading: boolean;
  examples: TestExample[];
  tryExample: (text: string) => void;
}

const ManualAnalyzer: React.FC<ManualAnalyzerProps> = ({ 
  input, setInput, handleSubmit, loading, examples, tryExample 
}) => {
  return (
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
  );
};

export default ManualAnalyzer;
