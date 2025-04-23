import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { api, ContentItem } from '../services/api';
import { useUser } from '../context/UserContext';
import { formatDate, formatDateTime } from '../utils/formatters';
import ContentSkeleton from '../components/content/ContentSkeleton';
import ContentCard from '../components/content/ContentCard';
import { interactionService } from '../services/interactions';
import ShareModal from '../components/common/ShareModal';

import FeedbackModal, { FeedbackData } from '../components/common/FeedbackModal';
import { feedbackService } from '../services/feedback';


// Fallback similar content component
const FallbackSimilarContent: React.FC<{ excludeId: string }> = ({ excludeId }) => {
  const { data, isLoading } = useQuery(
    ['fallbackSimilar', excludeId],
    async () => {
      // Get popular content as a fallback
      const popular = await api.getPopularContent(12);
      // Filter out the current item
      return popular.recommendations.filter(item => item.content_id !== excludeId).slice(0, 4);
    }
  );

  if (isLoading || !data) {
    return (
      <>
        {Array.from({ length: 4 }).map((_, index) => (
          <ContentSkeleton key={index} />
        ))}
      </>
    );
  }

  return (
    <>
      {data.map((item) => (
        <ContentCard key={item.content_id} content={item} />
      ))}
    </>
  );
};

const ContentDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useUser();
  const [content, setContent] = useState<ContentItem | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSaved, setIsSaved] = useState(false);
  const [isShareModalOpen, setIsShareModalOpen] = useState(false);

  const [showFeedback, setShowFeedback] = useState<boolean>(false);
  const [averageRating, setAverageRating] = useState<number | null>(null);




  useEffect(() => {
    if (content?.content_id) {
      const rating = feedbackService.getAverageRating(content.content_id);
      setAverageRating(rating);
    }
  }, [content]);

  // Check if item is saved on mount
  useEffect(() => {
    if (user && content?.content_id) {
      const itemIsSaved = interactionService.isItemSaved(user.id, content.content_id);
      setIsSaved(itemIsSaved);
    }
  }, [user, content?.content_id]);

  useEffect(() => {
    const fetchContent = async () => {
      if (!id) return;

      try {
        setIsLoading(true);
        console.log(`Fetching content with ID: ${id}`);

        // Handle fallback event IDs specially
        if (id.startsWith('fallback-')) {
          console.log('This is a fallback event, creating placeholder content');
          // Create a placeholder for fallback events
          setContent({
            content_id: id,
            title: id.includes('jazz') ? "Toronto Jazz Festival" :
              id.includes('film') ? "Toronto International Film Festival" :
                "Toronto Festival Event",
            description: "This is a sample event created to demonstrate the Toronto Trendspotter app. In a production system, this would be a real event from a database or API.",
            image_url: `https://source.unsplash.com/featured/?toronto,festival`,
            categories: ["event"],
            tags: ["toronto", "sample", "festival", "event"],
            score: 5.0,
            approach: "fallback",
            is_event: true,
            event_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
            event_venue: "Toronto Venue"
          });
          setIsLoading(false);
          return;
        }

        // Use the API service to get content
        const foundContent = await api.getContentById(id);

        if (foundContent) {
          console.log('Content found:', foundContent);
          setContent(foundContent);

          // Log view interaction if user is logged in
          if (user) {
            api.logInteraction(user.id, id, 'view');
          }
        } else {
          console.log('Content not found, creating placeholder');
          // Create a placeholder content item
          setContent({
            content_id: id,
            title: "Toronto Experience",
            description: "This content item couldn't be found. It might have been removed or is temporarily unavailable. Please try exploring other content on our site.",
            image_url: `https://source.unsplash.com/featured/?toronto,${Math.random()}`,
            categories: ["placeholder"],
            tags: ["toronto", "placeholder"],
            score: 5.0,
            approach: "placeholder"
          });
        }
      } catch (err) {
        console.error('Error loading content:', err);
        setError('Error loading content');
      } finally {
        setIsLoading(false);
      }
    };

    fetchContent();
  }, [id, user]);

  const handleFeedbackSubmit = async (feedbackData: FeedbackData) => {
    await feedbackService.submitFeedback({
      ...feedbackData,
      contentId: content?.content_id
    });

    // Update the average rating
    const newRating = feedbackService.getAverageRating(content?.content_id || '');
    setAverageRating(newRating);
  };

  const handleSave = () => {
    if (!user || !content) return;

    // Toggle saved state
    const newSavedState = !isSaved;
    setIsSaved(newSavedState);

    // Update saved status in service
    if (newSavedState) {
      interactionService.saveItem(user.id, content.content_id);
    } else {
      interactionService.unsaveItem(user.id, content.content_id);
    }

    // Log the interaction
    interactionService.logInteraction(user.id, content.content_id, newSavedState ? 'save' : 'click');
  };

  const handleShare = () => {
    setIsShareModalOpen(true);

    // Log the interaction
    if (user && content) {
      interactionService.logInteraction(user.id, content.content_id, 'share');
    }
  };

  // Determine if this is an event
  const isEvent = content ? api.isEvent(content) : false;

  // Format event date if applicable
  const eventDate = content?.event_date
    ? formatDateTime(new Date(content.event_date))
    : null;

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="animate-pulse">
          <div className="h-64 bg-gray-200 rounded-xl mb-6"></div>
          <div className="h-8 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-5/6 mb-8"></div>
          <div className="flex space-x-3 mb-8">
            <div className="h-10 w-24 bg-gray-200 rounded-md"></div>
            <div className="h-10 w-24 bg-gray-200 rounded-md"></div>
          </div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded w-full"></div>
            <div className="h-4 bg-gray-200 rounded w-full"></div>
            <div className="h-4 bg-gray-200 rounded w-4/5"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !content) {
    return (
      <div className="text-center py-16">
        <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h2 className="text-xl font-semibold text-gray-700 mb-2">Content Not Found</h2>
        <p className="text-gray-500 mb-6">
          {error || "We couldn't find the content you're looking for."}
        </p>
        <Link to="/explore" className="btn-primary">
          Explore Content
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Image */}
      <div className="rounded-xl overflow-hidden mb-6 bg-gray-100">
        {content.image_url ? (
          <img
            src={content.image_url}
            alt={content.title}
            className="w-full h-auto max-h-[500px] object-cover"
          />
        ) : (
          <div className="h-64 flex items-center justify-center bg-gray-200">
            <span className="text-gray-500">No image available</span>
          </div>
        )}
      </div>

      {/* Content info */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-3">{content.title}</h1>

        {/* Categories & Location */}
        <div className="flex flex-wrap gap-2 mb-3">
          {content.categories.map((category, index) => (
            <span
              key={`${category}-${index}`}
              className="px-3 py-1 rounded-full text-sm font-medium capitalize"
              style={{
                backgroundColor: getCategoryColor(category, '10'),
                color: getCategoryColor(category, '700')
              }}
            >
              {category}
            </span>
          ))}

          {content.neighborhood && (
            <Link
              to={`/neighborhood/${encodeURIComponent(content.neighborhood)}`}
              className="px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-700 hover:bg-gray-200"
            >
              {content.neighborhood}
            </Link>
          )}
        </div>

        {/* Event details */}
        {isEvent && eventDate && (
          <div className="bg-primary-50 rounded-lg p-4 mb-4 border border-primary-100">
            <div className="flex items-start">
              <div className="mr-4 bg-primary-100 p-2 rounded-lg">
                <svg className="w-6 h-6 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Event Details</h3>
                <p className="text-gray-700">{eventDate}</p>
                {content.event_venue && (
                  <p className="text-gray-700">
                    <span className="font-medium">Venue:</span> {content.event_venue}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Description */}
        <div className="prose prose-lg max-w-none text-gray-700 mb-6">
          <p>{content.description}</p>
        </div>

        {/* Tags */}
        {content.tags && content.tags.length > 0 && (
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Tags</h3>
            <div className="flex flex-wrap gap-2">
              {content.tags.map((tag, index) => (
                <span
                  key={`${tag}-${index}`}
                  className="px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Action buttons */}
        <div className="flex flex-wrap gap-3">
          <button
            onClick={handleSave}
            className={`flex items-center px-4 py-2 rounded-md font-medium ${isSaved
                ? 'bg-primary-500 text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
          >
            <svg
              className="w-5 h-5 mr-2"
              fill={isSaved ? 'currentColor' : 'none'}
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={isSaved ? 0 : 2}
                d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
              />
            </svg>
            {isSaved ? 'Saved' : 'Save'}
          </button>

          <button
            onClick={handleShare}
            className="flex items-center px-4 py-2 rounded-md font-medium bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
          >
            <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"
              />
            </svg>
            Share
          </button>

          <button
            onClick={() => setShowFeedback(true)}
            className="flex items-center px-4 py-2 rounded-md font-medium bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
          >
            <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
              />
            </svg>
            {averageRating ? `Rate (${averageRating.toFixed(1)}★)` : 'Rate'}
          </button>

          {content.neighborhood && (
            <Link
              to={`/neighborhood/${encodeURIComponent(content.neighborhood)}`}
              className="flex items-center px-4 py-2 rounded-md font-medium bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
            >
              <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
              Explore {content.neighborhood}
            </Link>
          )}
        </div>
      </div>

      {/* Similar Content */}
      <div className="mt-10">
        <h2 className="text-xl font-bold text-gray-900 mb-4">You Might Also Like</h2>
        <p className="text-gray-600 mb-6">Similar content you might enjoy</p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {isLoading ? (
            // Loading skeletons
            Array.from({ length: 4 }).map((_, index) => (
              <ContentSkeleton key={index} />
            ))
          ) : error ? (
            // Error state
            <div className="col-span-full bg-red-50 rounded-lg p-4 text-red-700">
              Unable to load similar content.
            </div>
          ) : (
            // Simplified similar content display - just show popular content
            <FallbackSimilarContent excludeId={content.content_id} />
          )}
        </div>
      </div>

      {/* Share modal */}
      {content && (
        <ShareModal
          contentId={content.content_id}
          title={content.title}
          isOpen={isShareModalOpen}
          onClose={() => setIsShareModalOpen(false)}
        />
      )}

      {/* Feedback modal */}
      <FeedbackModal
        isOpen={showFeedback}
        onClose={() => setShowFeedback(false)}
        onSubmit={handleFeedbackSubmit}
        contentId={content?.content_id}
        contentTitle={content?.title}
      />
    </div>
  );
};

// Helper to get a consistent color for categories
const getCategoryColor = (category: string, shade: string = '500'): string => {
  const colors: Record<string, Record<string, string>> = {
    food: {
      '10': '#fef3c7',  // amber-50
      '500': '#f59e0b', // amber-500
      '700': '#b45309'  // amber-700
    },
    art: {
      '10': '#f3e8ff',  // purple-50
      '500': '#8b5cf6', // purple-500
      '700': '#6d28d9'  // purple-700
    },
    outdoor: {
      '10': '#ecfdf5',  // emerald-50
      '500': '#10b981', // emerald-500
      '700': '#047857'  // emerald-700
    },
    event: {
      '10': '#fee2e2',  // red-50
      '500': '#ef4444', // red-500
      '700': '#b91c1c'  // red-700
    },
    shopping: {
      '10': '#dbeafe',  // blue-50
      '500': '#3b82f6', // blue-500
      '700': '#1d4ed8'  // blue-700
    },
    nightlife: {
      '10': '#eef2ff',  // indigo-50
      '500': '#6366f1', // indigo-500
      '700': '#4338ca'  // indigo-700
    }
  };

  const categoryColors = colors[category?.toLowerCase()] || colors['event'];
  return categoryColors[shade] || '#6b7280'; // gray-500 default
};

export default ContentDetailsPage;