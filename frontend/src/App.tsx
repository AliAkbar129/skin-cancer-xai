import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './Layout';
import { Dashboard } from './pages/Dashboard';
import { Analysis } from './pages/Analysis';

// Placeholder for other pages
const Placeholder = ({ title }: { title: string }) => (
  <div className="h-full flex items-center justify-center">
    <div className="text-center space-y-4">
      <h1 className="text-3xl font-bold text-gray-300">{title}</h1>
      <p className="text-gray-500">This module is part of the clinical roadmap.</p>
    </div>
  </div>
);

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="analysis" element={<Analysis />} />
          <Route path="patients" element={<Placeholder title="Patient Records" />} />
          <Route path="architecture" element={<Placeholder title="Model Architecture Visualization" />} />
          <Route path="settings" element={<Placeholder title="System Settings" />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
