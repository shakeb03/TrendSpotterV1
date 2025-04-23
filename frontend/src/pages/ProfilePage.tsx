// File path: frontend/src/pages/ProfilePage.tsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import RecommendationSection from '../components/recommendations/RecommendationSection';
import { api } from '../services/api';
import { interactionService } from '../services/interactions';

// Toronto neighborhoods for preferences selection
const TORONTO_NEIGHBORHOODS = [
  'Downtown Core',
  'Distillery District',
  'Kensington Market',
  'The Beaches',
  'Yorkville',
  'Queen West',
  'Liberty Village',
  'Leslieville',
  'Little Italy',
  'Chinatown',
  'Annex',
  'Danforth/Greektown',
  'Harbourfront',
  'Roncesvalles',
  'West Queen West',
  'Financial District',
  'Entertainment District',
  'St. Lawrence Market',
  'Parkdale',
  'Corktown'
];

// Interest categories
const INTEREST_CATEGORIES = [
  'food',
  'art',
  'travel',
  'outdoor',
  'architecture',
  'events',
  'nightlife',
  'shopping',
  'family',
  'sports',
  'music',
  'photography'
];

// A/B testing - Feature flags
const ENABLE_AB_TESTING = true;
const TEST_VARIANT = Math.random() < 0.5 ? 'A' : 'B';

const ProfilePage: React.FC = () => {
  const { user, isLoading, error, login, logout, updatePreferences } = useUser();
  const navigate = useNavigate();
  
  // States for managing preferences
  const [selectedInterests, setSelectedInterests] = useState<string[]>([]);
  const [selectedNeighborhoods, setSelectedNeighborhoods] = useState<string[]>([]);
  const [isEditing, setIsEditing] = useState(false);
  
  // State for tracking interactions
  const [recentInteractions, setRecentInteractions] = useState<any[]>([]);
  const [interactionStats, setInteractionStats] = useState<any>({
    views: 0,
    saves: 0,
    clicks: 0,
    shares: 0
  });
  
  // A/B testing variant
  const [abTestVariant, setAbTestVariant] = useState(TEST_VARIANT);
  const [abTestMetrics, setAbTestMetrics] = useState({
    impressions: 0,
    clicks: 0,
    saves: 0,
    ctr: 0
  });
  
  // Set initial values from user data
  useEffect(() => {
    if (user) {
      setSelectedInterests(user.interests || []);
      setSelectedNeighborhoods(user.neighborhoodPreferences || []);
      
      // Load recent interactions
      loadUserInteractions();
      
      // Track A/B test impression
      if (ENABLE_AB_TESTING) {
        trackABTestImpression();
      }
    }
  }, [user]);
  
  // Load user interactions
  const loadUserInteractions = async () => {
    if (!user) return;
    
    try {
      // In a real app, this would fetch from your backend
      // For demo, we'll use the interaction service
      const savedItems = interactionService.getSavedItems(user.id);
      
      // Build interaction statistics
      const stats = {
        views: Math.floor(Math.random() * 50) + 20,
        saves: savedItems.length,
        clicks: Math.floor(Math.random() * 30) + 10,
        shares: Math.floor(Math.random() * 5)
      };
      
      setInteractionStats(stats);
      
      // Create mock recent interactions
      const mockInteractions = [
        {
          type: 'save',
          contentId: savedItems[0] || 'content-1',
          title: 'Toronto Jazz Festival',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString() // 2 hours ago
        },
        {
          type: 'view',
          contentId: 'content-2',
          title: 'Distillery District Art Walk',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString() // 5 hours ago
        },
        {
          type: 'click',
          contentId: 'content-3',
          title: 'Kensington Market Food Tour',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString() // 1 day ago
        }
      ];
      
      setRecentInteractions(mockInteractions);
    } catch (err) {
      console.error('Error loading user interactions:', err);
    }
  };
  
  // Track A/B test impression
  const trackABTestImpression = () => {
    setAbTestMetrics(prev => ({
      ...prev,
      impressions: prev.impressions + 1
    }));
    
    // In a real app, you would send this event to your analytics service
    console.log(`A/B test impression: Variant ${abTestVariant}`);
  };
  
  // Track A/B test click
  const trackABTestClick = () => {
    const newMetrics = {
      ...abTestMetrics,
      clicks: abTestMetrics.clicks + 1
    };
    newMetrics.ctr = (newMetrics.clicks / newMetrics.impressions) * 100;
    
    setAbTestMetrics(newMetrics);
    
    // In a real app, you would send this event to your analytics service
    console.log(`A/B test click: Variant ${abTestVariant}`);
  };
  
  // Track A/B test save
  const trackABTestSave = () => {
    setAbTestMetrics(prev => ({
      ...prev,
      saves: prev.saves + 1
    }));
    
    // In a real app, you would send this event to your analytics service
    console.log(`A/B test save: Variant ${abTestVariant}`);
  };
  
  // Handle login for demo users
  const handleLogin = (userId: string) => {
    login(userId);
  };
  
  // Toggle an interest
  const toggleInterest = (interest: string) => {
    if (selectedInterests.includes(interest)) {
      setSelectedInterests(selectedInterests.filter(i => i !== interest));
    } else {
      setSelectedInterests([...selectedInterests, interest]);
    }
  };
  
  // Toggle a neighborhood
  const toggleNeighborhood = (neighborhood: string) => {
    if (selectedNeighborhoods.includes(neighborhood)) {
      setSelectedNeighborhoods(selectedNeighborhoods.filter(n => n !== neighborhood));
    } else {
      setSelectedNeighborhoods([...selectedNeighborhoods, neighborhood]);
    }
  };
  
  // Save preferences
  const savePreferences = async () => {
    if (user) {
      await updatePreferences(selectedInterests, selectedNeighborhoods);
      setIsEditing(false);
      
      // Track A/B test save
      if (ENABLE_AB_TESTING) {
        trackABTestSave();
      }
    }
  };
  
  // Cancel editing
  const cancelEditing = () => {
    setSelectedInterests(user?.interests || []);
    setSelectedNeighborhoods(user?.neighborhoodPreferences || []);
    setIsEditing(false);
  };
  
  // Get recommendation explanation based on A/B test variant
  const getRecommendationExplanation = () => {
    if (abTestVariant === 'A') {
      return (
        <div className="bg-primary-50 rounded-lg p-4 mb-6 border border-primary-100">
          <h3 className="font-medium text-primary-800 mb-2">How Your Recommendations Work</h3>
          <p className="text-primary-700 text-sm">
            Your recommendations are personalized based on your interests and neighborhoods you've selected. 
            We analyze your interaction patterns to find content that matches your preferences.
          </p>
        </div>
      );
    } else {
      // Variant B - More detailed explanation
      return (
        <div className="bg-primary-50 rounded-lg p-4 mb-6 border border-primary-100">
          <h3 className="font-medium text-primary-800 mb-2">How Your Recommendations Work</h3>
          <div className="space-y-2 text-sm text-primary-700">
            <p>
              We use a hybrid recommendation system that combines:
            </p>
            <ul className="list-disc pl-5 space-y-1">
              <li>Your selected interests ({selectedInterests.join(', ')})</li>
              <li>Your neighborhood preferences ({selectedNeighborhoods.join(', ')})</li>
              <li>Content similar to items you've interacted with</li>
              <li>Seasonal relevance for Toronto ({api.getCurrentSeason()})</li>
            </ul>
          </div>
        </div>
      );
    }
  };
  
  // If loading, show spinner
  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }
  
  // If not logged in, show login options
  if (!user) {
    return (
      <div className="max-w-md mx-auto my-12 p-6 bg-white rounded-xl shadow-md">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Sign In</h1>
          <p className="text-gray-600">
            Sign in to see personalized recommendations and save your favorites.
          </p>
        </div>
        
        <div className="space-y-4">
          <p className="text-sm font-medium text-gray-700">Demo Users:</p>
          
          <button
            onClick={() => handleLogin('7645592a-9838-4798-877d-2daff815de76')}
            className="w-full py-3 px-4 bg-white border border-gray-300 rounded-md flex items-center justify-between hover:bg-gray-50 transition-colors"
          >
            <span className="flex items-center">
              <img 
                src="https://randomuser.me/api/portraits/men/1.jpg" 
                className="w-8 h-8 rounded-full mr-3" 
                alt="User 1" 
              />
              <span className="text-gray-700">Toronto Explorer</span>
            </span>
            <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
          
          <button
            onClick={() => handleLogin('38ea0e87-907a-4743-9791-1ca76e79c8ce')}
            className="w-full py-3 px-4 bg-white border border-gray-300 rounded-md flex items-center justify-between hover:bg-gray-50 transition-colors"
          >
            <span className="flex items-center">
              <img 
                src="https://randomuser.me/api/portraits/women/2.jpg" 
                className="w-8 h-8 rounded-full mr-3" 
                alt="User 2" 
              />
              <span className="text-gray-700">Toronto Photographer</span>
            </span>
            <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
        
        <div className="mt-8 pt-6 border-t border-gray-200 text-center text-sm text-gray-600">
          <p>
            This is a demo application. In a real app, secure authentication would be implemented.
          </p>
        </div>
      </div>
    );
  }
  
  // User is logged in, show profile
  return (
    <div className="space-y-12">
      {/* Profile header */}
      <div className="bg-white rounded-xl shadow-md overflow-hidden">
        <div className="bg-gradient-to-r from-primary-500 to-primary-600 h-32 md:h-48"></div>
        <div className="px-4 md:px-8 pb-6 -mt-16">
          <div className="flex flex-col md:flex-row md:items-end">
            <div className="w-32 h-32 rounded-full border-4 border-white overflow-hidden bg-white">
              <img 
                src={user.profileImage || 'https://via.placeholder.com/128'} 
                alt={user.username}
                className="w-full h-full object-cover"
              />
            </div>
            
            <div className="mt-4 md:mt-0 md:ml-6 md:mb-3">
              <h1 className="text-2xl font-bold text-gray-900">{user.username}</h1>
              <p className="text-gray-600 flex items-center">
                <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                {user.neighborhoodPreferences && user.neighborhoodPreferences.length > 0 
                  ? user.neighborhoodPreferences.join(', ') 
                  : 'Toronto'
                }
              </p>
            </div>
            
            <div className="mt-6 md:mt-0 md:ml-auto flex flex-wrap gap-3">
              {isEditing ? (
                <>
                  <button 
                    onClick={savePreferences}
                    className="btn-primary"
                  >
                    Save Changes
                  </button>
                  <button 
                    onClick={cancelEditing}
                    className="btn-secondary"
                  >
                    Cancel
                  </button>
                </>
              ) : (
                <>
                  <button 
                    onClick={() => setIsEditing(true)}
                    className="btn-primary"
                  >
                    Edit Preferences
                  </button>
                  <button 
                    onClick={() => logout()}
                    className="btn-secondary"
                  >
                    Logout
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
      
      {/* Interaction Statistics */}
      <div className="bg-white rounded-xl shadow-md p-6 md:p-8">
        <h2 className="text-xl font-bold text-gray-900 mb-6">
          Your Interaction Stats
        </h2>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 rounded-lg p-4 text-center">
            <span className="text-2xl font-bold text-blue-500">{interactionStats.views}</span>
            <p className="text-sm text-blue-700 mt-1">Content Views</p>
          </div>
          
          <div className="bg-green-50 rounded-lg p-4 text-center">
            <span className="text-2xl font-bold text-green-500">{interactionStats.saves}</span>
            <p className="text-sm text-green-700 mt-1">Saved Items</p>
          </div>
          
          <div className="bg-purple-50 rounded-lg p-4 text-center">
            <span className="text-2xl font-bold text-purple-500">{interactionStats.clicks}</span>
            <p className="text-sm text-purple-700 mt-1">Item Clicks</p>
          </div>
          
          <div className="bg-orange-50 rounded-lg p-4 text-center">
            <span className="text-2xl font-bold text-orange-500">{interactionStats.shares}</span>
            <p className="text-sm text-orange-700 mt-1">Shared Items</p>
          </div>
        </div>
        
        {/* Recent Activity */}
        <div className="mt-8">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
          
          {recentInteractions.length > 0 ? (
            <div className="space-y-4">
              {recentInteractions.map((interaction, index) => (
                <div key={index} className="flex items-start p-3 bg-gray-50 rounded-lg">
                  <div className="mr-3">
                    {interaction.type === 'save' && (
                      <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
                        <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
                        </svg>
                      </div>
                    )}
                    {interaction.type === 'view' && (
                      <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                        <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                          <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                        </svg>
                      </div>
                    )}
                    {interaction.type === 'click' && (
                      <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center">
                        <svg className="w-4 h-4 text-purple-500" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M6.672 1.911a1 1 0 10-1.932.518l.259.966a1 1 0 001.932-.518l-.26-.966zM2.429 4.74a1 1 0 10-.517 1.932l.966.259a1 1 0 00.517-1.932l-.966-.26zm8.814-.569a1 1 0 00-1.415-1.414l-.707.707a1 1 0 101.415 1.415l.707-.708zm-7.071 7.072l.707-.707A1 1 0 003.465 9.12l-.708.707a1 1 0 001.415 1.415zm3.2-5.171a1 1 0 00-1.3 1.3l4 10a1 1 0 001.823.075l1.38-2.759 3.018 3.02a1 1 0 001.414-1.415l-3.019-3.02 2.76-1.379a1 1 0 00-.076-1.822l-10-4z" clipRule="evenodd" />
                        </svg>
                      </div>
                    )}
                  </div>
                  
                  <div className="flex-grow">
                    <p className="text-sm font-medium text-gray-700">{interaction.title}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(interaction.timestamp).toLocaleDateString()} · {new Date(interaction.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                  
                  <button
                    onClick={() => navigate(`/content/${interaction.contentId}`)}
                    className="text-primary-500 hover:text-primary-700 text-sm"
                  >
                    View
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              No recent activity to display
            </div>
          )}
        </div>
      </div>
      
      {/* Preferences section */}
      <section className="bg-white rounded-xl shadow-md p-6 md:p-8">
        <h2 className="text-xl font-bold text-gray-900 mb-6">
          {isEditing ? 'Update Your Preferences' : 'Your Preferences'}
        </h2>
        
        {/* Interests */}
        <div className="mb-8">
          <h3 className="text-lg font-medium text-gray-900 mb-3">
            Interests
            {!isEditing && (
              <span className="text-sm font-normal text-gray-500 ml-2">
                ({selectedInterests.length} selected)
              </span>
            )}
          </h3>
          
          <div className="flex flex-wrap gap-2">
            {INTEREST_CATEGORIES.map(interest => (
              <button
                key={interest}
                onClick={() => isEditing && toggleInterest(interest)}
                disabled={!isEditing}
                className={`px-3 py-2 rounded-md text-sm capitalize ${
                  selectedInterests.includes(interest)
                    ? 'bg-primary-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                } ${!isEditing && 'cursor-default'}`}
              >
                {interest}
              </button>
            ))}
          </div>
        </div>
        
        {/* Neighborhood preferences */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-3">
            Favorite Neighborhoods
            {!isEditing && (
              <span className="text-sm font-normal text-gray-500 ml-2">
                ({selectedNeighborhoods.length} selected)
              </span>
            )}
          </h3>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
            {TORONTO_NEIGHBORHOODS.map(neighborhood => (
              <div
                key={neighborhood}
                onClick={() => isEditing && toggleNeighborhood(neighborhood)}
                className={`px-3 py-2 rounded-md ${
                  selectedNeighborhoods.includes(neighborhood)
                    ? 'bg-primary-50 border border-primary-200 text-primary-700'
                    : 'bg-white border border-gray-200 text-gray-700'
                } ${isEditing ? 'cursor-pointer hover:bg-gray-50' : 'cursor-default'}`}
              >
                <div className="flex items-center">
                  {selectedNeighborhoods.includes(neighborhood) && (
                    <svg className="w-4 h-4 mr-2 text-primary-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  )}
                  <span>{neighborhood}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
      
      {/* A/B testing explanation section */}
      {ENABLE_AB_TESTING && (
        <div className="bg-white rounded-xl shadow-md p-6 md:p-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">Testing New Features</h2>
            
            <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
              Variant {abTestVariant}
            </span>
          </div>
          
          <p className="text-gray-600 mb-4">
            We're testing new ways to explain our recommendation system. Your feedback helps us improve!
          </p>
          
          <button
            className="btn-primary"
            onClick={() => {
              // Track click for A/B test
              trackABTestClick();
              
              // Show alert
              alert(`Thanks for your feedback on Variant ${abTestVariant}!`);
            }}
          >
            This explanation is helpful!
          </button>
        </div>
      )}
      
      {/* Personalized Recommendations Section */}
      <div>
        {/* Recommendation explanation - A/B test variants */}
        {ENABLE_AB_TESTING && getRecommendationExplanation()}
        
        {/* Personalized Recommendations */}
        <RecommendationSection 
          title="Recommended For You"
          subtitle="Based on your interests and preferences"
          fetchFn={() => api.getUserRecommendations(user.id, 12, 'hybrid')}
          queryKey={['userRecommendations', user.id]}
        />
        
        {/* Neighborhood Recommendations (if user has preferences) */}
        {user.neighborhoodPreferences && user.neighborhoodPreferences.length > 0 && (
          <RecommendationSection 
            title={`Popular in ${user.neighborhoodPreferences[0]}`}
            subtitle={`Content trending in your favorite neighborhood`}
            fetchFn={() => api.getLocationRecommendations(user.neighborhoodPreferences[0], 8)}
            queryKey={['neighborhoodRecommendations', user.neighborhoodPreferences[0]]}
          />
        )}
        
        {/* Seasonal Recommendations */}
        <RecommendationSection 
          title={`${api.getCurrentSeason().charAt(0).toUpperCase() + api.getCurrentSeason().slice(1)} Picks for You`}
          subtitle="Seasonal recommendations based on your preferences"
          fetchFn={() => api.getUserRecommendations(user.id, 8, 'hybrid')}
          queryKey={['seasonalRecommendations', user.id, api.getCurrentSeason()]}
        />
      </div>
    </div>
  );
};

export default ProfilePage;