import React from 'react';
import { Outlet } from 'react-router-dom';
import TopBar from './TopBar';
import Sidebar from './Sidebar';

const DashboardLayout: React.FC = () => {
  return (
    <div className="bg-surface text-on-surface min-h-screen flex">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Top Bar */}
        <TopBar />

        {/* Page Content Outlet — the ml-64/pt-14 offset accounts for the fixed
            Sidebar/TopBar and lives here once, so individual pages can't
            forget it (this was previously duplicated per-page and LexiconManager
            had drifted out of sync, rendering behind the sidebar). */}
        <main className="flex-1 overflow-y-auto ml-64 pt-14 min-h-screen bg-surface">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
