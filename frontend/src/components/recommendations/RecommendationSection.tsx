import React from 'react';
import { useQuery } from 'react-query';
import ContentGrid from '../content/ContentGrid';

interface RecommendationSectionProps {
  title: string;
  subtitle?: string;
  fetchFn: () => Promise<any>; 
  queryKey: string | string[];
  emptyMessage?: string;
}

const RecommendationSection: React.FC<RecommendationSectionProps> = ({
  title,
  subtitle,
  fetchFn,
  queryKey,
  emptyMessage = "No recommendations available"
}) => {
  // Fetch recommendations using React Query
  const { data, isLoading, error } = useQuery(
    queryKey, 
    async () => {
      try {
        console.log(`Fetching data for ${JSON.stringify(queryKey)}...`);
        const result = await fetchFn();
        console.log(`Received data for ${JSON.stringify(queryKey)}:`, result);
        
        // Handle different response formats
        if (result.recommendations) {
          return result.recommendations;
        } else if (result.similar_items) {
          return result.similar_items;
        } else {
          console.warn(`No valid data format found in response for ${JSON.stringify(queryKey)}`, result);
          return [];
        }
      } catch (err) {
        console.error(`Error fetching ${JSON.stringify(queryKey)}:`, err);
        return [];
      }
    }
  );

  return (
    <section className="mb-12">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
        {subtitle && (
          <p className="text-gray-600 mt-1">{subtitle}</p>
        )}
      </div>

      {error ? (
        <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" 
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" 
                  clipRule="evenodd" 
                />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-700">
                Error loading recommendations. Please try again later.
              </p>
            </div>
          </div>
        </div>
      ) : (
        <div>
          <p className="mb-4 text-sm text-gray-500">
            {isLoading ? 'Loading recommendations...' : 
             (data && data.length > 0) ? `Found ${data.length} items` : 
             'No items found'}
          </p>
          <ContentGrid 
            items={data || []} 
            isLoading={isLoading}
            emptyMessage={emptyMessage}
          />
        </div>
      )}
    </section>
  );
};

export default RecommendationSection;