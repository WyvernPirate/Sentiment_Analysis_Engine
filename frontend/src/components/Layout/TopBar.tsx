import React from 'react';

const TopBar: React.FC = () => {
  return (
    <header className="fixed top-0 left-64 right-0 z-50 border-b border-outline-variant/15 bg-surface flex justify-between items-center px-6 h-14">
      <div className="flex items-center gap-4">
        <span className="text-lg font-bold text-primary tracking-widest font-headline uppercase">SENTIMENT ENGINE // BW</span>
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
        <div className="flex gap-2">
          <button className="p-2 text-primary hover:bg-surface-container-high transition-colors">
            <span className="material-symbols-outlined">sensors</span>
          </button>
          <button className="p-2 text-primary hover:bg-surface-container-high transition-colors">
            <span className="material-symbols-outlined">speed</span>
          </button>
          <button className="p-2 text-primary hover:bg-surface-container-high transition-colors">
            <span className="material-symbols-outlined">database</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default TopBar;
