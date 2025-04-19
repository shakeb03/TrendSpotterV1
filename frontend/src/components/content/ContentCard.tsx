import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useUser } from '../../context/UserContext';
import { api, ContentItem } from '../../services/api';
import { formatDate } from '../../utils/formatters';

interface ContentCardProps {
  content: ContentItem;
  width?: number;
}

const ContentCard: React.FC<ContentCardProps> = ({ content, width }) => {
  const { user } = useUser();
  const [saved, setSaved] = useState(false);

  const _primaryCategory = content.categories[0] || 'misc';
  
  const handleSave = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    // Toggle saved state
    setSaved(!saved);
    
    // Log the interaction if a user is logged in
    if (user) {
      api.logInteraction(user.id, content.content_id, 'save');
    }
  };
  
  const handleClick = () => {
    // Log the click interaction if a user is logged in
    if (user) {
      api.logInteraction(user.id, content.content_id, 'click');
    }
  };
  
  // Determine if this is an event
  const isEvent = api.isEvent(content);
  
  // Get primary category (for styling)
  const primaryCategory = content.categories[0] || 'misc';
  
  // Format event date if applicable
  const eventDate = content.event_date ? formatDate(new Date(content.event_date)) : null;
  
  return (
    <div 
      className="content-card card hover:shadow-lg transition-shadow duration-300 break-inside-avoid"
      style={{ width: width ? `${width}px` : '100%' }}
    >
      <Link to={`/content/${content.content_id}`} onClick={handleClick}>
        {/* Image container with consistent aspect ratio */}
        <div className="relative pb-[66%] overflow-hidden bg-gray-100">
          {content.image_url ? (
            <img 
              src={content.image_url} 
              alt={content.title}
              className="absolute top-0 left-0 w-full h-full object-cover"
              onError={(e) => {
                // Fallback if image fails to load
                (e.target as HTMLImageElement).src = 'https://via.placeholder.com/300x200?text=Toronto';
              }}
            />
          ) : (
            <div className="absolute top-0 left-0 w-full h-full flex items-center justify-center bg-gray-200">
              <span className="text-gray-500">No image</span>
            </div>
          )}
          
          {/* Save button */}
          <button 
            className={`absolute top-2 right-2 p-2 rounded-full ${
              saved ? 'bg-primary-500 text-white' : 'bg-white text-gray-700'
            } shadow hover:shadow-md transition-all duration-200`}
            onClick={handleSave}
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path 
                fillRule="evenodd" 
                d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" 
                clipRule="evenodd" 
              />
            </svg>
          </button>
          
          {/* Event badge */}
          {isEvent && (
            <div className="absolute top-2 left-2 px-2 py-1 bg-toronto-red text-white text-xs font-semibold rounded">
              EVENT
            </div>
          )}
          
          {/* Neighborhood badge */}
          {content.neighborhood && (
            <div className="absolute bottom-2 left-2 px-2 py-1 bg-black bg-opacity-50 text-white text-xs rounded">
              {content.neighborhood}
            </div>
          )}
        </div>
        
        {/* Content details */}
        <div className="p-3">
          <h3 className="font-semibold text-gray-900 mb-1 line-clamp-2">
            {content.title}
          </h3>
          
          {/* Event date and venue */}
          {isEvent && eventDate && (
            <div className="flex items-center text-sm text-gray-600 mb-2">
              <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span>{eventDate}</span>
              
              {content.event_venue && (
                <>
                  <span className="mx-1">•</span>
                  <span className="truncate">{content.event_venue}</span>
                </>
              )}
            </div>
          )}
          
          {/* Description (truncated) */}
          {content.description && (
            <p className="text-sm text-gray-600 line-clamp-2 mb-2">
              {content.description}
            </p>
          )}
          
          {/* Categories/tags */}
          <div className="flex flex-wrap gap-1 mt-2">
            {content.categories.slice(0, 2).map((category, index) => (
              <span 
                key={`${category}-${index}`}
                className={`inline-block px-2 py-1 rounded-md text-xs font-medium bg-opacity-10 capitalize category-tag ${category}`}
                style={{ backgroundColor: getCategoryColor(category) }}
              >
                {category}
              </span>
            ))}
            
            {content.tags.slice(0, 2).map((tag, index) => (
              <span 
                key={`${tag}-${index}`}
                className="inline-block px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-800"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      </Link>
    </div>
  );
};

// Helper to get a consistent color for categories
const getCategoryColor = (category: string): string => {
  const colors: Record<string, string> = {
    food: '#f59e0b',         // amber-500
    art: '#8b5cf6',          // purple-500
    outdoor: '#10b981',      // emerald-500
    event: '#ef4444',        // red-500
    shopping: '#3b82f6',     // blue-500
    nightlife: '#6366f1',    // indigo-500
    entertainment: '#ec4899', // pink-500
    museum: '#8b5cf6',       // purple-500
    restaurant: '#f59e0b',   // amber-500
    park: '#10b981',         // emerald-500
    attraction: '#3b82f6',   // blue-500
    gallery: '#8b5cf6',      // purple-500
    festival: '#ef4444',     // red-500
    market: '#f59e0b',       // amber-500
    music: '#6366f1',        // indigo-500
    theater: '#ec4899',      // pink-500
  };

  return colors[category.toLowerCase()] || '#6b7280'; // gray-500 default
};

export default ContentCard;