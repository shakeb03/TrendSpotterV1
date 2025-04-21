import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { api } from '../../services/api'
import TorontoMap from './TorontoMap';
import ContentGrid from '../content/ContentGrid';

interface NeighborhoodMapperProps {
  initialNeighborhood?: string;
  height?: string | number;
  showContentGrid?: boolean;
  itemLimit?: number;
}

const NeighborhoodMapper: React.FC<NeighborhoodMapperProps> = ({
  initialNeighborhood,
  height = '500px',
  showContentGrid = true,
  itemLimit = 8
}) => {
  const [selectedNeighborhood, setSelectedNeighborhood] = useState<string | undefined>(initialNeighborhood);
  const [contentCounts, setContentCounts] = useState<Record<string, number>>({});
  
  // Fetch content for the selected neighborhood
  const { data, isLoading } = useQuery(
    ['neighborhoodMap', selectedNeighborhood],
    async () => {
      if (!selectedNeighborhood) {
        return [];
      }
      
      const result = await api.getLocationRecommendations(selectedNeighborhood, itemLimit);
      return result.recommendations;
    },
    {
      enabled: !!selectedNeighborhood,
    }
  );
  
  // Fetch content counts for all neighborhoods
  useEffect(() => {
    const fetchContentCounts = async () => {
      const counts: Record<string, number> = {};
      
      // This would ideally be a single API call in a real app
      // For demo purposes, we'll use a combination of real and mock data
      try {
        const neighborhoods = [
          'Downtown Core', 'Distillery District', 'Kensington Market', 
          'Queen West', 'Yorkville', 'The Beaches', 'Liberty Village',
          'Leslieville', 'Little Italy', 'Chinatown'
        ];
        
        for (const neighborhood of neighborhoods) {
          try {
            const result = await api.getLocationRecommendations(neighborhood, 1);
            // Use the actual count if available, otherwise use a placeholder
            counts[neighborhood] = result.count || Math.floor(Math.random() * 20) + 5;
          } catch (e) {
            // If API fails, use random data
            counts[neighborhood] = Math.floor(Math.random() * 20) + 5;
          }
        }
        
        setContentCounts(counts);
      } catch (error) {
        console.error('Error fetching neighborhood content counts:', error);
        // Provide fallback data
        setContentCounts({
          'Downtown Core': 25,
          'Distillery District': 18,
          'Kensington Market': 22,
          'Queen West': 15,
          'Yorkville': 12,
          'The Beaches': 8,
          'Liberty Village': 10,
          'Leslieville': 7,
          'Little Italy': 14,
          'Chinatown': 16
        });
      }
    };
    
    fetchContentCounts();
  }, []);

  return (
    <div className="space-y-6">
      <TorontoMap 
        selectedNeighborhood={selectedNeighborhood}
        onSelectNeighborhood={setSelectedNeighborhood}
        contentCountByNeighborhood={contentCounts}
        height={height}
      />
      
      {selectedNeighborhood && showContentGrid && (
        <div className="mt-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">
            Popular in {selectedNeighborhood}
          </h3>
          <ContentGrid 
            items={data || []} 
            isLoading={isLoading}
            emptyMessage={`No content found for ${selectedNeighborhood}`}
          />
        </div>
      )}
    </div>
  );
};

export default NeighborhoodMapper;