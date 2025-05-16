// File path: frontend/src/pages/HomePage.tsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import { api } from '../services/api';
import RecommendationSection from '../components/recommendations/RecommendationSection';
import SeasonalTheme from '../components/seasonal/SeasonalTheme';
import SearchBar from '../components/search/SearchBar';
import abTestingService, { TestName } from '../services/ab-testing';

// Toronto neighborhoods for quick navigation
const FEATURED_NEIGHBORHOODS = [
  { name: 'Downtown Core', image: 'https://upload.wikimedia.org/wikipedia/commons/c/c6/Toronto_-_ON_-_Toronto_Skyline2.jpg' },
  { name: 'Distillery District', image: 'https://media.cntraveler.com/photos/616480d36a69c761590b271a/16:9/w_2560,c_limit/Distillery%20District-57.jpg' },
  { name: 'Kensington Market', image: 'https://assets.simpleviewinc.com/simpleview/image/upload/c_fill,f_jpg,h_640,q_65,w_640/v1/clients/toronto/temp_7ccb30a5-9b57-4e2e-b1f5-85973634612d.jpg' },
  { name: 'Queen West', image: 'https://fr.spacingtoronto.ca/wp-content/uploads/2020/07/shopping-queen-street-13505540121.jpg' }
];

const HomePage: React.FC = () => {
  const { user } = useUser();
  const [currentSeason, setCurrentSeason] = useState<string>('');
  const [abTestVariant, setAbTestVariant] = useState<string | null>(null);
  
  useEffect(() => {
    // Determine current season
    setCurrentSeason(api.getCurrentSeason());
    
    // Get A/B test variant for homepage layout
    const variant = abTestingService.getVariant(TestName.HOMEPAGE_LAYOUT);
    setAbTestVariant(variant);
    
    // Track impression for A/B test
    if (variant) {
      abTestingService.trackImpression(TestName.HOMEPAGE_LAYOUT);
    }
  }, []);
  
  // Handle search from hero section
  const handleSearch = (searchData: any) => {
    const params = new URLSearchParams();
    if (searchData.query) params.append('q', searchData.query);
    if (searchData.category !== 'all') params.append('category', searchData.category);
    if (searchData.neighborhood !== 'All Neighborhoods') params.append('neighborhood', searchData.neighborhood);
    if (searchData.season !== 'all') params.append('season', searchData.season);
    
    window.location.href = `/explore?${params.toString()}`;
  };
  
  // Get content order based on A/B test variant
  const getOrderedSections = () => {
    if (abTestVariant === 'LocationFirst') {
      return (
        <>
          {/* Seasonal Theme */}
          <SeasonalTheme />
          
          {/* Featured Neighborhoods */}
          <section className="my-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Popular Neighborhoods</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {FEATURED_NEIGHBORHOODS.map((neighborhood) => (
                <Link 
                  to={`/neighborhood/${encodeURIComponent(neighborhood.name)}`}
                  key={neighborhood.name}
                  className="relative rounded-xl overflow-hidden group"
                  onClick={() => {
                    if (abTestVariant) {
                      abTestingService.trackConversion(TestName.HOMEPAGE_LAYOUT);
                    }
                  }}
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
          
          {/* Trending Events */}
          <RecommendationSection 
            title={`${currentSeason.charAt(0).toUpperCase() + currentSeason.slice(1)} Events in Toronto`}
            subtitle="Popular events happening now in the city"
            fetchFn={() => api.getPopularContent(8, 'event')}
            queryKey={['recommendations', 'events', currentSeason]}
            emptyMessage="No current events found"
          />
          
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
          
          {/* Popular Content */}
          <RecommendationSection 
            title="Popular in Toronto"
            subtitle="Trending content across the city"
            fetchFn={() => api.getPopularContent(12)}
            queryKey={['recommendations', 'popular']}
          />
        </>
      );
    } else if (abTestVariant === 'PersonalizedFirst') {
      return (
        <>
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
          
          {/* Seasonal Theme */}
          <SeasonalTheme />
          
          {/* Trending Events */}
          <RecommendationSection 
            title={`${currentSeason.charAt(0).toUpperCase() + currentSeason.slice(1)} Events in Toronto`}
            subtitle="Popular events happening now in the city"
            fetchFn={() => api.getPopularContent(8, 'event')}
            queryKey={['recommendations', 'events', currentSeason]}
            emptyMessage="No current events found"
          />
          
          {/* Featured Neighborhoods */}
          <section className="my-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Popular Neighborhoods</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {FEATURED_NEIGHBORHOODS.map((neighborhood) => (
                <Link 
                  to={`/neighborhood/${encodeURIComponent(neighborhood.name)}`}
                  key={neighborhood.name}
                  className="relative rounded-xl overflow-hidden group"
                  onClick={() => {
                    if (abTestVariant) {
                      abTestingService.trackConversion(TestName.HOMEPAGE_LAYOUT);
                    }
                  }}
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
          
          {/* Popular Content */}
          <RecommendationSection 
            title="Popular in Toronto"
            subtitle="Trending content across the city"
            fetchFn={() => api.getPopularContent(12)}
            queryKey={['recommendations', 'popular']}
          />
        </>
      );
    } else {
      // Default layout (Standard variant)
      return (
        <>
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
        </>
      );
    }
  };
  
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
          
          <div className="max-w-2xl mb-6">
            <SearchBar 
              variant="hero" 
              onSearch={handleSearch}
            />
          </div>
          
          <div className="flex flex-wrap gap-3">
            <Link to="/explore" className="btn-primary bg-white text-primary-600 hover:bg-gray-100">
              Explore Toronto
            </Link>
            
            <Link to="/explore/map" className="btn-secondary border-white text-white hover:bg-white/20">
              View Map
            </Link>
            
            {!user && (
              <Link to="/profile" className="btn-secondary border-white text-white hover:bg-white/20">
                Sign In
              </Link>
            )}
          </div>
        </div>
      </section>
      
      {/* Seasonal Theme - Only shown outside the A/B test or for Standard variant */}
      {(!abTestVariant || abTestVariant === 'Standard') && <SeasonalTheme />}
      
      {/* Featured Neighborhoods - Only shown outside A/B test or for Standard variant*/}
      {(!abTestVariant || abTestVariant === 'Standard') && (
        <section className="my-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Popular Neighborhoods</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {FEATURED_NEIGHBORHOODS.map((neighborhood) => (
              <Link 
                to={`/neighborhood/${encodeURIComponent(neighborhood.name)}`}
                key={neighborhood.name}
                className="relative rounded-xl overflow-hidden group"
                onClick={() => {
                  if (abTestVariant) {
                    abTestingService.trackConversion(TestName.HOMEPAGE_LAYOUT);
                  }
                }}
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
      )}
      
      {/* Dynamic content based on A/B test variant */}
      {abTestVariant && getOrderedSections()}
      
      {/* Bottom CTA */}
      {/* <div className="bg-gray-50 rounded-xl p-6 text-center">
        <h2 className="text-xl font-bold mb-2">Want to see how our recommendation engine works?</h2>
        <p className="text-gray-600 mb-4">Check out our technical visualization of the Toronto Trendspotter engine</p>
        <Link to="/engine-demo" className="btn-primary">
          View Recommendation Engine
        </Link>
      </div> */}
    </div>
  );
};

export default HomePage;