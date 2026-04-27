import React, { useEffect, useMemo, useState } from 'react';
import { sentimentApi } from '../services/sentimentApi';
import { SocialCollection, SocialHealthStatus } from '../types/sentiment';

const Scraping: React.FC = () => {
  const [socialHealth, setSocialHealth] = useState<SocialHealthStatus | null>(null);
  const [collections, setCollections] = useState<SocialCollection[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const fallbackSources = [
    { source: 'X API Stream', region: 'BW', status: 'ONLINE', recordsPerMin: 486, failureRate: '0.2%' },
    { source: 'Facebook Public Feed', region: 'BW', status: 'ONLINE', recordsPerMin: 221, failureRate: '0.9%' },
    { source: 'News RSS Cluster', region: 'SADC', status: 'DEGRADED', recordsPerMin: 77, failureRate: '3.1%' },
    { source: 'Community Forums', region: 'BW', status: 'ONLINE', recordsPerMin: 92, failureRate: '1.2%' },
  ];

  useEffect(() => {
    const loadSocialData = async () => {
      try {
        const [healthData, collectionData] = await Promise.all([
          sentimentApi.checkSocialHealth(),
          sentimentApi.listSocialCollections(10),
        ]);

        setSocialHealth(healthData);
        setCollections(collectionData);
      } finally {
        setLoading(false);
      }
    };

    void loadSocialData();
  }, []);

  const totalIngested = useMemo(() => collections.reduce((acc, row) => acc + (row.count || 0), 0), [collections]);

  const recentEvents = useMemo(() => {
    if (!collections.length) {
      return [
        '14:09:11 | CONNECTOR x-api-eu-west recovered',
        '14:03:28 | rss-botswana timeout spike detected',
        '13:57:05 | queue rebalance completed',
      ];
    }

    return collections.slice(0, 3).map((item) => {
      const timestamp = new Date(item.collected_at_utc).toLocaleTimeString([], { hour12: false });
      return `${timestamp} | ${item.collection_id} ingested ${item.count} records`;
    });
  }, [collections]);

  const sourceRows = useMemo(() => {
    if (!socialHealth) {
      return fallbackSources;
    }

    return [
      {
        source: 'Bright Data Provider',
        region: 'GLOBAL',
        status: socialHealth.brightdata_configured ? 'ONLINE' : 'DEGRADED',
        recordsPerMin: collections[0]?.count || 0,
        failureRate: socialHealth.brightdata_configured ? '0.3%' : '100%',
      },
      {
        source: 'Apify Provider',
        region: 'GLOBAL',
        status: socialHealth.apify_configured ? 'ONLINE' : 'DEGRADED',
        recordsPerMin: collections[1]?.count || 0,
        failureRate: socialHealth.apify_configured ? '0.6%' : '100%',
      },
      {
        source: 'Twikit Provider',
        region: 'BW',
        status: socialHealth.twikit_configured ? 'ONLINE' : 'DEGRADED',
        recordsPerMin: collections[2]?.count || 0,
        failureRate: socialHealth.twikit_configured ? '1.1%' : '100%',
      },
    ];
  }, [socialHealth, collections]);

  const activeSources = sourceRows.filter((row) => row.status === 'ONLINE').length;

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
            <p className="text-3xl font-headline font-bold text-primary mt-2">{activeSources || '--'}</p>
          </div>
          <div className="bg-surface-container-low border border-outline-variant/10 p-4">
            <p className="font-mono text-[10px] uppercase text-on-surface-variant">Ingested / Min</p>
            <p className="text-3xl font-headline font-bold text-secondary mt-2">{totalIngested || '--'}</p>
          </div>
          <div className="bg-surface-container-low border border-outline-variant/10 p-4">
            <p className="font-mono text-[10px] uppercase text-on-surface-variant">Queue Depth</p>
            <p className="text-3xl font-headline font-bold text-on-surface mt-2">{collections.length ? `${collections.length} B` : '--'}</p>
          </div>
          <div className="bg-surface-container-low border border-outline-variant/10 p-4">
            <p className="font-mono text-[10px] uppercase text-on-surface-variant">Provider Default</p>
            <p className="text-3xl font-headline font-bold text-tertiary mt-2">{socialHealth?.provider_default || '--'}</p>
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
                {sourceRows.map((row) => (
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
              <p className="text-secondary">{recentEvents[0]}</p>
              <p className="text-tertiary">{recentEvents[1] || 'NO_RECENT_EVENT'}</p>
              <p className="text-on-surface-variant">{recentEvents[2] || 'NO_RECENT_EVENT'}</p>
            </div>
          </div>
        </section>
        {loading && <p className="text-on-surface-variant font-mono text-[10px]">SYNCING_SOURCES...</p>}
      </div>
    </div>
  );
};

export default Scraping;
