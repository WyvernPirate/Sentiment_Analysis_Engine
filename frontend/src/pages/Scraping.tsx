import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { sentimentApi } from '../services/sentimentApi';
import { SocialCollection, SocialHealthStatus, SocialInputItem } from '../types/sentiment';

interface CsvPreviewRow extends SocialInputItem {
  isValid: boolean;
}

const FALLBACK_SOURCES = [
  { source: 'X API Stream', region: 'BW', status: 'ONLINE', recordsPerMin: 486, failureRate: '0.2%' },
  { source: 'Facebook Public Feed', region: 'BW', status: 'ONLINE', recordsPerMin: 221, failureRate: '0.9%' },
  { source: 'News RSS Cluster', region: 'SADC', status: 'DEGRADED', recordsPerMin: 77, failureRate: '3.1%' },
  { source: 'Community Forums', region: 'BW', status: 'ONLINE', recordsPerMin: 92, failureRate: '1.2%' },
];

const TEXT_COLUMN_NAMES = [
  'text', 'text_raw', 'content', 'tweet', 'message', 'post',
  'body', 'description', 'full_text', 'tweet_text', 'post_text',
];

const Scraping: React.FC = () => {
  const [socialHealth, setSocialHealth] = useState<SocialHealthStatus | null>(null);
  const [collections, setCollections] = useState<SocialCollection[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<string>('');
  const [statusError, setStatusError] = useState<string>('');
  const [provider, setProvider] = useState<string>('');
  const [query, setQuery] = useState<string>('botswana politics');
  const [maxResults, setMaxResults] = useState<number>(20);
  const [selectedCollectionId, setSelectedCollectionId] = useState<string>('');
  const [filterMode, setFilterMode] = useState<'relaxed' | 'strict'>('relaxed');
  const [csvRows, setCsvRows] = useState<SocialInputItem[]>([]);
  const [csvPreviewRows, setCsvPreviewRows] = useState<CsvPreviewRow[]>([]);
  const [csvFileName, setCsvFileName] = useState<string>('');
  const [csvType, setCsvType] = useState<'data' | 'url_only' | ''>('');
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [csvTextColumnDetected, setCsvTextColumnDetected] = useState<string>('');

  const refreshSocialData = useCallback(async () => {
    const [healthData, collectionData] = await Promise.all([
      sentimentApi.checkSocialHealth(),
      sentimentApi.listSocialCollections(10),
    ]);

    setSocialHealth(healthData);
    setCollections(collectionData);
    if (!selectedCollectionId && collectionData.length > 0) {
      setSelectedCollectionId(collectionData[0].collection_id);
    }
  }, [selectedCollectionId]);

  useEffect(() => {
    const loadSocialData = async () => {
      try {
        await refreshSocialData();
      } finally {
        setLoading(false);
      }
    };

    void loadSocialData();
  }, [refreshSocialData]);

  const parseCsvLine = (line: string): string[] => {
    const result: string[] = [];
    let current = '';
    let inQuotes = false;

    for (let i = 0; i < line.length; i += 1) {
      const char = line[i];

      if (char === '"') {
        if (inQuotes && line[i + 1] === '"') {
          current += '"';
          i += 1;
        } else {
          inQuotes = !inQuotes;
        }
      } else if (char === ',' && !inQuotes) {
        result.push(current.trim());
        current = '';
      } else {
        current += char;
      }
    }

    result.push(current.trim());
    return result;
  };

  const handleCsvFile = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    setStatusError('');
    setStatusMessage('');

    try {
      const text = await file.text();
      const lines = text.split(/\r?\n/).filter((line) => line.trim().length > 0);

      if (lines.length < 2) {
        setStatusError('CSV requires a header and at least one data row.');
        return;
      }

      const headers = parseCsvLine(lines[0]).map((header) => header.toLowerCase().trim());

      // Detect CSV type: does it have a text/content column?
      const hasTextColumn = headers.some((h) =>
        TEXT_COLUMN_NAMES.includes(h)
      );
      const detectedTextCol = headers.find((h) => TEXT_COLUMN_NAMES.includes(h)) || '';

      const previewRows: CsvPreviewRow[] = lines.slice(1).map((line) => {
        const values = parseCsvLine(line);
        const rowMap: Record<string, string> = {};

        headers.forEach((header, idx) => {
          rowMap[header] = values[idx] || '';
        });

        const mapped = {
          url: rowMap.url || rowMap.post_url || '',
          text: rowMap.text || rowMap.text_raw || rowMap.content || rowMap.tweet || rowMap.message || rowMap.post || rowMap.body || rowMap.description || rowMap.full_text || '',
          author: rowMap.author || rowMap.author_username || rowMap.user || rowMap.username || '',
          created_at: rowMap.created_at || rowMap.created_at_utc || rowMap.date || rowMap.timestamp || '',
        };

        return {
          ...mapped,
          isValid: Boolean(mapped.url || mapped.text),
        };
      });

      const rows = previewRows.filter((row) => row.isValid).map((row) => ({
        url: row.url,
        text: row.text,
        author: row.author,
        created_at: row.created_at,
      }));

      setCsvRows(rows);
      setCsvPreviewRows(previewRows);
      setCsvFileName(file.name);
      setCsvFile(file);

      if (hasTextColumn) {
        setCsvType('data');
        setCsvTextColumnDetected(detectedTextCol);
        setStatusMessage(`Detected: DATA CSV — ${rows.length} rows with text column "${detectedTextCol}" from ${file.name}.`);
      } else {
        setCsvType('url_only');
        setCsvTextColumnDetected('');
        setStatusMessage(`Detected: URL CSV — ${rows.length} URLs from ${file.name}.`);
      }
    } catch {
      setStatusError('Failed to parse CSV file.');
    }
  };

  const clearCsv = () => {
    setCsvRows([]);
    setCsvPreviewRows([]);
    setCsvFileName('');
    setCsvType('');
    setCsvFile(null);
    setCsvTextColumnDetected('');
  };

  const handleCollect = async () => {
    setActionLoading(true);
    setStatusError('');
    setStatusMessage('');

    try {
      // Data CSV → upload file directly to backend for parsing & ingestion
      if (csvType === 'data' && csvFile) {
        const result = await sentimentApi.uploadCsvFile(csvFile);
        if (result.error) {
          setStatusError(result.error);
          return;
        }
        setStatusMessage(`CSV ingested: ${result.count} records saved as ${result.collection_id}.`);
        await refreshSocialData();
        setSelectedCollectionId(result.collection_id);
        clearCsv();
        return;
      }

      // URL-only CSV or manual query → use existing collect endpoint
      const payload = {
        provider: provider || undefined,
        query: query || undefined,
        max_results: maxResults,
        input: csvRows.length ? csvRows : undefined,
      };

      const result = await sentimentApi.collectSocialPosts(payload);
      if (result.error) {
        setStatusError(result.error);
        return;
      }

      setStatusMessage(`Collection complete: ${result.count} records saved as ${result.collection_id}.`);
      await refreshSocialData();
      setSelectedCollectionId(result.collection_id);
    } finally {
      setActionLoading(false);
    }
  };

  const handleClean = async () => {
    if (!selectedCollectionId) {
      setStatusError('Select a collection to clean first.');
      return;
    }

    setActionLoading(true);
    setStatusError('');
    setStatusMessage('');

    try {
      const result = await sentimentApi.cleanSocialCollection({
        collection_id: selectedCollectionId,
        filter_mode: filterMode,
      });

      if (result.error) {
        setStatusError(result.error);
        return;
      }

      setStatusMessage(`Cleaning complete: ${result.cleaned_count}/${result.raw_count} records retained (${result.filter_mode}).`);
    } finally {
      setActionLoading(false);
    }
  };

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
      return FALLBACK_SOURCES;
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
      {
        source: 'CSV Upload',
        region: 'LOCAL',
        status: 'ONLINE',
        recordsPerMin: 0,
        failureRate: '0%',
      },
    ];
  }, [socialHealth, collections]);

  const activeSources = sourceRows.filter((row) => row.status === 'ONLINE').length;
  const invalidCsvCount = csvPreviewRows.filter((row) => !row.isValid).length;
  const previewRows = csvPreviewRows.slice(0, 8);

  return (
    <div className="ml-64 pt-14 min-h-screen bg-surface">
      <div className="p-6 space-y-6">
        <div className="flex items-end justify-between border-b border-outline-variant/10 pb-4">
          <div>
            <h1 className="text-4xl font-headline font-bold tracking-tight text-on-surface uppercase">Scraping Sources</h1>
            <p className="text-on-surface-variant font-mono text-xs mt-2">DATA_COLLECTION_SYSTEM</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => {
                void refreshSocialData();
              }}
              className="bg-surface-container-high hover:bg-surface-bright text-on-surface text-[10px] font-headline uppercase font-bold px-4 py-2 flex items-center gap-2 border-b-2 border-primary transition-all"
            >
              <span className="material-symbols-outlined text-sm">sync</span>
              Resync Sources
            </button>
          </div>
        </div>

        <section className="bg-surface-container-low border border-outline-variant/10 p-4 space-y-4">
          <h2 className="font-headline text-xs font-bold uppercase tracking-widest">Ingestion Control</h2>

          {/* CSV Upload Zone */}
          <div className="border border-dashed border-outline-variant/30 p-4 bg-surface-container-lowest">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-lg">upload_file</span>
                <span className="font-headline text-[10px] font-bold uppercase tracking-widest">CSV Data Upload</span>
              </div>
              {csvType && (
                <span className={`font-mono text-[10px] px-2 py-0.5 ${csvType === 'data' ? 'bg-secondary/10 text-secondary' : 'bg-primary/10 text-primary'}`}>
                  {csvType === 'data' ? `DATA_CSV // COL: ${csvTextColumnDetected.toUpperCase()}` : 'URL_LIST_CSV'}
                </span>
              )}
            </div>
            <div className="flex items-center gap-3">
              <input
                type="file"
                accept=".csv,text/csv"
                onChange={handleCsvFile}
                className="bg-surface-container-lowest border border-outline-variant/20 text-xs font-mono px-3 py-2 file:mr-2 file:border-0 file:bg-primary/10 file:text-primary file:px-2 file:py-1 flex-1"
              />
              {csvFileName && (
                <button
                  type="button"
                  onClick={clearCsv}
                  className="font-mono text-[10px] text-on-surface-variant hover:text-tertiary px-2 py-1 border border-outline-variant/20 transition-colors"
                >
                  CLEAR
                </button>
              )}
            </div>
            <p className="font-mono text-[9px] text-on-surface-variant mt-2">
              Accepts data CSVs (with text/content column) or URL-only CSVs. Auto-detects column mapping.
            </p>
          </div>

          {/* Query-based collection controls */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <input
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              placeholder="provider (optional)"
              className="bg-surface-container-lowest border border-outline-variant/20 text-xs font-mono px-3 py-2 focus:ring-0"
            />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="query"
              className="bg-surface-container-lowest border border-outline-variant/20 text-xs font-mono px-3 py-2 focus:ring-0"
            />
            <input
              type="number"
              min={1}
              value={maxResults}
              onChange={(e) => setMaxResults(Number(e.target.value))}
              className="bg-surface-container-lowest border border-outline-variant/20 text-xs font-mono px-3 py-2 focus:ring-0"
            />
            <div /> {/* spacer */}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <select
              value={selectedCollectionId}
              onChange={(e) => setSelectedCollectionId(e.target.value)}
              className="bg-surface-container-lowest border border-outline-variant/20 text-xs font-mono px-3 py-2 focus:ring-0"
            >
              <option value="">Select collection</option>
              {collections.map((entry) => (
                <option key={entry.collection_id} value={entry.collection_id}>
                  {entry.collection_id}
                </option>
              ))}
            </select>
            <select
              value={filterMode}
              onChange={(e) => setFilterMode(e.target.value as 'relaxed' | 'strict')}
              className="bg-surface-container-lowest border border-outline-variant/20 text-xs font-mono px-3 py-2 focus:ring-0"
            >
              <option value="relaxed">filter: relaxed</option>
              <option value="strict">filter: strict</option>
            </select>
            <button
              type="button"
              onClick={() => {
                void handleCollect();
              }}
              disabled={actionLoading}
              className="bg-primary text-on-primary text-[10px] font-headline uppercase font-bold px-4 py-2 disabled:opacity-60 flex items-center justify-center gap-2"
            >
              {actionLoading && <span className="material-symbols-outlined text-sm animate-spin">progress_activity</span>}
              {csvType === 'data' ? `Ingest CSV (${csvRows.length} rows)` : csvRows.length ? `Collect (${csvRows.length} URLs)` : 'Collect'}
            </button>
            <button
              type="button"
              onClick={() => {
                void handleClean();
              }}
              disabled={actionLoading || !selectedCollectionId}
              className="bg-surface-container-high text-on-surface text-[10px] font-headline uppercase font-bold px-4 py-2 border-b-2 border-primary disabled:opacity-60"
            >
              Clean Selected
            </button>
          </div>
          {(statusMessage || statusError) && (
            <div className="space-y-1">
              {statusMessage && <p className="font-mono text-[10px] text-secondary">{statusMessage}</p>}
              {statusError && <p className="font-mono text-[10px] text-tertiary">{statusError}</p>}
            </div>
          )}
        </section>

        {csvPreviewRows.length > 0 && (
          <section className="bg-surface-container-low border border-outline-variant/10 p-4 space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="font-headline text-xs font-bold uppercase tracking-widest flex items-center gap-2">
                <span className={`w-1.5 h-1.5 ${csvType === 'data' ? 'bg-secondary' : 'bg-primary'}`}></span>
                CSV Preview
                <span className={`font-mono text-[9px] ml-2 px-1.5 py-0.5 ${csvType === 'data' ? 'bg-secondary/10 text-secondary' : 'bg-primary/10 text-primary'}`}>
                  {csvType === 'data' ? 'DATA MODE' : 'URL MODE'}
                </span>
              </h2>
              <div className="flex gap-3 font-mono text-[10px]">
                <span className="text-secondary">VALID: {csvRows.length}</span>
                <span className="text-tertiary">INVALID: {invalidCsvCount}</span>
                <span className="text-on-surface-variant">TOTAL: {csvPreviewRows.length}</span>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="text-left font-mono text-[9px] text-on-surface-variant uppercase border-b border-outline-variant/20">
                    <th className="pb-2 font-normal">Status</th>
                    {csvType === 'data' && <th className="pb-2 font-normal">Text</th>}
                    {csvType !== 'data' && <th className="pb-2 font-normal">URL</th>}
                    <th className="pb-2 font-normal">Author</th>
                    <th className="pb-2 font-normal">Date</th>
                  </tr>
                </thead>
                <tbody className="font-mono text-[10px]">
                  {previewRows.map((row, idx) => (
                    <tr key={`${row.url || row.text || 'row'}-${idx}`} className="border-b border-outline-variant/10">
                      <td className={`py-2 ${row.isValid ? 'text-secondary' : 'text-tertiary'}`}>
                        {row.isValid ? 'VALID' : 'INVALID'}
                      </td>
                      {csvType === 'data' && (
                        <td className="py-2 max-w-[400px] truncate">{row.text || '--'}</td>
                      )}
                      {csvType !== 'data' && (
                        <td className="py-2 text-primary max-w-[300px] truncate">{row.url || '--'}</td>
                      )}
                      <td className="py-2">{row.author || '--'}</td>
                      <td className="py-2">{row.created_at || '--'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {csvPreviewRows.length > previewRows.length && (
              <p className="font-mono text-[10px] text-on-surface-variant">
                Showing {previewRows.length} of {csvPreviewRows.length} parsed rows.
              </p>
            )}
            {invalidCsvCount > 0 && (
              <p className="font-mono text-[10px] text-tertiary">
                Invalid rows are skipped automatically (must contain at least URL or text).
              </p>
            )}
          </section>
        )}

        <section className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-surface-container-low border border-outline-variant/10 p-4">
            <p className="font-mono text-[10px] uppercase text-on-surface-variant">Active Sources</p>
            <p className="text-3xl font-headline font-bold text-primary mt-2">{activeSources || '--'}</p>
          </div>
          <div className="bg-surface-container-low border border-outline-variant/10 p-4">
            <p className="font-mono text-[10px] uppercase text-on-surface-variant">Total Ingested</p>
            <p className="text-3xl font-headline font-bold text-secondary mt-2">{totalIngested || '--'}</p>
          </div>
          <div className="bg-surface-container-low border border-outline-variant/10 p-4">
            <p className="font-mono text-[10px] uppercase text-on-surface-variant">Collections</p>
            <p className="text-3xl font-headline font-bold text-on-surface mt-2">{collections.length ? `${collections.length}` : '--'}</p>
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
                  <span>CSV_UPLOAD_PIPELINE</span>
                  <span className="text-primary">100%</span>
                </div>
                <div className="h-1 bg-surface-container-highest">
                  <div className="h-1 bg-primary" style={{ width: '100%' }}></div>
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
