import React from 'react';

interface SentimentDataPoint {
  label: string;
  percentage: number;
  color: string;
}

interface FeedItem {
  author: string;
  timestamp: string;
  text: string;
  sentiment: 'POS' | 'NEU' | 'NEG';
  tags: string[];
}

interface TemporalData {
  entity: string;
  score: number;
  percentage: number;
  color: string;
}

const Analytics: React.FC = () => {
  // Mock data
  const sentimentDistribution: SentimentDataPoint[] = [
    { label: 'Positive', percentage: 40, color: 'primary' },
    { label: 'Neutral', percentage: 35, color: 'on-surface-variant' },
    { label: 'Negative', percentage: 25, color: 'tertiary' },
  ];

  const feedItems: FeedItem[] = [
    {
      author: '@Lobatse_Voice',
      timestamp: '14:02:11',
      text: 'Dumelang bagaetsho! The new diamond deal is exactly what our economy needed. Pula! 💎✨',
      sentiment: 'POS',
      tags: ['#ECONOMY', '#BDP'],
    },
    {
      author: '@KgalagadiUser',
      timestamp: '14:01:45',
      text: 'Still waiting for drought relief funds in our district. Bo mmasepala must explain gore madi a ile kae. Very frustrated.',
      sentiment: 'NEG',
      tags: ['#SERVICE_DELIVERY'],
    },
    {
      author: '@Bots_Politics',
      timestamp: '13:59:02',
      text: 'Constituency boundaries review meeting taking place at 3PM today. No major updates yet.',
      sentiment: 'NEU',
      tags: ['#IEC'],
    },
  ];

  const temporalData: TemporalData[] = [
    { entity: 'BDP', score: 0.55, percentage: 65, color: 'primary' },
    { entity: 'UDC', score: -0.12, percentage: 42, color: 'tertiary' },
    { entity: 'BCP', score: 0.05, percentage: 28, color: 'on-surface-variant' },
  ];

  const policyReceptivity = [
    { label: 'Diamond Revenue Framework', favourable: 82 },
    { label: 'Drought Relief Measures', favourable: 38 },
    { label: 'Land Reform Program', favourable: 51 },
  ];

  const influencerMatrix = [
    { handle: '@POLITICO_BW', reach: '452.1K', sentiment: '+0.78', volatility: 0.12, engagement: 4.2 },
    { handle: '@YOUTH_VOICE_BW', reach: '211.5K', sentiment: '-0.34', volatility: 0.88, engagement: 12.5 },
    { handle: '@TLOKWENG_TIMES', reach: '88.2K', sentiment: '+0.02', volatility: 0.45, engagement: 1.8 },
    { handle: '@BW_ECON_WATCH', reach: '156.0K', sentiment: '+0.61', volatility: 0.21, engagement: 7.9 },
  ];

  return (
    <div className="ml-64 pt-14 min-h-screen bg-surface">
      <div className="p-6 space-y-6">
        {/* Header Section */}
        <div className="flex justify-between items-end pb-4 border-b border-outline-variant/10">
          <div>
            <h1 className="text-4xl font-headline font-bold tracking-tight text-on-surface uppercase">Analytics</h1>
            <p className="text-on-surface-variant font-mono text-xs mt-1">
              Status: <span className="text-secondary">SYSTEM_OPTIMAL</span> | Latency: <span className="text-primary">42ms</span> | Region: Gaborone_HQ
            </p>
          </div>
          <div className="flex gap-2">
            <button className="bg-surface-container-high hover:bg-surface-bright text-on-surface text-[10px] font-headline uppercase font-bold px-4 py-2 flex items-center gap-2 border-b-2 border-primary transition-all">
              <span className="material-symbols-outlined text-sm">refresh</span> Refresh Data
            </button>
            <button className="bg-primary text-on-primary text-[10px] font-headline uppercase font-bold px-4 py-2 flex items-center gap-2 transition-all hover:brightness-110">
              <span className="material-symbols-outlined text-sm">download</span> Export
            </button>
          </div>
        </div>

        {/* Filters & Global Stats Bar */}
        <section className="flex flex-wrap items-center justify-between gap-4 bg-surface-container-low p-4 border border-outline-variant/10">
          <div className="flex items-center gap-4">
            <div className="flex flex-col">
              <span className="font-label text-[10px] text-on-surface-variant uppercase tracking-[0.2em]">Filter Profile</span>
              <div className="flex gap-2 mt-1">
                <select className="bg-surface-container-lowest border-0 text-xs font-mono text-primary px-2 py-1 focus:ring-0">
                  <option>REGION: GABORONE</option>
                  <option>REGION: NORTH_WEST</option>
                </select>
                <select className="bg-surface-container-lowest border-0 text-xs font-mono text-primary px-2 py-1 focus:ring-0">
                  <option>PARTY: ALL_GROUPS</option>
                  <option>PARTY: BDP</option>
                  <option>PARTY: UDC</option>
                </select>
                <select className="bg-surface-container-lowest border-0 text-xs font-mono text-primary px-2 py-1 focus:ring-0">
                  <option>SOURCE: X_FIREHOSE</option>
                  <option>SOURCE: FB_PUBLIC</option>
                </select>
              </div>
            </div>
          </div>
          <div className="flex gap-8">
            <div className="text-right">
              <p className="font-mono text-[10px] text-on-surface-variant uppercase">Aggregated Score</p>
              <p className="font-headline font-bold text-secondary text-2xl">
                +0.42 <span className="text-xs font-mono font-normal ml-1">POS</span>
              </p>
            </div>
            <div className="text-right">
              <p className="font-mono text-[10px] text-on-surface-variant uppercase">Voter Volatility</p>
              <p className="font-headline font-bold text-tertiary text-2xl">
                12.4% <span className="text-xs font-mono font-normal ml-1">HIGH</span>
              </p>
            </div>
          </div>
        </section>

        {/* Main Grid */}
        <div className="grid grid-cols-12 gap-6">
          {/* Sentiment Distribution Chart */}
          <div className="col-span-12 lg:col-span-8 bg-surface-container-low border border-outline-variant/10 overflow-hidden">
            <div className="p-4 border-b border-outline-variant/10 flex justify-between items-center">
              <h2 className="font-headline text-xs font-bold uppercase tracking-widest flex items-center gap-2">
                <span className="w-1.5 h-1.5 bg-primary"></span>
                SENTIMENT_DISTRIBUTION
              </h2>
              <span className="font-mono text-[10px] text-on-surface-variant">MAP_ID: BW_G_57</span>
            </div>
            <div className="relative h-80 bg-black/40 flex items-center justify-center p-8">
              <div className="flex flex-col md:flex-row items-center justify-center gap-12 w-full max-w-2xl">
                {/* Pie Chart Visualization (SVG) */}
                <div className="relative w-64 h-64">
                  <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                    <circle
                      cx="50"
                      cy="50"
                      r="40"
                      fill="transparent"
                      stroke="#86bdf7"
                      strokeDasharray="100.5 150.7"
                      strokeDashoffset="-113"
                      strokeWidth="20"
                      className="opacity-80 hover:opacity-100 transition-opacity cursor-pointer"
                    />
                    <circle
                      cx="50"
                      cy="50"
                      r="40"
                      fill="transparent"
                      stroke="#adaaaa"
                      strokeDasharray="87.9 163.3"
                      strokeDashoffset="-25.1"
                      strokeWidth="20"
                      className="opacity-80 hover:opacity-100 transition-opacity cursor-pointer"
                    />
                    <circle
                      cx="50"
                      cy="50"
                      r="40"
                      fill="transparent"
                      stroke="#ff716c"
                      strokeDasharray="15.7 235.5"
                      strokeDashoffset="0"
                      strokeWidth="20"
                      className="opacity-80 hover:opacity-100 transition-opacity cursor-pointer"
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                    <span className="font-headline text-3xl font-black text-on-surface tracking-tighter">100%</span>
                    <span className="font-mono text-[8px] text-on-surface-variant uppercase">Total Ingested</span>
                  </div>
                </div>

                {/* Legend */}
                <div className="space-y-6 min-w-[200px]">
                  {sentimentDistribution.map((item) => (
                    <div key={item.label} className="flex items-center justify-between border-b border-outline-variant/10 pb-2">
                      <div className="flex items-center gap-3">
                        <div
                          className={`w-3 h-3 ${
                            item.color === 'primary'
                              ? 'bg-primary'
                              : item.color === 'on-surface-variant'
                                ? 'bg-on-surface-variant'
                                : 'bg-tertiary'
                          }`}
                        ></div>
                        <span className="font-mono text-xs uppercase text-on-surface-variant">{item.label}</span>
                      </div>
                      <span className={`font-headline font-bold ${item.color === 'primary' ? 'text-primary' : item.color === 'on-surface-variant' ? 'text-on-surface' : 'text-tertiary'}`}>
                        {item.percentage}%
                      </span>
                    </div>
                  ))}
                  <div className="pt-2">
                    <p className="font-mono text-[10px] text-primary bg-primary/5 p-2 border-l border-primary">
                      <span className="material-symbols-outlined text-[12px] align-text-bottom">trending_up</span> Net positive sentiment
                      increased by 3.2% in last 6h interval.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Real-time Feed */}
          <div className="col-span-12 lg:col-span-4 bg-surface-container-low border border-outline-variant/10 flex flex-col max-h-96">
            <div className="p-4 border-b border-outline-variant/10 flex justify-between items-center bg-black/20">
              <h2 className="font-headline text-xs font-bold uppercase tracking-widest flex items-center gap-2">
                <span className="w-1.5 h-1.5 bg-tertiary animate-pulse"></span>
                REALTIME_INGESTION_FEED
              </h2>
              <span className="font-mono text-[10px] text-secondary">LIVE_SYNC</span>
            </div>
            <div className="overflow-y-auto flex-1 p-4 font-mono text-[11px] space-y-4">
              {feedItems.map((item, idx) => (
                <div key={idx} className="group hover:bg-surface-container-high p-2 border-l border-outline-variant/30 transition-all">
                  <div className="flex justify-between mb-1">
                    <span className="text-primary-dim">{item.author}</span>
                    <span className="text-on-surface-variant">{item.timestamp}</span>
                  </div>
                  <p className="text-on-surface text-sm">{item.text}</p>
                  <div className="mt-2 flex gap-2">
                    <span
                      className={`px-1 text-[9px] ${
                        item.sentiment === 'POS' ? 'bg-secondary/10 text-secondary' : item.sentiment === 'NEG' ? 'bg-tertiary/10 text-tertiary' : 'bg-on-surface-variant/10 text-on-surface-variant'
                      }`}
                    >
                      SENTIMENT: {item.sentiment}
                    </span>
                    <span className="text-on-surface-variant text-[9px]">{item.tags.join(' ')}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Temporal Sentiment Chart */}
          <div className="col-span-12 md:col-span-6 bg-surface-container-low border border-outline-variant/10 p-4">
            <h2 className="font-headline text-xs font-bold uppercase tracking-widest flex items-center gap-2 mb-6">
              <span className="w-1.5 h-1.5 bg-primary"></span>
              TEMPORAL_SENTIMENT_VARIATION (24H)
            </h2>
            <div className="space-y-4">
              {temporalData.map((item) => (
                <div key={item.entity} className="flex items-center gap-4">
                  <span className="font-mono text-[10px] w-8">{item.entity}</span>
                  <div className="flex-1 h-3 bg-surface-container-highest border border-outline-variant/10">
                    <div
                      className={`h-full ${item.color === 'primary' ? 'bg-primary' : item.color === 'on-surface-variant' ? 'bg-on-surface-variant' : 'bg-tertiary'}`}
                      style={{ width: `${item.percentage}%` }}
                    ></div>
                  </div>
                  <span className={`font-mono text-[10px] ${item.color === 'primary' ? 'text-secondary' : item.color === 'on-surface-variant' ? 'text-on-surface-variant' : 'text-tertiary'}`}>
                    {item.score > 0 ? '+' : ''}{item.score.toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Policy Receptivity */}
          <div className="col-span-12 md:col-span-6 bg-surface-container-low border border-outline-variant/10 p-4">
            <h2 className="font-headline text-xs font-bold uppercase tracking-widest flex items-center gap-2 mb-6">
              <span className="w-1.5 h-1.5 bg-primary"></span>
              CRITICAL_POLICY_RECEPTIVITY
            </h2>
            <div className="space-y-6">
              {policyReceptivity.map((policy) => (
                <div key={policy.label}>
                  <div className="flex justify-between mb-1">
                    <span className="font-mono text-[10px] text-on-surface uppercase">{policy.label}</span>
                    <span className="font-mono text-[10px] text-secondary">{policy.favourable}% FAV</span>
                  </div>
                  <div className="w-full h-1 bg-surface-container-highest">
                    <div className="h-full bg-secondary" style={{ width: `${policy.favourable}%` }}></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Influencer Matrix */}
          <div className="col-span-12 bg-surface-container-low border border-outline-variant/10 p-4">
            <h2 className="font-headline text-xs font-bold uppercase tracking-widest flex items-center gap-2 mb-4">
              <span className="w-1.5 h-1.5 bg-primary"></span>
              INFLUENCE_IMPACT_MATRIX
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="text-left font-mono text-[9px] text-on-surface-variant uppercase border-b border-outline-variant/20">
                    <th className="pb-2 font-normal">Entity_ID</th>
                    <th className="pb-2 font-normal text-right">Reach_Metric</th>
                    <th className="pb-2 font-normal text-right">Sentiment_Index</th>
                    <th className="pb-2 font-normal text-right">Volatility_Score</th>
                    <th className="pb-2 font-normal text-right">Engagement_Ratio</th>
                  </tr>
                </thead>
                <tbody className="font-mono text-[10px]">
                  {influencerMatrix.map((row, idx) => (
                    <tr key={idx} className="border-b border-outline-variant/10 hover:bg-surface-container-high transition-colors">
                      <td className="py-3 text-primary">{row.handle}</td>
                      <td className="py-3 text-right">{row.reach}</td>
                      <td className={`py-3 text-right ${row.sentiment.startsWith('+') ? 'text-secondary' : 'text-tertiary'}`}>{row.sentiment}</td>
                      <td className="py-3 text-right">{row.volatility.toFixed(2)}</td>
                      <td className="py-3 text-right">{row.engagement.toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="flex justify-between items-center pt-8 pb-4 border-t border-outline-variant/10">
          <div className="flex items-center gap-4">
            <div className="bg-primary/10 border border-primary/30 px-3 py-1">
              <span className="font-headline text-[10px] font-black text-primary uppercase tracking-widest">BDPA COMPLIANT 2024</span>
            </div>
            <span className="font-mono text-[9px] text-on-surface-variant">DATA_SOURCE: BW_NATIONAL_FIREHOSE_V3</span>
          </div>
          <div className="flex items-center gap-6">
            <div className="flex flex-col text-right">
              <span className="font-mono text-[9px] text-on-surface-variant">SYSTEM_LATENCY</span>
              <span className="font-mono text-[10px] text-secondary">142ms</span>
            </div>
            <div className="flex flex-col text-right">
              <span className="font-mono text-[9px] text-on-surface-variant">LAST_BACKUP</span>
              <span className="font-mono text-[10px] text-on-surface">02:00:00 UTC</span>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default Analytics;
