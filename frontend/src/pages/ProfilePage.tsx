import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import RecommendationSection from '../components/recommendations/RecommendationSection';
import { api } from '../services/api';

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

const ProfilePage: React.FC = () => {
  const { user, isLoading, error, login, logout, updatePreferences } = useUser();
  const navigate = useNavigate();
  
  // States for managing preferences
  const [selectedInterests, setSelectedInterests] = useState<string[]>(user?.interests || []);
  const [selectedNeighborhoods, setSelectedNeighborhoods] = useState<string[]>(user?.neighborhoodPreferences || []);
  
  // State for editing mode
  const [isEditing, setIsEditing] = useState(false);
  
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
    }
  };
  
  // Cancel editing
  const cancelEditing = () => {
    setSelectedInterests(user?.interests || []);
    setSelectedNeighborhoods(user?.neighborhoodPreferences || []);
    setIsEditing(false);
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
  );
};

export default ProfilePage;