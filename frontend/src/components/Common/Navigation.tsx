import React from 'react';

interface NavigationProps {
  activeTab: string;
  setActiveTab: (tab: any) => void;
  healthStatus: any;
}

const Navigation: React.FC<NavigationProps> = ({ activeTab, setActiveTab, healthStatus }) => {
  const tabs = [
    { id: 'insights', label: '🧠 Intelligence' },
    { id: 'dashboard', label: '📊 Overview' },
    { id: 'analyzer', label: '🔍 Analyzer' },
    { id: 'lexicon', label: '🔧 Management' }
  ];

  return (
    <header style={{ textAlign: 'center', marginBottom: '2rem' }}>
      <h1 style={{ color: '#2c3e50' }}>🇧🇼 Botswana Political Sentiment Analysis</h1>
      <p style={{ color: '#7f8c8d' }}>
        Advanced sentiment analysis with Setswana-English code-switching support
      </p>
      
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        gap: '0.5rem', 
        marginTop: '1.5rem',
        marginBottom: '1rem'
      }}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: '0.75rem 1.25rem',
              background: activeTab === tab.id ? '#007bff' : '#f8f9fa',
              color: activeTab === tab.id ? 'white' : '#6c757d',
              border: '1px solid #dee2e6',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.95rem',
              fontWeight: activeTab === tab.id ? 'bold' : 'normal'
            }}
          >
            {tab.label}
          </button>
        ))}
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
  );
};

export default Navigation;
