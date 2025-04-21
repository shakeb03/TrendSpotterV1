import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useUser } from '../../context/UserContext';
import { api, ContentItem } from '../../services/api';
import { formatDate } from '../../utils/formatters';
import { interactionService } from '../../services/interactions';

interface ContentCardProps {
  content: ContentItem;
  width?: number;
  onRemove?: (contentId: string) => void;
}

const ContentCard: React.FC<ContentCardProps> = ({ content, width, onRemove }) => {
  const { user } = useUser();
  const [saved, setSaved] = useState(false);
  
  // Check if item is saved on mount
  useEffect(() => {
    if (user && content.content_id) {
      const isSaved = interactionService.isItemSaved(user.id, content.content_id);
      setSaved(isSaved);
    }
  }, [user, content.content_id]);
  
  // Validate content object to prevent errors
  if (!content || typeof content !== 'object' || !content.content_id) {
    console.error('Invalid content object:', content);
    return null; // Don't render if content is invalid
  }
  
  const handleSave = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!user) return;
    
    // Toggle saved state
    const newSavedState = !saved;
    setSaved(newSavedState);
    
    // Update saved status
    if (newSavedState) {
      interactionService.saveItem(user.id, content.content_id);
    } else {
      interactionService.unsaveItem(user.id, content.content_id);
      
      // If onRemove is provided, call it (for SavedItemsPage)
      if (onRemove) {
        onRemove(content.content_id);
      }
    }
    
    // Log the interaction
    interactionService.logInteraction(user.id, content.content_id, newSavedState ? 'save' : 'click');
  };
  
  const handleClick = () => {
    // Log the click interaction if a user is logged in
    if (user) {
      interactionService.logInteraction(user.id, content.content_id, 'click');
    }
  };
  
  const handleShare = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    // Share the content
    interactionService.shareItem(content.content_id, 'clipboard');
    
    // Log the interaction if a user is logged in
    if (user) {
      interactionService.logInteraction(user.id, content.content_id, 'share');
    }
  };
  
  // Determine if this is an event
  const isEvent = content.is_event || api.isEvent(content);
  
  // Get primary category (for styling)
  // (We keep this for future potential styling purposes)
  const _primaryCategory = content.categories && content.categories.length > 0 
    ? content.categories[0] 
    : 'misc';
  
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
                const target = e.target as HTMLImageElement;
                console.log(`Image failed to load for ${content.title}:`, content.image_url);
                target.src = `https://via.placeholder.com/300x200/e2e8f0/1e293b?text=${encodeURIComponent(content.title.substring(0, 20))}`;
              }}
            />
          ) : (
            <div className="absolute top-0 left-0 w-full h-full flex items-center justify-center bg-gray-200">
              <span className="text-gray-500">No image</span>
            </div>
          )}
          
          {/* Action buttons */}
          <div className="absolute top-2 right-2 flex space-x-2">
            {/* Save button */}
            <button 
              className={`p-2 rounded-full ${
                saved ? 'bg-primary-500 text-white' : 'bg-white text-gray-700'
              } shadow hover:shadow-md transition-all duration-200`}
              onClick={handleSave}
              aria-label={saved ? "Unsave" : "Save"}
              title={saved ? "Unsave" : "Save"}
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path 
                  fillRule="evenodd" 
                  d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" 
                  clipRule="evenodd" 
                />
              </svg>
            </button>
            
            {/* Share button */}
            <button 
              className="p-2 rounded-full bg-white text-gray-700 shadow hover:shadow-md transition-all duration-200"
              onClick={handleShare}
              aria-label="Share"
              title="Share"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" 
                />
              </svg>
            </button>
          </div>
          
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
            {content.categories && content.categories.slice(0, 2).map((category, index) => (
              <span 
                key={`${category}-${index}`}
                className={`inline-block px-2 py-1 rounded-md text-xs font-medium bg-opacity-10 capitalize category-tag ${category}`}
                style={{ backgroundColor: getCategoryColor(category) }}
              >
                {category}
              </span>
            ))}
            
            {content.tags && content.tags.slice(0, 2).map((tag, index) => (
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

  return colors[category?.toLowerCase()] || '#6b7280'; // gray-500 default
};

export default ContentCard;