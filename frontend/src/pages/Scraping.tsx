import React from 'react';

const Scraping: React.FC = () => {
  const sources = [
    { source: 'X API Stream', region: 'BW', status: 'ONLINE', recordsPerMin: 486, failureRate: '0.2%' },
    { source: 'Facebook Public Feed', region: 'BW', status: 'ONLINE', recordsPerMin: 221, failureRate: '0.9%' },
    { source: 'News RSS Cluster', region: 'SADC', status: 'DEGRADED', recordsPerMin: 77, failureRate: '3.1%' },
    { source: 'Community Forums', region: 'BW', status: 'ONLINE', recordsPerMin: 92, failureRate: '1.2%' },
  ];

  return (
    <div className="ml-64 pt-14 min-h-screen bg-surface">
      <div className="p-6 space-y-6">
        <div className="flex items-end justify-between border-b border-outline-variant/10 pb-4">
          <div>
            <h1 className="text-4xl font-headline font-bold tracking-tight text-on-surface uppercase">Scraping Sources</h1>
            <p className="text-on-surface-variant font-mono text-xs mt-2">DATA_COLLECTION_SYSTEM</p>
          </div>
          <button className="bg-surface-container-high hover:bg-surface-bright text-on-surface text-[10px] font-headline uppercase font-bold px-4 py-2 flex items-center gap-2 border-b-2 border-primary transition-all">
            <span className="material-symbols-outlined text-sm">sync</span>
            Resync Sources
          </button>
        </div>

        <section className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-surface-container-low border border-outline-variant/10 p-4">
            <p className="font-mono text-[10px] uppercase text-on-surface-variant">Active Sources</p>
            <p className="text-3xl font-headline font-bold text-primary mt-2">12</p>
          </div>
          <div className="bg-surface-container-low border border-outline-variant/10 p-4">
            <p className="font-mono text-[10px] uppercase text-on-surface-variant">Ingested / Min</p>
            <p className="text-3xl font-headline font-bold text-secondary mt-2">876</p>
          </div>
          <div className="bg-surface-container-low border border-outline-variant/10 p-4">
            <p className="font-mono text-[10px] uppercase text-on-surface-variant">Queue Depth</p>
            <p className="text-3xl font-headline font-bold text-on-surface mt-2">2.4K</p>
          </div>
          <div className="bg-surface-container-low border border-outline-variant/10 p-4">
            <p className="font-mono text-[10px] uppercase text-on-surface-variant">Failed Jobs (24h)</p>
            <p className="text-3xl font-headline font-bold text-tertiary mt-2">17</p>
          </div>
        </section>

        <section className="bg-surface-container-low border border-outline-variant/10 p-4">
          <h2 className="font-headline text-xs font-bold uppercase tracking-widest mb-4">Source Health Matrix</h2>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="text-left font-mono text-[9px] text-on-surface-variant uppercase border-b border-outline-variant/20">
                  <th className="pb-2 font-normal">Source</th>
                  <th className="pb-2 font-normal text-right">Region</th>
                  <th className="pb-2 font-normal text-right">Status</th>
                  <th className="pb-2 font-normal text-right">Records / Min</th>
                  <th className="pb-2 font-normal text-right">Failure Rate</th>
                </tr>
              </thead>
              <tbody className="font-mono text-[10px]">
                {sources.map((row) => (
                  <tr key={row.source} className="border-b border-outline-variant/10 hover:bg-surface-container-high transition-colors">
                    <td className="py-3 text-primary">{row.source}</td>
                    <td className="py-3 text-right">{row.region}</td>
                    <td className={`py-3 text-right ${row.status === 'ONLINE' ? 'text-secondary' : 'text-tertiary'}`}>
                      {row.status}
                    </td>
                    <td className="py-3 text-right">{row.recordsPerMin}</td>
                    <td className="py-3 text-right">{row.failureRate}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-surface-container-low border border-outline-variant/10 p-4">
            <h3 className="font-headline text-xs font-bold uppercase tracking-widest mb-3">Collector Throughput</h3>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between font-mono text-[10px] mb-1">
                  <span>X_STREAM_CLUSTER</span>
                  <span className="text-secondary">92%</span>
                </div>
                <div className="h-1 bg-surface-container-highest">
                  <div className="h-1 bg-secondary" style={{ width: '92%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between font-mono text-[10px] mb-1">
                  <span>RSS_POLLING_POOL</span>
                  <span className="text-primary">67%</span>
                </div>
                <div className="h-1 bg-surface-container-highest">
                  <div className="h-1 bg-primary" style={{ width: '67%' }}></div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-surface-container-low border border-outline-variant/10 p-4">
            <h3 className="font-headline text-xs font-bold uppercase tracking-widest mb-3">Recent Events</h3>
            <div className="space-y-2 font-mono text-[10px]">
              <p className="text-secondary">14:09:11 | CONNECTOR x-api-eu-west recovered</p>
              <p className="text-tertiary">14:03:28 | rss-botswana timeout spike detected</p>
              <p className="text-on-surface-variant">13:57:05 | queue rebalance completed</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Scraping;
