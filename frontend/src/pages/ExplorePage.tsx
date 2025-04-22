import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { api } from '../services/api';
import ContentGrid from '../components/content/ContentGrid';
import { useUser } from '../context/UserContext';
import { Link, useSearchParams } from 'react-router-dom';
import SearchBar from '../components/search/SearchBar';

const ExplorePage: React.FC = () => {
  const { user } = useUser();
  const [searchParams, setSearchParams] = useSearchParams();
  
  // Extract search parameters
  const searchQuery = searchParams.get('q') || '';
  const categoryParam = searchParams.get('category') || 'all';
  const neighborhoodParam = searchParams.get('neighborhood') || 'All Neighborhoods';
  const seasonParam = searchParams.get('season') || 'all';
  
  const [activeCategory, setActiveCategory] = useState(categoryParam);
  const [activeNeighborhood, setActiveNeighborhood] = useState(neighborhoodParam);
  const [searchTerm, setSearchTerm] = useState(searchQuery);
  const [activeSeason, setActiveSeason] = useState(seasonParam);
  
  // Update URL when filters change
  useEffect(() => {
    const params = new URLSearchParams();
    if (searchTerm) params.append('q', searchTerm);
    if (activeCategory !== 'all') params.append('category', activeCategory);
    if (activeNeighborhood !== 'All Neighborhoods') params.append('neighborhood', activeNeighborhood);
    if (activeSeason !== 'all') params.append('season', activeSeason);
    
    setSearchParams(params);
  }, [activeCategory, activeNeighborhood, searchTerm, activeSeason, setSearchParams]);
  
  // Categories for filtering
  const CATEGORIES = [
    'all', 'food', 'art', 'outdoor', 'event', 
    'shopping', 'nightlife', 'attraction'
  ];

  // Toronto neighborhoods for filtering
  const NEIGHBORHOODS = [
    'All Neighborhoods',
    'Downtown Core',
    'Distillery District',
    'Kensington Market',
    'Queen West',
    'Yorkville',
    'The Beaches',
    'Liberty Village',
    'Little Italy',
    'Chinatown'
  ];
  
  // Seasons for filtering
  const SEASONS = [
    { value: 'all', label: 'All Seasons' },
    { value: 'spring', label: 'Spring' },
    { value: 'summer', label: 'Summer' },
    { value: 'fall', label: 'Fall' },
    { value: 'winter', label: 'Winter' }
  ];
  
  // Get current season
  const getCurrentSeason = () => {
    const month = new Date().getMonth();
    if (month >= 2 && month <= 4) return 'spring';
    if (month >= 5 && month <= 7) return 'summer';
    if (month >= 8 && month <= 10) return 'fall';
    return 'winter';
  };
  
  // Fetch recommendations based on user (if logged in) or popular content
  const { data, isLoading, error } = useQuery(
    ['explore', user?.id, activeCategory, activeNeighborhood, searchTerm, activeSeason],
    async () => {
      let result;
      
      try {
        // Use search functionality if we have search parameters
        if (searchTerm || activeCategory !== 'all' || activeNeighborhood !== 'All Neighborhoods' || activeSeason !== 'all') {
          // Neighborhood-specific recommendations
          if (activeNeighborhood !== 'All Neighborhoods') {
            result = await api.getLocationRecommendations(activeNeighborhood, 50);
            console.log('Neighborhood recommendations:', result);
          } 
          // Category-specific recommendations
          else if (activeCategory !== 'all') {
            result = await api.getPopularContent(50, activeCategory);
            console.log('Category recommendations:', result);
          } 
          else {
            // General search
            result = await api.getPopularContent(50);
          }
        }
        // Personalized recommendations if user is logged in
        else if (user) {
          result = await api.getUserRecommendations(user.id, 50, 'hybrid');
          console.log('User recommendations:', result);
        } 
        // Popular content if no user is logged in
        else {
          result = await api.getPopularContent(50);
          console.log('Popular recommendations:', result);
        }
        
        return result.recommendations;
      } catch (err) {
        console.error('Error fetching recommendations:', err);
        return [];
      }
    },
    {
      // Refetch when these dependencies change
      enabled: true,
      refetchOnWindowFocus: false,
    }
  );
  
  // Filter content based on search query and active filters
  const filteredContent = React.useMemo(() => {
    if (!data) return [];
    
    return data.filter(item => {
      // Filter by search query
      const searchMatch = 
        searchTerm === '' || 
        item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (item.description && item.description.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (item.tags && item.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase())));
      
      // Filter by category
      const categoryMatch = 
        activeCategory === 'all' || 
        (item.categories && item.categories.some(cat => cat.toLowerCase() === activeCategory.toLowerCase()));
      
      // Filter by season
      const seasonMatch = 
        activeSeason === 'all' || 
        (item.tags && item.tags.some(tag => tag.toLowerCase() === activeSeason.toLowerCase()));
      
      return searchMatch && categoryMatch && seasonMatch;
    });
  }, [data, activeCategory, searchTerm, activeSeason]);
  
  const handleCategoryChange = (category: string) => {
    setActiveCategory(category);
  };
  
  const handleNeighborhoodChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setActiveNeighborhood(event.target.value);
  };
  
  const handleSearch = (searchData: any) => {
    setSearchTerm(searchData.query);
    setActiveCategory(searchData.category);
    setActiveNeighborhood(searchData.neighborhood);
    setActiveSeason(searchData.season);
  };

  const handleSeasonChange = (season: string) => {
    setActiveSeason(season);
  };

  return (
    <div>
      <>
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Explore Toronto</h1>
          <Link 
            to="/explore/map"
            className="btn-secondary flex items-center text-sm"
          >
            <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" 
              />
            </svg>
            View Map
          </Link>
        </div>
        <p className="text-gray-600 max-w-3xl">
          Discover the best events, places, and experiences Toronto has to offer. 
          Filter by category, search for specific interests, or browse by neighborhood.
        </p>
      </div>
  
        {/* Enhanced search bar */}
        <div className="my-6">
          <SearchBar 
            variant="default" 
            onSearch={handleSearch} 
            initialQuery={searchTerm}
          />
        </div>

        {/* Filters and search */}
        <div className="flex flex-col md:flex-row gap-4 items-start mb-8">
          {/* Category filters */}
          <div className="flex overflow-x-auto pb-2 md:pb-0 scrollbar-hide gap-2 flex-grow">
            {CATEGORIES.map(category => (
              <button
                key={category}
                onClick={() => handleCategoryChange(category)}
                className={`px-4 py-2 rounded-full text-sm whitespace-nowrap ${
                  activeCategory === category
                    ? 'bg-primary-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {category.charAt(0).toUpperCase() + category.slice(1)}
              </button>
            ))}
          </div>
  
          {/* Neighborhood filter */}
          <div className="w-full md:w-auto">
            <select
              className="input-field w-full md:w-60"
              value={activeNeighborhood}
              onChange={handleNeighborhoodChange}
            >
              {NEIGHBORHOODS.map(neighborhood => (
                <option key={neighborhood} value={neighborhood}>
                  {neighborhood}
                </option>
              ))}
            </select>
          </div>
          
          {/* Season filter */}
          <div className="w-full md:w-auto">
            <select
              className="input-field w-full md:w-40"
              value={activeSeason}
              onChange={(e) => handleSeasonChange(e.target.value)}
            >
              {SEASONS.map(season => (
                <option key={season.value} value={season.value}>
                  {season.label}
                </option>
              ))}
            </select>
          </div>
        </div>
  
        {/* Error state */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" 
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" 
                    clipRule="evenodd" 
                  />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">
                  Error loading content. Please try again later.
                </p>
              </div>
            </div>
          </div>
        )}
  
        {/* Display filter info */}
        <div className="flex justify-between items-center mb-4">
          <p className="text-gray-600 text-sm">
            {filteredContent.length === 0 && !isLoading 
              ? 'No results found' 
              : `Showing ${filteredContent.length} results`}
          </p>
  
          {/* Clear filters button */}
          {(activeCategory !== 'all' || activeNeighborhood !== 'All Neighborhoods' || searchTerm || activeSeason !== 'all') && (
            <button
              onClick={() => {
                setActiveCategory('all');
                setActiveNeighborhood('All Neighborhoods');
                setSearchTerm('');
                setActiveSeason('all');
              }}
              className="text-primary-500 text-sm hover:text-primary-700"
            >
              Clear filters
            </button>
          )}
        </div>
  
        {/* Content grid */}
        <ContentGrid 
          items={filteredContent} 
          isLoading={isLoading} 
          emptyMessage={
            searchTerm 
              ? "No results match your search"
              : "No content found for the selected filters"
          }
        />
      </>
    </div>
  );
};

export default ExplorePage;