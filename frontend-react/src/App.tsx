import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { Toaster } from './components/ui/sonner';

// Lazy load pages
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const UserAnalysis = React.lazy(() => import('./pages/UserAnalysis'));
const Insights = React.lazy(() => import('./pages/Insights'));
const Simulation = React.lazy(() => import('./pages/Simulation'));
const BatchUpload = React.lazy(() => import('./pages/BatchUpload'));

const LoadingFallback = () => (
  <div className="h-full w-full flex items-center justify-center flex-col animate-in fade-in duration-500">
    <div className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin"></div>
    <p className="mt-4 text-sm text-muted-foreground font-medium">Loading view...</p>
  </div>
);

function App() {
  return (
    <Router>
      <React.Suspense fallback={<LoadingFallback />}>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="user-analysis" element={<UserAnalysis />} />
            <Route path="insights" element={<Insights />} />
            <Route path="simulation" element={<Simulation />} />
            <Route path="batch" element={<BatchUpload />} />
          </Route>
        </Routes>
      </React.Suspense>
      <Toaster position="top-center" />
    </Router>
  );
}

export default App;
