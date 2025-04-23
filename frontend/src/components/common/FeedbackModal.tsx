// File path: frontend/src/components/common/FeedbackModal.tsx
import React, { useState } from 'react';

interface FeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (feedback: FeedbackData) => void;
  contentId?: string;
  contentTitle?: string;
}

export interface FeedbackData {
  rating: number;
  relevance: number;
  comments: string;
  contentId?: string;
  userId?: string;
  timestamp: string;
}

const FeedbackModal: React.FC<FeedbackModalProps> = ({ 
  isOpen, 
  onClose, 
  onSubmit,
  contentId,
  contentTitle 
}) => {
  const [rating, setRating] = useState<number>(0);
  const [relevance, setRelevance] = useState<number>(0);
  const [comments, setComments] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [submitted, setSubmitted] = useState<boolean>(false);

  if (!isOpen) {
    return null;
  }
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    const feedbackData: FeedbackData = {
      rating,
      relevance,
      comments,
      contentId,
      timestamp: new Date().toISOString()
    };
    
    // Simulate API delay
    setTimeout(() => {
      onSubmit(feedbackData);
      setIsSubmitting(false);
      setSubmitted(true);
      
      // Reset form after submission
      setTimeout(() => {
        setRating(0);
        setRelevance(0);
        setComments('');
        setSubmitted(false);
        onClose();
      }, 1500);
    }, 500);
  };
  
  // Handle click outside to close
  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      onClick={handleBackdropClick}
    >
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6 relative">
        {/* Close button */}
        <button 
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
          aria-label="Close"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        
        {submitted ? (
          <div className="text-center py-6">
            <div className="w-16 h-16 bg-green-100 text-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Thank You!</h3>
            <p className="text-gray-600">
              Your feedback has been submitted and will help us improve our recommendations.
            </p>
          </div>
        ) : (
          <>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              {contentTitle ? `Rate "${contentTitle}"` : "Rate This Recommendation"}
            </h2>
            
            {contentId && (
              <p className="mb-4 text-sm text-gray-500">
                Help us improve our recommendation engine by rating this content.
              </p>
            )}
            
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Overall Rating */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Overall Rating
                </label>
                <div className="flex space-x-1">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      type="button"
                      onClick={() => setRating(star)}
                      className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        rating >= star ? 'text-yellow-500' : 'text-gray-300'
                      }`}
                    >
                      <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                    </button>
                  ))}
                </div>
              </div>
              
              {/* Relevance Rating */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  How relevant was this recommendation to you?
                </label>
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-gray-500">Not Relevant</span>
                  <div className="flex-1 flex justify-between">
                    {[1, 2, 3, 4, 5].map((value) => (
                      <button
                        key={value}
                        type="button"
                        onClick={() => setRelevance(value)}
                        className={`w-8 h-8 rounded-full ${
                          relevance === value 
                            ? 'bg-primary-500 text-white' 
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {value}
                      </button>
                    ))}
                  </div>
                  <span className="text-xs text-gray-500">Very Relevant</span>
                </div>
              </div>
              
              {/* Comments */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Additional Comments (Optional)
                </label>
                <textarea
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Share your thoughts on this recommendation..."
                  value={comments}
                  onChange={(e) => setComments(e.target.value)}
                ></textarea>
              </div>
              
              {/* Submit Button */}
              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={onClose}
                  className="mr-3 px-4 py-2 text-sm text-gray-700 hover:text-gray-900"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting || rating === 0 || relevance === 0}
                  className={`px-4 py-2 rounded-md text-white ${
                    rating === 0 || relevance === 0 || isSubmitting
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-primary-500 hover:bg-primary-600'
                  }`}
                >
                  {isSubmitting ? (
                    <div className="flex items-center">
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Submitting...
                    </div>
                  ) : 'Submit Feedback'}
                </button>
              </div>
            </form>
          </>
        )}
      </div>
    </div>
  );
};

export default FeedbackModal;