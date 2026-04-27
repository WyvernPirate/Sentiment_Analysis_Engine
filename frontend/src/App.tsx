import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import DashboardLayout from './components/Layout/DashboardLayout';
import Analytics from './pages/Analytics';
import Entities from './pages/Entities';
import Scraping from './pages/Scraping';
import Health from './pages/Health';
import Logs from './pages/Logs';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<DashboardLayout />}>
          <Route path="/" element={<Navigate to="/analytics" replace />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/entities" element={<Entities />} />
          <Route path="/scraping" element={<Scraping />} />
          <Route path="/health" element={<Health />} />
          <Route path="/logs" element={<Logs />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;