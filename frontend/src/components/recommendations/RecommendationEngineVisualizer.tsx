import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, LineChart, Line, XAxis, YAxis, CartesianGrid, Legend, BarChart, Bar } from 'recharts';

const RecommendationEngineVisualizer = () => {
  const [currentTab, setCurrentTab] = useState('overview');
  const [isAnimating, setIsAnimating] = useState(false);
  
  // Start animation effect
  const startAnimation = () => {
    setIsAnimating(true);
    setTimeout(() => setIsAnimating(false), 3000);
  };

  useEffect(() => {
    // Start animation on first load
    startAnimation();
  }, []);

  // Algorithm weight data for visualization
  const algorithmWeights = [
    { name: 'Collaborative Filtering', value: 35 },
    { name: 'Content-Based', value: 30 },
    { name: 'Location-Based', value: 25 },
    { name: 'Temporal', value: 10 },
  ];
  
  // Colors for pie chart
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];
  
  // Engagement metrics over time
  const engagementData = [
    { month: 'Jan', clicks: 1200, saves: 800, shares: 400 },
    { month: 'Feb', clicks: 1900, saves: 1200, shares: 600 },
    { month: 'Mar', clicks: 2400, saves: 1600, shares: 900 },
    { month: 'Apr', clicks: 1800, saves: 1400, shares: 700 },
    { month: 'May', clicks: 2200, saves: 1700, shares: 800 },
    { month: 'Jun', clicks: 2600, saves: 2000, shares: 1000 },
  ];
  
  // Neighborhood popularity data
  const neighborhoodData = [
    { name: 'Downtown Core', value: 85 },
    { name: 'Distillery District', value: 72 },
    { name: 'Kensington Market', value: 68 },
    { name: 'Queen West', value: 65 },
    { name: 'Yorkville', value: 62 },
    { name: 'The Beaches', value: 48 },
    { name: 'Liberty Village', value: 45 },
  ];
  
  // Recommendation pipeline steps data
  const pipelineData = [
    { name: 'Data Collection', count: 100 },
    { name: 'Feature Extraction', count: 90 },
    { name: 'User Profiling', count: 80 },
    { name: 'Model Training', count: 70 },
    { name: 'Hybrid Blending', count: 60 },
    { name: 'Location Enhancement', count: 50 },
    { name: 'Seasonal Adjustment', count: 40 },
    { name: 'Final Ranking', count: 30 },
  ];
  
  // Custom tooltip for pie chart
  const CustomTooltip: React.FC<{ active?: boolean; payload?: { name: string; value: number }[] }> = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-2 border border-gray-200 rounded shadow-sm">
          <p className="font-medium">{payload[0].name}</p>
          <p className="text-gray-700">{`Weight: ${payload[0].value}%`}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Toronto Trendspotter Recommendation Engine</h2>
      
      {/* Tabs */}
      <div className="flex mb-6 border-b">
        <button 
          className={`px-4 py-2 font-medium ${currentTab === 'overview' ? 'text-primary-600 border-b-2 border-primary-500' : 'text-gray-600 hover:text-gray-800'}`}
          onClick={() => setCurrentTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`px-4 py-2 font-medium ${currentTab === 'algorithms' ? 'text-primary-600 border-b-2 border-primary-500' : 'text-gray-600 hover:text-gray-800'}`}
          onClick={() => setCurrentTab('algorithms')}
        >
          Algorithm Mix
        </button>
        <button 
          className={`px-4 py-2 font-medium ${currentTab === 'engagement' ? 'text-primary-600 border-b-2 border-primary-500' : 'text-gray-600 hover:text-gray-800'}`}
          onClick={() => setCurrentTab('engagement')}
        >
          Engagement
        </button>
        <button 
          className={`px-4 py-2 font-medium ${currentTab === 'locations' ? 'text-primary-600 border-b-2 border-primary-500' : 'text-gray-600 hover:text-gray-800'}`}
          onClick={() => setCurrentTab('locations')}
        >
          Locations
        </button>
      </div>
      
      {/* Tab content */}
      <div className="h-96">
        {currentTab === 'overview' && (
          <div className="h-full">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 h-full">
              <div className="bg-gray-50 rounded-lg p-4 flex flex-col">
                <h3 className="text-lg font-semibold mb-2">Recommendation Flow</h3>
                <p className="text-gray-600 mb-4">Visual representation of the data pipeline powering Toronto-specific recommendations.</p>
                <div className="flex-grow">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={pipelineData}
                      layout="vertical"
                      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" />
                      <YAxis dataKey="name" type="category" width={120} />
                      <Tooltip />
                      <Bar 
                        dataKey="count" 
                        fill="#8884d8" 
                        barSize={20} 
                        animationDuration={2000}
                        animationBegin={300}
                        isAnimationActive={isAnimating}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4 flex flex-col">
                <h3 className="text-lg font-semibold mb-2">How It Works</h3>
                <div className="space-y-3 text-gray-700">
                  <p><strong>1. Data Collection:</strong> We gather Toronto-specific content from multiple sources.</p>
                  <p><strong>2. Feature Extraction:</strong> Our ML system extracts visual, textual, and location features.</p>
                  <p><strong>3. User Profiling:</strong> We analyze your interactions to understand your preferences.</p>
                  <p><strong>4. Hybrid Approach:</strong> We combine collaborative filtering with content-based methods.</p>
                  <p><strong>5. Location Enhancement:</strong> Recommendations are boosted based on Toronto neighborhoods.</p>
                  <p><strong>6. Seasonal Adaptation:</strong> Content relevance shifts with Toronto's seasons.</p>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {currentTab === 'algorithms' && (
          <div className="h-full">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 h-full">
              <div className="bg-gray-50 rounded-lg p-4 flex flex-col">
                <h3 className="text-lg font-semibold mb-2">Algorithm Weight Distribution</h3>
                <p className="text-gray-600 mb-4">Our hybrid approach combines multiple algorithms for optimal recommendations.</p>
                <div className="flex-grow">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={algorithmWeights}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        animationDuration={2000}
                        animationBegin={300}
                        isAnimationActive={isAnimating}
                      >
                        {algorithmWeights.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip content={<CustomTooltip />} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4 flex flex-col">
                <h3 className="text-lg font-semibold mb-2">Algorithm Descriptions</h3>
                <div className="space-y-3 text-gray-700">
                  <p><strong className="text-blue-500">Collaborative Filtering (35%):</strong> Recommends items based on preferences of users with similar taste patterns.</p>
                  <p><strong className="text-green-500">Content-Based (30%):</strong> Analyzes item features (images, descriptions, tags) to find similar content.</p>
                  <p><strong className="text-yellow-500">Location-Based (25%):</strong> Prioritizes content from Toronto neighborhoods you prefer or have interacted with.</p>
                  <p><strong className="text-orange-500">Temporal (10%):</strong> Adjusts recommendations based on time of year, upcoming events, and seasonal relevance.</p>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {currentTab === 'engagement' && (
          <div className="h-full">
            <div className="bg-gray-50 rounded-lg p-4 h-full">
              <h3 className="text-lg font-semibold mb-2">User Engagement Metrics</h3>
              <p className="text-gray-600 mb-4">Tracking interaction patterns helps us improve recommendations over time.</p>
              <div className="h-4/5">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={engagementData}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey="clicks" 
                      stroke="#8884d8" 
                      activeDot={{ r: 8 }} 
                      animationDuration={2000}
                      animationBegin={300}
                      isAnimationActive={isAnimating}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="saves" 
                      stroke="#82ca9d" 
                      animationDuration={2000}
                      animationBegin={600}
                      isAnimationActive={isAnimating}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="shares" 
                      stroke="#ffc658" 
                      animationDuration={2000}
                      animationBegin={900}
                      isAnimationActive={isAnimating}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}
        
        {currentTab === 'locations' && (
          <div className="h-full">
            <div className="bg-gray-50 rounded-lg p-4 h-full">
              <h3 className="text-lg font-semibold mb-2">Neighborhood Popularity</h3>
              <p className="text-gray-600 mb-4">Content engagement across Toronto's most popular neighborhoods.</p>
              <div className="h-4/5">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={neighborhoodData}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis label={{ value: 'Popularity Score', angle: -90, position: 'insideLeft' }} />
                    <Tooltip />
                    <Bar 
                      dataKey="value" 
                      fill="#8884d8" 
                      animationDuration={2000}
                      animationBegin={300}
                      isAnimationActive={isAnimating}
                    >
                      {neighborhoodData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}
      </div>
      
      <div className="mt-6 pt-4 border-t border-gray-200">
        <h3 className="text-lg font-semibold mb-2">Why This Matters for Pinterest</h3>
        <p className="text-gray-700">
          This recommendation engine demonstrates my ability to build scalable, personalized content discovery systems—directly relevant to Pinterest's core product. By combining collaborative filtering with content-based analysis and adding location-specific features, this system delivers the kind of hyper-relevant recommendations that drive user engagement.
        </p>
      </div>

      <div className="mt-4 flex justify-end">
        <button 
          onClick={startAnimation} 
          className="px-4 py-2 bg-primary-500 text-white rounded hover:bg-primary-600 transition-colors"
        >
          Refresh Visualization
        </button>
      </div>
    </div>
  );
};

export default RecommendationEngineVisualizer;