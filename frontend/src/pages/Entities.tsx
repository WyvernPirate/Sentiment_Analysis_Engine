import React, { useEffect, useMemo, useState } from 'react';
import { sentimentApi } from '../services/sentimentApi';
import { PoliticalEntity } from '../types/sentiment';

const FALLBACK_ENTITIES = [
  { name: 'BDP', aliases: 19, mentions24h: 1282, netSentiment: '+0.55', risk: 'LOW' },
  { name: 'UDC', aliases: 14, mentions24h: 1033, netSentiment: '-0.12', risk: 'MED' },
  { name: 'BCP', aliases: 11, mentions24h: 618, netSentiment: '+0.05', risk: 'LOW' },
  { name: 'BPF', aliases: 9, mentions24h: 407, netSentiment: '-0.27', risk: 'HIGH' },
];

const Entities: React.FC = () => {
  const [apiEntities, setApiEntities] = useState<PoliticalEntity[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newEntity, setNewEntity] = useState({ entity: '', type: 'PARTY', full_name: '', description: '' });

  const loadEntities = async () => {
    setLoading(true);
    try {
      const entities = await sentimentApi.listPoliticalEntities();
      setApiEntities(entities);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadEntities();
  }, []);

  const filteredEntities = useMemo(() => {
    return apiEntities.filter(ent => 
      ent.entity.toLowerCase().includes(searchTerm.toLowerCase()) || 
      ent.full_name?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [apiEntities, searchTerm]);

  const tableRows = useMemo(() => {
    if (!filteredEntities.length && !searchTerm) {
      return FALLBACK_ENTITIES.map(ent => ({ ...ent, id: -1 }));
    }

    return filteredEntities.map((item) => ({
      id: item.id,
      name: item.entity,
      aliases: item.full_name ? 2 : 1,
      mentions24h: 0,
      netSentiment: 'N/A',
      risk: 'LOW',
    }));
  }, [filteredEntities, searchTerm]);

  const handleDelete = async (id: number) => {
    if (id === -1) return;
    if (window.confirm('Are you sure you want to delete this entity?')) {
      const ok = await sentimentApi.deletePoliticalEntity(id);
      if (ok) {
        void loadEntities();
      }
    }
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await sentimentApi.addPoliticalEntity(newEntity);
    if (res.ok) {
      setIsAddModalOpen(false);
      setNewEntity({ entity: '', type: 'PARTY', full_name: '', description: '' });
      void loadEntities();
    } else {
      alert(res.message);
    }
  };

  const trackedCount = apiEntities.length || 42;

  return (
    <div className="ml-64 pt-14 min-h-screen bg-surface">
      <div className="p-6 space-y-6">
        <div className="flex items-end justify-between border-b border-outline-variant/10 pb-4">
          <div>
            <h1 className="text-4xl font-headline font-bold tracking-tight text-on-surface uppercase">Political Entities</h1>
            <p className="text-on-surface-variant font-mono text-xs mt-2">ENTITY_MANAGEMENT_SYSTEM</p>
          </div>
          <button 
            onClick={() => setIsAddModalOpen(true)}
            className="bg-primary text-on-primary text-[10px] font-headline uppercase font-bold px-4 py-2 flex items-center gap-2 hover:brightness-110 transition-all"
          >
            <span className="material-symbols-outlined text-sm">add</span>
            Add Entity
          </button>
        </div>

        {/* Add Entity Modal */}
        {isAddModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
            <div className="bg-surface-container-low border border-outline-variant/20 w-full max-w-md p-6 space-y-4">
              <div className="flex justify-between items-center border-b border-outline-variant/10 pb-3">
                <h2 className="font-headline text-lg font-bold uppercase tracking-tight">Register New Entity</h2>
                <button onClick={() => setIsAddModalOpen(false)} className="text-on-surface-variant hover:text-on-surface">
                  <span className="material-symbols-outlined">close</span>
                </button>
              </div>
              <form onSubmit={handleAdd} className="space-y-4 font-mono text-[11px]">
                <div className="space-y-1">
                  <label className="text-on-surface-variant uppercase">Entity Short Name (ID)</label>
                  <input
                    required
                    type="text"
                    value={newEntity.entity}
                    onChange={e => setNewEntity({ ...newEntity, entity: e.target.value })}
                    className="w-full bg-surface-container-highest border border-outline-variant/20 px-3 py-2 text-on-surface focus:ring-1 focus:ring-primary focus:outline-none"
                    placeholder="e.g. BDP"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-on-surface-variant uppercase">Entity Type</label>
                  <select
                    value={newEntity.type}
                    onChange={e => setNewEntity({ ...newEntity, type: e.target.value })}
                    className="w-full bg-surface-container-highest border border-outline-variant/20 px-3 py-2 text-on-surface focus:ring-1 focus:ring-primary focus:outline-none"
                  >
                    <option value="PARTY">POLITICAL_PARTY</option>
                    <option value="PERSON">POLITICAL_LEADER</option>
                    <option value="LOCATION">DISTRICT_LOCATION</option>
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="text-on-surface-variant uppercase">Full Legal Name</label>
                  <input
                    type="text"
                    value={newEntity.full_name}
                    onChange={e => setNewEntity({ ...newEntity, full_name: e.target.value })}
                    className="w-full bg-surface-container-highest border border-outline-variant/20 px-3 py-2 text-on-surface focus:ring-1 focus:ring-primary focus:outline-none"
                    placeholder="e.g. Botswana Democratic Party"
                  />
                </div>
                <div className="pt-2">
                  <button type="submit" className="w-full bg-primary text-on-primary py-3 font-headline font-bold uppercase tracking-widest hover:brightness-110">
                    Submit Registry
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-surface-container-low border border-outline-variant/10 p-4">
            <p className="font-mono text-[10px] uppercase text-on-surface-variant">Tracked Entities</p>
            <p className="text-3xl font-headline font-bold text-primary mt-2">{trackedCount}</p>
          </div>
          <div className="bg-surface-container-low border border-outline-variant/10 p-4">
            <p className="font-mono text-[10px] uppercase text-on-surface-variant">Total Mentions (24h)</p>
            <p className="text-3xl font-headline font-bold text-secondary mt-2">5,941</p>
          </div>
          <div className="bg-surface-container-low border border-outline-variant/10 p-4">
            <p className="font-mono text-[10px] uppercase text-on-surface-variant">High-Risk Entities</p>
            <p className="text-3xl font-headline font-bold text-tertiary mt-2">3</p>
          </div>
        </section>

        <section className="grid grid-cols-12 gap-6">
          <div className="col-span-12 lg:col-span-8 bg-surface-container-low border border-outline-variant/10 p-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-headline text-xs font-bold uppercase tracking-widest">Entity Registry</h2>
            <div className="flex items-center gap-2 bg-surface-container-lowest border border-outline-variant/20 px-3 py-1.5">
              <span className="material-symbols-outlined text-sm text-on-surface-variant">search</span>
              <input
                type="text"
                placeholder="FILTER_ENTITY..."
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                className="bg-transparent border-0 text-xs font-mono text-on-surface placeholder-on-surface-variant/40 focus:ring-0 w-44"
              />
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="text-left font-mono text-[9px] text-on-surface-variant uppercase border-b border-outline-variant/20">
                  <th className="pb-2 font-normal">Entity</th>
                  <th className="pb-2 font-normal text-right">Action</th>
                  <th className="pb-2 font-normal text-right">Aliases</th>
                  <th className="pb-2 font-normal text-right">Mentions 24H</th>
                  <th className="pb-2 font-normal text-right">Net Sentiment</th>
                  <th className="pb-2 font-normal text-right">Risk</th>
                </tr>
              </thead>
              <tbody className="font-mono text-[10px]">
                {tableRows.map((entity) => (
                  <tr key={entity.name} className="border-b border-outline-variant/10 hover:bg-surface-container-high transition-colors">
                    <td className="py-3 text-primary font-bold">{entity.name}</td>
                    <td className="py-3 text-right">
                      {entity.id !== -1 && (
                        <button 
                          onClick={() => handleDelete(entity.id)}
                          className="text-tertiary hover:text-tertiary/80 transition-colors"
                        >
                          <span className="material-symbols-outlined text-sm">delete</span>
                        </button>
                      )}
                    </td>
                    <td className="py-3 text-right">{entity.aliases}</td>
                    <td className="py-3 text-right">{entity.mentions24h || '--'}</td>
                    <td
                      className={`py-3 text-right ${
                        entity.netSentiment === 'N/A'
                          ? 'text-on-surface-variant'
                          : entity.netSentiment.startsWith('+')
                            ? 'text-secondary'
                            : 'text-tertiary'
                      }`}
                    >
                      {entity.netSentiment}
                    </td>
                    <td
                      className={`py-3 text-right ${
                        entity.risk === 'HIGH' ? 'text-tertiary' : entity.risk === 'MED' ? 'text-primary' : 'text-secondary'
                      }`}
                    >
                      {entity.risk}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {loading && <p className="text-on-surface-variant font-mono text-[10px] mt-3 animate-pulse">SYNCING_ENTITY_REGISTRY...</p>}
          </div>

          <div className="col-span-12 lg:col-span-4 bg-surface-container-low border border-outline-variant/10 p-4">
            <h2 className="font-headline text-xs font-bold uppercase tracking-widest mb-4">Ingestion Protocols</h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-surface-container-high border-l-2 border-primary">
                <div>
                  <p className="text-xs font-bold uppercase tracking-tighter">TWITTER_API_V2</p>
                  <p className="text-[10px] text-on-surface-variant font-mono">Status: Stream Active</p>
                </div>
                <div className="w-9 h-5 bg-secondary flex items-center px-0.5">
                  <div className="w-3 h-3 bg-on-secondary"></div>
                </div>
              </div>
              <div className="flex items-center justify-between p-3 bg-surface-container-high border-l-2 border-outline-variant/40">
                <div>
                  <p className="text-xs font-bold uppercase tracking-tighter">FACEBOOK_SELENIUM</p>
                  <p className="text-[10px] text-on-surface-variant font-mono">Status: Headless Sleep</p>
                </div>
                <div className="w-9 h-5 bg-surface-container-highest flex items-center justify-end px-0.5">
                  <div className="w-3 h-3 bg-outline"></div>
                </div>
              </div>
              <div className="flex items-center justify-between p-3 bg-surface-container-high border-l-2 border-primary">
                <div>
                  <p className="text-xs font-bold uppercase tracking-tighter">LOCAL_NEWS_RSS</p>
                  <p className="text-[10px] text-on-surface-variant font-mono">Status: 24 Sinks Active</p>
                </div>
                <div className="w-9 h-5 bg-secondary flex items-center px-0.5">
                  <div className="w-3 h-3 bg-on-secondary"></div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-surface-container-low border border-outline-variant/15 p-4">
            <p className="font-headline text-[10px] uppercase tracking-widest text-on-surface-variant mb-2">Ingestion Latency</p>
            <p className="font-mono text-3xl font-bold text-secondary">142<span className="text-xs ml-1">ms</span></p>
          </div>
          <div className="bg-surface-container-low border border-outline-variant/15 p-4">
            <p className="font-headline text-[10px] uppercase tracking-widest text-on-surface-variant mb-2">Payload Error Rate</p>
            <p className="font-mono text-3xl font-bold text-on-surface">0.04<span className="text-xs ml-1">%</span></p>
          </div>
          <div className="bg-surface-container-low border border-outline-variant/15 p-4">
            <p className="font-headline text-[10px] uppercase tracking-widest text-on-surface-variant mb-2">Compute Utilization</p>
            <p className="font-mono text-3xl font-bold text-primary">68.2<span className="text-xs ml-1">%</span></p>
          </div>
        </section>

        <section className="bg-surface-container-low border border-outline-variant/15 p-4">
          <h2 className="font-headline text-xs font-bold uppercase tracking-widest mb-3">Live Signal Feed</h2>
          <div className="space-y-2 font-mono text-[11px]">
            <p className="text-on-surface-variant hover:text-on-surface transition-colors">[14:22:01] [INGEST_OK] Source: @Twitter_BW - Entity: UDC - Sentiment: POSITIVE - Mentions: 1.2k</p>
            <p className="text-on-surface-variant hover:text-on-surface transition-colors">[14:21:58] [ANOMALY_DET] Source: Facebook_BW - Keyword match: Election Volatility - Severity: MEDIUM</p>
            <p className="text-on-surface-variant hover:text-on-surface transition-colors">[14:21:45] [INGEST_OK] Source: DailyNews_BW - Entity: BDP - Sentiment: NEUTRAL - Mentions: 450</p>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Entities;
