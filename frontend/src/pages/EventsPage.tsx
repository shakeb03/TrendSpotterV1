import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { api } from '../services/api';
import ContentGrid from '../components/content/ContentGrid';

const SEASONS = ['spring', 'summer', 'fall', 'winter', 'all'];

const EventsPage: React.FC = () => {
  const [activeSeason, setActiveSeason] = useState(() => {
    // Default to current season
    const currentSeason = api.getCurrentSeason();
    return currentSeason === 'winter' || currentSeason === 'summer' ? 
      currentSeason : 'all';
  });
  
  const [searchQuery, setSearchQuery] = useState('');
  
  // Fetch all events
  const { data, isLoading, error } = useQuery(
    ['events'],
    async () => {
      const result = await api.getPopularContent(50, 'event');
      return result.recommendations;
    }
  );
  
  // Filter events by season and search query
  const filteredEvents = React.useMemo(() => {
    if (!data) return [];
    
    return data.filter(item => {
      // Season filter
      const seasonMatch = 
        activeSeason === 'all' || 
        item.tags.includes(activeSeason);
      
      // Search filter
      const searchMatch = 
        searchQuery === '' || 
        item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (item.description && item.description.toLowerCase().includes(searchQuery.toLowerCase())) ||
        item.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
      
      return seasonMatch && searchMatch;
    });
  }, [data, activeSeason, searchQuery]);
  
  // Group events by date for UI
  const upcomingEvents = filteredEvents.filter(event => 
    event.event_date && new Date(event.event_date) >= new Date()
  );
  
  // Sort by date
  upcomingEvents.sort((a, b) => {
    if (a.event_date && b.event_date) {
      return new Date(a.event_date).getTime() - new Date(b.event_date).getTime();
    }
    return 0;
  });

  return (
    <div className="space-y-8">
      <div className="space-y-4">
        <h1 className="text-3xl font-bold text-gray-900">Toronto Events</h1>
        <p className="text-gray-600 max-w-3xl">
          Discover upcoming events, festivals, and things to do in Toronto. 
          Filter by season or search for specific events.
        </p>
      </div>
      
      <div>
        {/* Filters */}
        <div className="flex flex-col md:flex-row gap-4 mb-8">
          {/* Season filters */}
          <div className="flex overflow-x-auto pb-2 md:pb-0 scrollbar-hide gap-2">
            {SEASONS.map(season => (
              <button
                key={season}
                onClick={() => setActiveSeason(season)}
                className={`px-4 py-2 rounded-full text-sm capitalize whitespace-nowrap ${
                  activeSeason === season
                    ? 'bg-primary-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {season === 'all' ? 'All Seasons' : season}
              </button>
            ))}
          </div>
          
          {/* Search form */}
          <div className="w-full md:w-auto">
            <div className="relative">
              <input
                type="text"
                className="input-field w-full md:w-64 pl-10"
                placeholder="Search events..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
              />
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" 
                    d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" 
                    clipRule="evenodd" 
                  />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div>
  <>
    {/* Error state */}
    {error && (
      <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
          </div>
          <div className="ml-3">
            <p className="text-sm text-red-700">
              {error instanceof Error
                ? error.message
                : typeof error === 'string'
                ? error
                : 'Error loading events. Please try again later.'}
            </p>
          </div>
        </div>
      </div>
    )}

    {/* Display filter info */}
    <div className="mb-4">
      <p className="text-gray-600 text-sm">
        {upcomingEvents.length === 0 && !isLoading
          ? 'No events found'
          : `Showing ${upcomingEvents.length} events`}
      </p>
    </div>

    {/* Events grid */}
    <ContentGrid
      items={upcomingEvents}
      isLoading={isLoading}
      emptyMessage={
        searchQuery
          ? 'No events match your search'
          : 'No events found for the selected season'
      }
    />
  </>
</div>
      
      <div>
        {/* Featured event venues */}
        <section className="mt-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Popular Event Venues</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {POPULAR_VENUES.map(venue => (
              <div key={venue.name} className="bg-white rounded-xl shadow-md overflow-hidden flex flex-col">
                <div className="h-40 bg-gray-200">
                  <img 
                    src={venue.image} 
                    alt={venue.name} 
                    className="w-full h-full object-cover"
                  />
                </div>
                
                <div className="p-4 flex-grow">
                  <h3 className="font-semibold text-gray-900 mb-1">{venue.name}</h3>
                  <p className="text-gray-600 text-sm">{venue.description}</p>
                  
                  <div className="mt-3 text-sm text-gray-500 flex items-center">
                    <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    {venue.location}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
};

// Popular event venues data
const POPULAR_VENUES = [
  {
    name: 'Scotiabank Arena',
    description: 'Major sports and entertainment venue, home to the Toronto Maple Leafs and Toronto Raptors.',
    image: 'https://images.unsplash.com/photo-1583512603866-910c8542ba9d',
    location: 'Downtown Core'
  },
  {
    name: 'Meridian Hall',
    description: 'Performing arts venue hosting concerts, ballet, theater, and special events.',
    image: 'https://images.unsplash.com/photo-1578944932516-4a83dbee3b99',
    location: 'Downtown Core'
  },
  {
    name: 'The Distillery District',
    description: 'Historic district with cobblestone streets hosting cultural events and festivals.',
    image: 'https://images.unsplash.com/photo-1569880153113-76e33fc52d5f',
    location: 'Distillery District'
  },
  {
    name: 'Nathan Phillips Square',
    description: 'Urban plaza and event space in front of Toronto City Hall.',
    image: 'https://images.unsplash.com/photo-1541199918405-73a419cdf8a4',
    location: 'Downtown Core'
  },
  {
    name: 'Exhibition Place',
    description: 'Large entertainment and exhibition complex hosting the CNE and various events.',
    image: 'https://images.unsplash.com/photo-1566737236500-c8ac43014a67',
    location: 'Exhibition Place'
  },
  {
    name: 'Budweiser Stage',
    description: 'Outdoor amphitheater on the lake hosting concerts during summer months.',
    image: 'https://images.unsplash.com/photo-1501612780327-45045538702b',
    location: 'Harbourfront'
  }
];

export default EventsPage;