import React from 'react';
import Masonry from 'react-masonry-css';
import ContentCard from './ContentCard';
import { ContentItem } from '../../services/api';
import ContentSkeleton from './ContentSkeleton'

interface ContentGridProps {
  items: ContentItem[];
  isLoading?: boolean;
  emptyMessage?: string;
}

const ContentGrid: React.FC<ContentGridProps> = ({ 
  items, 
  isLoading = false, 
  emptyMessage = "No content found" 
}) => {
  // Define breakpoints for the masonry grid
  const breakpointColumnsObj = {
    default: 4,
    1280: 3,
    1024: 3,
    768: 2,
    640: 1
  };

  // If loading, show skeleton
  if (isLoading) {
    return (
      <Masonry
        breakpointCols={breakpointColumnsObj}
        className="masonry-grid"
        columnClassName="masonry-grid_column"
      >
        {Array.from({ length: 8 }).map((_, index) => (
          <ContentSkeleton key={index} />
        ))}
      </Masonry>
    );
  }

  // If no items, show empty message
  if (items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <svg 
          className="w-16 h-16 text-gray-400 mb-4" 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={1.5} 
            d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"
          />
        </svg>
        <p className="text-gray-600">{emptyMessage}</p>
      </div>
    );
  }

  // Render the masonry grid with content cards
  return (
    <Masonry
      breakpointCols={breakpointColumnsObj}
      className="masonry-grid"
      columnClassName="masonry-grid_column"
    >
      {items.map((item) => (
        <ContentCard key={item.content_id} content={item} />
      ))}
    </Masonry>
  );
};

export default ContentGrid;