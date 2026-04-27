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

  useEffect(() => {
    const loadEntities = async () => {
      try {
        const entities = await sentimentApi.listPoliticalEntities();
        setApiEntities(entities);
      } finally {
        setLoading(false);
      }
    };

    void loadEntities();
  }, []);

  const tableRows = useMemo(() => {
    if (!apiEntities.length) {
      return FALLBACK_ENTITIES;
    }

    return apiEntities.map((item) => ({
      name: item.entity,
      aliases: item.full_name ? 2 : 1,
      mentions24h: 0,
      netSentiment: 'N/A',
      risk: 'LOW',
    }));
  }, [apiEntities]);

  const trackedCount = apiEntities.length || 42;

  return (
    <div className="ml-64 pt-14 min-h-screen bg-surface">
      <div className="p-6 space-y-6">
        <div className="flex items-end justify-between border-b border-outline-variant/10 pb-4">
          <div>
            <h1 className="text-4xl font-headline font-bold tracking-tight text-on-surface uppercase">Political Entities</h1>
            <p className="text-on-surface-variant font-mono text-xs mt-2">ENTITY_MANAGEMENT_SYSTEM</p>
          </div>
          <button className="bg-primary text-on-primary text-[10px] font-headline uppercase font-bold px-4 py-2 flex items-center gap-2 hover:brightness-110 transition-all">
            <span className="material-symbols-outlined text-sm">add</span>
            Add Entity
          </button>
        </div>

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

        <section className="bg-surface-container-low border border-outline-variant/10 p-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-headline text-xs font-bold uppercase tracking-widest">Entity Registry</h2>
            <div className="flex items-center gap-2 bg-surface-container-lowest border border-outline-variant/20 px-3 py-1.5">
              <span className="material-symbols-outlined text-sm text-on-surface-variant">search</span>
              <input
                type="text"
                placeholder="FILTER_ENTITY..."
                className="bg-transparent border-0 text-xs font-mono text-on-surface placeholder-on-surface-variant/40 focus:ring-0 w-44"
              />
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="text-left font-mono text-[9px] text-on-surface-variant uppercase border-b border-outline-variant/20">
                  <th className="pb-2 font-normal">Entity</th>
                  <th className="pb-2 font-normal text-right">Aliases</th>
                  <th className="pb-2 font-normal text-right">Mentions 24H</th>
                  <th className="pb-2 font-normal text-right">Net Sentiment</th>
                  <th className="pb-2 font-normal text-right">Risk</th>
                </tr>
              </thead>
              <tbody className="font-mono text-[10px]">
                {tableRows.map((entity) => (
                  <tr key={entity.name} className="border-b border-outline-variant/10 hover:bg-surface-container-high transition-colors">
                    <td className="py-3 text-primary">{entity.name}</td>
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
          {loading && <p className="text-on-surface-variant font-mono text-[10px] mt-3">SYNCING_ENTITY_REGISTRY...</p>}
        </section>
      </div>
    </div>
  );
};

export default Entities;
