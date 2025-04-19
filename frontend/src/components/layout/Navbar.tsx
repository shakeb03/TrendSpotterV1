import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useUser } from '../../context/UserContext';

const Navbar: React.FC = () => {
  const { user, login, logout } = useUser();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();

  // For demo purposes, we'll provide a way to quickly login as sample users
  const [showLoginOptions, setShowLoginOptions] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const handleLogin = (userId: string) => {
    login(userId);
    setShowLoginOptions(false);
  };

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex-shrink-0 flex items-center">
              <div className="h-8 w-8 rounded-full bg-toronto-red flex items-center justify-center mr-2">
                <span className="text-white font-bold">T</span>
              </div>
              <span className="font-bold text-lg text-gray-900">Toronto Trendspotter</span>
            </Link>
          </div>

          {/* Desktop menu */}
          <div className="hidden md:ml-6 md:flex md:items-center md:space-x-4">
            <Link 
              to="/" 
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                isActive('/') 
                  ? 'bg-primary-50 text-primary-600' 
                  : 'text-gray-700 hover:text-primary-600'
              }`}
            >
              Home
            </Link>
            <Link 
              to="/explore" 
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                isActive('/explore') 
                  ? 'bg-primary-50 text-primary-600' 
                  : 'text-gray-700 hover:text-primary-600'
              }`}
            >
              Explore
            </Link>
            <Link 
              to="/events" 
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                isActive('/events') 
                  ? 'bg-primary-50 text-primary-600' 
                  : 'text-gray-700 hover:text-primary-600'
              }`}
            >
              Events
            </Link>
            {user && (
              <Link 
                to="/profile" 
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  isActive('/profile') 
                    ? 'bg-primary-50 text-primary-600' 
                    : 'text-gray-700 hover:text-primary-600'
                }`}
              >
                Profile
              </Link>
            )}
          </div>

          <div className="hidden md:flex items-center">
            {user ? (
              <div className="flex items-center space-x-2">
                <div className="rounded-full h-8 w-8 overflow-hidden">
                  <img 
                    src={user.profileImage || 'https://via.placeholder.com/40'} 
                    alt={user.username}
                    className="h-full w-full object-cover"
                  />
                </div>
                <span className="text-sm font-medium text-gray-700">
                  {user.username}
                </span>
                <button
                  onClick={() => logout()}
                  className="ml-2 px-3 py-1 text-sm font-medium rounded-md bg-gray-100 text-gray-700 hover:bg-gray-200"
                >
                  Logout
                </button>
              </div>
            ) : (
              <div className="relative">
                <button
                  onClick={() => setShowLoginOptions(!showLoginOptions)}
                  className="btn-primary"
                >
                  Login
                </button>
                
                {showLoginOptions && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-10">
                    <div className="px-4 py-2 text-sm text-gray-700 font-semibold border-b">
                      Demo Users
                    </div>
                    <button
                      className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      onClick={() => handleLogin('7645592a-9838-4798-877d-2daff815de76')}
                    >
                      User 1: torontoexplorer
                    </button>
                    <button
                      className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      onClick={() => handleLogin('38ea0e87-907a-4743-9791-1ca76e79c8ce')}
                    >
                      User 2: tdotphotographer2017
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="flex items-center md:hidden">
            <button
              onClick={toggleMenu}
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-700 hover:text-primary-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500"
              aria-expanded={isMenuOpen ? 'true' : 'false'}
            >
              <span className="sr-only">Open main menu</span>
              {/* Icon when menu is closed */}
              {!isMenuOpen ? (
                <svg className="block h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              ) : (
                /* Icon when menu is open */
                <svg className="block h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu, show/hide based on menu state */}
      {isMenuOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            <Link 
              to="/" 
              className={`block px-3 py-2 rounded-md text-base font-medium ${
                isActive('/') 
                  ? 'bg-primary-50 text-primary-600' 
                  : 'text-gray-700 hover:bg-gray-50 hover:text-primary-600'
              }`}
              onClick={() => setIsMenuOpen(false)}
            >
              Home
            </Link>
            <Link 
              to="/explore" 
              className={`block px-3 py-2 rounded-md text-base font-medium ${
                isActive('/explore') 
                  ? 'bg-primary-50 text-primary-600' 
                  : 'text-gray-700 hover:bg-gray-50 hover:text-primary-600'
              }`}
              onClick={() => setIsMenuOpen(false)}
            >
              Explore
            </Link>
            <Link 
              to="/events" 
              className={`block px-3 py-2 rounded-md text-base font-medium ${
                isActive('/events') 
                  ? 'bg-primary-50 text-primary-600' 
                  : 'text-gray-700 hover:bg-gray-50 hover:text-primary-600'
              }`}
              onClick={() => setIsMenuOpen(false)}
            >
              Events
            </Link>
            {user && (
              <Link 
                to="/profile" 
                className={`block px-3 py-2 rounded-md text-base font-medium ${
                  isActive('/profile') 
                    ? 'bg-primary-50 text-primary-600' 
                    : 'text-gray-700 hover:bg-gray-50 hover:text-primary-600'
                }`}
                onClick={() => setIsMenuOpen(false)}
              >
                Profile
              </Link>
            )}
          </div>
          
          <div className="pt-4 pb-3 border-t border-gray-200">
            {user ? (
              <div className="flex items-center px-5">
                <div className="flex-shrink-0">
                  <img 
                    src={user.profileImage || 'https://via.placeholder.com/40'} 
                    alt={user.username}
                    className="h-10 w-10 rounded-full"
                  />
                </div>
                <div className="ml-3">
                  <div className="text-base font-medium text-gray-800">{user.username}</div>
                </div>
                <button
                  onClick={() => {
                    logout();
                    setIsMenuOpen(false);
                  }}
                  className="ml-auto flex-shrink-0 bg-white p-1 rounded-full text-gray-400 hover:text-gray-500"
                >
                  <span className="sr-only">Logout</span>
                  <span className="px-3 py-1 text-sm font-medium rounded-md bg-gray-100 text-gray-700 hover:bg-gray-200">
                    Logout
                  </span>
                </button>
              </div>
            ) : (
              <div className="px-5">
                <button
                  onClick={() => setShowLoginOptions(!showLoginOptions)}
                  className="btn-primary w-full"
                >
                  Login
                </button>
                
                {showLoginOptions && (
                  <div className="mt-2 w-full bg-white rounded-md shadow-lg py-1 z-10">
                    <div className="px-4 py-2 text-sm text-gray-700 font-semibold border-b">
                      Demo Users
                    </div>
                    <button
                      className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      onClick={() => {
                        handleLogin('7645592a-9838-4798-877d-2daff815de76');
                        setIsMenuOpen(false);
                      }}
                    >
                      User 1: torontoexplorer
                    </button>
                    <button
                      className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      onClick={() => {
                        handleLogin('38ea0e87-907a-4743-9791-1ca76e79c8ce');
                        setIsMenuOpen(false);
                      }}
                    >
                      User 2: tdotphotographer2017
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;