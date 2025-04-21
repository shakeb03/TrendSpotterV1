import React, { useState } from 'react';
import { interactionService } from '../../services/interactions';

interface ShareModalProps {
  contentId: string;
  title: string;
  isOpen: boolean;
  onClose: () => void;
}

const ShareModal: React.FC<ShareModalProps> = ({ contentId, title, isOpen, onClose }) => {
  const [copySuccess, setCopySuccess] = useState<string | null>(null);
  
  if (!isOpen) return null;
  
  const shareUrl = `${window.location.origin}/content/${contentId}`;
  
  const handleShare = async (platform: string) => {
    try {
      await interactionService.shareItem(contentId, platform);
      
      if (platform === 'clipboard') {
        setCopySuccess('Link copied to clipboard!');
        setTimeout(() => setCopySuccess(null), 2000);
      } else {
        onClose();
      }
    } catch (error) {
      console.error(`Error sharing to ${platform}:`, error);
      setCopySuccess('Failed to share. Please try again.');
      setTimeout(() => setCopySuccess(null), 2000);
    }
  };
  
  // Handle click outside to close
  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      onClick={handleBackdropClick}
    >
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Share</h3>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <p className="text-gray-600 mb-4 line-clamp-2">{title}</p>
        
        <div className="flex space-x-4 mb-6">
          <button 
            onClick={() => handleShare('twitter')}
            className="flex flex-col items-center justify-center w-16 h-16 rounded-lg bg-blue-50 text-blue-500 hover:bg-blue-100"
            aria-label="Share on Twitter"
          >
            <svg className="w-6 h-6 mb-1" fill="currentColor" viewBox="0 0 24 24">
              <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z" />
            </svg>
            <span className="text-xs">Twitter</span>
          </button>
          
          <button 
            onClick={() => handleShare('facebook')}
            className="flex flex-col items-center justify-center w-16 h-16 rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-100"
            aria-label="Share on Facebook"
          >
            <svg className="w-6 h-6 mb-1" fill="currentColor" viewBox="0 0 24 24">
              <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
            </svg>
            <span className="text-xs">Facebook</span>
          </button>
          
          <button 
            onClick={() => handleShare('email')}
            className="flex flex-col items-center justify-center w-16 h-16 rounded-lg bg-red-50 text-red-500 hover:bg-red-100"
            aria-label="Share via Email"
          >
            <svg className="w-6 h-6 mb-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            <span className="text-xs">Email</span>
          </button>
          
          <button 
            onClick={() => handleShare('clipboard')}
            className="flex flex-col items-center justify-center w-16 h-16 rounded-lg bg-gray-50 text-gray-500 hover:bg-gray-100"
            aria-label="Copy Link"
          >
            <svg className="w-6 h-6 mb-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
            </svg>
            <span className="text-xs">Copy Link</span>
          </button>
        </div>
        
        <div className="mt-4">
          <div className="flex">
            <input
              type="text"
              value={shareUrl}
              readOnly
              className="flex-grow input-field bg-gray-50 rounded-l-md rounded-r-none"
            />
            <button
              onClick={() => handleShare('clipboard')}
              className="bg-primary-500 text-white px-4 rounded-r-md hover:bg-primary-600"
            >
              Copy
            </button>
          </div>
          
          {copySuccess && (
            <p className="text-green-500 text-sm mt-2">{copySuccess}</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default ShareModal;