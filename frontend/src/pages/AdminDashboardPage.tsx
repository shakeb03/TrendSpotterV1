// File path: frontend/src/pages/AdminDashboardPage.tsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import PerformanceDashboard from '../components/admin/PerformanceDashboard';
import { useUser } from '../context/UserContext';

const AdminDashboardPage: React.FC = () => {
  const { user } = useUser();
  const [activeTab, setActiveTab] = useState<string>('performance');
  
  // Simple authentication check
  if (!user) {
    return (
      <div className="max-w-md mx-auto my-12 p-6 bg-white rounded-xl shadow-md">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Admin Access Required</h1>
          <p className="text-gray-600">
            You need to be logged in to access the admin dashboard.
          </p>
        </div>
        
        <Link
          to="/profile"
          className="w-full block text-center py-2 px-4 bg-primary-500 text-white rounded-md hover:bg-primary-600 transition-colors"
        >
          Sign In
        </Link>
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
          <p className="text-gray-600 max-w-3xl">
            Monitor system performance and analyze recommendation effectiveness
          </p>
        </div>
        
        <div className="flex space-x-2">
          <Link
            to="/"
            className="px-4 py-2 bg-white border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            Back to Site
          </Link>
        </div>
      </div>
      
      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'performance'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => setActiveTab('performance')}
          >
            Performance Metrics
          </button>
          <button
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'users'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => setActiveTab('users')}
          >
            User Analytics
          </button>
          <button
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'content'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => setActiveTab('content')}
          >
            Content Management
          </button>
          <button
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'settings'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => setActiveTab('settings')}
          >
            System Settings
          </button>
        </nav>
      </div>
      
      {/* Tab Content */}
      <div>
        {activeTab === 'performance' && (
          <PerformanceDashboard />
        )}
        
        {activeTab === 'users' && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-gray-900">User Analytics</h2>
              <button className="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600">
                Export Data
              </button>
            </div>
            
            <div className="text-center py-16">
              <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">User Analytics Module</h3>
              <p className="text-gray-500 max-w-md mx-auto">
                This feature will be available in the next version. It will provide detailed insights into user behavior and preferences.
              </p>
            </div>
          </div>
        )}
        
        {activeTab === 'content' && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-gray-900">Content Management</h2>
              <div className="flex space-x-2">
                <button className="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600">
                  Add Content
                </button>
                <button className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50">
                  Import
                </button>
              </div>
            </div>
            
            <div className="text-center py-16">
              <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Content Management Module</h3>
              <p className="text-gray-500 max-w-md mx-auto">
                This feature will be available in the next version. It will allow you to manage all content and track performance metrics.
              </p>
            </div>
          </div>
        )}
        
        {activeTab === 'settings' && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="mb-6">
              <h2 className="text-xl font-bold text-gray-900">System Settings</h2>
              <p className="text-gray-600">
                Configure recommendation engine parameters and system behavior
              </p>
            </div>
            
            <div className="space-y-6">
              <div className="border-b border-gray-200 pb-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Recommendation Engine</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Personalization Strength
                    </label>
                    <div className="flex items-center">
                      <span className="text-sm text-gray-500 w-20">Generic</span>
                      <input
                        type="range"
                        min="0"
                        max="100"
                        defaultValue="60"
                        className="mx-2 w-full"
                      />
                      <span className="text-sm text-gray-500 w-20">Personal</span>
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Location Priority
                    </label>
                    <div className="flex items-center">
                      <span className="text-sm text-gray-500 w-20">Global</span>
                      <input
                        type="range"
                        min="0"
                        max="100"
                        defaultValue="75"
                        className="mx-2 w-full"
                      />
                      <span className="text-sm text-gray-500 w-20">Local</span>
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Content Diversity
                    </label>
                    <div className="flex items-center">
                      <span className="text-sm text-gray-500 w-20">Similar</span>
                      <input
                        type="range"
                        min="0"
                        max="100"
                        defaultValue="40"
                        className="mx-2 w-full"
                      />
                      <span className="text-sm text-gray-500 w-20">Diverse</span>
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Seasonal Boost
                    </label>
                    <div className="flex items-center">
                      <span className="text-sm text-gray-500 w-20">Low</span>
                      <input
                        type="range"
                        min="0"
                        max="100"
                        defaultValue="80"
                        className="mx-2 w-full"
                      />
                      <span className="text-sm text-gray-500 w-20">High</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="border-b border-gray-200 pb-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">A/B Testing Configuration</h3>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-gray-900">Recommendation Explanation Test</h4>
                      <p className="text-sm text-gray-500">Testing different explanation styles for recommendations</p>
                    </div>
                    <div className="relative inline-block w-12 mr-2 align-middle select-none">
                      <input type="checkbox" name="toggle" id="toggle1" className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer" defaultChecked />
                      <label htmlFor="toggle1" className="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"></label>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-gray-900">Homepage Layout Test</h4>
                      <p className="text-sm text-gray-500">Testing different homepage layouts and content order</p>
                    </div>
                    <div className="relative inline-block w-12 mr-2 align-middle select-none">
                      <input type="checkbox" name="toggle" id="toggle2" className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer" />
                      <label htmlFor="toggle2" className="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"></label>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-gray-900">Location Priority Test</h4>
                      <p className="text-sm text-gray-500">Testing global vs local content prioritization</p>
                    </div>
                    <div className="relative inline-block w-12 mr-2 align-middle select-none">
                      <input type="checkbox" name="toggle" id="toggle3" className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer" defaultChecked />
                      <label htmlFor="toggle3" className="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"></label>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="flex justify-end">
                <button className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 mr-3">
                  Reset to Defaults
                </button>
                <button className="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600">
                  Save Settings
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboardPage;