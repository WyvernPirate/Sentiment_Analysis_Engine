import React, { useMemo, useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { sentimentApi } from '../services/sentimentApi';
import { PoliticalEntity, EntityStatsResponse, SocialCollection } from '../types/sentiment';

const escapeRegExp = (value: string) => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

const Entities: React.FC = () => {
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState('');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newEntity, setNewEntity] = useState({ entity: '', type: 'PARTY', full_name: '', description: '' });

  const entitiesQuery = useQuery<PoliticalEntity[]>({
    queryKey: ['political-entities'],
    queryFn: () => sentimentApi.listPoliticalEntities(),
  });
  const statsQuery = useQuery<EntityStatsResponse | null>({
    queryKey: ['entity-stats'],
    queryFn: () => sentimentApi.getEntityStats(),
  });
  const collectionsQuery = useQuery<SocialCollection[]>({
    queryKey: ['social-collections', 10],
    queryFn: () => sentimentApi.listSocialCollections(10),
    refetchInterval: 5000,
  });

  // Cast rather than rely on inference: @tanstack/react-query v5's generics
  // don't fully resolve under this project's pinned TypeScript 4.9 (a known,
  // separately-tracked upgrade candidate), so `.data` otherwise widens to `any`.
  const apiEntities = useMemo(() => (entitiesQuery.data ?? []) as PoliticalEntity[], [entitiesQuery.data]);
  const entityStats = (statsQuery.data ?? null) as EntityStatsResponse | null;
  const loading = entitiesQuery.isFetching || statsQuery.isFetching;

  const trackedEntities = useMemo(
    () => apiEntities.map((entity) => entity.entity.trim()).filter(Boolean),
    [apiEntities]
  );

  const liveFeed = useMemo(() => {
    const collections = (collectionsQuery.data ?? []) as SocialCollection[];

    return collections.slice(0, 12).map((collection) => {
      const meta = (collection.run_meta || {}) as Record<string, unknown>;
      const preview = Array.isArray(meta.records_preview) ? (meta.records_preview as Array<Record<string, unknown>>) : [];
      const textPool = [collection.query || '']
        .concat(preview.map((record) => String(record.text_raw || record.text || record.content || '')))
        .join(' ')
        .toLowerCase();

      const entityCounts = new Map<string, number>();
      trackedEntities.forEach((entity) => {
        const regex = new RegExp(`\\b${escapeRegExp(entity)}\\b`, 'i');
        const matchesInQuery = regex.test(collection.query || '');
        const matchesInPreview = preview.some((record) => {
          const recordText = String(record.text_raw || record.text || record.content || '');
          return regex.test(recordText);
        });

        if (matchesInQuery || matchesInPreview || textPool.includes(entity.toLowerCase())) {
          const previewMentions = preview.reduce((count, record) => {
            const recordText = String(record.text_raw || record.text || record.content || '');
            return count + (regex.test(recordText) ? 1 : 0);
          }, 0);
          entityCounts.set(entity, Math.max(1, previewMentions));
        }
      });

      const snippets = preview
        .map((record) => String(record.text_raw || record.text || record.content || '').trim())
        .filter(Boolean)
        .slice(0, 2)
        .map((snippet) => (snippet.length > 150 ? `${snippet.slice(0, 150)}...` : snippet));

      return {
        time: collection.collected_at_utc || '',
        provider: collection.source || 'x',
        query: collection.query || '',
        count: collection.count || 0,
        entities: Array.from(entityCounts.entries()).map(([name, count]) => ({ name, count })),
        snippets,
      };
    });
  }, [collectionsQuery.data, trackedEntities]);

  const filteredEntities = useMemo(() => {
    return apiEntities.filter(ent =>
      ent.entity.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ent.full_name?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [apiEntities, searchTerm]);

  const tableRows = useMemo(() => {
    return filteredEntities.map((item) => {
      const stats = entityStats?.entities[item.entity];
      return {
        id: item.id,
        name: item.entity,
        mentions: stats?.mentions ?? 0,
        netSentiment: stats ? stats.net_sentiment : null,
        risk: stats?.risk ?? 'LOW',
      };
    });
  }, [filteredEntities, entityStats]);

  const invalidateEntities = () => {
    void queryClient.invalidateQueries({ queryKey: ['political-entities'] });
    void queryClient.invalidateQueries({ queryKey: ['entity-stats'] });
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this entity?')) {
      const ok = await sentimentApi.deletePoliticalEntity(id);
      if (ok) {
        invalidateEntities();
      }
    }
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await sentimentApi.addPoliticalEntity(newEntity);
    if (res.ok) {
      setIsAddModalOpen(false);
      setNewEntity({ entity: '', type: 'PARTY', full_name: '', description: '' });
      invalidateEntities();
    } else {
      alert(res.message);
    }
  };

  const trackedCount = apiEntities.length;

  return (
    <>
      <div className="p-6 space-y-6">
        <div className="flex items-end justify-between border-b border-outline-variant/10 pb-4">
          <div>
            <h1 className="text-4xl font-headline font-bold tracking-tight text-on-surface uppercase">Political Entities</h1>
            <p className="text-on-surface-variant font-mono text-xs mt-2">ENTITY_MANAGEMENT_SYSTEM</p>
          </div>
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="bg-primary text-on-primary text-[10px] font-headline uppercase font-bold px-4 py-2 flex items-center gap-2 hover:brightness-110 transition-all focus-visible:outline focus-visible:outline-2 focus-visible:outline-on-primary"
          >
            <span className="material-symbols-outlined text-sm" aria-hidden="true">add</span>
            Add Entity
          </button>
        </div>

        {/* Add Entity Modal */}
        {isAddModalOpen && (
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="add-entity-heading"
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
          >
            <div className="bg-surface-container-low border border-outline-variant/20 w-full max-w-md p-6 space-y-4">
              <div className="flex justify-between items-center border-b border-outline-variant/10 pb-3">
                <h2 id="add-entity-heading" className="font-headline text-lg font-bold uppercase tracking-tight">Register New Entity</h2>
                <button
                  onClick={() => setIsAddModalOpen(false)}
                  aria-label="Close dialog"
                  className="text-on-surface-variant hover:text-on-surface focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary"
                >
                  <span className="material-symbols-outlined" aria-hidden="true">close</span>
                </button>
              </div>
              <form onSubmit={handleAdd} className="space-y-4 font-mono text-[11px]">
                <div className="space-y-1">
                  <label htmlFor="entity-short-name" className="text-on-surface-variant uppercase">Entity Short Name (ID)</label>
                  <input
                    id="entity-short-name"
                    required
                    type="text"
                    value={newEntity.entity}
                    onChange={e => setNewEntity({ ...newEntity, entity: e.target.value })}
                    className="w-full bg-surface-container-highest border border-outline-variant/20 px-3 py-2 text-on-surface focus:ring-1 focus:ring-primary focus:outline-none"
                    placeholder="e.g. BDP"
                  />
                </div>
                <div className="space-y-1">
                  <label htmlFor="entity-type" className="text-on-surface-variant uppercase">Entity Type</label>
                  <select
                    id="entity-type"
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
                  <label htmlFor="entity-full-name" className="text-on-surface-variant uppercase">Full Legal Name</label>
                  <input
                    id="entity-full-name"
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
            <p className="font-mono text-[10px] uppercase text-on-surface-variant">Total Mentions</p>
            <p className="text-3xl font-headline font-bold text-secondary mt-2">{entityStats?.total_mentions ?? 0}</p>
          </div>
          <div className="bg-surface-container-low border border-outline-variant/10 p-4">
            <p className="font-mono text-[10px] uppercase text-on-surface-variant">High-Risk Entities</p>
            <p className="text-3xl font-headline font-bold text-tertiary mt-2">{entityStats?.high_risk_count ?? 0}</p>
          </div>
        </section>

        <section className="grid grid-cols-12 gap-6">
          <div className="col-span-12 lg:col-span-8 bg-surface-container-low border border-outline-variant/10 p-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-headline text-xs font-bold uppercase tracking-widest">Entity Registry</h2>
            <div className="flex items-center gap-2 bg-surface-container-lowest border border-outline-variant/20 px-3 py-1.5">
              <span className="material-symbols-outlined text-sm text-on-surface-variant" aria-hidden="true">search</span>
              <label htmlFor="entity-filter" className="sr-only">Filter entities</label>
              <input
                id="entity-filter"
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
                  <th className="pb-2 font-normal text-right">Mentions</th>
                  <th className="pb-2 font-normal text-right">Net Sentiment</th>
                  <th className="pb-2 font-normal text-right">Risk</th>
                </tr>
              </thead>
              <tbody className="font-mono text-[10px]">
                {tableRows.map((entity) => (
                  <tr key={entity.name} className="border-b border-outline-variant/10 hover:bg-surface-container-high transition-colors">
                    <td className="py-3 text-primary font-bold">{entity.name}</td>
                    <td className="py-3 text-right">
                      <button
                        onClick={() => handleDelete(entity.id)}
                        aria-label={`Delete ${entity.name}`}
                        className="text-tertiary hover:text-tertiary/80 transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-tertiary"
                      >
                        <span className="material-symbols-outlined text-sm" aria-hidden="true">delete</span>
                      </button>
                    </td>
                    <td className="py-3 text-right">{entity.mentions || '--'}</td>
                    <td
                      className={`py-3 text-right ${
                        entity.netSentiment === null
                          ? 'text-on-surface-variant'
                          : entity.netSentiment > 0
                            ? 'text-secondary'
                            : entity.netSentiment < 0
                              ? 'text-tertiary'
                              : 'text-on-surface-variant'
                      }`}
                    >
                      {entity.netSentiment === null
                        ? 'N/A'
                        : `${entity.netSentiment > 0 ? '+' : ''}${entity.netSentiment.toFixed(2)}`}
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

          {/* Ingestion Protocols removed - simplified layout */}
        </section>

        <section className="bg-surface-container-low border border-outline-variant/15 p-4">
          <h2 className="font-headline text-xs font-bold uppercase tracking-widest mb-3">Live Signal Feed</h2>
          <div className="space-y-3 font-mono text-[11px]">
            {liveFeed.length === 0 && <p className="text-on-surface-variant">No live signals yet.</p>}
            {liveFeed.map((entry, idx) => (
              <div key={`${entry.time}-${idx}`} className="border border-outline-variant/10 bg-surface-container-high/60 p-3 space-y-2">
                <div className="flex flex-wrap items-center gap-2 text-[10px] uppercase tracking-widest text-on-surface-variant">
                  <span>{entry.time ? entry.time.replace('T', ' ').split('.')[0] : '--'}</span>
                  <span className="text-primary">{entry.provider}</span>
                  <span>count {entry.count}</span>
                </div>
                <p className="text-on-surface text-[11px] leading-5">
                  Query: {entry.query || 'N/A'}
                </p>
                <div className="flex flex-wrap gap-2">
                  {entry.entities.length > 0 ? (
                    entry.entities.map((entity) => (
                      <span key={entity.name} className="px-2 py-1 bg-primary/15 text-primary border border-primary/20 text-[10px] uppercase tracking-widest">
                        {entity.name} x{entity.count}
                      </span>
                    ))
                  ) : (
                    <span className="text-on-surface-variant text-[10px] uppercase tracking-widest">No entity match yet</span>
                  )}
                </div>
                {entry.snippets.length > 0 && (
                  <div className="space-y-1">
                    {entry.snippets.map((snippet, snippetIndex) => (
                      <p key={`${entry.time}-${snippetIndex}`} className="text-on-surface-variant text-[10px] leading-5">
                        {snippet}
                      </p>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      </div>
    </>
  );
};

export default Entities;
