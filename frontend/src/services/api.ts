import axios from 'axios';

// Define the base URL for our API
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-type': 'application/json'
  }
});

// Types for API responses
export interface ContentItem {
  content_id: string;
  title: string;
  description?: string;
  image_url?: string;
  categories: string[];
  tags: string[];
  neighborhood?: string;
  score: number;
  approach: string;
  is_event?: boolean;
  event_date?: string;
  event_venue?: string;
}

export interface RecommendationResponse {
  recommendations: ContentItem[];
  count: number;
  model_used: string;
  execution_time: number;
}

export interface SimilarContentResponse {
  similar_items: ContentItem[];
  count: number;
  content_id: string;
  content_title: string;
  execution_time: number;
}

// API functions
export const api = {
  /**
   * Get recommendations for a user
   */
  getUserRecommendations: async (
    userId: string, 
    count = 20, 
    modelType = 'hybrid', 
    neighborhood?: string
  ): Promise<RecommendationResponse> => {
    try {
      const params = { count, model_type: modelType };
      if (neighborhood) {
        Object.assign(params, { neighborhood });
      }
      
      const response = await apiClient.get(
        `/recommendations/user/${userId}`, 
        { params }
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching user recommendations:', error);
      throw error;
    }
  },
  
  /**
   * Get content similar to a specific item
   */
  getSimilarContent: async (
    contentId: string, 
    count = 10, 
    modelType = 'content'
  ): Promise<SimilarContentResponse> => {
    try {
      const response = await apiClient.get(
        `/recommendations/similar/${contentId}`, 
        { params: { count, model_type: modelType } }
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching similar content:', error);
      throw error;
    }
  },
  
  /**
   * Get recommendations based on neighborhood
   */
  getLocationRecommendations: async (
    neighborhood: string, 
    count = 20, 
    season?: string
  ): Promise<RecommendationResponse> => {
    try {
      const params = { count };
      if (season) {
        Object.assign(params, { season });
      }
      
      const response = await apiClient.get(
        `/recommendations/location?neighborhood=${encodeURIComponent(neighborhood)}`, 
        { params }
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching location recommendations:', error);
      throw error;
    }
  },
  
  /**
   * Get popular content items
   */
  getPopularContent: async (
    count = 20, 
    category?: string
  ): Promise<RecommendationResponse> => {
    try {
      const params = { count };
      if (category) {
        Object.assign(params, { category });
      }
      
      const response = await apiClient.get('/recommendations/popular', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching popular content:', error);
      throw error;
    }
  },
  
  /**
   * Log user interaction with content
   */
  logInteraction: async (
    userId: string, 
    contentId: string, 
    interactionType: 'view' | 'save' | 'click' | 'share'
  ) => {
    try {
      const response = await apiClient.post('/interactions', {
        user_id: userId,
        content_id: contentId,
        interaction_type: interactionType,
        timestamp: new Date().toISOString(),
        metadata: {
          platform: 'web'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error logging interaction:', error);
      // Don't throw here - we don't want user experience to break if logging fails
    }
  },
  
  /**
   * Get current seasonal information
   */
  getCurrentSeason: (): string => {
    const month = new Date().getMonth() + 1; // JavaScript months are 0-indexed
    
    if (month >= 3 && month <= 5) return 'spring';
    if (month >= 6 && month <= 8) return 'summer';
    if (month >= 9 && month <= 11) return 'fall';
    return 'winter';
  },
  
  /**
   * Helper to determine if a content is an event
   */
  isEvent: (content: ContentItem): boolean => {
    return content.is_event || (
      content.categories.includes('event') || 
      content.tags.includes('event')
    );
  }
};