import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useAnalytics } from '../../context/AnalyticsContext';

const TopBar: React.FC = () => {
  const location = useLocation();
  const { startDate, setStartDate, endDate, setEndDate } = useAnalytics();
  const [showDatePicker, setShowDatePicker] = useState(false);

  return (
    <header className="fixed top-0 left-64 right-0 z-50 border-b border-outline-variant/15 bg-surface flex justify-between items-center px-6 h-14">
      <div className="flex items-center gap-8">
        <span className="text-lg font-bold text-primary tracking-widest font-headline uppercase">SENTIMENT ENGINE // BW</span>
        {/* Navigation moved to Sidebar; header keeps title/search/actions only */}
      </div>

      <div className="flex items-center gap-4">
        {/* Search box */}
        <div className="hidden md:flex items-center bg-surface-container-lowest border border-outline-variant/20 px-3 py-1.5">
          <span className="material-symbols-outlined text-sm text-on-surface-variant mr-2">search</span>
          <input
            type="text"
            placeholder="SYS_QUERY_EXEC..."
            className="bg-transparent border-0 text-xs font-mono text-on-surface placeholder-on-surface-variant/40 focus:ring-0 w-48"
          />
        </div>

        {/* Icon buttons */}
        <div className="flex gap-2 relative">
          <button 
            className={`p-2 transition-colors relative group ${showDatePicker ? 'text-primary bg-surface-container-high' : 'text-on-surface-variant hover:text-primary hover:bg-surface-container-high'}`}
            onClick={() => setShowDatePicker(!showDatePicker)}
          >
            <span className="material-symbols-outlined">calendar_today</span>
            {(startDate || endDate) && <span className="absolute top-1 right-1 w-1.5 h-1.5 bg-primary rounded-full"></span>}
            
            {/* Tooltip */}
            <span className="absolute -bottom-10 left-1/2 -translate-x-1/2 bg-surface-container-highest text-[8px] font-mono py-1 px-2 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-50">
              DATE_RANGE_FILTER
            </span>
          </button>

          {showDatePicker && (
            <div className="absolute top-full right-0 mt-2 w-64 bg-surface-container-low border border-outline-variant/30 shadow-xl p-4 z-[100] animate-in fade-in slide-in-from-top-1">
              <h3 className="font-mono text-[9px] uppercase text-on-surface-variant mb-3 flex justify-between items-center">
                Select Range
                <button onClick={() => { setStartDate(''); setEndDate(''); }} className="text-tertiary hover:underline">Clear</button>
              </h3>
              
              {/* Preset buttons */}
              <div className="grid grid-cols-1 gap-1 mb-4">
                {[
                  { label: 'LAST_14_DAYS', days: 14 },
                  { label: 'LAST_MONTH', days: 30 },
                  { label: 'LAST_3_MONTHS', days: 90 },
                ].map((preset) => (
                  <button
                    key={preset.label}
                    onClick={() => {
                      const end = new Date();
                      const start = new Date();
                      start.setDate(end.getDate() - preset.days);
                      setStartDate(start.toISOString().split('T')[0]);
                      setEndDate(end.toISOString().split('T')[0]);
                    }}
                    className="text-[8px] font-mono text-left px-2 py-1.5 bg-surface-container-highest/50 hover:bg-primary/20 hover:text-primary transition-colors border border-outline-variant/10 uppercase"
                  >
                    {preset.label}
                  </button>
                ))}
              </div>

              <div className="space-y-3">
                <div className="space-y-1">
                  <label className="font-mono text-[8px] text-on-surface-variant uppercase">Start Date</label>
                  <input 
                    type="date" 
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full bg-surface-container-lowest border border-outline-variant/20 text-[10px] font-mono p-1.5 focus:ring-1 focus:ring-primary/40 outline-none" 
                  />
                </div>
                <div className="space-y-1">
                  <label className="font-mono text-[8px] text-on-surface-variant uppercase">End Date</label>
                  <input 
                    type="date" 
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="w-full bg-surface-container-lowest border border-outline-variant/20 text-[10px] font-mono p-1.5 focus:ring-1 focus:ring-primary/40 outline-none" 
                  />
                </div>
              </div>
              <button 
                onClick={() => setShowDatePicker(false)}
                className="w-full mt-4 bg-primary text-on-primary font-headline text-[9px] uppercase py-2 hover:bg-primary/90"
              >
                Apply Filter
              </button>
            </div>
          )}

          <button className="p-2 text-on-surface-variant hover:text-primary hover:bg-surface-container-high transition-colors group relative">
            <span className="material-symbols-outlined">tune</span>
            <span className="absolute -bottom-10 left-1/2 -translate-x-1/2 bg-surface-container-highest text-[8px] font-mono py-1 px-2 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-50">
              ANALYSIS_PARAMETERS
            </span>
          </button>
          
          <button className="p-2 text-primary hover:bg-surface-container-high transition-colors group relative">
            <span className="material-symbols-outlined">sensors</span>
            <span className="absolute -bottom-10 left-1/2 -translate-x-1/2 bg-surface-container-highest text-[8px] font-mono py-1 px-2 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-50">
              LIVE_DATA_STREAM: ACTIVE
            </span>
          </button>

          <button className="p-2 text-primary hover:bg-surface-container-high transition-colors group relative">
            <span className="material-symbols-outlined animate-pulse">speed</span>
            <span className="absolute -bottom-10 left-1/2 -translate-x-1/2 bg-surface-container-highest text-[8px] font-mono py-1 px-2 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-50">
              PERF_LATENCY: 42ms
            </span>
          </button>

          <button className="p-2 text-primary hover:bg-surface-container-high transition-colors relative group">
            <span className="material-symbols-outlined">database</span>
            <span className="absolute right-1 top-1 w-1.5 h-1.5 bg-tertiary"></span>
            <span className="absolute -bottom-10 left-1/2 -translate-x-1/2 bg-surface-container-highest text-[8px] font-mono py-1 px-2 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-50">
              STORAGE_STATUS: 84%_FULL
            </span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default TopBar;
