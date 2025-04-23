// File path: frontend/src/components/seasonal/SeasonalTheme.tsx
import React, { useState, useEffect } from 'react';

// Define TypeScript interface for upcoming event
interface UpcomingEvent {
  name: string;
  date: string;
}

const SeasonalTheme: React.FC = () => {
  const [currentSeason, setCurrentSeason] = useState<string>('');
  const [upcomingEvent, setUpcomingEvent] = useState<UpcomingEvent | null>(null);
  const [daysUntil, setDaysUntil] = useState<number>(0);
  const [seasonalTips, setSeasonalTips] = useState<string[]>([]);
  
  // Get seasonal tips based on current season
  const getSeasonalTips = (season: string): string[] => {
    switch(season) {
      case 'winter':
        return [
          "Check out the skating rink at Nathan Phillips Square",
          "Visit the Toronto Christmas Market at the Distillery District",
          "Take a winter hike at Rouge Valley"
        ];
      case 'spring':
        return [
          "Explore the cherry blossoms at High Park",
          "Visit the Allan Gardens Conservatory",
          "Check out the Toronto Botanical Garden"
        ];
      case 'summer':
        return [
          "Take a ferry to Toronto Islands",
          "Enjoy the beaches along Lake Ontario",
          "Check out the outdoor patios in Kensington Market"
        ];
      case 'fall':
        return [
          "See the fall colors at Don Valley",
          "Visit Evergreen Brick Works Farmers' Market",
          "Take a scenic drive through the Don Valley Parkway"
        ];
      default:
        return [];
    }
  };
  
  useEffect(() => {
    // Get current season
    const getCurrentSeason = (): string => {
      const month = new Date().getMonth();
      if (month >= 2 && month <= 4) return 'spring';
      if (month >= 5 && month <= 7) return 'summer';
      if (month >= 8 && month <= 10) return 'fall';
      return 'winter';
    };
    
    const season = getCurrentSeason();
    setCurrentSeason(season);
    
    // Set upcoming event based on season
    const today = new Date();
    let eventDate = new Date();
    let eventName = '';
    
    switch(season) {
      case 'winter':
        // Winter Festival
        eventDate = new Date(today.getFullYear(), 1, 15); // Feb 15
        eventName = 'Toronto Winter Festival';
        break;
      case 'spring':
        // Cherry Blossom Festival
        eventDate = new Date(today.getFullYear(), 4, 5); // May 5
        eventName = 'High Park Cherry Blossom Festival';
        break;
      case 'summer':
        // Toronto Fringe Festival
        eventDate = new Date(today.getFullYear(), 6, 10); // July 10
        eventName = 'Toronto Fringe Festival';
        break;
      case 'fall':
        // Nuit Blanche
        eventDate = new Date(today.getFullYear(), 9, 5); // Oct 5
        eventName = 'Nuit Blanche Toronto';
        break;
      default:
        eventDate = today;
    }
    
    // If event date has passed, set it to next year
    if (eventDate < today) {
      eventDate.setFullYear(today.getFullYear() + 1);
    }
    
    // Calculate days until event
    const diffTime = Math.abs(eventDate.getTime() - today.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    setUpcomingEvent({
      name: eventName,
      date: eventDate.toLocaleDateString('en-CA', { month: 'long', day: 'numeric' })
    });
    setDaysUntil(diffDays);
    
    // Set seasonal tips
    const tips = getSeasonalTips(season);
    setSeasonalTips(tips);
  }, []);
  
  // Interface for seasonal styles
  interface SeasonalStyle {
    gradient: string;
    accentColor: string;
    bgColor: string;
    borderColor: string;
    icon: React.ReactNode;
  }
  
  // Get season-specific colors and styling
  const getSeasonalStyles = (): SeasonalStyle => {
    switch(currentSeason) {
      case 'winter':
        return {
          gradient: 'from-blue-500 to-indigo-600',
          accentColor: 'text-blue-500',
          bgColor: 'bg-blue-50',
          borderColor: 'border-blue-200',
          icon: (
            <svg className="w-6 h-6 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 2a.75.75 0 01.75.75v.731a2 2 0 01-1.257 1.856l-.496.22a1 1 0 00-.5.866V7a1 1 0 001 1h2.5a1 1 0 01.8.4l.739 1.478a1 1 0 001.924-.358l.5-3a1 1 0 00-.8-1.12L13 5a1 1 0 01-.8-1 2 2 0 112 2 1 1 0 011 1 1 1 0 01-1 1h-6.8a1 1 0 00-.916.599l-1.85 3.7a1 1 0 00-.075.38V15a1 1 0 00.925.994l10.002.006a1 1 0 00.897-.585l1.935-4.192A3.48 3.48 0 0019 9.5 3.5 3.5 0 0015.5 6h-.443a.959.959 0 01-.906-.664l-.5-1.5A1 1 0 0012.75 3h-2.5a.75.75 0 01-.75-.75v-.5A.75.75 0 0110 1z" />
            </svg>
          )
        };
      case 'spring':
        return {
          gradient: 'from-green-400 to-teal-500',
          accentColor: 'text-green-500',
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200',
          icon: (
            <svg className="w-6 h-6 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path d="M15.98 1.804a1 1 0 00-1.96 0l-.24 1.192a1 1 0 01-.784.785l-1.192.238a1 1 0 000 1.962l1.192.238a1 1 0 01.785.785l.238 1.192a1 1 0 001.962 0l.238-1.192a1 1 0 01.785-.785l1.192-.238a1 1 0 000-1.962l-1.192-.238a1 1 0 01-.785-.785l-.238-1.192zM6.949 5.684a1 1 0 00-1.898 0l-.683 2.051a1 1 0 01-.633.633l-2.051.683a1 1 0 000 1.898l2.051.684a1 1 0 01.633.632l.683 2.051a1 1 0 001.898 0l.683-2.051a1 1 0 01.633-.633l2.051-.683a1 1 0 000-1.898l-2.051-.683a1 1 0 01-.633-.633L6.95 5.684zM13.949 13.684a1 1 0 00-1.898 0l-.184.551a1 1 0 01-.632.633l-.552.183a1 1 0 000 1.898l.552.183a1 1 0 01.633.633l.183.551a1 1 0 001.898 0l.184-.551a1 1 0 01.632-.633l.552-.183a1 1 0 000-1.898l-.552-.184a1 1 0 01-.633-.632l-.183-.551z" />
            </svg>
          )
        };
      case 'summer':
        return {
          gradient: 'from-yellow-400 to-orange-500',
          accentColor: 'text-yellow-600',
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-200',
          icon: (
            <svg className="w-6 h-6 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
            </svg>
          )
        };
      case 'fall':
        return {
          gradient: 'from-red-500 to-orange-400',
          accentColor: 'text-orange-500',
          bgColor: 'bg-orange-50',
          borderColor: 'border-orange-200',
          icon: (
            <svg className="w-6 h-6 text-orange-500" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 2a8 8 0 100 16 8 8 0 000-16zm0 2c-.76 0-1.521.151-2.229.446a4.993 4.993 0 019.114 2.9 5.002 5.002 0 01-6.885 4.654zM12 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          )
        };
      default:
        return {
          gradient: 'from-gray-500 to-gray-600',
          accentColor: 'text-gray-500',
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-200',
          icon: null
        };
    }
  };
  
  const seasonalStyles = getSeasonalStyles();

  return (
    <div className={`rounded-xl overflow-hidden shadow-md mb-8 ${seasonalStyles.bgColor} border ${seasonalStyles.borderColor}`}>
      {/* Header */}
      <div className={`bg-gradient-to-r ${seasonalStyles.gradient} text-white p-4`}>
        <div className="flex items-center">
          {seasonalStyles.icon && (
            <div className="mr-3 bg-white bg-opacity-20 p-2 rounded-full">
              {seasonalStyles.icon}
            </div>
          )}
          <div>
            <h2 className="text-xl font-bold">
              Toronto in {currentSeason.charAt(0).toUpperCase() + currentSeason.slice(1)}
            </h2>
            <p className="text-white text-opacity-90">
              Seasonal recommendations and events
            </p>
          </div>
        </div>
      </div>
      
      {/* Content */}
      <div className="p-4">
        {/* Upcoming event countdown */}
        {upcomingEvent && (
          <div className="flex items-center mb-4 p-3 rounded-lg bg-white shadow-sm">
            <div className={`w-12 h-12 rounded-full ${seasonalStyles.accentColor} bg-opacity-10 flex items-center justify-center mr-3`}>
              <svg className={`w-6 h-6 ${seasonalStyles.accentColor}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <h3 className="font-medium">Coming Up: {upcomingEvent.name}</h3>
              <p className="text-sm text-gray-600">
                {upcomingEvent.date} <span className="font-medium">({daysUntil} days away)</span>
              </p>
            </div>
          </div>
        )}
        
        {/* Seasonal tips */}
        <div className="mb-4">
          <h3 className={`font-medium ${seasonalStyles.accentColor} mb-2`}>
            {currentSeason.charAt(0).toUpperCase() + currentSeason.slice(1)} in Toronto
          </h3>
          <ul className="space-y-2">
            {seasonalTips.map((tip, index) => (
              <li key={index} className="flex items-start">
                <svg className={`w-5 h-5 ${seasonalStyles.accentColor} mr-2 mt-0.5 flex-shrink-0`} fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-700">{tip}</span>
              </li>
            ))}
          </ul>
        </div>
        
        {/* Action buttons */}
        <div className="flex flex-wrap gap-2">
          <button 
            onClick={() => window.location.href = `/explore?season=${currentSeason}`}
            className={`px-4 py-2 rounded-md text-sm font-medium text-white bg-gradient-to-r ${seasonalStyles.gradient} hover:opacity-90 transition-opacity`}
          >
            Explore {currentSeason.charAt(0).toUpperCase() + currentSeason.slice(1)} Content
          </button>
          
          <button 
            onClick={() => window.location.href = '/events'}
            className="px-4 py-2 rounded-md text-sm font-medium border border-gray-300 text-gray-700 hover:bg-gray-50"
          >
            View Upcoming Events
          </button>
        </div>
      </div>
    </div>
  );
};

export default SeasonalTheme;