import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { api, ContentItem } from '../services/api';
import ContentGrid from '../components/content/ContentGrid';
import { useUser } from '../context/UserContext';

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

const ExplorePage: React.FC = () => {
  const { user } = useUser();
  const [activeCategory, setActiveCategory] = useState('all');
  const [activeNeighborhood, setActiveNeighborhood] = useState('All Neighborhoods');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Fetch recommendations based on user (if logged in) or popular content
  const { data, isLoading, error } = useQuery(
    ['explore', user?.id, activeCategory, activeNeighborhood],
    async () => {
      let result;
      
      try {
        if (activeNeighborhood !== 'All Neighborhoods') {
          // Fetch neighborhood-specific recommendations
          result = await api.getLocationRecommendations(activeNeighborhood, 50);
          console.log('Neighborhood recommendations:', result);
        } else if (activeCategory !== 'all') {
          // Fetch category-specific recommendations
          result = await api.getPopularContent(50, activeCategory);
          console.log('Category recommendations:', result);
        } else if (user) {
          // Fetch personalized recommendations if user is logged in
          result = await api.getUserRecommendations(user.id, 50, 'hybrid');
          console.log('User recommendations:', result);
        } else {
          // Fetch popular content if no user is logged in
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
  
  // Filter content based on category and search query
  const filteredContent = React.useMemo(() => {
    if (!data) return [];
    
    return data.filter(item => {
      // Filter by category
      const categoryMatch = 
        activeCategory === 'all' || 
        item.categories.some(cat => cat.toLowerCase() === activeCategory.toLowerCase());
      
      // Filter by search query
      const searchMatch = 
        searchQuery === '' || 
        item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (item.description && item.description.toLowerCase().includes(searchQuery.toLowerCase())) ||
        item.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
      
      return categoryMatch && searchMatch;
    });
  }, [data, activeCategory, searchQuery]);
  
  const handleCategoryChange = (category: string) => {
    setActiveCategory(category);
  };
  
  const handleNeighborhoodChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setActiveNeighborhood(event.target.value);
  };
  
  const handleSearch = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    // Search is already handled by the filteredContent memo
  };

  return (
    <div>
      <>
        <div className="space-y-4">
          <h1 className="text-3xl font-bold text-gray-900">Explore Toronto</h1>
          <p className="text-gray-600 max-w-3xl">
            Discover the best events, places, and experiences Toronto has to offer. 
            Filter by category, search for specific interests, or browse by neighborhood.
          </p>
        </div>
  
        {/* Filters and search */}
        <div className="flex flex-col md:flex-row gap-4 items-start mb-8 mt-8">
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
  
          {/* Search form */}
          <form onSubmit={handleSearch} className="w-full md:w-auto">
            <div className="relative">
              <input
                type="text"
                className="input-field w-full md:w-64 pl-10"
                placeholder="Search..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
              />
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" 
                    d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" 
                    clipRule="evenodd" 
                  />
                </svg>
              </div>
            </div>
          </form>
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
          {(activeCategory !== 'all' || activeNeighborhood !== 'All Neighborhoods' || searchQuery) && (
            <button
              onClick={() => {
                setActiveCategory('all');
                setActiveNeighborhood('All Neighborhoods');
                setSearchQuery('');
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
            searchQuery 
              ? "No results match your search"
              : "No content found for the selected filters"
          }
        />
      </>
    </div>
  );
};

export default ExplorePage;