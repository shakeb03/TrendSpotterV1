// File path: frontend/src/App.tsx
import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';
import HomePage from './pages/HomePage';
import ExplorePage from './pages/ExplorePage';
import ExploreMapPage from './pages/ExploreMapPage';
import ContentDetailsPage from './pages/ContentDetailsPage';
import EventsPage from './pages/EventsPage';
import NeighborhoodPage from './pages/NeighborhoodPage';
import ProfilePage from './pages/ProfilePage';
import SavedItemsPage from './pages/SavedItemsPage';
import NotFoundPage from './pages/NotFoundPage';
import AdminDashboardPage from './pages/AdminDashboardPage';
import { UserProvider } from './context/UserContext';
import SearchWrapper from './components/search/SearchWrapper';
import RecommendationEngineVisualizer from './components/recommendations/RecommendationEngineVisualizer';
import './App.css';

import { Analytics } from '@vercel/analytics/react';

// ScrollToTop component to reset scroll position when navigating
function ScrollToTop() {
  const { pathname } = useLocation();
  
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);
  
  return null;
}

function App() {
  return (
    <UserProvider>
      <Router>
        <ScrollToTop />
        <div className="flex flex-col min-h-screen">
          <Analytics />
          <Navbar />
          <main className="flex-grow container mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/explore" element={<ExplorePage />} />
              <Route path="/explore/map" element={<ExploreMapPage />} />
              <Route path="/content/:id" element={<ContentDetailsPage />} />
              <Route path="/events" element={<EventsPage />} />
              <Route path="/neighborhood/:name" element={<NeighborhoodPage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/saved" element={<SavedItemsPage />} />
              <Route path="/search" element={<SearchWrapper />} />
              {/* <Route path="/engine-demo" element={<RecommendationEngineVisualizer />} /> */}
              {/* <Route path="/admin" element={<AdminDashboardPage />} /> */}
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </UserProvider>
  );
}

export default App;