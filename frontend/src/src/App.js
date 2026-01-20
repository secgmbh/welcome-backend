import { useEffect, lazy, Suspense } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { HelmetProvider } from 'react-helmet-async';
import { initPWA } from './lib/pwa';
import { initPerformanceOptimizations } from './lib/performance';

// Lazy load pages for better performance
const HomePage = lazy(() => import('./pages/HomePage'));
const FeaturesPage = lazy(() => import('./pages/FeaturesPage'));
const PricingPage = lazy(() => import('./pages/PricingPage'));
const ResourcesPage = lazy(() => import('./pages/ResourcesPage'));
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const PropertyManagementPage = lazy(() => import('./pages/PropertyManagementPage'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const RegisterPage = lazy(() => import('./pages/RegisterPage'));

function App() {
  useEffect(() => {
    // Initialize PWA features
    initPWA().then(registration => {
      console.log('PWA initialized:', registration);
    }).catch(error => {
      console.error('PWA initialization failed:', error);
    });

    // Initialize performance optimizations
    initPerformanceOptimizations();
  }, []);

  return (
    <HelmetProvider>
      <div className="App">
        <BrowserRouter>
          <Suspense fallback={
            <div className="flex items-center justify-center min-h-screen bg-white dark:bg-slate-900">
              <div className="text-xl text-gray-600 dark:text-gray-300">Lädt...</div>
            </div>
          }>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/features" element={<FeaturesPage />} />
              <Route path="/pricing" element={<PricingPage />} />
              <Route path="/resources" element={<ResourcesPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/management" element={<PropertyManagementPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/demo" element={<LoginPage />} />
              <Route path="/integrations" element={<FeaturesPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/contact" element={<HomePage />} />
              <Route path="/about" element={<HomePage />} />
              <Route path="/impressum" element={<HomePage />} />
              <Route path="/datenschutz" element={<HomePage />} />
              <Route path="/agb" element={<HomePage />} />
            </Routes>
          </Suspense>
        </BrowserRouter>
      </div>
    </HelmetProvider>
  );
}

export default App;
