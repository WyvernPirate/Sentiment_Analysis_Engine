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
      // Heuristic for messy scrapers (X or Facebook)
      const isFacebook = headers.some(h => h.includes('x1i10') || h.includes('xdj'));
      const isXMessy = !hasTextColumn && headers.some(h => h.includes('css-') || h.includes('r-'));
      const isMessyScraper = isFacebook || isXMessy;

      const previewRows: CsvPreviewRow[] = lines.slice(1).map((line) => {
        const values = parseCsvLine(line);
        const rowMap: Record<string, string> = {};

        headers.forEach((header, idx) => {
          rowMap[header] = values[idx] || '';
        });

        // If messy scraper, we perform a frontend version of the 'stitch' logic for the preview
        let textVal = rowMap.text || rowMap.text_raw || rowMap.content || rowMap.tweet || rowMap.message || rowMap.post || rowMap.body || rowMap.description || rowMap.full_text || '';
        
        if (isMessyScraper && !textVal) {
          // Heuristic: for FB we scan more columns, for X we scan 7-12
          const searchRange = isFacebook ? headers.slice(3, 20) : headers.slice(7, 12);
          textVal = searchRange
            .map(h => rowMap[h])
            .filter(v => v && !v.startsWith('http') && v.length > 2)
            .join(' ');
        }

        const mapped = {
          url: rowMap.url || rowMap.post_url || (isFacebook ? rowMap[headers[0]] : rowMap[headers[5]]) || '',
          text: textVal,
          author: rowMap.author || rowMap.author_username || rowMap.user || rowMap.username || (isFacebook ? rowMap[headers[1]] : rowMap[headers[2]]) || '',
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
        setStatusMessage(`DETECTED: DATA_MODE // ${rows.length} records // Text Column: "${detectedTextCol}"`);
      } else if (isFacebook) {
        setCsvType('data');
        setCsvTextColumnDetected('REPAIR_FACEBOOK');
        setStatusMessage(`DETECTED: MESSY_FACEBOOK_SCRAPER // AUTO_REPAIR ACTIVE // ${rows.length} records`);
      } else if (isXMessy) {
        setCsvType('data');
        setCsvTextColumnDetected('REPAIR_X_SCRAPER');
        setStatusMessage(`DETECTED: MESSY_X_SCRAPER // AUTO_REPAIR ACTIVE // ${rows.length} records`);
      } else {
        setCsvType('url_only');
        setCsvTextColumnDetected('');
        setStatusMessage(`DETECTED: URL_LIST_MODE // ${rows.length} links found`);
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

  const [autoClean, setAutoClean] = useState<boolean>(true);

  const handleCollect = async () => {
    setActionLoading(true);
    setStatusError('');
    setStatusMessage('');

    try {
      // Data CSV → upload file directly to backend for parsing & ingestion
      if (csvType === 'data' && csvFile) {
        const result = await sentimentApi.uploadCsvFile(csvFile, autoClean ? filterMode : undefined);
        if (result.error) {
          setStatusError(result.error);
          return;
        }
        
        const cleanStatus = result.meta?.auto_cleaned ? ` (Auto-Cleaned: ${result.meta.cleaning_report?.cleaned_records} records kept)` : '';
        setStatusMessage(`CSV ingested: ${result.count} records saved as ${result.collection_id}${cleanStatus}.`);
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
            <h1 className="text-4xl font-headline font-bold tracking-tight text-on-surface uppercase">Ingestion Engine</h1>
            <p className="text-on-surface-variant font-mono text-xs mt-2 flex items-center gap-2">
              <span className="w-2 h-2 bg-secondary animate-pulse rounded-full"></span>
              CORE_PIPELINE_ACTIVE // {activeSources} SOURCES_CONNECTED
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => {
                void refreshSocialData();
              }}
              className="bg-surface-container-high hover:bg-surface-bright text-on-surface text-[10px] font-headline uppercase font-bold px-4 py-2 flex items-center gap-2 border-b-2 border-primary transition-all active:translate-y-0.5"
            >
              <span className="material-symbols-outlined text-sm">sync</span>
              Sync Data Lake
            </button>
          </div>
        </div>

        {/* Primary Controls: CSV Upload & Query */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <section className="lg:col-span-3 bg-surface-container-low border border-outline-variant/10 p-5 space-y-5">
            <div className="flex items-center justify-between">
              <h2 className="font-headline text-xs font-bold uppercase tracking-widest text-primary flex items-center gap-2">
                <span className="material-symbols-outlined text-sm">input</span>
                Data Entry Portal
              </h2>
              {csvType && (
                <div className="flex items-center gap-2 animate-in fade-in slide-in-from-right-2">
                  <span className={`font-mono text-[9px] px-2 py-0.5 border ${csvType === 'data' ? 'bg-secondary/10 border-secondary/30 text-secondary' : 'bg-primary/10 border-primary/30 text-primary'}`}>
                    {csvType === 'data' ? `MODE: ${csvTextColumnDetected}` : 'MODE: URL_LIST'}
                  </span>
                  <button onClick={clearCsv} className="text-[9px] font-mono text-tertiary hover:underline">ABORT</button>
                </div>
              )}
            </div>

            {/* Drag & Drop style zone (simplified) */}
            <div className={`relative border-2 border-dashed p-6 transition-colors ${csvFileName ? 'border-secondary/50 bg-secondary/5' : 'border-outline-variant/30 bg-surface-container-lowest'}`}>
              <div className="flex flex-col items-center justify-center text-center space-y-3">
                {!csvFileName ? (
                  <>
                    <span className="material-symbols-outlined text-4xl text-outline-variant/50">cloud_upload</span>
                    <div>
                      <p className="font-headline text-[11px] font-bold uppercase">Drop Social Data CSV Here</p>
                      <p className="font-mono text-[9px] text-on-surface-variant mt-1">SUPPORTED: X (Instant Data), FB (Technical), Custom Headers</p>
                    </div>
                    <input
                      type="file"
                      accept=".csv,text/csv"
                      onChange={handleCsvFile}
                      className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    />
                    <button className="bg-primary/10 text-primary text-[10px] font-bold px-4 py-1.5 border border-primary/20 pointer-events-none uppercase">Browse Local Files</button>
                  </>
                ) : (
                  <div className="w-full flex items-center justify-between">
                    <div className="flex items-center gap-4 text-left">
                      <span className="material-symbols-outlined text-3xl text-secondary">description</span>
                      <div>
                        <p className="font-headline text-[11px] font-bold uppercase text-secondary">{csvFileName}</p>
                        <p className="font-mono text-[9px] text-on-surface-variant">{csvRows.length} RECORDS_DETECTED // {csvType.toUpperCase()}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <label className="flex items-center gap-2 cursor-pointer group">
                        <input
                          type="checkbox"
                          checked={autoClean}
                          onChange={(e) => setAutoClean(e.target.checked)}
                          className="w-3 h-3 accent-primary"
                        />
                        <span className="font-mono text-[10px] text-on-surface-variant group-hover:text-secondary uppercase">Auto-Filter</span>
                      </label>
                      <button
                        onClick={() => void handleCollect()}
                        disabled={actionLoading}
                        className="bg-secondary text-on-secondary text-[10px] font-headline uppercase font-bold px-6 py-2 shadow-[0_4px_10px_rgba(var(--secondary-rgb),0.3)] hover:brightness-110 disabled:opacity-50 transition-all"
                      >
                        {actionLoading ? 'PROCESS...' : 'Commence Ingestion'}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <p className="font-mono text-[9px] uppercase text-on-surface-variant">Remote Collection Query</p>
                <div className="flex gap-2">
                  <input
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search query..."
                    className="flex-1 bg-surface-container-lowest border border-outline-variant/20 text-xs font-mono px-3 py-2 focus:border-primary outline-none transition-colors"
                  />
                  <select
                    value={provider}
                    onChange={(e) => setProvider(e.target.value)}
                    className="bg-surface-container-lowest border border-outline-variant/20 text-[10px] font-mono px-2 py-1 outline-none"
                  >
                    <option value="">AUTO_SELECT</option>
                    <option value="brightdata">BRIGHT_DATA</option>
                    <option value="apify">APIFY_JS</option>
                    <option value="twikit">TWIKIT_BW</option>
                  </select>
                </div>
              </div>
              <div className="space-y-2 text-right">
                <p className="font-mono text-[9px] uppercase text-on-surface-variant">Batch Size</p>
                <div className="flex items-center justify-end gap-3">
                  <input
                    type="range"
                    min="10"
                    max="500"
                    step="10"
                    value={maxResults}
                    onChange={(e) => setMaxResults(Number(e.target.value))}
                    className="w-32 accent-primary h-1 bg-outline-variant/20 rounded-lg appearance-none cursor-pointer"
                  />
                  <span className="font-mono text-xs text-primary font-bold">{maxResults}</span>
                  <button 
                    onClick={() => void handleCollect()}
                    disabled={actionLoading || !!csvFileName}
                    className="bg-primary/10 text-primary text-[10px] font-bold px-4 py-2 border border-primary/20 hover:bg-primary/20 disabled:hidden uppercase"
                  >
                    Fetch Remote
                  </button>
                </div>
              </div>
            </div>
            
            {statusMessage && (
              <div className="bg-secondary/5 border-l-2 border-secondary p-2 animate-in slide-in-from-left-2">
                <p className="font-mono text-[10px] text-secondary flex items-center gap-2">
                  <span className="material-symbols-outlined text-[12px]">check_circle</span>
                  {statusMessage}
                </p>
              </div>
            )}
            {statusError && (
              <div className="bg-tertiary/5 border-l-2 border-tertiary p-2 animate-in slide-in-from-left-2">
                <p className="font-mono text-[10px] text-tertiary flex items-center gap-2">
                  <span className="material-symbols-outlined text-[12px]">error</span>
                  {statusError}
                </p>
              </div>
            )}
          </section>

          {/* Right Column: Metrics & Status */}
          <section className="space-y-6 lg:col-span-1">
            <div className="bg-surface-container-low border border-outline-variant/10 p-4">
              <h2 className="font-headline text-xs font-bold uppercase tracking-widest text-on-surface mb-4">Pipeline Metrics</h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between border-b border-outline-variant/5 pb-2">
                  <span className="font-mono text-[10px] text-on-surface-variant">TOTAL_RECORDS</span>
                  <span className="text-xl font-headline font-bold text-secondary">{totalIngested.toLocaleString()}</span>
                </div>
                <div className="flex items-center justify-between border-b border-outline-variant/5 pb-2">
                  <span className="font-mono text-[10px] text-on-surface-variant">DATA_LAKE_SIZE</span>
                  <span className="text-xl font-headline font-bold text-on-surface">{collections.length} BATCHES</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="font-mono text-[10px] text-on-surface-variant">HEALTH_STATUS</span>
                  <span className="font-mono text-[10px] text-secondary bg-secondary/10 px-2 py-0.5 rounded">OPTIMAL</span>
                </div>
              </div>
            </div>

            <div className="bg-surface-container-lowest border border-outline-variant/20 p-4 flex flex-col">
              <div className="flex items-center justify-between mb-3 border-b border-outline-variant/10 pb-2">
                <h3 className="font-mono text-[10px] font-bold text-primary uppercase">Activity Log</h3>
                <span className="text-[10px] font-mono text-outline-variant/50 animate-pulse italic">LIVE</span>
              </div>
              <div className="space-y-1.5 font-mono text-[9px] overflow-y-auto scrollbar-hide">
                {recentEvents.map((evt, i) => (
                  <p key={i} className={`${i === 0 ? 'text-secondary font-bold' : 'text-on-surface-variant'}`}>
                    {evt}
                  </p>
                ))}
                {loading && <p className="text-primary animate-pulse italic mt-2">SYNCING...</p>}
              </div>
            </div>
          </section>
        </div>

        {/* Data Lake View (Collections) */}
        <section className="bg-surface-container-low border border-outline-variant/10 p-5">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="font-headline text-xs font-bold uppercase tracking-widest text-on-surface">Recent Collections</h2>
              <p className="font-mono text-[9px] text-on-surface-variant mt-1">Collected batches ready for analysis</p>
            </div>
            <div className="flex gap-3">
               <select
                  value={selectedCollectionId}
                  onChange={(e) => setSelectedCollectionId(e.target.value)}
                  className="bg-surface-container-lowest border border-outline-variant/20 text-[10px] font-mono px-3 py-1 outline-none min-w-[200px]"
                >
                  <option value="">Filter by batch ID...</option>
                  {collections.map((entry) => (
                    <option key={entry.collection_id} value={entry.collection_id}>
                      {entry.collection_id} ({entry.count} recs)
                    </option>
                  ))}
                </select>
                <button
                  onClick={() => void handleClean()}
                  disabled={!selectedCollectionId || actionLoading}
                  className="bg-surface-bright border border-primary/30 text-primary text-[10px] font-bold px-4 py-1 flex items-center gap-2 hover:bg-primary/10 disabled:opacity-40 transition-all active:scale-95"
                >
                  <span className="material-symbols-outlined text-sm">cleaning_services</span>
                  RUN CLEANER
                </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {collections.map((col) => (
              <div 
                key={col.collection_id} 
                onClick={() => setSelectedCollectionId(col.collection_id)}
                className={`p-4 border transition-all cursor-pointer group ${selectedCollectionId === col.collection_id ? 'bg-primary/5 border-primary/50' : 'bg-surface-container-lowest border-outline-variant/10 hover:border-outline-variant/30'}`}
              >
                <div className="flex justify-between items-start mb-3">
                  <div className={`p-1.5 rounded bg-surface-container-high group-hover:bg-surface-bright transition-colors`}>
                    <span className="material-symbols-outlined text-lg text-primary">database</span>
                  </div>
                  <span className="font-mono text-[10px] text-secondary font-bold bg-secondary/10 px-2 py-0.5 rounded">
                    {col.count} ITEMS
                  </span>
                </div>
                <h4 className="font-mono text-[11px] font-bold text-on-surface mb-1 truncate" title={col.collection_id}>
                  {col.collection_id}
                </h4>
                <div className="space-y-1.5 opacity-70 group-hover:opacity-100 transition-opacity">
                   <div className="flex items-center gap-2 font-mono text-[9px]">
                    <span className="material-symbols-outlined text-[10px]">search</span>
                    <span className="truncate">{col.query || 'NO_QUERY'}</span>
                  </div>
                  <div className="flex items-center gap-2 font-mono text-[9px]">
                    <span className="material-symbols-outlined text-[10px]">calendar_today</span>
                    <span>{new Date(col.collected_at_utc).toLocaleString()}</span>
                  </div>
                  <div className="flex items-center gap-2 font-mono text-[9px]">
                    <span className="material-symbols-outlined text-[10px]">source</span>
                    <span className="uppercase text-primary">{col.source}</span>
                  </div>
                </div>
                {selectedCollectionId === col.collection_id && (
                  <div className="mt-4 pt-3 border-t border-primary/20 flex justify-end">
                    <span className="font-headline text-[9px] font-bold text-primary uppercase flex items-center gap-1">
                      SELECTED <span className="material-symbols-outlined text-xs">check</span>
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* CSV Preview Modal (Conditional) */}
        {csvPreviewRows.length > 0 && (
          <section className="bg-surface-container-low border border-outline-variant/10 p-5 space-y-4 animate-in fade-in slide-in-from-bottom-4">
             <div className="flex items-center justify-between border-b border-outline-variant/10 pb-3">
                <h2 className="font-headline text-xs font-bold uppercase tracking-widest text-on-surface">Parsed Records Preview</h2>
                <div className="flex gap-4 font-mono text-[10px]">
                  <span className="text-secondary bg-secondary/10 px-2 py-0.5 rounded">VALID: {csvRows.length}</span>
                  <span className="text-tertiary bg-tertiary/10 px-2 py-0.5 rounded">FILTERED: {invalidCsvCount}</span>
                </div>
             </div>
             <div className="overflow-x-auto">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="text-left font-mono text-[9px] text-on-surface-variant uppercase border-b border-outline-variant/20">
                      <th className="pb-3 font-normal">Buffer_ID</th>
                      <th className="pb-3 font-normal">Content_Stream</th>
                      <th className="pb-3 font-normal">Source_Handle</th>
                      <th className="pb-3 font-normal">Timestamp_ISO</th>
                      <th className="pb-3 font-normal text-right">Integrity</th>
                    </tr>
                  </thead>
                  <tbody className="font-mono text-[10px]">
                    {csvPreviewRows.slice(0, 10).map((row, idx) => (
                      <tr key={idx} className="border-b border-outline-variant/5 hover:bg-surface-container-highest transition-colors">
                        <td className="py-3 text-outline-variant/50">#{idx + 1}</td>
                        <td className="py-3 max-w-[500px] truncate pr-8">{row.text || <span className="text-tertiary font-bold italic">[URL_ONLY_STREAM]</span>}</td>
                        <td className="py-3 text-secondary truncate max-w-[150px]">{row.author || 'ANONYMOUS'}</td>
                        <td className="py-3 text-on-surface-variant">{row.created_at || 'NO_DATE'}</td>
                        <td className={`py-3 text-right font-bold ${row.isValid ? 'text-secondary' : 'text-tertiary animate-pulse'}`}>
                          {row.isValid ? 'OK' : 'ERR:MISSING_DATA'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
             </div>
             <p className="font-mono text-[9px] text-outline-variant/50 italic text-right">* Previewing first 10 records. {csvPreviewRows.length} total parsed.</p>
          </section>
        )}

        <section className="bg-surface-container-low border border-outline-variant/10 p-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-headline text-xs font-bold uppercase tracking-widest">Global Provider Status</h2>
            <div className="flex items-center gap-4 font-mono text-[9px]">
               <div className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 bg-secondary rounded-full"></span> NOMINAL</div>
               <div className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 bg-tertiary rounded-full"></span> OFFLINE</div>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="text-left font-mono text-[9px] text-on-surface-variant uppercase border-b border-outline-variant/20">
                  <th className="pb-2 font-normal">Source_Node</th>
                  <th className="pb-2 font-normal text-right">Region</th>
                  <th className="pb-2 font-normal text-right">Vector_Status</th>
                  <th className="pb-2 font-normal text-right">Ingestion_Rate</th>
                  <th className="pb-2 font-normal text-right">Error_Delta</th>
                </tr>
              </thead>
              <tbody className="font-mono text-[10px]">
                {sourceRows.map((row) => (
                  <tr key={row.source} className="border-b border-outline-variant/5 hover:bg-surface-container-high transition-colors group">
                    <td className="py-4 text-primary font-bold">{row.source}</td>
                    <td className="py-4 text-right text-on-surface-variant">{row.region}</td>
                    <td className={`py-4 text-right font-mono font-bold ${row.status === 'ONLINE' ? 'text-secondary' : 'text-tertiary'}`}>
                      {row.status === 'ONLINE' ? 'ACTIVE_SCAN' : 'AUTH_FAILED'}
                    </td>
                    <td className="py-4 text-right font-mono">{row.recordsPerMin} R/min</td>
                    <td className="py-4 text-right font-mono text-outline-variant/50 group-hover:text-on-surface transition-colors">{row.failureRate}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Scraping;
