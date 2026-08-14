import React from 'react';
import { NavLink } from 'react-router-dom';

interface NavItem {
  to: string;
  icon: string;
  label: string;
}

// Each new page needs one entry here — NavLink computes its own active
// state from the current route, so (unlike the previous isAnalytics/
// isEntities/... boolean-prop pattern) DashboardLayout doesn't need to know
// the route list at all, and adding a page can't drift out of sync the way
// LexiconManager's missing sidebar offset once did.
const NAV_ITEMS: NavItem[] = [
  { to: '/analytics', icon: 'monitoring', label: 'Analytics' },
  { to: '/analyze', icon: 'search', label: 'Manual Analyzer' },
  { to: '/entities', icon: 'database', label: 'Political Entities' },
  { to: '/scraping', icon: 'rss_feed', label: 'Scraping Sources' },
  { to: '/health', icon: 'monitor_heart', label: 'System Diagnostics' },
  { to: '/lexicon', icon: 'dictionary', label: 'Lexicon Pool' },
];

const Sidebar: React.FC = () => {
  return (
    <aside className="fixed left-0 top-0 h-full w-64 border-r border-outline-variant/15 bg-surface-container-low flex flex-col py-8 z-40">
      {/* Header */}
      <div className="px-6 mb-10">
        <h2 className="text-primary font-black font-headline text-xs uppercase tracking-widest">COMMAND_CENTER</h2>
        <p className="text-on-surface-variant font-mono text-[10px] uppercase tracking-widest mt-1">BW_REGION_ALPHA</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1" aria-label="Main navigation">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 py-3 px-4 font-mono text-[11px] uppercase tracking-widest transition-all ${
                isActive
                  ? 'text-primary border-l-2 border-primary bg-surface-container-high'
                  : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high'
              }`
            }
          >
            <span className="material-symbols-outlined" aria-hidden="true">{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="mx-4 p-3 border border-outline-variant/20 bg-surface-container-high flex items-center gap-3">
        <div className="w-8 h-8 bg-surface-container-highest border border-primary/30 flex items-center justify-center">
          <span className="material-symbols-outlined text-primary text-sm" aria-hidden="true">person</span>
        </div>
        <div>
          <p className="font-mono text-[10px] text-on-surface">ANALYST_01</p>
          <p className="font-mono text-[8px] text-secondary">LEVEL_4_AUTH</p>
        </div>
      </div>

      {/* Footer intentionally left minimal (removed Settings/Logout) */}
      <div className="px-6 pt-6 border-t border-outline-variant/10" />
    </aside>
  );
};

export default Sidebar;
