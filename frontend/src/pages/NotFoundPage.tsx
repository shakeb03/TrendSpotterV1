import React from 'react';
import { Link } from 'react-router-dom';

const NotFoundPage: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center px-4">
      <svg
        className="w-20 h-20 text-primary-400 mb-6"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      
      <h1 className="text-4xl font-bold text-gray-900 mb-2">404</h1>
      <h2 className="text-2xl font-semibold text-gray-700 mb-4">Page Not Found</h2>
      
      <p className="text-gray-600 max-w-md mb-8">
        We couldn't find the page you're looking for. The page may have been moved, or it no longer exists.
      </p>
      
      <div className="flex flex-col sm:flex-row gap-4">
        <Link to="/" className="btn-primary">
          Go Home
        </Link>
        <Link to="/explore" className="btn-secondary">
          Explore Content
        </Link>
      </div>
    </div>
  );
};

export default NotFoundPage;