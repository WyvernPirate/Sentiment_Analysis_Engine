import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import TopBar from './TopBar';
import Sidebar from './Sidebar';

const DashboardLayout: React.FC = () => {
  const location = useLocation();

  const isAnalytics = location.pathname === '/analytics';
  const isEntities = location.pathname === '/entities';
  const isScraping = location.pathname === '/scraping';
  const isHealth = location.pathname === '/health';
  const isLogs = location.pathname === '/logs';

  return (
    <div className="bg-surface text-on-surface min-h-screen flex">
      {/* Sidebar */}
      <Sidebar isAnalytics={isAnalytics} isEntities={isEntities} isScraping={isScraping} isHealth={isHealth} isLogs={isLogs} />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Top Bar */}
        <TopBar />

        {/* Page Content Outlet */}
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
