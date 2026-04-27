import React from 'react';
import { Link } from 'react-router-dom';

interface SidebarProps {
  isAnalytics: boolean;
  isEntities: boolean;
  isScraping: boolean;
  isHealth: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({ isAnalytics, isEntities, isScraping, isHealth }) => {
  return (
    <aside className="fixed left-0 top-0 h-full w-64 border-r border-outline-variant/15 bg-surface-container-low flex flex-col py-8 z-40">
      {/* Header */}
      <div className="px-6 mb-10">
        <h2 className="text-primary font-black font-headline text-xs uppercase tracking-widest">COMMAND_CENTER</h2>
        <p className="text-on-surface-variant font-mono text-[10px] uppercase tracking-widest mt-1">BW_REGION_ALPHA</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1">
        <Link
          to="/analytics"
          className={`flex items-center gap-3 py-3 px-4 font-mono text-[11px] uppercase tracking-widest transition-all ${
            isAnalytics
              ? 'text-primary border-l-2 border-primary bg-surface-container-high'
              : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high'
          }`}
        >
          <span className="material-symbols-outlined">monitoring</span>
          <span>Analytics</span>
        </Link>

        <Link
          to="/entities"
          className={`flex items-center gap-3 py-3 px-4 font-mono text-[11px] uppercase tracking-widest transition-all ${
            isEntities
              ? 'text-primary border-l-2 border-primary bg-surface-container-high'
              : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high'
          }`}
        >
          <span className="material-symbols-outlined">database</span>
          <span>Political Entities</span>
        </Link>

        <Link
          to="/scraping"
          className={`flex items-center gap-3 py-3 px-4 font-mono text-[11px] uppercase tracking-widest transition-all ${
            isScraping
              ? 'text-primary border-l-2 border-primary bg-surface-container-high'
              : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high'
          }`}
        >
          <span className="material-symbols-outlined">rss_feed</span>
          <span>Scraping Sources</span>
        </Link>

        <Link
          to="/health"
          className={`flex items-center gap-3 py-3 px-4 font-mono text-[11px] uppercase tracking-widest transition-all ${
            isHealth
              ? 'text-primary border-l-2 border-primary bg-surface-container-high'
              : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high'
          }`}
        >
          <span className="material-symbols-outlined">monitor_heart</span>
          <span>Data Health</span>
        </Link>
      </nav>

      {/* Footer */}
      <div className="px-6 pt-6 border-t border-outline-variant/10">
        <button
          type="button"
          className="flex w-full items-center gap-3 py-2 text-on-surface-variant hover:text-on-surface transition-colors font-mono text-xs uppercase"
        >
          <span className="material-symbols-outlined text-sm">settings</span>
          <span>Settings</span>
        </button>
        <button
          type="button"
          className="flex w-full items-center gap-3 py-2 text-on-surface-variant hover:text-on-surface transition-colors font-mono text-xs uppercase"
        >
          <span className="material-symbols-outlined text-sm">logout</span>
          <span>Logout</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
