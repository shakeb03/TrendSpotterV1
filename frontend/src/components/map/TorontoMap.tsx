import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useNavigate } from 'react-router-dom';
import L from 'leaflet';
import './LeafletSetup';

// Fix marker icons in Leaflet with React
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

const DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

// Toronto neighborhoods with location data
interface Neighborhood {
  name: string;
  position: [number, number]; // [lat, lng]
  contentCount?: number;
}

const TORONTO_NEIGHBORHOODS: Neighborhood[] = [
  { name: 'Downtown Core', position: [43.6511, -79.3832] },
  { name: 'Distillery District', position: [43.6503, -79.3597] },
  { name: 'Kensington Market', position: [43.6547, -79.4005] },
  { name: 'The Beaches', position: [43.6762, -79.2995] },
  { name: 'Yorkville', position: [43.6709, -79.3933] },
  { name: 'Queen West', position: [43.6468, -79.4119] },
  { name: 'Liberty Village', position: [43.6371, -79.4208] },
  { name: 'Leslieville', position: [43.6626, -79.3357] },
  { name: 'Little Italy', position: [43.6547, -79.4228] },
  { name: 'Chinatown', position: [43.6529, -79.3975] },
  { name: 'Annex', position: [43.6688, -79.4030] },
  { name: 'Danforth/Greektown', position: [43.6796, -79.3518] },
  { name: 'Harbourfront', position: [43.6382, -79.3767] },
  { name: 'Roncesvalles', position: [43.6393, -79.4487] },
  { name: 'West Queen West', position: [43.6442, -79.4196] }
];

// Center to focus the map on (Toronto)
const TORONTO_CENTER: [number, number] = [43.6532, -79.3832];

// Component to adjust map view based on selectedNeighborhood
const MapViewAdjuster: React.FC<{ 
  center: [number, number];
  zoom: number;
}> = ({ center, zoom }) => {
  const map = useMap();
  
  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);
  
  return null;
};

interface TorontoMapProps {
  selectedNeighborhood?: string;
  onSelectNeighborhood?: (neighborhood: string) => void;
  contentCountByNeighborhood?: Record<string, number>;
  height?: string | number;
}

const TorontoMap: React.FC<TorontoMapProps> = ({ 
  selectedNeighborhood,
  onSelectNeighborhood,
  contentCountByNeighborhood = {},
  height = '500px'
}) => {
  const navigate = useNavigate();
  
  // Find the selected neighborhood data
  const selectedNeighborhoodData = selectedNeighborhood 
    ? TORONTO_NEIGHBORHOODS.find(n => n.name === selectedNeighborhood)
    : null;
  
  // Map center and zoom level
  const center = selectedNeighborhoodData?.position || TORONTO_CENTER;
  const zoom = selectedNeighborhood ? 14 : 12;
  
  // Update neighborhood content counts
  const neighborhoodsWithCounts = TORONTO_NEIGHBORHOODS.map(neighborhood => ({
    ...neighborhood,
    contentCount: contentCountByNeighborhood[neighborhood.name] || 0
  }));

  return (
    <div style={{ height, width: '100%' }} className="rounded-xl overflow-hidden shadow-md">
      <MapContainer 
        center={center}
        zoom={zoom} 
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {/* Adjust the view when selectedNeighborhood changes */}
        <MapViewAdjuster center={center} zoom={zoom} />
        
        {/* Render markers for neighborhoods */}
        {neighborhoodsWithCounts.map((neighborhood) => (
          <Marker 
            key={neighborhood.name}
            position={neighborhood.position}
            eventHandlers={{
              click: () => {
                if (onSelectNeighborhood) {
                  onSelectNeighborhood(neighborhood.name);
                } else {
                  // Navigate to neighborhood page if no handler provided
                  navigate(`/neighborhood/${encodeURIComponent(neighborhood.name)}`);
                }
              }
            }}
          >
            <Popup>
              <div className="text-center">
                <h3 className="font-semibold text-primary-600">{neighborhood.name}</h3>
                {neighborhood.contentCount > 0 && (
                  <p className="text-sm text-gray-600 mt-1">
                    {neighborhood.contentCount} items to explore
                  </p>
                )}
                <button
                  className="mt-2 text-xs text-white bg-primary-500 px-2 py-1 rounded hover:bg-primary-600 w-full"
                  onClick={() => navigate(`/neighborhood/${encodeURIComponent(neighborhood.name)}`)}
                >
                  Explore
                </button>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
};

export default TorontoMap;