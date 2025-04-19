import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from 'react-query';
import { api } from '../services/api';
import ContentGrid from '../components/content/ContentGrid';
import RecommendationSection from '../components/recommendations/RecommendationSection';

// Neighborhood information for the header
const NEIGHBORHOOD_INFO: Record<string, { 
  description: string; 
  image: string;
  features: string[];
}> = {
  'Downtown Core': {
    description: 'The heart of Toronto featuring skyscrapers, entertainment venues, shopping districts, and cultural attractions.',
    image: 'https://images.unsplash.com/photo-1514924013411-cbf25faa35bb',
    features: ['Urban', 'Business', 'Shopping', 'Entertainment']
  },
  'Distillery District': {
    description: 'A historic district featuring Victorian industrial architecture, boutiques, cafes, restaurants, and art galleries.',
    image: 'https://images.unsplash.com/photo-1569880153113-76e33fc52d5f',
    features: ['Historic', 'Artistic', 'Pedestrian', 'Dining']
  },
  'Kensington Market': {
    description: 'An eclectic and multicultural neighborhood known for vintage shops, diverse food options, and street art.',
    image: 'https://images.unsplash.com/photo-1596395464941-de917238027a',
    features: ['Eclectic', 'Multicultural', 'Shopping', 'Food']
  },
  'Queen West': {
    description: 'A trendy area with hip boutiques, galleries, restaurants, and bars that showcases Torontos creative side.',
    image: 'https://images.unsplash.com/photo-1596395463910-4ab618e3c4e4',
    features: ['Trendy', 'Artistic', 'Fashion', 'Nightlife']
  },
  'Yorkville': {
    description: 'An upscale district featuring luxury shopping, fine dining, high-end hotels, and cultural institutions.',
    image: 'https://images.unsplash.com/photo-1603464707576-93d3c6955ad4',
    features: ['Luxury', 'Upscale', 'Shopping', 'Dining']
  },
  'The Beaches': {
    description: 'A laid-back waterfront community with beaches, parks, a boardwalk, and a relaxed small-town feel.',
    image: 'https://images.unsplash.com/photo-1588701199633-127faccbd2f7',
    features: ['Beach', 'Relaxed', 'Family-friendly', 'Outdoor']
  },
  'Liberty Village': {
    description: 'A modern urban community in revitalized industrial buildings, popular with young professionals.',
    image: 'https://images.unsplash.com/photo-1583268426029-4ab35cb8a5a6',
    features: ['Modern', 'Urban', 'Industrial', 'Young']
  },
  'Leslieville': {
    description: 'A hip residential area with indie cafes, restaurants, and shops that has blossomed in recent years.',
    image: 'https://images.unsplash.com/photo-1582217900003-2b13bff567c7',
    features: ['Trendy', 'Foodie', 'Residential', 'Family-friendly']
  },
  'Little Italy': {
    description: 'A vibrant neighborhood centered around College Street, known for Italian restaurants, bars, and cafes.',
    image: 'https://images.unsplash.com/photo-1574800009408-aba6abe933d3',
    features: ['Italian', 'Dining', 'Lively', 'Cultural']
  },
  'Chinatown': {
    description: 'A bustling area with a high concentration of Chinese businesses, restaurants, and cultural institutions.',
    image: 'https://images.unsplash.com/photo-1616313253719-c46004fdf747',
    features: ['Asian', 'Cultural', 'Dining', 'Shopping']
  }
};

// Default info if neighborhood not found
const DEFAULT_INFO = {
  description: 'Discover the unique character and attractions of this Toronto neighborhood.',
  image: 'https://images.unsplash.com/photo-1517090504586-fde19ea6066f',
  features: ['Toronto', 'Neighborhood', 'Local']
};

const NeighborhoodPage: React.FC = () => {
  const { name } = useParams<{ name: string }>();
  const decodedName = name ? decodeURIComponent(name) : '';
  
  // Get neighborhood info (or default if not found)
  const neighborhoodInfo = NEIGHBORHOOD_INFO[decodedName] || DEFAULT_INFO;

  return (
    <div className="space-y-8">
      {/* Neighborhood header */}
      <section className="relative rounded-xl overflow-hidden">
        <div className="h-64 md:h-80">
          <img 
            src={neighborhoodInfo.image}
            alt={decodedName}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent"></div>
        </div>
        
        <div className="absolute bottom-0 left-0 p-6 md:p-8 text-white">
          <h1 className="text-3xl md:text-4xl font-bold mb-2">{decodedName}</h1>
          <p className="text-white/90 text-lg max-w-2xl">{neighborhoodInfo.description}</p>
          
          <div className="flex flex-wrap gap-2 mt-3">
            {neighborhoodInfo.features.map((feature) => (
              <span 
                key={feature} 
                className="bg-white/20 backdrop-blur-sm text-white text-sm px-3 py-1 rounded-full"
              >
                {feature}
              </span>
            ))}
          </div>
        </div>
      </section>
      
      {/* Trending in this neighborhood */}
      <RecommendationSection
        title={`Trending in ${decodedName}`}
        subtitle="See what's popular in this neighborhood right now"
        fetchFn={() => api.getLocationRecommendations(decodedName, 12)}
        queryKey={['neighborhood', decodedName, 'trending']}
        emptyMessage={`No trending content found for ${decodedName}`}
      />
      
      {/* Events in this neighborhood */}
      <RecommendationSection
        title={`Events in ${decodedName}`}
        subtitle="Upcoming events and activities"
        fetchFn={() => api.getLocationRecommendations(decodedName, 8)}
        queryKey={['neighborhood', decodedName, 'events']}
        emptyMessage={`No events found for ${decodedName}`}
      />
      
      {/* Places to visit */}
      <RecommendationSection
        title={`Places to Visit in ${decodedName}`}
        subtitle="Popular attractions and hidden gems"
        fetchFn={() => api.getLocationRecommendations(decodedName, 8)}
        queryKey={['neighborhood', decodedName, 'places']}
        emptyMessage={`No places found for ${decodedName}`}
      />
    </div>
  );
};

export default NeighborhoodPage;