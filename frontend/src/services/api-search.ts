// Update to api.ts to add search functionality

// This service extends the existing api.ts file with search-specific methods

import axios from 'axios';

// Define the base URL for our API
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-type': 'application/json'
  },
  // Add better error handling
  validateStatus: (status) => {
    // Consider any 2xx status code as successful
    // For 422 errors, we'll handle them in the catch block
    return status >= 200 && status < 300;
  }
});

// Add search-related API functions to the existing api object
export const searchApi = {
  /**
   * Search content with filters
   */
  searchContent: async (
    query: string,
    filters: {
      category?: string;
      neighborhood?: string;
      season?: string;
      limit?: number;
    } = {}
  ) => {
    try {
      // Build query parameters
      const params: any = { limit: filters.limit || 50 };
      
      // Add filters if provided
      if (query) params.q = query;
      if (filters.category && filters.category !== 'all') params.category = filters.category;
      if (filters.neighborhood && filters.neighborhood !== 'All Neighborhoods') {
        params.neighborhood = filters.neighborhood;
      }
      if (filters.season && filters.season !== 'all') params.season = filters.season;
      
      console.log('Search API call with params:', params);
      
      // Choose the right endpoint based on filters
      let endpoint = '/recommendations/popular';
      
      // If neighborhood is specified, use location endpoint
      if (filters.neighborhood && filters.neighborhood !== 'All Neighborhoods') {
        return await apiClient.get(
          `/recommendations/location?neighborhood=${encodeURIComponent(filters.neighborhood)}`,
          { params }
        ).then(response => response.data);
      }
      
      // Otherwise use general endpoint with category filter
      return await apiClient.get(endpoint, { params })
        .then(response => response.data);
    } catch (error) {
      console.error('Error searching content:', error);
      throw error;
    }
  },
  
  /**
   * Get search suggestions based on query
   */
  getSearchSuggestions: async (query: string, limit: number = 5) => {
    try {
      // In a real app, this would call a backend API
      // For now, generate mock suggestions
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 300));
      
      // Generate mock suggestions based on query
      const mockSuggestions = [
        `${query} in Toronto`,
        `${query} events`,
        `best ${query}`,
        `${query} Downtown Core`,
        `popular ${query}`,
        `${query} restaurants`,
        `${query} summer`,
      ].slice(0, limit);
      
      return mockSuggestions;
    } catch (error) {
      console.error('Error getting search suggestions:', error);
      return [];
    }
  },
  
  /**
   * Log search interaction
   */
  logSearch: async (
    userId: string | null,
    query: string,
    filters: any,
    resultCount: number
  ) => {
    try {
      // In a production app, this would send analytics to the backend
      console.log('Search logged:', {
        user_id: userId,
        query,
        filters,
        result_count: resultCount,
        timestamp: new Date().toISOString()
      });
      
      // For now, just return success
      return true;
    } catch (error) {
      console.error('Error logging search:', error);
      // Don't throw here - we don't want to break the UX if logging fails
      return false;
    }
  }
};

// Extend the existing api object with search methods
export const api = {
  ...require('../services/api').api,  // Import the existing api methods
  ...searchApi                        // Add the new search methods
};