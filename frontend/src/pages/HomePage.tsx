import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import { api } from '../services/api';
import RecommendationSection from '../components/recommendations/RecommendationSection';

// Toronto neighborhoods for quick navigation
const FEATURED_NEIGHBORHOODS = [
  { name: 'Downtown Core', image: 'https://images.unsplash.com/photo-1514924013411-cbf25faa35bb' },
  { name: 'Distillery District', image: 'https://images.unsplash.com/photo-1569880153113-76e33fc52d5f' },
  { name: 'Kensington Market', image: 'https://images.unsplash.com/photo-1596395464941-de917238027a' },
  { name: 'Queen West', image: 'https://images.unsplash.com/photo-1596395463910-4ab618e3c4e4' }
];

const HomePage: React.FC = () => {
  const { user } = useUser();
  const [currentSeason, setCurrentSeason] = useState<string>('');
  
  useEffect(() => {
    // Determine current season
    setCurrentSeason(api.getCurrentSeason());
  }, []);
  
  return (
    <div className="flex flex-col space-y-8">
      {/* Hero section */}
      <section className="relative rounded-xl overflow-hidden bg-gradient-to-r from-primary-600 to-primary-800 text-white mb-8">
        <div className="absolute inset-0 opacity-20">
          <img 
            src="https://images.unsplash.com/photo-1514924013411-cbf25faa35bb" 
            alt="Toronto Skyline"
            className="w-full h-full object-cover"
          />
        </div>
        
        <div className="relative px-6 py-12 md:py-16 md:px-12 max-w-4xl">
          <h1 className="text-3xl md:text-4xl font-bold mb-4">
            Discover Toronto's Hidden Gems
          </h1>
          <p className="text-lg md:text-xl opacity-90 mb-6 max-w-2xl">
            Personalized recommendations for events, places, and experiences in Toronto
            tailored to your interests and preferred neighborhoods.
          </p>
          
          <div className="flex flex-wrap gap-3">
            <Link to="/explore" className="btn-primary bg-white text-primary-600 hover:bg-gray-100">
              Explore Toronto
            </Link>
            
            {!user && (
              <Link to="/profile" className="btn-secondary border-white text-white hover:bg-white/20">
                Sign In
              </Link>
            )}
          </div>
        </div>
      </section>
      
      {/* Featured Neighborhoods */}
      <section className="my-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Popular Neighborhoods</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {FEATURED_NEIGHBORHOODS.map((neighborhood) => (
            <Link 
              to={`/neighborhood/${encodeURIComponent(neighborhood.name)}`}
              key={neighborhood.name}
              className="relative rounded-xl overflow-hidden group"
            >
              <div className="aspect-w-16 aspect-h-9 bg-gray-200">
                <img 
                  src={neighborhood.image}
                  alt={neighborhood.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent"></div>
                <div className="absolute bottom-0 left-0 p-4">
                  <h3 className="text-white font-semibold text-lg">{neighborhood.name}</h3>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>
      
      {/* Personalized Recommendations (if logged in) */}
      {user && (
        <RecommendationSection 
          title="For You"
          subtitle="Personalized recommendations based on your interests"
          fetchFn={() => api.getUserRecommendations(user.id, 12, 'hybrid')}
          queryKey={['recommendations', 'forYou', user.id]}
          emptyMessage="Login to see personalized recommendations"
        />
      )}
      
      {/* Trending Events */}
      <RecommendationSection 
        title={`${currentSeason.charAt(0).toUpperCase() + currentSeason.slice(1)} Events in Toronto`}
        subtitle="Popular events happening now in the city"
        fetchFn={() => api.getPopularContent(8, 'event')}
        queryKey={['recommendations', 'events', currentSeason]}
        emptyMessage="No current events found"
      />
      
      {/* Popular Content */}
      <RecommendationSection 
        title="Popular in Toronto"
        subtitle="Trending content across the city"
        fetchFn={() => api.getPopularContent(12)}
        queryKey={['recommendations', 'popular']}
      />
      
      {/* Neighborhood-specific section */}
      {user && user.neighborhoodPreferences && user.neighborhoodPreferences.length > 0 && (
        <RecommendationSection 
          title={`Trending in ${user.neighborhoodPreferences[0]}`}
          subtitle={`Discover what's popular in your favorite neighborhood`}
          fetchFn={() => api.getLocationRecommendations(user.neighborhoodPreferences[0], 8)}
          queryKey={['recommendations', 'neighborhood', user.neighborhoodPreferences[0]]}
        />
      )}
    </div>
  );
};

export default HomePage;