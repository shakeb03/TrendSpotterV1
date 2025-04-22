import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { api } from '../../services/api';
import ContentGrid from '../content/ContentGrid'
import SearchBar from './SearchBar';

const SearchWrapper: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  
  // Extract search parameters
  const query = searchParams.get('q') || '';
  const category = searchParams.get('category') || 'all';
  const neighborhood = searchParams.get('neighborhood') || 'All Neighborhoods';
  const season = searchParams.get('season') || 'all';
  
  // Get analytics data
  const hasFilters = category !== 'all' || neighborhood !== 'All Neighborhoods' || season !== 'all';
  
  // Fetch search results
  useEffect(() => {
    const fetchResults = async () => {
      if (!query && !hasFilters) return;
      
      setIsLoading(true);
      setError(null);
      
      try {
        let results;
        
        // If filtering by neighborhood
        if (neighborhood !== 'All Neighborhoods') {
          results = await api.getLocationRecommendations(neighborhood, 50);
        } 
        // If filtering by category
        else if (category !== 'all') {
          results = await api.getPopularContent(50, category);
        } 
        // Default search
        else {
          results = await api.getPopularContent(50);
        }
        
        if (results && results.recommendations) {
          let filteredResults = results.recommendations;
          
          // Filter by search query if provided
          if (query) {
            filteredResults = filteredResults.filter((item: any) => {
              const matchesTitle = item.title.toLowerCase().includes(query.toLowerCase());
              const matchesDescription = item.description?.toLowerCase().includes(query.toLowerCase());
              const matchesTags = item.tags?.some((tag: string) => 
                tag.toLowerCase().includes(query.toLowerCase())
              );
              
              return matchesTitle || matchesDescription || matchesTags;
            });
          }
          
          // Filter by season if specified
          if (season !== 'all') {
            filteredResults = filteredResults.filter((item: any) => {
              // Check if item has season tag
              return item.tags?.includes(season.toLowerCase());
            });
          }
          
          setSearchResults(filteredResults);
        } else {
          setSearchResults([]);
        }
      } catch (err) {
        console.error('Error searching:', err);
        setError('Failed to retrieve search results. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchResults();
  }, [query, category, neighborhood, season]);
  
  // Handle new search
  const handleSearch = (searchData: any) => {
    const params = new URLSearchParams();
    if (searchData.query) params.append('q', searchData.query);
    if (searchData.category !== 'all') params.append('category', searchData.category);
    if (searchData.neighborhood !== 'All Neighborhoods') params.append('neighborhood', searchData.neighborhood);
    if (searchData.season !== 'all') params.append('season', searchData.season);
    
    navigate(`/explore?${params.toString()}`);
  };
  
  // Track search analytics
  useEffect(() => {
    // In a real app, this would send analytics data to a backend
    if (query || hasFilters) {
      console.log('Search Analytics:', {
        query,
        category,
        neighborhood,
        season,
        resultCount: searchResults.length,
        timestamp: new Date().toISOString()
      });
    }
  }, [searchResults.length]);
  
  // Determine search description
  const getSearchDescription = () => {
    let description = [];
    
    if (query) description.push(`"${query}"`);
    if (category !== 'all') description.push(category);
    if (neighborhood !== 'All Neighborhoods') description.push(`in ${neighborhood}`);
    if (season !== 'all') description.push(`during ${season}`);
    
    if (description.length === 0) return 'All content';
    return description.join(' ');
  };
  
  return (
    <div className="mb-8">
      {/* Hero search bar */}
      <div className="mb-8 p-6 bg-gray-50 rounded-xl">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Toronto Trendspotter Search</h1>
        <SearchBar 
          variant="hero" 
          onSearch={handleSearch} 
          initialQuery={query}
          className="mx-auto"
        />
      </div>
      
      {/* Search results */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">
            {isLoading ? 'Searching...' : `Results for ${getSearchDescription()}`}
          </h2>
          
          {/* Result count */}
          <p className="text-gray-500 text-sm">
            {isLoading ? '' : `Found ${searchResults.length} items`}
          </p>
        </div>
        
        {/* Show error if any */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-4">
            <p className="text-red-700">{error}</p>
          </div>
        )}
        
        {/* Results grid */}
        <ContentGrid 
          items={searchResults} 
          isLoading={isLoading} 
          emptyMessage={
            query
              ? `No results found for "${query}". Try a different search term or remove some filters.`
              : "No content matches the selected filters."
          }
        />
        
        {/* No results suggestions */}
        {!isLoading && searchResults.length === 0 && (
          <div className="mt-6 bg-white p-4 rounded-lg border border-gray-200">
            <h3 className="font-medium text-gray-900 mb-2">Suggestions:</h3>
            <ul className="list-disc pl-5 text-gray-600">
              <li>Check the spelling of your search term</li>
              <li>Try more general keywords</li>
              <li>Try different keywords</li>
              <li>
                <button 
                  onClick={() => handleSearch({ 
                    query: '', 
                    category: 'all', 
                    neighborhood: 'All Neighborhoods',
                    season: 'all'
                  })}
                  className="text-primary-500 hover:text-primary-700"
                >
                  Clear all filters
                </button>
              </li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchWrapper;