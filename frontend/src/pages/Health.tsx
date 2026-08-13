import React, { useEffect, useState, useRef } from 'react';
import { sentimentApi } from '../services/sentimentApi';
import { SystemHealth } from '../types/sentiment';

const Health: React.FC = () => {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [command, setCommand] = useState('');
  const logEndRef = useRef<HTMLDivElement>(null);

  const fetchDiagnostics = async () => {
    try {
      const [healthData, logData] = await Promise.all([
        sentimentApi.checkSystemHealth(),
        sentimentApi.getSystemLogs(100)
      ]);
      setHealth(healthData);
      setLogs(logData);
    } catch (err) {
      console.error("Failed to fetch diagnostics", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDiagnostics();
    const interval = setInterval(fetchDiagnostics, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const handleCommand = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!command.trim()) return;
    
    await sentimentApi.logSystemEvent('INFO', `Manual Command Executed: ${command}`);
    setCommand('');
    fetchDiagnostics();
  };

  return (
    <>
      <div className="p-6 space-y-6">
        <div className="flex items-end justify-between border-b border-outline-variant/10 pb-4">
          <div>
            <h1 className="text-4xl font-headline font-bold tracking-tight text-on-surface uppercase">System Diagnostics</h1>
            <p className="text-on-surface-variant font-mono text-xs mt-2">HEALTH_MONITOR // LOG_STREAM</p>
          </div>
          <button 
            onClick={() => { setLoading(true); fetchDiagnostics(); }}
            disabled={loading}
            className="bg-surface-container-high hover:bg-surface-bright text-on-surface text-[10px] font-headline uppercase font-bold px-4 py-2 flex items-center gap-2 border-b-2 border-primary transition-all active:translate-y-0.5"
          >
            <span className="material-symbols-outlined text-sm">refresh</span>
            {loading ? 'Refreshing...' : 'Refresh Stack'}
          </button>
        </div>

        <section className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-surface-container-low border border-outline-variant/10 p-4">
            <p className="font-mono text-[10px] uppercase text-on-surface-variant">CPU Load</p>
            <p className="text-3xl font-headline font-bold text-secondary mt-2">{health?.resources.cpu_usage || '--'}</p>
          </div>
          <div className="bg-surface-container-low border border-outline-variant/10 p-4">
            <p className="font-mono text-[10px] uppercase text-on-surface-variant">Memory Usage</p>
            <p className="text-3xl font-headline font-bold text-primary mt-2">{health?.resources.memory_usage || '--'}</p>
          </div>
          <div className="bg-surface-container-low border border-outline-variant/10 p-4">
            <p className="font-mono text-[10px] uppercase text-on-surface-variant">Disk Capacity</p>
            <p className="text-3xl font-headline font-bold text-on-surface mt-2">{health?.resources.disk_usage || '--'}</p>
          </div>
          <div className="bg-surface-container-low border border-outline-variant/10 p-4">
            <p className="font-mono text-[10px] uppercase text-on-surface-variant">System Status</p>
            <p className={`text-3xl font-headline font-bold mt-2 ${health?.status === 'healthy' ? 'text-secondary' : 'text-error'}`}>
              {health?.status.toUpperCase() || 'OFFLINE'}
            </p>
          </div>
        </section>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 bg-surface-container-low border border-outline-variant/10 p-4 h-fit">
            <h2 className="font-headline text-xs font-bold uppercase tracking-widest mb-4">Service Matrix</h2>
            <div className="space-y-3">
              {health?.services.map((service) => (
                <div key={service.name} className="flex items-center justify-between p-2 border-b border-outline-variant/5">
                  <span className="font-mono text-[10px] text-primary">{service.name}</span>
                  <div className="flex items-center gap-4">
                    <span className="font-mono text-[9px] text-on-surface-variant">{service.latency}</span>
                    <span className={`px-1.5 py-0.5 font-mono text-[9px] ${service.status === 'PASS' ? 'bg-secondary/10 text-secondary' : 'bg-error/10 text-error'}`}>
                      {service.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-8 pt-4 border-t border-outline-variant/10">
              <h2 className="font-headline text-xs font-bold uppercase tracking-widest mb-4">Host Environment</h2>
              <div className="space-y-2 font-mono text-[10px]">
                <div className="flex justify-between">
                  <span className="text-on-surface-variant">OS:</span>
                  <span className="text-on-surface">{health?.os.system} {health?.os.machine}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-on-surface-variant">KERNEL:</span>
                  <span className="text-on-surface">{health?.os.release}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="lg:col-span-2 bg-black border border-outline-variant/20 flex h-[calc(100vh-8.5rem)] min-h-[500px] flex-col overflow-hidden">
            <div className="bg-surface-container-high px-4 py-2 border-b border-outline-variant/20 flex justify-between items-center">
              <div className="flex items-center gap-3">
                <div className="flex gap-1.5">
                  <div className="w-2 h-2 rounded-full bg-error animate-pulse"></div>
                  <div className="w-2 h-2 rounded-full bg-primary"></div>
                  <div className="w-2 h-2 rounded-full bg-secondary"></div>
                </div>
                <span className="text-[10px] font-mono text-on-surface-variant tracking-wider uppercase">Live System Logs</span>
              </div>
              <div className="flex gap-4">
                <span className="text-[9px] font-mono text-secondary uppercase animate-pulse">STREAMING</span>
                <span className="text-[9px] font-mono text-on-surface-variant uppercase">FILTER: ALL</span>
              </div>
            </div>
            
            <div className="min-h-0 flex-1 overflow-y-auto p-4 font-mono text-[11px] leading-relaxed bg-surface-container-lowest space-y-1 custom-scrollbar">
              {logs.length > 0 ? (
                logs.map((log, idx) => {
                  return (
                    <pre key={idx} className="text-on-surface-variant whitespace-pre-wrap break-all">
                      {log}
                    </pre>
                  );
                })
              ) : (
                <p className="text-on-surface-variant/30 italic">Waiting for log stream...</p>
              )}
              <div ref={logEndRef} />
            </div>

            <form onSubmit={handleCommand} className="bg-surface-container-high px-4 py-1.5 flex items-center border-t border-outline-variant/20">
              <span className="text-primary font-mono text-[10px] mr-2">root@sentiment:~$</span>
              <input
                type="text"
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                placeholder="execute diagnostic command..."
                className="bg-transparent border-none focus:ring-0 text-[10px] font-mono w-full p-0 text-on-surface placeholder-on-surface-variant/40"
              />
            </form>
          </div>
        </div>
      </div>
    </>
  );
};

export default Health;
