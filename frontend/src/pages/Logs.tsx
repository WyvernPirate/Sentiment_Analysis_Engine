import React from 'react';

const Logs: React.FC = () => {
  const logLines = [
    '[2026-04-27 14:02:11] [INFO] Pipeline connection established to source: RSS_GOV_BW',
    '[2026-04-27 14:02:13] [INFO] Batch 0x9f4a processed: 42 entities extracted.',
    '[2026-04-27 14:02:45] [WARN] Memory threshold reached (82%). Triggering garbage_collection_v2.',
    '[2026-04-27 14:03:01] [ERR!] JSON_PARSE_ERROR at source: TWITTER_STREAM_ALPHA',
    '[2026-04-27 14:03:08] [INFO] Cache cleared. 1.4GB freed in 12ms.',
  ];

  return (
    <div className="ml-64 pt-14 min-h-screen bg-surface">
      <div className="p-6 space-y-6">
        <div className="flex items-end justify-between border-b border-outline-variant/10 pb-4">
          <div>
            <h1 className="text-4xl font-headline font-bold tracking-tight text-on-surface uppercase">System Logs</h1>
            <p className="text-on-surface-variant font-mono text-xs mt-2">LIVE_LOG_STREAM // TTY1</p>
          </div>
        </div>

        <section className="bg-black border border-outline-variant/20 flex flex-col">
          <div className="bg-surface-container-high px-4 py-2 border-b border-outline-variant/20 flex justify-between items-center">
            <span className="text-[10px] font-mono text-primary">LIVE_LOG_STREAM</span>
            <span className="text-[10px] font-mono text-secondary">RECORDING</span>
          </div>
          <div className="h-96 overflow-y-auto p-4 font-mono text-[11px] space-y-2 bg-surface-container-lowest">
            {logLines.map((line, idx) => (
              <p key={idx} className="text-on-surface-variant hover:text-on-surface transition-colors">{line}</p>
            ))}
          </div>
          <div className="bg-surface-container-high px-4 py-1.5 border-t border-outline-variant/20 flex items-center">
            <span className="text-primary font-mono text-[10px] mr-2">admin@sovereign:~$</span>
            <input
              type="text"
              placeholder="type command and press enter..."
              className="bg-transparent border-0 focus:ring-0 text-[10px] font-mono w-full p-0 text-on-surface placeholder-on-surface-variant/40"
            />
          </div>
        </section>
      </div>
    </div>
  );
};

export default Logs;
