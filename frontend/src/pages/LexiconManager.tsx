import React, { useEffect, useMemo, useState } from 'react';
import { sentimentApi } from '../services/sentimentApi';

interface LexiconStats {
  category_stats: Record<string, { word_count: number; recent_additions: number }>;
  metadata: {
    version: string;
    last_updated: string;
    total_words: number;
  };
  total_words: number;
}

interface LexiconEntry {
  word: string;
  category: string;
  details: {
    meaning: string;
  };
}

interface LexiconForm {
  word: string;
  meaning: string;
  category: string;
  context_sentence: string;
}

const LexiconManager: React.FC = () => {
  const [stats, setStats] = useState<LexiconStats | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<LexiconEntry[]>([]);
  const [entry, setEntry] = useState<LexiconForm>({
    word: '',
    meaning: '',
    category: 'political',
    context_sentence: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadStats();
  }, []);

  const totalCategories = useMemo(
    () => Object.keys(stats?.category_stats ?? {}).length,
    [stats]
  );

  const recentUpdatedAt = useMemo(() => {
    if (!stats?.metadata.last_updated) {
      return 'Unknown';
    }

    return new Date(stats.metadata.last_updated).toLocaleString();
  }, [stats]);

  const categoryCards = useMemo(
    () => Object.entries(stats?.category_stats ?? {}),
    [stats]
  );

  const loadStats = async () => {
    const data = await sentimentApi.getLexiconStats();
    setStats(data);
  };

  const searchLexicon = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }
    const results = await sentimentApi.searchLexicon(searchQuery);
    setSearchResults(results);
  };

  const addWord = async () => {
    if (!entry.word.trim() || !entry.meaning.trim() || !entry.context_sentence.trim()) {
      setMessage('Word, meaning, and context are required.');
      return;
    }

    setLoading(true);
    setMessage('');

    const result = await sentimentApi.addLexiconWord(entry);

    if (result.ok) {
      setMessage(`Added "${entry.word}" to the lexicon.`);
      setEntry({ word: '', meaning: '', category: 'political', context_sentence: '' });
      await loadStats();
    } else {
      setMessage(result.message);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-surface text-on-surface">
      <div className="mx-auto max-w-7xl px-6 py-8 space-y-8">
        <section className="relative overflow-hidden rounded-[28px] border border-outline-variant/15 bg-gradient-to-br from-surface-container-low via-surface-container-low to-surface-container-high p-6 shadow-[0_24px_80px_rgba(0,0,0,0.14)]">
          <div className="absolute inset-0 opacity-40" style={{ background: 'radial-gradient(circle at top right, rgba(59,130,246,0.14), transparent 28%), radial-gradient(circle at bottom left, rgba(16,185,129,0.12), transparent 24%)' }} />
          <div className="relative flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-2xl space-y-3">
              <p className="font-mono text-[10px] uppercase tracking-[0.4em] text-primary">Lexicon Manager</p>
              <h1 className="text-4xl font-headline font-black tracking-tight uppercase sm:text-5xl">Word Bank Control Room</h1>
              <p className="max-w-xl text-sm leading-6 text-on-surface-variant">
                Keep the sentiment engine sharp. Add words and search meanings from one clean workspace.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3 sm:min-w-[360px]">
              <div className="rounded-2xl border border-outline-variant/15 bg-surface-container-low/90 p-4 backdrop-blur">
                <span className="block font-mono text-[10px] uppercase tracking-widest text-on-surface-variant">Total Words</span>
                <strong className="mt-2 block text-3xl font-headline font-black text-primary">{stats?.total_words ?? 0}</strong>
              </div>
              <div className="rounded-2xl border border-outline-variant/15 bg-surface-container-low/90 p-4 backdrop-blur">
                <span className="block font-mono text-[10px] uppercase tracking-widest text-on-surface-variant">Categories</span>
                <strong className="mt-2 block text-3xl font-headline font-black text-secondary">{totalCategories}</strong>
              </div>
              <div className="rounded-2xl border border-outline-variant/15 bg-surface-container-low/90 p-4 backdrop-blur">
                <span className="block font-mono text-[10px] uppercase tracking-widest text-on-surface-variant">Updated</span>
                <strong className="mt-2 block text-sm font-semibold text-on-surface">{recentUpdatedAt}</strong>
              </div>
            </div>
          </div>

          {message && (
            <div className="relative mt-6 rounded-2xl border border-primary/20 bg-primary/10 px-4 py-3 text-sm text-on-surface">
              {message}
            </div>
          )}
        </section>

        <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
          <div className="space-y-6">
            <div className="rounded-[24px] border border-outline-variant/15 bg-surface-container-low p-5 shadow-[0_20px_60px_rgba(0,0,0,0.08)]">
              <div className="flex items-start justify-between gap-4 border-b border-outline-variant/10 pb-4">
                <div>
                  <p className="font-mono text-[10px] uppercase tracking-[0.3em] text-on-surface-variant">Lexicon Search</p>
                  <h2 className="mt-1 text-xl font-headline font-bold uppercase">Find words and meanings</h2>
                </div>
                <span className="rounded-full border border-outline-variant/15 bg-surface-container-high px-3 py-1 font-mono text-[10px] uppercase tracking-widest text-on-surface-variant">
                  {searchResults.length} results
                </span>
              </div>

              <div className="mt-4 flex flex-col gap-3 lg:flex-row">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search words or meanings"
                  className="min-h-12 flex-1 rounded-xl border border-outline-variant/20 bg-surface-container-highest px-4 text-sm outline-none transition-colors placeholder:text-on-surface-variant/40 focus:border-primary"
                />
                <button
                  type="button"
                  onClick={searchLexicon}
                  className="min-h-12 rounded-xl bg-primary px-5 text-sm font-semibold text-on-primary transition-all hover:brightness-110"
                >
                  Search
                </button>
              </div>

              <div className="mt-5 space-y-3">
                {searchResults.length === 0 ? (
                  <div className="rounded-2xl border border-dashed border-outline-variant/20 bg-surface-container-lowest px-4 py-6 text-sm text-on-surface-variant">
                    Search results will appear here.
                  </div>
                ) : (
                  searchResults.map((item, index) => (
                    <article
                      key={`${item.word}-${index}`}
                      className="rounded-2xl border border-outline-variant/10 bg-surface-container-high px-4 py-4"
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <strong className="text-base uppercase tracking-wide text-primary">{item.word}</strong>
                        <span className="rounded-full bg-secondary/10 px-3 py-1 font-mono text-[10px] uppercase tracking-widest text-secondary">
                          {item.category}
                        </span>
                      </div>
                      <p className="mt-2 text-sm leading-6 text-on-surface-variant">{item.details.meaning}</p>
                    </article>
                  ))
                )}
              </div>
            </div>

            <div className="rounded-[24px] border border-outline-variant/15 bg-surface-container-low p-5 shadow-[0_20px_60px_rgba(0,0,0,0.08)]">
              <div className="flex items-start justify-between gap-4 border-b border-outline-variant/10 pb-4">
                <div>
                  <p className="font-mono text-[10px] uppercase tracking-[0.3em] text-on-surface-variant">Add Word</p>
                  <h2 className="mt-1 text-xl font-headline font-bold uppercase">Grow the lexicon</h2>
                </div>
                <span className="rounded-full border border-outline-variant/15 bg-surface-container-high px-3 py-1 font-mono text-[10px] uppercase tracking-widest text-on-surface-variant">
                  Live sync
                </span>
              </div>

              <div className="mt-4 grid gap-3">
                <input
                  type="text"
                  value={entry.word}
                  onChange={(e) => setEntry({ ...entry, word: e.target.value })}
                  placeholder="Word"
                  className="min-h-12 rounded-xl border border-outline-variant/20 bg-surface-container-highest px-4 text-sm outline-none transition-colors placeholder:text-on-surface-variant/40 focus:border-primary"
                />
                <input
                  type="text"
                  value={entry.meaning}
                  onChange={(e) => setEntry({ ...entry, meaning: e.target.value })}
                  placeholder="Meaning"
                  className="min-h-12 rounded-xl border border-outline-variant/20 bg-surface-container-highest px-4 text-sm outline-none transition-colors placeholder:text-on-surface-variant/40 focus:border-primary"
                />
                <select
                  value={entry.category}
                  onChange={(e) => setEntry({ ...entry, category: e.target.value })}
                  className="min-h-12 rounded-xl border border-outline-variant/20 bg-surface-container-highest px-4 text-sm outline-none transition-colors focus:border-primary"
                >
                  <option value="political">Political</option>
                  <option value="positive">Positive</option>
                  <option value="negative">Negative</option>
                  <option value="common_words">Common words</option>
                  <option value="botswana_specific">Botswana specific</option>
                </select>
                <textarea
                  value={entry.context_sentence}
                  onChange={(e) => setEntry({ ...entry, context_sentence: e.target.value })}
                  placeholder="Example sentence"
                  rows={4}
                  className="rounded-xl border border-outline-variant/20 bg-surface-container-highest px-4 py-3 text-sm outline-none transition-colors placeholder:text-on-surface-variant/40 focus:border-primary"
                />
                <button
                  type="button"
                  onClick={addWord}
                  disabled={loading}
                  className="min-h-12 rounded-xl bg-secondary px-5 text-sm font-semibold text-on-secondary transition-all hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {loading ? 'Saving...' : 'Add to lexicon'}
                </button>
              </div>
            </div>
          </div>

          <aside className="space-y-6">
            <div className="rounded-[24px] border border-outline-variant/15 bg-surface-container-low p-5 shadow-[0_20px_60px_rgba(0,0,0,0.08)]">
              <div className="flex items-start justify-between gap-4 border-b border-outline-variant/10 pb-4">
                <div>
                  <p className="font-mono text-[10px] uppercase tracking-[0.3em] text-on-surface-variant">Category Overview</p>
                  <h2 className="mt-1 text-xl font-headline font-bold uppercase">Lexicon distribution</h2>
                </div>
                <span className="rounded-full border border-outline-variant/15 bg-surface-container-high px-3 py-1 font-mono text-[10px] uppercase tracking-widest text-on-surface-variant">
                  {categoryCards.length} groups
                </span>
              </div>

              <div className="mt-4 grid grid-cols-2 gap-3">
                {categoryCards.length === 0 ? (
                  <div className="col-span-2 rounded-2xl border border-dashed border-outline-variant/20 bg-surface-container-lowest px-4 py-6 text-sm text-on-surface-variant">
                    No category data yet.
                  </div>
                ) : (
                  categoryCards.map(([category, info]) => (
                    <div key={category} className="rounded-2xl border border-outline-variant/10 bg-surface-container-high p-4">
                      <span className="block text-[10px] uppercase tracking-[0.3em] text-on-surface-variant">{category}</span>
                      <strong className="mt-2 block text-2xl font-headline font-black text-on-surface">{info.word_count}</strong>
                      <span className="mt-1 block text-xs text-on-surface-variant">{info.recent_additions} recent additions</span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </aside>
        </section>
      </div>
    </div>
  );
};

export default LexiconManager;
