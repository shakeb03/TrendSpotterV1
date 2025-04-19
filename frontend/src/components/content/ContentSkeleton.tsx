import React from 'react';

const ContentSkeleton: React.FC = () => {
  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden animate-pulse">
      {/* Image placeholder */}
      <div className="relative pb-[66%] bg-gray-200"></div>
      
      {/* Content placeholder */}
      <div className="p-3">
        {/* Title placeholder */}
        <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
        <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
        
        {/* Description placeholder */}
        <div className="h-3 bg-gray-100 rounded w-full mb-1"></div>
        <div className="h-3 bg-gray-100 rounded w-5/6"></div>
        
        {/* Tags placeholder */}
        <div className="flex flex-wrap gap-1 mt-3">
          <div className="h-5 w-16 bg-gray-100 rounded-md"></div>
          <div className="h-5 w-12 bg-gray-100 rounded-md"></div>
        </div>
      </div>
    </div>
  );
};

export default ContentSkeleton;