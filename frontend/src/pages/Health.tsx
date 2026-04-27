import React, { useEffect, useState } from 'react';
import { sentimentApi } from '../services/sentimentApi';
import { HealthStatus } from '../types/sentiment';

const Health: React.FC = () => {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const loadHealth = async () => {
      try {
        const data = await sentimentApi.checkHealth();
        setHealth(data);
      } catch {
        setHealth(null);
      } finally {
        setLoading(false);
      }
    };

    void loadHealth();
  }, []);

  const checks = [
    { name: 'API_GATEWAY', status: 'PASS', latency: '42ms' },
    { name: 'NLP_SENTIMENT_ENGINE', status: 'PASS', latency: '58ms' },
    { name: 'ENTITY_MATCHER', status: 'WARN', latency: '113ms' },
    { name: 'DATA_CLEANER_PIPELINE', status: 'PASS', latency: '64ms' },
    { name: 'LEXICON_STORAGE', status: 'PASS', latency: '22ms' },
  ];

  return (
    <div className="ml-64 pt-14 min-h-screen bg-surface">
      <div className="p-6 space-y-6">
        <div className="flex items-end justify-between border-b border-outline-variant/10 pb-4">
          <div>
            <h1 className="text-4xl font-headline font-bold tracking-tight text-on-surface uppercase">Data Health</h1>
            <p className="text-on-surface-variant font-mono text-xs mt-2">SYSTEM_DIAGNOSTICS</p>
          </div>
          <button className="bg-surface-container-high hover:bg-surface-bright text-on-surface text-[10px] font-headline uppercase font-bold px-4 py-2 flex items-center gap-2 border-b-2 border-primary transition-all">
            <span className="material-symbols-outlined text-sm">health_and_safety</span>
            Run Diagnostics
          </button>
        </div>

        <section className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-surface-container-low border border-outline-variant/10 p-4">
            <p className="font-mono text-[10px] uppercase text-on-surface-variant">Pipeline Uptime</p>
            <p className="text-3xl font-headline font-bold text-secondary mt-2">99.92%</p>
          </div>
          <div className="bg-surface-container-low border border-outline-variant/10 p-4">
            <p className="font-mono text-[10px] uppercase text-on-surface-variant">Duplicate Ratio</p>
            <p className="text-3xl font-headline font-bold text-primary mt-2">0.8%</p>
          </div>
          <div className="bg-surface-container-low border border-outline-variant/10 p-4">
            <p className="font-mono text-[10px] uppercase text-on-surface-variant">Setswana Lexicon</p>
            <p className="text-3xl font-headline font-bold text-on-surface mt-2">{health?.lexicon_stats?.setswana_words ?? '--'}</p>
          </div>
          <div className="bg-surface-container-low border border-outline-variant/10 p-4">
            <p className="font-mono text-[10px] uppercase text-on-surface-variant">Political Terms</p>
            <p className="text-3xl font-headline font-bold text-tertiary mt-2">{health?.lexicon_stats?.political_terms ?? '--'}</p>
          </div>
        </section>

        <section className="bg-surface-container-low border border-outline-variant/10 p-4">
          <p className="font-mono text-[10px] uppercase text-on-surface-variant">API Health Status</p>
          <p className={`font-headline text-xl mt-2 ${health?.status === 'healthy' ? 'text-secondary' : 'text-tertiary'}`}>
            {loading ? 'CHECKING...' : health?.status?.toUpperCase() || 'UNREACHABLE'}
          </p>
        </section>

        <section className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2 bg-surface-container-low border border-outline-variant/10 p-4">
            <h2 className="font-headline text-xs font-bold uppercase tracking-widest mb-4">Service Diagnostics</h2>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="text-left font-mono text-[9px] text-on-surface-variant uppercase border-b border-outline-variant/20">
                    <th className="pb-2 font-normal">Service</th>
                    <th className="pb-2 font-normal text-right">Status</th>
                    <th className="pb-2 font-normal text-right">Latency</th>
                  </tr>
                </thead>
                <tbody className="font-mono text-[10px]">
                  {checks.map((check) => (
                    <tr key={check.name} className="border-b border-outline-variant/10 hover:bg-surface-container-high transition-colors">
                      <td className="py-3 text-primary">{check.name}</td>
                      <td className={`py-3 text-right ${check.status === 'PASS' ? 'text-secondary' : 'text-tertiary'}`}>
                        {check.status}
                      </td>
                      <td className="py-3 text-right">{check.latency}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-surface-container-low border border-outline-variant/10 p-4">
            <h2 className="font-headline text-xs font-bold uppercase tracking-widest mb-4">Data Quality Score</h2>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between font-mono text-[10px] mb-1">
                  <span>Schema Integrity</span>
                  <span className="text-secondary">98%</span>
                </div>
                <div className="h-1 bg-surface-container-highest">
                  <div className="h-1 bg-secondary" style={{ width: '98%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between font-mono text-[10px] mb-1">
                  <span>Language Coverage</span>
                  <span className="text-primary">84%</span>
                </div>
                <div className="h-1 bg-surface-container-highest">
                  <div className="h-1 bg-primary" style={{ width: '84%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between font-mono text-[10px] mb-1">
                  <span>Label Confidence</span>
                  <span className="text-on-surface">79%</span>
                </div>
                <div className="h-1 bg-surface-container-highest">
                  <div className="h-1 bg-on-surface" style={{ width: '79%' }}></div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Health;
