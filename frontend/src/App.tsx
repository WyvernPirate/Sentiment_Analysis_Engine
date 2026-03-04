import React, { useState, useEffect } from 'react';
import './App.css';
import DashboardPage from './pages/DashboardPage';
import EnhancedDashboard from './components/EnhancedDashboard';
import LexiconManager from './LexiconManager';

// New Components
import Navigation from './components/Common/Navigation';
import ManualAnalyzer from './components/Analysis/ManualAnalyzer';
import ResultDisplay from './components/Analysis/ResultDisplay';

// Services and Types
import { sentimentApi } from './services/sentimentApi';
import { SentimentResult, TestExample, HealthStatus } from './types/sentiment';

function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'insights' | 'analyzer' | 'lexicon'>('analyzer');
  const [input, setInput] = useState('');
  const [result, setResult] = useState<SentimentResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [examples, setExamples] = useState<TestExample[]>([]);
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null);

  useEffect(() => {
    sentimentApi.loadTestExamples().then(setExamples).catch(console.error);
    sentimentApi.checkHealth().then(setHealthStatus).catch(console.error);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await sentimentApi.analyzeText(input);
      setResult(data);
    } catch (error) {
      setResult({ error: 'API connection failed' } as SentimentResult);
    }
    setLoading(false);
  };

  const tryExample = (text: string) => {
    setInput(text);
    sentimentApi.analyzeText(text).then(setResult).catch(() => setResult({ error: 'API failed' } as SentimentResult));
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '2rem auto', fontFamily: 'Arial, sans-serif', padding: '0 1rem' }}>
      <Navigation 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        healthStatus={healthStatus} 
      />

      <main>
        {activeTab === 'insights' && <EnhancedDashboard />}
        {activeTab === 'dashboard' && <DashboardPage />}
        {activeTab === 'analyzer' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
            <ManualAnalyzer 
              input={input} 
              setInput={setInput} 
              handleSubmit={handleSubmit}
              loading={loading}
              examples={examples}
              tryExample={tryExample}
            />
            <ResultDisplay result={result} loading={loading} />
          </div>
        )}
        {activeTab === 'lexicon' && <LexiconManager />}
      </main>

      <footer style={{ marginTop: '3rem', padding: '1rem', textAlign: 'center', color: '#6c757d', borderTop: '1px solid #e9ecef' }}>
        <p>🚀 Botswana Political Sentiment Analysis Platform | Refactored Monorepo</p>
      </footer>
    </div>
  );
}

export default App;