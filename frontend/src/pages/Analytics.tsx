import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { PieChart, Pie, Cell } from 'recharts';
import { sentimentApi } from '../services/sentimentApi';
import {
  SocialCollection,
  BatchAnalysisResult,
  AnalysisJob,
  AnalyzedRow,
} from '../types/sentiment';
import WordCloud from '../components/Analysis/WordCloud';
import { useAnalytics } from '../context/AnalyticsContext';

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

const sanitizeFileName = (value: string) => value.replace(/[^a-z0-9-_]+/gi, '_').replace(/^_+|_+$/g, '') || 'analysis';

const escapeCsvCell = (value: unknown) => {
  const text = value === null || value === undefined ? '' : String(value);
  if (/[",\n\r;]/.test(text)) {
    return `"${text.replace(/"/g, '""')}"`;
  }
  return text;
};

const toCsvRow = (row: AnalyzedRow) => {
  const entities = row.entities.map((entity) => `${entity.entity}:${entity.type}`).join('; ');
  const politicalWords = row.political_words.map((word) => `${word.term}:${word.meaning}`).join('; ');

  return [
    row.row_index,
    row.meta.date || '',
    row.meta.author || '',
    row.meta.source || '',
    row.meta.url || '',
    row.sentiment,
    row.confidence,
    row.model_used,
    row.trigger_words.positive.join('; '),
    row.trigger_words.negative.join('; '),
    entities,
    politicalWords,
    row.text,
  ].map(escapeCsvCell).join(',');
};

const downloadTextFile = (filename: string, content: string, mimeType: string) => {
  const blob = new Blob([content], { type: mimeType });
  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  window.URL.revokeObjectURL(url);
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
  const [searchQuery, setSearchQuery] = useState('');
  const [triggerWordFilter, setTriggerWordFilter] = useState<string | null>(null);
  const [entityFilter, setEntityFilter] = useState<string | null>(null);

  const { startDate, endDate, setStartDate, setEndDate } = useAnalytics();

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

  const handleExportCsv = () => {
    if (!analysisResult) return;

    const header = [
      'row_index',
      'date',
      'author',
      'source',
      'url',
      'sentiment',
      'confidence',
      'model_used',
      'positive_trigger_words',
      'negative_trigger_words',
      'entities',
      'political_words',
      'text',
    ];

    const csvContent = [header.join(','), ...filteredRows.map((row) => toCsvRow(row))].join('\n');
    const filename = sanitizeFileName(
      `${analysisResult.collection_id}_${analysisResult.job_id || 'filtered'}_${new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-')}`,
    );

    downloadTextFile(`${filename}.csv`, csvContent, 'text/csv;charset=utf-8');
  };

  const handleExportJson = () => {
    if (!analysisResult) return;

    const exportPayload = {
      job_id: analysisResult.job_id,
      collection_id: analysisResult.collection_id,
      filename: analysisResult.filename,
      analyzed_at: analysisResult.analyzed_at,
      filters: {
        sentiment: sentimentFilter,
        entity: entityFilter,
        trigger_word: triggerWordFilter,
        search_query: searchQuery,
        start_date: startDate,
        end_date: endDate,
        sort_by: sortBy,
      },
      summary: displayAgg,
      rows: filteredRows,
    };

    const filename = sanitizeFileName(
      `${analysisResult.collection_id}_${analysisResult.job_id || 'filtered'}_${new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-')}`,
    );

    downloadTextFile(`${filename}.json`, JSON.stringify(exportPayload, null, 2), 'application/json;charset=utf-8');
  };


  const filteredRows = useMemo(() => {
    if (!analysisResult) return [];
    let rows = [...analysisResult.rows];
    if (sentimentFilter !== 'all') {
      rows = rows.filter((r) => r.sentiment === sentimentFilter);
    }
    if (entityFilter) {
      rows = rows.filter((r) => r.entities.some((e) => e.entity === entityFilter));
    }
    if (triggerWordFilter) {
      rows = rows.filter((r) => 
        r.trigger_words.positive.some(w => w.toLowerCase() === triggerWordFilter.toLowerCase()) ||
        r.trigger_words.negative.some(w => w.toLowerCase() === triggerWordFilter.toLowerCase())
      );
    }
    if (searchQuery) {
      rows = rows.filter((r) => r.text.toLowerCase().includes(searchQuery.toLowerCase()));
    }
    
    // Global Date Filtering
    if (startDate) {
      rows = rows.filter((r) => r.meta.date >= startDate);
    }
    if (endDate) {
      rows = rows.filter((r) => r.meta.date <= endDate);
    }

    if (sortBy === 'confidence') {
      rows.sort((a, b) => b.confidence - a.confidence);
    }
    return rows;
  }, [analysisResult, sentimentFilter, sortBy, entityFilter, triggerWordFilter, searchQuery, startDate, endDate]);

  const filteredAgg = useMemo(() => {
    if (!analysisResult || filteredRows.length === 0) return null;

    const total_rows = filteredRows.length;
    const sentiment_distribution = {
      positive: filteredRows.filter(r => r.sentiment === 'positive').length,
      neutral: filteredRows.filter(r => r.sentiment === 'neutral').length,
      negative: filteredRows.filter(r => r.sentiment === 'negative').length,
    };
    const avg_confidence = filteredRows.reduce((acc, r) => acc + r.confidence, 0) / total_rows;

    const entityCounts: Record<string, number> = {};
    filteredRows.forEach(row => {
      row.entities.forEach(ent => {
        entityCounts[ent.entity] = (entityCounts[ent.entity] || 0) + 1;
      });
    });
    const top_entities = Object.entries(entityCounts)
      .map(([entity, count]) => ({ entity, count }))
      .sort((a, b) => b.count - a.count);

    const triggerWordCounts: Record<string, { count: number; type: string }> = {};
    filteredRows.forEach(row => {
      ['positive', 'negative'].forEach(type => {
        row.trigger_words[type as 'positive' | 'negative'].forEach(word => {
          const key = word.toLowerCase();
          if (!triggerWordCounts[key]) {
            triggerWordCounts[key] = { count: 0, type };
          }
          triggerWordCounts[key].count++;
        });
      });
    });
    const top_trigger_words = Object.entries(triggerWordCounts)
      .map(([word, data]) => ({ word, ...data }))
      .sort((a, b) => b.count - a.count);

    const entitySentimentCounts: Record<string, { positive: number; negative: number }> = {};
    filteredRows.forEach(row => {
      row.entities.forEach(ent => {
        if (!entitySentimentCounts[ent.entity]) {
          entitySentimentCounts[ent.entity] = { positive: 0, negative: 0 };
        }
        if (row.sentiment === 'positive') entitySentimentCounts[ent.entity].positive++;
        if (row.sentiment === 'negative') entitySentimentCounts[ent.entity].negative++;
      });
    });

    const top_positive_entities = Object.entries(entitySentimentCounts)
      .map(([entity, scores]) => ({ entity, count: scores.positive }))
      .filter(e => e.count > 0)
      .sort((a, b) => b.count - a.count);

    const top_negative_entities = Object.entries(entitySentimentCounts)
      .map(([entity, scores]) => ({ entity, count: scores.negative }))
      .filter(e => e.count > 0)
      .sort((a, b) => b.count - a.count);

    return {
      total_rows,
      sentiment_distribution,
      avg_confidence,
      top_entities,
      top_trigger_words,
      top_positive_entities,
      top_negative_entities
    };
  }, [analysisResult, filteredRows]);

  const agg = analysisResult?.aggregate;
  const displayAgg = filteredAgg || agg;
  const dist = displayAgg?.sentiment_distribution;

  const total = (dist?.positive ?? 0) + (dist?.neutral ?? 0) + (dist?.negative ?? 0);
  const pctPos = total ? Math.round((dist!.positive / total) * 100) : 0;
  const pctNeu = total ? Math.round((dist!.neutral / total) * 100) : 0;
  const pctNeg = total ? 100 - pctPos - pctNeu : 0;

  const pieData = [
    { key: 'positive' as SentimentFilter, name: 'Positive', value: dist?.positive ?? 0, color: '#86bdf7' },
    { key: 'neutral' as SentimentFilter, name: 'Neutral', value: dist?.neutral ?? 0, color: '#adaaaa' },
    { key: 'negative' as SentimentFilter, name: 'Negative', value: dist?.negative ?? 0, color: '#ff716c' },
  ];

  return (
    <>
      <div className="p-6 space-y-6">
        {/* Header & Main Controls */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-6 border-b border-outline-variant/10">
          <div>
            <h1 className="text-4xl font-headline font-bold tracking-tight text-on-surface uppercase">Analytics</h1>
            <p className="text-on-surface-variant font-mono text-[10px] mt-1">
              BATCH_SENTIMENT_ANALYSIS {analysisResult ? `// JOB: ${analysisResult.job_id}` : ''}
            </p>
          </div>
          
          <div className="flex flex-wrap items-center gap-2">
            <select
              value={selectedCollectionId}
              onChange={(e) => setSelectedCollectionId(e.target.value)}
              className="bg-surface-container-low border border-outline-variant/20 text-[10px] font-mono px-3 py-2 focus:ring-0 w-64"
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
        </div>

        {/* Global Filter Bar */}
        <section className="bg-surface-container-low border border-outline-variant/10 p-3 flex flex-wrap items-center gap-4 sticky top-14 z-20 shadow-sm">
          <div className="flex items-center gap-2 bg-surface-container-lowest border border-outline-variant/20 px-3 py-1.5 flex-1 min-w-[200px]">
            <span className="material-symbols-outlined text-sm text-on-surface-variant">search</span>
            <input 
              type="text"
              placeholder="SEARCH_TEXT..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-transparent border-none text-[10px] font-mono focus:ring-0 w-full"
            />
          </div>

          <div className="flex items-center gap-1 border-l border-outline-variant/20 pl-4">
            <p className="font-mono text-[9px] uppercase text-on-surface-variant mr-2">Filter:</p>
            {[
              { key: 'all', label: 'ALL', color: 'text-on-surface' },
              { key: 'positive', label: 'POS', color: 'text-secondary' },
              { key: 'neutral', label: 'NEU', color: 'text-on-surface-variant' },
              { key: 'negative', label: 'NEG', color: 'text-tertiary' },
            ].map((f) => (
              <button 
                key={f.key}
                onClick={() => setSentimentFilter(f.key as SentimentFilter)}
                className={`px-2 py-1 text-[9px] font-mono border ${sentimentFilter === f.key ? 'bg-primary/10 border-primary text-primary' : 'border-transparent hover:border-outline-variant/30 text-on-surface-variant'}`}
              >
                {f.label}
              </button>
            ))}
          </div>

          {(sentimentFilter !== 'all' || entityFilter || triggerWordFilter || searchQuery || startDate || endDate) && (
            <button 
              onClick={() => {
                setSentimentFilter('all');
                setEntityFilter(null);
                setTriggerWordFilter(null);
                setSearchQuery('');
                setStartDate('');
                setEndDate('');
              }}
              className="flex items-center gap-1 text-[9px] font-mono text-tertiary hover:underline ml-auto"
            >
              <span className="material-symbols-outlined text-[10px]">close</span>
              RESET_ALL
            </button>
          )}
        </section>

        {error && <p className="font-mono text-[10px] text-tertiary">{error}</p>}
        {loading && <p className="font-mono text-[10px] text-on-surface-variant animate-pulse">LOADING_DATA...</p>}

        {/* Results — only show after analysis */}
        {analysisResult && agg && dist && (
          <>
            {/* Stat Cards */}
            <section className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <div 
                className={`bg-surface-container-low border border-outline-variant/10 p-4 cursor-pointer transition-colors hover:bg-surface-container-high ${sentimentFilter === 'all' && !entityFilter && !triggerWordFilter ? 'border-primary/40' : ''}`}
                onClick={() => { 
                  setSentimentFilter('all'); 
                  setEntityFilter(null); 
                  setTriggerWordFilter(null);
                }}
              >
                <p className="font-mono text-[10px] uppercase text-on-surface-variant">Total Rows</p>
                <p className="text-3xl font-headline font-bold text-primary mt-2">{displayAgg.total_rows}</p>
              </div>
              <div 
                className={`bg-surface-container-low border border-outline-variant/10 p-4 cursor-pointer transition-colors hover:bg-surface-container-high ${sentimentFilter === 'positive' ? 'border-secondary/40' : ''}`}
                onClick={() => {
                  setSentimentFilter('positive');
                  setEntityFilter(null);
                  setTriggerWordFilter(null);
                }}
              >
                <p className="font-mono text-[10px] uppercase text-on-surface-variant">Positive</p>
                <p className="text-3xl font-headline font-bold text-secondary mt-2">{dist.positive} <span className="text-xs font-mono font-normal">{pctPos}%</span></p>
              </div>
              <div 
                className={`bg-surface-container-low border border-outline-variant/10 p-4 cursor-pointer transition-colors hover:bg-surface-container-high ${sentimentFilter === 'neutral' ? 'border-on-surface-variant/40' : ''}`}
                onClick={() => {
                  setSentimentFilter('neutral');
                  setEntityFilter(null);
                  setTriggerWordFilter(null);
                }}
              >
                <p className="font-mono text-[10px] uppercase text-on-surface-variant">Neutral</p>
                <p className="text-3xl font-headline font-bold text-on-surface-variant mt-2">{dist.neutral} <span className="text-xs font-mono font-normal">{pctNeu}%</span></p>
              </div>
              <div 
                className={`bg-surface-container-low border border-outline-variant/10 p-4 cursor-pointer transition-colors hover:bg-surface-container-high ${sentimentFilter === 'negative' ? 'border-tertiary/40' : ''}`}
                onClick={() => {
                  setSentimentFilter('negative');
                  setEntityFilter(null);
                  setTriggerWordFilter(null);
                }}
              >
                <p className="font-mono text-[10px] uppercase text-on-surface-variant">Negative</p>
                <p className="text-3xl font-headline font-bold text-tertiary mt-2">{dist.negative} <span className="text-xs font-mono font-normal">{pctNeg}%</span></p>
              </div>
              <div className="bg-surface-container-low border border-outline-variant/10 p-4">
                <p className="font-mono text-[10px] uppercase text-on-surface-variant">Avg Confidence</p>
                <p className="text-3xl font-headline font-bold text-primary mt-2">{(displayAgg.avg_confidence * 100).toFixed(1)}%</p>
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
                    <PieChart width={192} height={192}>
                      <Pie
                        data={pieData}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        innerRadius={58}
                        outerRadius={80}
                        paddingAngle={total ? 2 : 0}
                        startAngle={90}
                        endAngle={-270}
                        isAnimationActive={false}
                        onClick={(entry: any) => setSentimentFilter(entry.key as SentimentFilter)}
                      >
                        {pieData.map((entry) => (
                          <Cell
                            key={entry.key}
                            fill={entry.color}
                            fillOpacity={sentimentFilter === entry.key ? 1 : 0.8}
                            stroke={sentimentFilter === entry.key ? entry.color : 'none'}
                            strokeWidth={sentimentFilter === entry.key ? 2 : 0}
                            style={{ cursor: 'pointer' }}
                          />
                        ))}
                      </Pie>
                    </PieChart>
                    <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                      <span className="font-headline text-2xl font-black text-on-surface">{total}</span>
                      <span className="font-mono text-[8px] text-on-surface-variant uppercase">Analyzed</span>
                    </div>
                  </div>
                  <div className="space-y-4">
                    {[
                      { label: 'Positive', key: 'positive' as SentimentFilter, pct: pctPos, color: 'bg-[#86bdf7]', text: 'text-secondary' },
                      { label: 'Neutral', key: 'neutral' as SentimentFilter, pct: pctNeu, color: 'bg-[#adaaaa]', text: 'text-on-surface-variant' },
                      { label: 'Negative', key: 'negative' as SentimentFilter, pct: pctNeg, color: 'bg-[#ff716c]', text: 'text-tertiary' },
                    ].map((item) => (
                      <div 
                        key={item.label} 
                        className={`flex items-center gap-3 cursor-pointer p-1 rounded transition-colors hover:bg-surface-container-high ${sentimentFilter === item.key ? 'bg-surface-container-high ring-1 ring-outline-variant/20' : ''}`}
                        onClick={() => setSentimentFilter(item.key)}
                      >
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
                  {entityFilter && (
                    <button 
                      className="ml-auto text-[9px] text-primary underline uppercase tracking-tighter"
                      onClick={() => setEntityFilter(null)}
                    >
                      Clear
                    </button>
                  )}
                </h2>
                {displayAgg.top_entities.length === 0 && <p className="font-mono text-[10px] text-on-surface-variant">No entities detected</p>}
                <div className="space-y-2">
                  {displayAgg.top_entities.slice(0, 8).map((ent) => (
                    <div 
                      key={ent.entity} 
                      className={`flex items-center justify-between cursor-pointer p-1 transition-colors hover:bg-surface-container-high ${entityFilter === ent.entity ? 'bg-surface-container-high' : ''}`}
                      onClick={() => setEntityFilter(ent.entity)}
                    >
                      <span className="font-mono text-[10px] text-primary">{ent.entity}</span>
                      <div className="flex items-center gap-2">
                        <div className="w-24 h-1 bg-surface-container-highest">
                          <div className="h-1 bg-primary" style={{ width: `${Math.min(100, (ent.count / (displayAgg.top_entities[0]?.count || 1)) * 100)}%` }}></div>
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
                  {triggerWordFilter && (
                    <button 
                      className="ml-auto text-[9px] text-primary underline uppercase tracking-tighter"
                      onClick={() => setTriggerWordFilter(null)}
                    >
                      Clear
                    </button>
                  )}
                </h2>
                <WordCloud 
                  words={displayAgg.top_trigger_words} 
                  maxWords={15} 
                  onWordClick={(w) => setTriggerWordFilter(w === triggerWordFilter ? null : w)}
                  selectedWord={triggerWordFilter}
                />
              </div>
            </div>

            {/* Entity Sentiment Analysis Section */}
            <div className="grid grid-cols-12 gap-6">
              {/* Positive Sentiment by Entity */}
              <div className="col-span-12 lg:col-span-6 bg-surface-container-low border border-outline-variant/10 p-4">
                <h2 className="font-headline text-xs font-bold uppercase tracking-widest flex items-center gap-2 mb-4">
                  <span className="w-1.5 h-1.5 bg-secondary"></span> POSITIVE_SENTIMENT_BY_ENTITY
                </h2>
                {displayAgg.top_positive_entities?.length === 0 && <p className="font-mono text-[10px] text-on-surface-variant">No positive mentions found</p>}
                <div className="space-y-3">
                  {displayAgg.top_positive_entities?.slice(0, 5).map((ent) => (
                    <div 
                      key={ent.entity} 
                      className="cursor-pointer group"
                      onClick={() => { setEntityFilter(ent.entity); setSentimentFilter('positive'); }}
                    >
                      <div className="flex justify-between items-center mb-1">
                        <span className="font-mono text-[10px] text-on-surface uppercase">{ent.entity}</span>
                        <span className="font-mono text-[10px] text-secondary font-bold">{ent.count} POS</span>
                      </div>
                      <div className="w-full h-2 bg-surface-container-highest rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-secondary transition-all duration-500" 
                          style={{ width: `${(ent.count / (displayAgg.top_positive_entities?.[0]?.count || 1)) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Negative Sentiment by Entity */}
              <div className="col-span-12 lg:col-span-6 bg-surface-container-low border border-outline-variant/10 p-4">
                <h2 className="font-headline text-xs font-bold uppercase tracking-widest flex items-center gap-2 mb-4">
                  <span className="w-1.5 h-1.5 bg-tertiary"></span> NEGATIVE_SENTIMENT_BY_ENTITY
                </h2>
                {displayAgg.top_negative_entities?.length === 0 && <p className="font-mono text-[10px] text-on-surface-variant">No negative mentions found</p>}
                <div className="space-y-3">
                  {displayAgg.top_negative_entities?.slice(0, 5).map((ent) => (
                    <div 
                      key={ent.entity} 
                      className="cursor-pointer group"
                      onClick={() => { setEntityFilter(ent.entity); setSentimentFilter('negative'); }}
                    >
                      <div className="flex justify-between items-center mb-1">
                        <span className="font-mono text-[10px] text-on-surface uppercase">{ent.entity}</span>
                        <span className="font-mono text-[10px] text-tertiary font-bold">{ent.count} NEG</span>
                      </div>
                      <div className="w-full h-2 bg-surface-container-highest rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-tertiary transition-all duration-500" 
                          style={{ width: `${(ent.count / (displayAgg.top_negative_entities?.[0]?.count || 1)) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
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
                  <button 
                    type="button" 
                    onClick={() => setSortBy(sortBy === 'index' ? 'confidence' : 'index')}
                    className="flex items-center gap-1 font-mono text-[9px] text-on-surface-variant hover:text-primary px-2 py-1 border border-outline-variant/20 bg-surface-container-lowest"
                  >
                    <span className="material-symbols-outlined text-[10px]">
                      {sortBy === 'index' ? 'sort_by_alpha' : 'monitoring'}
                    </span>
                    {sortBy === 'index' ? 'ORDER' : 'CONFIDENCE'}
                  </button>
                  <button
                    type="button"
                    onClick={() => void handleExportCsv()}
                    disabled={!analysisResult}
                    className="flex items-center gap-1 font-mono text-[9px] text-on-surface-variant hover:text-primary px-2 py-1 border border-outline-variant/20 bg-surface-container-lowest disabled:opacity-50"
                  >
                    <span className="material-symbols-outlined text-[10px]">download</span>
                    CSV
                  </button>
                  <button
                    type="button"
                    onClick={() => void handleExportJson()}
                    disabled={!analysisResult}
                    className="flex items-center gap-1 font-mono text-[9px] text-on-surface-variant hover:text-primary px-2 py-1 border border-outline-variant/20 bg-surface-container-lowest disabled:opacity-50"
                  >
                    <span className="material-symbols-outlined text-[10px]">data_object</span>
                    JSON
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
    </>
  );
};

export default Analytics;
