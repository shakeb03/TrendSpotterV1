import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import { ContentItem } from '../services/api';
import { interactionService } from '../services/interactions';
import ContentGrid from '../components/content/ContentGrid';
import { api } from '../services/api';

const SavedItemsPage: React.FC = () => {
  const { user } = useUser();
  const navigate = useNavigate();
  const [savedItems, setSavedItems] = useState<ContentItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    const fetchSavedItems = async () => {
      if (!user) {
        navigate('/profile');
        return;
      }
      
      setIsLoading(true);
      
      try {
        // Get saved item IDs from local storage
        const savedItemIds = interactionService.getSavedItems(user.id);
        
        if (savedItemIds.length === 0) {
          setSavedItems([]);
          setIsLoading(false);
          return;
        }
        
        // Fetch details for each saved item
        const itemDetails: ContentItem[] = [];
        
        for (const itemId of savedItemIds) {
          try {
            const item = await api.getContentById(itemId);
            if (item) {
              itemDetails.push(item);
            }
          } catch (error) {
            console.error(`Failed to fetch details for item ${itemId}:`, error);
          }
        }
        
        setSavedItems(itemDetails);
      } catch (error) {
        console.error('Error fetching saved items:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchSavedItems();
  }, [user, navigate]);
  
  const handleRemoveItem = (contentId: string) => {
    if (!user) return;
    
    // Remove from local storage
    interactionService.unsaveItem(user.id, contentId);
    
    // Update state
    setSavedItems(savedItems.filter(item => item.content_id !== contentId));
  };

  // If user is not logged in
  if (!user) {
    return null; // navigate will redirect to profile page
  }

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-gray-900">Saved Items</h1>
        <p className="text-gray-600 max-w-3xl">
          View and manage your saved content from across Toronto.
        </p>
      </div>
      
      {savedItems.length === 0 && !isLoading ? (
        <div className="bg-white rounded-xl shadow-md p-8 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary-100 text-primary-600 mb-4">
            <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">No Saved Items</h2>
          <p className="text-gray-600 mb-6">
            You haven't saved any items yet. Explore Toronto and save your favorite places and events!
          </p>
          <button 
            onClick={() => navigate('/explore')}
            className="btn-primary"
          >
            Explore Toronto
          </button>
        </div>
      ) : (
        <>
          <div className="flex justify-between items-center">
            <p className="text-gray-600 text-sm">
              {isLoading ? 'Loading your saved items...' : `${savedItems.length} saved items`}
            </p>
            {savedItems.length > 0 && (
              <button 
                onClick={() => navigate('/explore')}
                className="text-primary-600 text-sm hover:text-primary-700"
              >
                Find more to save
              </button>
            )}
          </div>
          
          <ContentGrid 
            items={savedItems} 
            isLoading={isLoading}
            emptyMessage="You haven't saved any items yet. Explore Toronto to find places and events to save."
          />
        </>
      )}
    </div>
  );
};

export default SavedItemsPage;