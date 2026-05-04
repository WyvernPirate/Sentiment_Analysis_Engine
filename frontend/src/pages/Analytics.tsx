import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { sentimentApi } from '../services/sentimentApi';
import {
  SocialCollection,
  BatchAnalysisResult,
  AnalysisJob,
  AnalyzedRow,
} from '../types/sentiment';
import WordCloud from '../components/Analysis/WordCloud';

type SentimentFilter = 'all' | 'positive' | 'neutral' | 'negative';

const SENTIMENT_COLORS: Record<string, string> = {
  positive: 'text-secondary',
  neutral: 'text-on-surface-variant',
  negative: 'text-tertiary',
};
const SENTIMENT_BG: Record<string, string> = {
  positive: 'bg-secondary/10 text-secondary',
  neutral: 'bg-on-surface-variant/10 text-on-surface-variant',
  negative: 'bg-tertiary/10 text-tertiary',
};

const Analytics: React.FC = () => {
  const [collections, setCollections] = useState<SocialCollection[]>([]);
  const [selectedCollectionId, setSelectedCollectionId] = useState('');
  const [analysisResult, setAnalysisResult] = useState<BatchAnalysisResult | null>(null);
  const [pastJobs, setPastJobs] = useState<AnalysisJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState('');
  const [sentimentFilter, setSentimentFilter] = useState<SentimentFilter>('all');
  const [expandedRow, setExpandedRow] = useState<number | null>(null);
  const [sortBy, setSortBy] = useState<'index' | 'confidence'>('index');

  const loadData = useCallback(async () => {
    const [colls, jobs] = await Promise.all([
      sentimentApi.listSocialCollections(50),
      sentimentApi.listAnalysisJobs(20),
    ]);
    setCollections(colls);
    setPastJobs(jobs);
    if (!selectedCollectionId && colls.length > 0) {
      setSelectedCollectionId(colls[0].collection_id);
    }
  }, [selectedCollectionId]);

  useEffect(() => {
    void loadData().finally(() => setLoading(false));
  }, [loadData]);

  const handleRunAnalysis = async () => {
    if (!selectedCollectionId) return;
    setAnalyzing(true);
    setError('');
    setAnalysisResult(null);
    try {
      const result = await sentimentApi.runBatchAnalysis(selectedCollectionId);
      if (result.error) {
        setError(result.error);
      } else {
        setAnalysisResult(result);
        await loadData();
      }
    } finally {
      setAnalyzing(false);
    }
  };

  const handleLoadJob = async (jobId: string) => {
    setAnalyzing(true);
    setError('');
    try {
      const result = await sentimentApi.getAnalysisJob(jobId);
      if (result) {
        setAnalysisResult(result);
        setSelectedCollectionId(result.collection_id);
      }
    } finally {
      setAnalyzing(false);
    }
  };

  const agg = analysisResult?.aggregate;
  const dist = agg?.sentiment_distribution;
  const total = (dist?.positive ?? 0) + (dist?.neutral ?? 0) + (dist?.negative ?? 0);

  const pctPos = total ? Math.round((dist!.positive / total) * 100) : 0;
  const pctNeu = total ? Math.round((dist!.neutral / total) * 100) : 0;
  const pctNeg = total ? 100 - pctPos - pctNeu : 0;

  // SVG donut math
  const circumference = 2 * Math.PI * 40;
  const posArc = (pctPos / 100) * circumference;
  const neuArc = (pctNeu / 100) * circumference;
  const negArc = (pctNeg / 100) * circumference;

  const filteredRows = useMemo(() => {
    if (!analysisResult) return [];
    let rows = [...analysisResult.rows];
    if (sentimentFilter !== 'all') {
      rows = rows.filter((r) => r.sentiment === sentimentFilter);
    }
    if (sortBy === 'confidence') {
      rows.sort((a, b) => b.confidence - a.confidence);
    }
    return rows;
  }, [analysisResult, sentimentFilter, sortBy]);

  return (
    <div className="ml-64 pt-14 min-h-screen bg-surface">
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex justify-between items-end pb-4 border-b border-outline-variant/10">
          <div>
            <h1 className="text-4xl font-headline font-bold tracking-tight text-on-surface uppercase">Analytics</h1>
            <p className="text-on-surface-variant font-mono text-xs mt-1">
              BATCH_SENTIMENT_ANALYSIS {analysisResult ? `// JOB: ${analysisResult.job_id}` : ''}
            </p>
          </div>
        </div>

        {/* Controls */}
        <section className="bg-surface-container-low border border-outline-variant/10 p-4 space-y-3">
          <h2 className="font-headline text-xs font-bold uppercase tracking-widest">Analysis Control</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <select
              value={selectedCollectionId}
              onChange={(e) => setSelectedCollectionId(e.target.value)}
              className="col-span-2 bg-surface-container-lowest border border-outline-variant/20 text-xs font-mono px-3 py-2 focus:ring-0"
            >
              <option value="">Select collection...</option>
              {collections.map((c) => (
                <option key={c.collection_id} value={c.collection_id}>
                  {c.collection_id} ({c.count} records)
                </option>
              ))}
            </select>
            <button
              type="button"
              onClick={() => void handleRunAnalysis()}
              disabled={analyzing || !selectedCollectionId}
              className="bg-primary text-on-primary text-[10px] font-headline uppercase font-bold px-4 py-2 disabled:opacity-60 flex items-center justify-center gap-2"
            >
              {analyzing && <span className="material-symbols-outlined text-sm animate-spin">progress_activity</span>}
              {analyzing ? 'Analyzing...' : 'Run Analysis'}
            </button>
            <button
              type="button"
              onClick={() => void loadData()}
              className="bg-surface-container-high text-on-surface text-[10px] font-headline uppercase font-bold px-4 py-2 border-b-2 border-primary"
            >
              Refresh
            </button>
          </div>
          {error && <p className="font-mono text-[10px] text-tertiary">{error}</p>}
          {loading && <p className="font-mono text-[10px] text-on-surface-variant">LOADING_COLLECTIONS...</p>}
        </section>

        {/* Results — only show after analysis */}
        {analysisResult && agg && dist && (
          <>
            {/* Stat Cards */}
            <section className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <div className="bg-surface-container-low border border-outline-variant/10 p-4">
                <p className="font-mono text-[10px] uppercase text-on-surface-variant">Total Rows</p>
                <p className="text-3xl font-headline font-bold text-primary mt-2">{agg.total_rows}</p>
              </div>
              <div className="bg-surface-container-low border border-outline-variant/10 p-4">
                <p className="font-mono text-[10px] uppercase text-on-surface-variant">Positive</p>
                <p className="text-3xl font-headline font-bold text-secondary mt-2">{dist.positive} <span className="text-xs font-mono font-normal">{pctPos}%</span></p>
              </div>
              <div className="bg-surface-container-low border border-outline-variant/10 p-4">
                <p className="font-mono text-[10px] uppercase text-on-surface-variant">Neutral</p>
                <p className="text-3xl font-headline font-bold text-on-surface-variant mt-2">{dist.neutral} <span className="text-xs font-mono font-normal">{pctNeu}%</span></p>
              </div>
              <div className="bg-surface-container-low border border-outline-variant/10 p-4">
                <p className="font-mono text-[10px] uppercase text-on-surface-variant">Negative</p>
                <p className="text-3xl font-headline font-bold text-tertiary mt-2">{dist.negative} <span className="text-xs font-mono font-normal">{pctNeg}%</span></p>
              </div>
              <div className="bg-surface-container-low border border-outline-variant/10 p-4">
                <p className="font-mono text-[10px] uppercase text-on-surface-variant">Avg Confidence</p>
                <p className="text-3xl font-headline font-bold text-primary mt-2">{(agg.avg_confidence * 100).toFixed(1)}%</p>
              </div>
            </section>

            {/* Chart + Sidebar */}
            <div className="grid grid-cols-12 gap-6">
              {/* Donut Chart */}
              <div className="col-span-12 lg:col-span-5 bg-surface-container-low border border-outline-variant/10 p-6">
                <h2 className="font-headline text-xs font-bold uppercase tracking-widest flex items-center gap-2 mb-6">
                  <span className="w-1.5 h-1.5 bg-primary"></span> SENTIMENT_DISTRIBUTION
                </h2>
                <div className="flex items-center justify-center gap-10">
                  <div className="relative w-48 h-48">
                    <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                      <circle cx="50" cy="50" r="40" fill="transparent" stroke="#86bdf7" strokeWidth="18"
                        strokeDasharray={`${posArc} ${circumference - posArc}`} strokeDashoffset="0"
                        className="opacity-80 hover:opacity-100 transition-opacity" />
                      <circle cx="50" cy="50" r="40" fill="transparent" stroke="#adaaaa" strokeWidth="18"
                        strokeDasharray={`${neuArc} ${circumference - neuArc}`} strokeDashoffset={`${-posArc}`}
                        className="opacity-80 hover:opacity-100 transition-opacity" />
                      <circle cx="50" cy="50" r="40" fill="transparent" stroke="#ff716c" strokeWidth="18"
                        strokeDasharray={`${negArc} ${circumference - negArc}`} strokeDashoffset={`${-(posArc + neuArc)}`}
                        className="opacity-80 hover:opacity-100 transition-opacity" />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="font-headline text-2xl font-black text-on-surface">{total}</span>
                      <span className="font-mono text-[8px] text-on-surface-variant uppercase">Analyzed</span>
                    </div>
                  </div>
                  <div className="space-y-4">
                    {[
                      { label: 'Positive', pct: pctPos, color: 'bg-[#86bdf7]', text: 'text-secondary' },
                      { label: 'Neutral', pct: pctNeu, color: 'bg-[#adaaaa]', text: 'text-on-surface-variant' },
                      { label: 'Negative', pct: pctNeg, color: 'bg-[#ff716c]', text: 'text-tertiary' },
                    ].map((item) => (
                      <div key={item.label} className="flex items-center gap-3">
                        <div className={`w-3 h-3 ${item.color}`}></div>
                        <span className="font-mono text-xs uppercase text-on-surface-variant w-16">{item.label}</span>
                        <span className={`font-headline font-bold ${item.text}`}>{item.pct}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Top Entities */}
              <div className="col-span-12 lg:col-span-4 bg-surface-container-low border border-outline-variant/10 p-4">
                <h2 className="font-headline text-xs font-bold uppercase tracking-widest flex items-center gap-2 mb-4">
                  <span className="w-1.5 h-1.5 bg-primary"></span> TOP_ENTITIES
                </h2>
                {agg.top_entities.length === 0 && <p className="font-mono text-[10px] text-on-surface-variant">No entities detected</p>}
                <div className="space-y-2">
                  {agg.top_entities.slice(0, 8).map((ent) => (
                    <div key={ent.entity} className="flex items-center justify-between">
                      <span className="font-mono text-[10px] text-primary">{ent.entity}</span>
                      <div className="flex items-center gap-2">
                        <div className="w-24 h-1 bg-surface-container-highest">
                          <div className="h-1 bg-primary" style={{ width: `${Math.min(100, (ent.count / (agg.top_entities[0]?.count || 1)) * 100)}%` }}></div>
                        </div>
                        <span className="font-mono text-[10px] text-on-surface-variant w-6 text-right">{ent.count}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Trigger Words (Word Cloud) */}
              <div className="col-span-12 lg:col-span-3 bg-surface-container-low border border-outline-variant/10 p-4">
                <h2 className="font-headline text-xs font-bold uppercase tracking-widest flex items-center gap-2 mb-4">
                  <span className="w-1.5 h-1.5 bg-primary"></span> TRIGGER_WORDS
                </h2>
                <WordCloud words={agg.top_trigger_words} maxWords={15} />
              </div>
            </div>

            {/* Per-Row Results Table */}
            <section className="bg-surface-container-low border border-outline-variant/10 p-4">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-headline text-xs font-bold uppercase tracking-widest flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-primary"></span> PER_ROW_RESULTS
                  <span className="font-mono text-[9px] text-on-surface-variant ml-2">({filteredRows.length} rows)</span>
                </h2>
                <div className="flex gap-2">
                  {(['all', 'positive', 'neutral', 'negative'] as SentimentFilter[]).map((f) => (
                    <button key={f} type="button" onClick={() => setSentimentFilter(f)}
                      className={`font-mono text-[9px] uppercase px-2 py-1 transition-colors ${sentimentFilter === f ? 'bg-primary/20 text-primary' : 'text-on-surface-variant hover:text-on-surface'}`}>
                      {f}
                    </button>
                  ))}
                  <button type="button" onClick={() => setSortBy(sortBy === 'index' ? 'confidence' : 'index')}
                    className="font-mono text-[9px] text-on-surface-variant hover:text-primary px-2 py-1 border-l border-outline-variant/20">
                    SORT: {sortBy === 'index' ? 'ORDER' : 'CONFIDENCE'}
                  </button>
                </div>
              </div>
              <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
                <table className="w-full border-collapse">
                  <thead className="sticky top-0 bg-surface-container-low">
                    <tr className="text-left font-mono text-[9px] text-on-surface-variant uppercase border-b border-outline-variant/20">
                      <th className="pb-2 font-normal w-8">#</th>
                      <th className="pb-2 font-normal">Text</th>
                      <th className="pb-2 font-normal w-16">Author</th>
                      <th className="pb-2 font-normal text-center w-20">Sentiment</th>
                      <th className="pb-2 font-normal text-right w-20">Confidence</th>
                      <th className="pb-2 font-normal text-right w-20">Entities</th>
                    </tr>
                  </thead>
                  <tbody className="font-mono text-[10px]">
                    {filteredRows.map((row) => (
                      <React.Fragment key={row.row_index}>
                        <tr
                          className="border-b border-outline-variant/10 hover:bg-surface-container-high transition-colors cursor-pointer"
                          onClick={() => setExpandedRow(expandedRow === row.row_index ? null : row.row_index)}
                        >
                          <td className="py-2 text-on-surface-variant">{row.row_index}</td>
                          <td className="py-2 max-w-[400px] truncate">{row.text}</td>
                          <td className="py-2 text-primary">{row.meta.author || '--'}</td>
                          <td className="py-2 text-center">
                            <span className={`px-1.5 py-0.5 text-[9px] uppercase ${SENTIMENT_BG[row.sentiment] || ''}`}>
                              {row.sentiment}
                            </span>
                          </td>
                          <td className={`py-2 text-right ${SENTIMENT_COLORS[row.sentiment] || ''}`}>
                            {(row.confidence * 100).toFixed(1)}%
                          </td>
                          <td className="py-2 text-right text-on-surface-variant">{row.entities.length || '--'}</td>
                        </tr>
                        {expandedRow === row.row_index && (
                          <tr className="bg-surface-container-high/50">
                            <td colSpan={6} className="p-4 space-y-2">
                              <p className="text-xs text-on-surface whitespace-pre-wrap">{row.text}</p>
                              <div className="flex gap-4 flex-wrap">
                                {row.trigger_words.positive.length > 0 && (
                                  <div><span className="text-[9px] text-on-surface-variant">POS_WORDS: </span>
                                    {row.trigger_words.positive.map((w) => <span key={w} className="text-secondary text-[9px] mr-1">{w}</span>)}</div>
                                )}
                                {row.trigger_words.negative.length > 0 && (
                                  <div><span className="text-[9px] text-on-surface-variant">NEG_WORDS: </span>
                                    {row.trigger_words.negative.map((w) => <span key={w} className="text-tertiary text-[9px] mr-1">{w}</span>)}</div>
                                )}
                                {row.entities.length > 0 && (
                                  <div><span className="text-[9px] text-on-surface-variant">ENTITIES: </span>
                                    {row.entities.map((e) => <span key={e.entity} className="text-primary text-[9px] mr-1">{e.entity}</span>)}</div>
                                )}
                                {row.political_words.length > 0 && (
                                  <div><span className="text-[9px] text-on-surface-variant">POLITICAL: </span>
                                    {row.political_words.map((w) => <span key={w.term} className="text-primary text-[9px] mr-1" title={w.meaning}>{w.term}</span>)}</div>
                                )}
                              </div>
                              <p className="text-[9px] text-on-surface-variant">MODEL: {row.model_used} | DATE: {row.meta.date || 'N/A'}</p>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </>
        )}

        {/* Past Jobs */}
        <section className="bg-surface-container-low border border-outline-variant/10 p-4">
          <h2 className="font-headline text-xs font-bold uppercase tracking-widest flex items-center gap-2 mb-4">
            <span className="w-1.5 h-1.5 bg-primary"></span> ANALYSIS_HISTORY
          </h2>
          {pastJobs.length === 0 && <p className="font-mono text-[10px] text-on-surface-variant">No past analyses. Select a collection and run analysis.</p>}
          <div className="space-y-1">
            {pastJobs.map((job) => (
              <div key={job.job_id}
                className="flex items-center justify-between p-2 hover:bg-surface-container-high transition-colors cursor-pointer border-b border-outline-variant/10"
                onClick={() => void handleLoadJob(job.job_id)}
              >
                <div className="flex items-center gap-4">
                  <span className="font-mono text-[10px] text-primary">{job.job_id}</span>
                  <span className="font-mono text-[9px] text-on-surface-variant">{job.row_count} rows</span>
                </div>
                <div className="flex items-center gap-3 font-mono text-[9px]">
                  <span className="text-secondary">POS:{job.sentiment_summary?.positive || 0}</span>
                  <span className="text-on-surface-variant">NEU:{job.sentiment_summary?.neutral || 0}</span>
                  <span className="text-tertiary">NEG:{job.sentiment_summary?.negative || 0}</span>
                  <span className="text-on-surface-variant">{new Date(job.analyzed_at).toLocaleString()}</span>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* No results placeholder */}
        {!analysisResult && !loading && (
          <section className="bg-surface-container-low border border-outline-variant/10 p-12 flex flex-col items-center justify-center">
            <span className="material-symbols-outlined text-4xl text-on-surface-variant/30 mb-4">monitoring</span>
            <p className="font-headline text-xs font-bold uppercase tracking-widest text-on-surface-variant mb-2">No Analysis Results</p>
            <p className="font-mono text-[10px] text-on-surface-variant text-center max-w-md">
              Select a collection from the dropdown above and click "Run Analysis" to process it through the sentiment pipeline.
              Upload CSV data via the Scraping Sources page first.
            </p>
          </section>
        )}
      </div>
    </div>
  );
};

export default Analytics;
