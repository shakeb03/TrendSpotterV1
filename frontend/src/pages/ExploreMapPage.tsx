import React from 'react';
import NeighborhoodMapper from '../components/map/NeighborhoodMapper';

const ExploreMapPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-gray-900">Toronto Neighborhood Map</h1>
        <p className="text-gray-600 max-w-3xl">
          Explore Toronto through our interactive map. Click on a neighborhood marker to see 
          popular content and recommendations specific to that area.
        </p>
      </div>
      
      {/* Interactive Map */}
      <NeighborhoodMapper height="600px" itemLimit={12} />
      
      <div className="mt-8 bg-white rounded-xl shadow p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-3">About Toronto's Neighborhoods</h2>
        <p className="text-gray-700 mb-4">
          Toronto is known for its diverse neighborhoods, each with its own unique character and attractions.
          From the historic Distillery District to the bohemian Kensington Market, there's something for everyone 
          in Toronto's distinctive areas.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-1">Downtown Core</h3>
            <p className="text-sm text-gray-600">
              The heart of Toronto featuring skyscrapers, entertainment venues, shopping districts, and cultural attractions.
            </p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-1">Distillery District</h3>
            <p className="text-sm text-gray-600">
              A historic district with Victorian industrial architecture, boutiques, cafes, restaurants, and art galleries.
            </p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-1">Kensington Market</h3>
            <p className="text-sm text-gray-600">
              An eclectic and multicultural neighborhood known for vintage shops, diverse food options, and street art.
            </p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-1">Queen West</h3>
            <p className="text-sm text-gray-600">
              A trendy area with hip boutiques, galleries, restaurants, and bars that showcases Toronto's creative side.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExploreMapPage;