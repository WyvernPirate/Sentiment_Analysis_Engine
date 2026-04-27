import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const TopBar: React.FC = () => {
  const location = useLocation();

  return (
    <header className="fixed top-0 left-64 right-0 z-50 border-b border-outline-variant/15 bg-surface flex justify-between items-center px-6 h-14">
      <div className="flex items-center gap-8">
        <span className="text-lg font-bold text-primary tracking-widest font-headline uppercase">SENTIMENT ENGINE // BW</span>
        <nav className="hidden md:flex items-center gap-4 h-full">
          <Link
            to="/analytics"
            className={`font-headline tracking-tight uppercase text-xs px-2 py-1 transition-colors ${
              location.pathname === '/analytics' ? 'text-primary border-b-2 border-primary' : 'text-on-surface-variant hover:bg-surface-container-high'
            }`}
          >
            Analytics
          </Link>
          <Link
            to="/entities"
            className={`font-headline tracking-tight uppercase text-xs px-2 py-1 transition-colors ${
              location.pathname === '/entities' ? 'text-primary border-b-2 border-primary' : 'text-on-surface-variant hover:bg-surface-container-high'
            }`}
          >
            Entities
          </Link>
          <Link
            to="/health"
            className={`font-headline tracking-tight uppercase text-xs px-2 py-1 transition-colors ${
              location.pathname === '/health' ? 'text-primary border-b-2 border-primary' : 'text-on-surface-variant hover:bg-surface-container-high'
            }`}
          >
            Health
          </Link>
        </nav>
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
          <button className="p-2 text-on-surface-variant hover:text-primary hover:bg-surface-container-high transition-colors">
            <span className="material-symbols-outlined">calendar_today</span>
          </button>
          <button className="p-2 text-on-surface-variant hover:text-primary hover:bg-surface-container-high transition-colors">
            <span className="material-symbols-outlined">tune</span>
          </button>
          <button className="p-2 text-primary hover:bg-surface-container-high transition-colors">
            <span className="material-symbols-outlined">sensors</span>
          </button>
          <button className="p-2 text-primary hover:bg-surface-container-high transition-colors">
            <span className="material-symbols-outlined">speed</span>
          </button>
          <button className="p-2 text-primary hover:bg-surface-container-high transition-colors relative">
            <span className="material-symbols-outlined">database</span>
            <span className="absolute right-1 top-1 w-1.5 h-1.5 bg-tertiary"></span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default TopBar;
