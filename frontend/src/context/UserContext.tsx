import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

interface User {
  id: string;
  username: string;
  interests: string[];
  neighborhoodPreferences: string[];
  profileImage?: string;
}

interface UserContextType {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  login: (userId: string) => Promise<void>;
  logout: () => void;
  updatePreferences: (interests: string[], neighborhoods: string[]) => Promise<void>;
}

// Create context with default values
const UserContext = createContext<UserContextType>({
  user: null,
  isLoading: false,
  error: null,
  login: async () => {},
  logout: () => {},
  updatePreferences: async () => {},
});

// For development, we'll use this mock user when no user is provided
const MOCK_USERS = [
  {
    id: '7645592a-9838-4798-877d-2daff815de76',
    username: 'torontoexplorer',
    interests: ['food', 'outdoor', 'photography', 'events'],
    neighborhoodPreferences: ['Downtown Core', 'Distillery District', 'Kensington Market'],
    profileImage: 'https://randomuser.me/api/portraits/men/1.jpg'
  },
  {
    id: '38ea0e87-907a-4743-9791-1ca76e79c8ce',
    username: 'tdotphotographer2017',
    interests: ['photography', 'art', 'architecture'],
    neighborhoodPreferences: ['Queen West', 'Distillery District'],
    profileImage: 'https://randomuser.me/api/portraits/women/2.jpg'
  }
];

export const UserProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  // In a real app, we'd check for a token in localStorage and auto-login
  useEffect(() => {
    const savedUser = localStorage.getItem('trendspotter_user');
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch (error) {
        console.error('Error parsing saved user:', error);
      }
    }
  }, []);
  
  const login = async (userId: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // In a real app, we'd make an API call to verify the user
      // For now, we'll use our mock users
      const foundUser = MOCK_USERS.find(user => user.id === userId);
      
      if (foundUser) {
        setUser(foundUser);
        localStorage.setItem('trendspotter_user', JSON.stringify(foundUser));
      } else {
        throw new Error('User not found');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      console.error('Login error:', err);
    } finally {
      setIsLoading(false);
    }
  };
  
  const logout = () => {
    setUser(null);
    localStorage.removeItem('trendspotter_user');
  };
  
  const updatePreferences = async (interests: string[], neighborhoods: string[]) => {
    if (!user) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      // In a real app, we'd send this update to the server
      const updatedUser = {
        ...user,
        interests,
        neighborhoodPreferences: neighborhoods,
      };
      
      setUser(updatedUser);
      localStorage.setItem('trendspotter_user', JSON.stringify(updatedUser));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      console.error('Update preferences error:', err);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <UserContext.Provider value={{ 
      user, 
      isLoading, 
      error, 
      login, 
      logout, 
      updatePreferences 
    }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => useContext(UserContext);