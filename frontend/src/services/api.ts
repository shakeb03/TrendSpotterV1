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
      
      console.log(`Fetching recommendations for user ${userId} with params:`, params);
      const response = await apiClient.get(
        `/recommendations/user/${userId}`, 
        { params }
      );
      console.log(`Got user recommendations:`, response.data);
      return response.data;
    } catch (error) {
      console.error('Error fetching user recommendations:', error);
      // Return empty recommendations object to avoid breaking UI
      return {
        recommendations: [],
        count: 0,
        model_used: "error",
        execution_time: 0
      };
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
      console.log(`Fetching similar content to ${contentId}`);
      const response = await apiClient.get(
        `/recommendations/similar/${contentId}`, 
        { params: { count, model_type: modelType } }
      );
      console.log(`Got similar content:`, response.data);
      return response.data;
    } catch (error) {
      console.error('Error fetching similar content:', error);
      // Return empty response to avoid breaking UI
      return {
        similar_items: [],
        count: 0,
        content_id: contentId,
        content_title: "",
        execution_time: 0
      };
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
      const params: any = { count };
      if (season) {
        params.season = season;
      }
      
      console.log(`Fetching recommendations for neighborhood ${neighborhood} with params:`, params);
      const response = await apiClient.get(
        `/recommendations/location?neighborhood=${encodeURIComponent(neighborhood)}`, 
        { params }
      );
      console.log(`Got neighborhood recommendations:`, response.data);
      return response.data;
    } catch (error) {
      console.error('Error fetching location recommendations:', error);
      // Return empty recommendations to avoid breaking UI
      return {
        recommendations: [],
        count: 0,
        model_used: "error",
        execution_time: 0
      };
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
   * Get direct content item by ID (using dedicated endpoint)
   */
  getContentById: async (contentId: string): Promise<ContentItem | null> => {
    console.log(`Trying to find content with ID: ${contentId}`);
    
    try {
      // Try the direct endpoint first
      const response = await apiClient.get(`/content/${contentId}`);
      console.log(`Got direct content response:`, response.data);
      
      // Convert the response to match ContentItem format
      const item: ContentItem = {
        content_id: response.data.content_id,
        title: response.data.title,
        description: response.data.description || "",
        image_url: response.data.image_url || "",
        categories: response.data.categories || [],
        tags: response.data.tags || [],
        neighborhood: response.data.neighborhood || undefined,
        score: 1.0, // Default score
        approach: "direct",
        is_event: response.data.is_event || false,
        event_date: response.data.event_date,
        event_venue: response.data.event_venue
      };
      
      return item;
    } catch (directError) {
      console.warn('Direct endpoint failed, falling back to search:', directError);
      
      try {
        // First try popular content
        const popular = await api.getPopularContent(100);
        console.log(`Got ${popular.recommendations.length} popular items to search`);
        
        let foundItem = popular.recommendations.find(item => 
          item.content_id === contentId || 
          item.content_id.toString() === contentId.toString()
        );
        
        if (foundItem) {
          console.log('Found item in popular content');
          return foundItem;
        }
        
        // Try different categories
        const categories = ['food', 'art', 'outdoor', 'event', 'shopping', 'nightlife'];
        for (const category of categories) {
          console.log(`Searching in ${category} category...`);
          const categoryContent = await api.getPopularContent(50, category);
          
          foundItem = categoryContent.recommendations.find(item => 
            item.content_id === contentId || 
            item.content_id.toString() === contentId.toString()
          );
          
          if (foundItem) {
            console.log(`Found item in ${category} category`);
            return foundItem;
          }
        }
        
        console.log('Content not found in any category');
        return null;
      } catch (error) {
        console.error('Error searching for content by ID:', error);
        return null;
      }
    }
  },

  /**
   * Get Toronto events
   */
  getEvents: async (count = 50): Promise<ContentItem[]> => {
    try {
      console.log('Fetching events specifically');
      
      // Try multiple approaches to find events
      const results: ContentItem[] = [];
      
      // 1. Try the popular content endpoint with event category filter
      try {
        const popular = await api.getPopularContent(count, 'event');
        if (popular.recommendations?.length > 0) {
          console.log(`Found ${popular.recommendations.length} events from popular endpoint`);
          results.push(...popular.recommendations);
        }
      } catch (err) {
        console.warn('Error fetching events from popular endpoint:', err);
      }
      
      // 2. Directly query the events if needed
      /* if (results.length < 1) {
        try {
          // Create mock event data as a fallback
          console.log('Creating fallback event data');
          const fallbackEvents: ContentItem[] = [
            {
              content_id: "event1",
              title: "Toronto Jazz Festival",
              description: "Annual festival celebrating jazz music with performances by local and international artists.",
              image_url: "https://source.unsplash.com/random/800x600/?jazz,music",
              categories: ["event", "music"],
              tags: ["summer", "festival", "jazz", "music", "toronto"],
              score: 5,
              approach: "fallback",
              is_event: true,
              event_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(), // 7 days in the future
              event_venue: "Nathan Phillips Square"
            },
            {
              content_id: "event2",
              title: "Toronto International Film Festival",
              description: "One of the largest publicly attended film festivals in the world.",
              image_url: "https://source.unsplash.com/random/800x600/?film,cinema",
              categories: ["event", "film"],
              tags: ["fall", "festival", "film", "cinema", "toronto"],
              score: 5,
              approach: "fallback",
              is_event: true,
              event_date: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(), // 14 days in the future
              event_venue: "TIFF Bell Lightbox"
            },
            {
              content_id: "event3",
              title: "Taste of Toronto Food Festival",
              description: "Culinary festival featuring Toronto's best restaurants and food vendors.",
              image_url: "https://source.unsplash.com/random/800x600/?food,festival",
              categories: ["event", "food"],
              tags: ["summer", "festival", "food", "culinary", "toronto"],
              score: 4.5,
              approach: "fallback",
              is_event: true,
              event_date: new Date(Date.now() + 21 * 24 * 60 * 60 * 1000).toISOString(), // 21 days in the future
              event_venue: "Distillery District"
            }
          ];
          
          // Only add fallbacks if we have very few real events
          if (results.length < 3) {
            results.push(...fallbackEvents);
          }
        } catch (err) {
          console.warn('Error creating fallback events:', err);
        }
      } */
      
      console.log(`Returning ${results.length} events`);
      return results;
    } catch (error) {
      console.error('Error fetching events:', error);
      return [];
    }
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