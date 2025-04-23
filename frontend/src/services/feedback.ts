// File path: frontend/src/services/feedback.ts
import { FeedbackData } from '../components/common/FeedbackModal';
import { api } from './api';

/**
 * Feedback Service
 * 
 * This service handles the collection and submission of user feedback
 * on recommendations and content in the Toronto Trendspotter application.
 */

// Store feedback locally for demonstration purposes
let collectedFeedback: FeedbackData[] = [];

export const feedbackService = {
  /**
   * Submit feedback from a user
   * @param feedback The feedback data to submit
   * @returns A promise that resolves when the feedback is submitted
   */
  submitFeedback: async (feedback: FeedbackData): Promise<boolean> => {
    try {
      // Get current user ID if available
      const user = JSON.parse(localStorage.getItem('trendspotter_user') || '{}');
      
      // Add user ID to feedback if available
      if (user && user.id) {
        feedback.userId = user.id;
      }
      
      // In a production app, this would send the feedback to a backend API
      // For demo purposes, we'll store it locally
      collectedFeedback.push(feedback);
      
      // Log feedback for demonstration
      console.log('Feedback submitted:', feedback);
      
      // If content ID is provided, log as interaction
      if (feedback.contentId && feedback.userId) {
        await api.logInteraction(feedback.userId, feedback.contentId, 'feedback');
      }
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500));
      
      return true;
    } catch (error) {
      console.error('Error submitting feedback:', error);
      return false;
    }
  },
  
  /**
   * Get all collected feedback (for demonstration and testing)
   * @returns An array of feedback data
   */
  getAllFeedback: (): FeedbackData[] => {
    return [...collectedFeedback];
  },
  
  /**
   * Get feedback for a specific content item
   * @param contentId The ID of the content to get feedback for
   * @returns An array of feedback data for the specified content
   */
  getFeedbackForContent: (contentId: string): FeedbackData[] => {
    return collectedFeedback.filter(feedback => feedback.contentId === contentId);
  },
  
  /**
   * Get feedback from a specific user
   * @param userId The ID of the user to get feedback from
   * @returns An array of feedback data from the specified user
   */
  getFeedbackFromUser: (userId: string): FeedbackData[] => {
    return collectedFeedback.filter(feedback => feedback.userId === userId);
  },
  
  /**
   * Calculate average rating for a content item
   * @param contentId The ID of the content to calculate rating for
   * @returns The average rating or null if no ratings
   */
  getAverageRating: (contentId: string): number | null => {
    const feedbackForContent = collectedFeedback.filter(
      feedback => feedback.contentId === contentId
    );
    
    if (feedbackForContent.length === 0) {
      return null;
    }
    
    const totalRating = feedbackForContent.reduce(
      (sum, feedback) => sum + feedback.rating, 
      0
    );
    
    return totalRating / feedbackForContent.length;
  },
  
  /**
   * Calculate average relevance for a content item
   * @param contentId The ID of the content to calculate relevance for
   * @returns The average relevance or null if no ratings
   */
  getAverageRelevance: (contentId: string): number | null => {
    const feedbackForContent = collectedFeedback.filter(
      feedback => feedback.contentId === contentId
    );
    
    if (feedbackForContent.length === 0) {
      return null;
    }
    
    const totalRelevance = feedbackForContent.reduce(
      (sum, feedback) => sum + feedback.relevance, 
      0
    );
    
    return totalRelevance / feedbackForContent.length;
  },
  
  /**
   * Clear all feedback (for testing purposes)
   */
  clearAllFeedback: (): void => {
    collectedFeedback = [];
  }
};

export default feedbackService;