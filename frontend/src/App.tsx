import React, { useEffect, useState } from 'react';
import './App.css';
import LexiconManager from './LexiconManager';
import ManualAnalyzer from './components/Analysis/ManualAnalyzer';
import ResultDisplay from './components/Analysis/ResultDisplay';
import { sentimentApi } from './services/sentimentApi';
import { HealthStatus, SentimentResult, TestExample } from './types/sentiment';

function App() {
  const [input, setInput] = useState('');
  const [result, setResult] = useState<SentimentResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [examples, setExamples] = useState<TestExample[]>([]);
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null);

  useEffect(() => {
    // Keep startup work small: only load test examples and a basic health check.
    sentimentApi.loadTestExamples().then(setExamples).catch(() => setExamples([]));
    sentimentApi.checkHealth().then(setHealthStatus).catch(() => setHealthStatus(null));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) {
      return;
    }

    setLoading(true);
    try {
      const data = await sentimentApi.analyzeText(input);
      setResult(data);
    } catch {
      setResult({ error: 'API connection failed' } as SentimentResult);
    } finally {
      setLoading(false);
    }
  };

  const tryExample = (text: string) => {
    setInput(text);
    setLoading(true);
    sentimentApi.analyzeText(text)
      .then(setResult)
      .catch(() => setResult({ error: 'API failed' } as SentimentResult))
      .finally(() => setLoading(false));
  };

  return (
    <div className="app-shell">
      <header className="hero-card">
        <div>
          <p className="eyebrow">Sentiment Analysis Engine</p>
          <h1>English sentiment with live political word matching</h1>
          <p className="hero-copy">
            Submit plain English text, inspect the transformer result, and update the lexicon without restarting the server.
          </p>
        </div>

        <div className="health-chip">
          <span className={`health-dot ${healthStatus?.status === 'healthy' ? 'healthy' : 'offline'}`} />
          <span>{healthStatus?.status === 'healthy' ? 'Backend healthy' : 'Backend unavailable'}</span>
        </div>
      </header>

      <main className="app-grid">
        <section className="panel">
          <ManualAnalyzer
            input={input}
            setInput={setInput}
            handleSubmit={handleSubmit}
            loading={loading}
            examples={examples}
            tryExample={tryExample}
          />
        </section>

        <section className="panel">
          <ResultDisplay result={result} loading={loading} />
        </section>

        <section className="panel panel-span">
          <LexiconManager />
        </section>
      </main>

      <footer className="app-footer">
        <span>Minimal frontend: analyzer + lexicon only.</span>
      </footer>
    </div>
  );
}

export default App;