import { api } from './api';

// Types for user interactions
export type InteractionType = 'view' | 'save' | 'click' | 'share';

export interface UserInteraction {
  userId: string;
  contentId: string;
  type: InteractionType;
  timestamp: string;
  metadata?: Record<string, any>;
}

// For demo purposes, we store saved items in local storage
const SAVED_ITEMS_KEY = 'trendspotter_saved_items';

export const interactionService = {
  /**
   * Log a user interaction
   */
  logInteraction: async (
    userId: string,
    contentId: string,
    type: InteractionType,
    metadata?: Record<string, any>
  ): Promise<boolean> => {
    try {
      // Send to API
      await api.logInteraction(userId, contentId, type);
      
      // If it's a save interaction, also store in local storage
      if (type === 'save') {
        interactionService.saveItem(userId, contentId);
      }
      
      return true;
    } catch (error) {
      console.error(`Error logging ${type} interaction:`, error);
      return false;
    }
  },
  
  /**
   * Save an item for a user
   */
  saveItem: (userId: string, contentId: string): void => {
    try {
      // Get current saved items from local storage
      const savedItemsStr = localStorage.getItem(SAVED_ITEMS_KEY);
      let savedItems: Record<string, string[]> = {};
      
      if (savedItemsStr) {
        savedItems = JSON.parse(savedItemsStr);
      }
      
      // Add the item to the user's saved items
      if (!savedItems[userId]) {
        savedItems[userId] = [];
      }
      
      // Only add if not already saved
      if (!savedItems[userId].includes(contentId)) {
        savedItems[userId].push(contentId);
        localStorage.setItem(SAVED_ITEMS_KEY, JSON.stringify(savedItems));
      }
    } catch (error) {
      console.error('Error saving item:', error);
    }
  },
  
  /**
   * Remove a saved item for a user
   */
  unsaveItem: (userId: string, contentId: string): void => {
    try {
      // Get current saved items from local storage
      const savedItemsStr = localStorage.getItem(SAVED_ITEMS_KEY);
      let savedItems: Record<string, string[]> = {};
      
      if (savedItemsStr) {
        savedItems = JSON.parse(savedItemsStr);
      }
      
      // Remove the item from the user's saved items
      if (savedItems[userId]) {
        savedItems[userId] = savedItems[userId].filter(id => id !== contentId);
        localStorage.setItem(SAVED_ITEMS_KEY, JSON.stringify(savedItems));
      }
    } catch (error) {
      console.error('Error removing saved item:', error);
    }
  },
  
  /**
   * Check if an item is saved by a user
   */
  isItemSaved: (userId: string, contentId: string): boolean => {
    try {
      // Get saved items from local storage
      const savedItemsStr = localStorage.getItem(SAVED_ITEMS_KEY);
      
      if (!savedItemsStr) {
        return false;
      }
      
      const savedItems: Record<string, string[]> = JSON.parse(savedItemsStr);
      
      return savedItems[userId]?.includes(contentId) || false;
    } catch (error) {
      console.error('Error checking if item is saved:', error);
      return false;
    }
  },
  
  /**
   * Get all saved items for a user
   */
  getSavedItems: (userId: string): string[] => {
    try {
      // Get saved items from local storage
      const savedItemsStr = localStorage.getItem(SAVED_ITEMS_KEY);
      
      if (!savedItemsStr) {
        return [];
      }
      
      const savedItems: Record<string, string[]> = JSON.parse(savedItemsStr);
      
      return savedItems[userId] || [];
    } catch (error) {
      console.error('Error getting saved items:', error);
      return [];
    }
  },
  
  /**
   * Share an item
   */
  shareItem: async (contentId: string, platform: string): Promise<boolean> => {
    try {
      // In a real app, this would implement actual sharing functionality
      // For the demo, we'll just show how it would work
      const shareUrl = `${window.location.origin}/content/${contentId}`;
      
      switch (platform) {
        case 'twitter':
          window.open(`https://twitter.com/intent/tweet?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent('Check out this Toronto highlight!')}`, '_blank');
          break;
        case 'facebook':
          window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`, '_blank');
          break;
        case 'email':
          window.open(`mailto:?subject=${encodeURIComponent('Check out this Toronto highlight!')}&body=${encodeURIComponent(`I found this interesting content about Toronto: ${shareUrl}`)}`, '_blank');
          break;
        case 'clipboard':
          await navigator.clipboard.writeText(shareUrl);
          alert('Link copied to clipboard!');
          break;
        default:
          console.warn(`Sharing platform '${platform}' not supported`);
          return false;
      }
      
      return true;
    } catch (error) {
      console.error('Error sharing item:', error);
      return false;
    }
  }
};