import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import DashboardLayout from './components/Layout/DashboardLayout';
import Analytics from './pages/Analytics';
import Entities from './pages/Entities';
import Scraping from './pages/Scraping';
import Health from './pages/Health';
import LexiconManager from './pages/LexiconManager';
import ManualAnalyzer from './pages/ManualAnalyzer';

import { AnalyticsProvider } from './context/AnalyticsContext';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AnalyticsProvider>
        <BrowserRouter>
          <Routes>
            <Route element={<DashboardLayout />}>
              <Route path="/" element={<Navigate to="/analytics" replace />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/analyze" element={<ManualAnalyzer />} />
              <Route path="/entities" element={<Entities />} />
              <Route path="/scraping" element={<Scraping />} />
              <Route path="/health" element={<Health />} />
              <Route path="/lexicon" element={<LexiconManager />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AnalyticsProvider>
    </QueryClientProvider>
  );
}

export default App;
