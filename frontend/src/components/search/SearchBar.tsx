import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

interface SearchBarProps {
  variant?: 'default' | 'minimal' | 'hero';
  onSearch?: (params: { query: string; category: string; neighborhood: string; season: string }) => void;
  initialQuery?: string;
  className?: string;
}

const SearchBar: React.FC<SearchBarProps> = ({ variant = 'default', onSearch, initialQuery = '', className = '' }) => {
  const [searchQuery, setSearchQuery] = useState(initialQuery);
  const [isExpanded, setIsExpanded] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedNeighborhood, setSelectedNeighborhood] = useState('All Neighborhoods');
  const [selectedSeason, setSelectedSeason] = useState('all');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  // Categories for filtering
  const CATEGORIES = [
    'all', 'food', 'art', 'outdoor', 'event', 
    'shopping', 'nightlife', 'attraction'
  ];

  // Toronto neighborhoods
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

  // Seasons
  const SEASONS = [
    'all', 'spring', 'summer', 'fall', 'winter'
  ];

  // Get suggested search terms
  useEffect(() => {
    const getSuggestions = async () => {
      // Only fetch suggestions if query has at least 2 characters
      if (searchQuery.length < 2) {
        setSuggestions([]);
        return;
      }

      setIsLoading(true);

      // Simulated API call - in a real app, this would fetch from your backend
      setTimeout(() => {
        // Mock suggestions based on query
        const mockSuggestions = [
          `${searchQuery} in Toronto`,
          `${searchQuery} events`,
          `best ${searchQuery}`,
          `${searchQuery} Downtown Core`,
          `popular ${searchQuery}`
        ];
        
        setSuggestions(mockSuggestions);
        setIsLoading(false);
      }, 300);
    };

    getSuggestions();
  }, [searchQuery]);

  // Close expanded search when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: { target: any; }) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setIsExpanded(false);
        setShowFilters(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleSubmit = (e: { preventDefault: any; }) => {
    e.preventDefault();
    
    // Build search params
    const params = new URLSearchParams();
    if (searchQuery) params.append('q', searchQuery);
    if (selectedCategory !== 'all') params.append('category', selectedCategory);
    if (selectedNeighborhood !== 'All Neighborhoods') params.append('neighborhood', selectedNeighborhood);
    if (selectedSeason !== 'all') params.append('season', selectedSeason);
    
    // If custom onSearch handler provided, use it
    if (onSearch) {
      onSearch?.({
        query: searchQuery,
        category: selectedCategory,
        neighborhood: selectedNeighborhood,
        season: selectedSeason
      });
      setIsExpanded(false);
    } else {
      // Otherwise navigate to search results page
      navigate(`/explore?${params.toString()}`);
      setIsExpanded(false);
    }
  };

  const handleSuggestionClick = (suggestion: React.SetStateAction<string>) => {
    setSearchQuery(suggestion);
    handleSubmit({ preventDefault: () => {} });
  };

  // Determine styles based on variant
  const getStyles = () => {
    switch (variant) {
      case 'minimal':
        return {
          container: 'relative',
          input: 'w-full pl-10 pr-4 py-2 rounded-full border border-gray-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all',
          icon: 'absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400',
          expandedContainer: 'absolute top-full mt-2 w-96 bg-white rounded-lg shadow-xl p-4 z-50 border border-gray-200'
        };
      case 'hero':
        return {
          container: 'relative w-full max-w-2xl',
          input: 'w-full pl-12 pr-4 py-4 text-lg rounded-full border-2 border-gray-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 shadow-lg transition-all',
          icon: 'absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-400',
          expandedContainer: 'absolute top-full mt-2 w-full bg-white rounded-lg shadow-xl p-4 z-50 border border-gray-200'
        };
      default:
        return {
          container: 'relative',
          input: 'w-full pl-10 pr-4 py-2 rounded-md border border-gray-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all',
          icon: 'absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400',
          expandedContainer: 'absolute top-full mt-2 w-96 bg-white rounded-lg shadow-xl p-4 z-50 border border-gray-200'
        };
    }
  };

  const styles = getStyles();

  return (
    <div className={`${styles.container} ${className}`} ref={searchRef}>
      <form onSubmit={handleSubmit}>
        <div className="relative">
          <div className={styles.icon}>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          
          <input
            type="text"
            className={styles.input}
            placeholder="Search for events, places, categories..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => setIsExpanded(true)}
            aria-label="Search"
          />
          
          {searchQuery && (
            <button
              type="button"
              className="absolute inset-y-0 right-10 flex items-center text-gray-400 hover:text-gray-600"
              onClick={() => setSearchQuery('')}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
          
          <button
            type="button"
            className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600"
            onClick={() => setShowFilters(!showFilters)}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
            </svg>
          </button>
        </div>
        
        {isExpanded && (
          <div className={styles.expandedContainer}>
            {/* Filter options */}
            {showFilters && (
              <div className="mb-4 border-b border-gray-200 pb-4">
                <h3 className="text-sm font-medium text-gray-700 mb-2">Filter By:</h3>
                
                {/* Categories */}
                <div className="mb-3">
                  <label className="block text-xs font-medium text-gray-500 mb-1">Category</label>
                  <div className="flex flex-wrap gap-2">
                    {CATEGORIES.map(category => (
                      <button
                        key={category}
                        type="button"
                        className={`px-2 py-1 text-xs rounded-full ${
                          selectedCategory === category
                            ? 'bg-primary-500 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                        onClick={() => setSelectedCategory(category)}
                      >
                        {category === 'all' ? 'All Categories' : category.charAt(0).toUpperCase() + category.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>
                
                {/* Neighborhoods */}
                <div className="mb-3">
                  <label className="block text-xs font-medium text-gray-500 mb-1">Neighborhood</label>
                  <select
                    className="w-full text-sm rounded-md border border-gray-300 py-1"
                    value={selectedNeighborhood}
                    onChange={(e) => setSelectedNeighborhood(e.target.value)}
                  >
                    {NEIGHBORHOODS.map(neighborhood => (
                      <option key={neighborhood} value={neighborhood}>
                        {neighborhood}
                      </option>
                    ))}
                  </select>
                </div>
                
                {/* Seasons */}
                <div className="mb-2">
                  <label className="block text-xs font-medium text-gray-500 mb-1">Season</label>
                  <div className="flex flex-wrap gap-2">
                    {SEASONS.map(season => (
                      <button
                        key={season}
                        type="button"
                        className={`px-2 py-1 text-xs rounded-full ${
                          selectedSeason === season
                            ? 'bg-primary-500 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                        onClick={() => setSelectedSeason(season)}
                      >
                        {season === 'all' ? 'All Seasons' : season.charAt(0).toUpperCase() + season.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>
                
                <button
                  type="button"
                  className="w-full py-1 mt-2 text-xs text-primary-500 hover:text-primary-700"
                  onClick={() => {
                    setSelectedCategory('all');
                    setSelectedNeighborhood('All Neighborhoods');
                    setSelectedSeason('all');
                  }}
                >
                  Reset Filters
                </button>
              </div>
            )}
            
            {/* Suggestions */}
            {suggestions.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Suggestions:</h3>
                <ul className="space-y-1">
                  {suggestions.map((suggestion, index) => (
                    <li key={index}>
                      <button
                        type="button"
                        className="w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded-md flex items-center"
                        onClick={() => handleSuggestionClick(suggestion)}
                      >
                        <svg className="w-4 h-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                        {suggestion}
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {/* Loading indicator */}
            {isLoading && (
              <div className="flex justify-center py-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-500"></div>
              </div>
            )}
            
            {/* No results */}
            {searchQuery.length >= 2 && !isLoading && suggestions.length === 0 && (
              <div className="text-center py-2 text-sm text-gray-500">
                No suggestions found
              </div>
            )}
            
            {/* Search button */}
            <button
              type="submit"
              className="w-full mt-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 transition-colors"
            >
              Search
            </button>
          </div>
        )}
      </form>
    </div>
  );
};

export default SearchBar;