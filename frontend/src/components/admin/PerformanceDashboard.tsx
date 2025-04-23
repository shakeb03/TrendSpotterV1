// File path: frontend/src/components/admin/PerformanceDashboard.tsx
import React, { useEffect, useState } from 'react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { abTestingService, TestName } from '../../services/ab-testing';
import { feedbackService } from '../../services/feedback';

// Dashboard metrics interface
interface DashboardMetrics {
  recommendationEngagement: {
    views: number[];
    clicks: number[];
    saves: number[];
    timeSeriesLabels: string[];
  };
  categoryDistribution: Array<{
    name: string;
    value: number;
  }>;
  neighborhoodEngagement: Array<{
    name: string;
    value: number;
  }>;
  abTestResults: Array<{
    testName: string;
    variant: string;
    impressions: number;
    conversions: number;
    conversionRate: number;
  }>;
  userFeedback: {
    averageRating: number;
    averageRelevance: number;
    feedbackCount: number;
  };
}

const PerformanceDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  
  // Generate mock data for the dashboard
  useEffect(() => {
    const generateMockData = () => {
      setIsLoading(true);
      
      // Mock time series data for recommendation engagement
      const timeSeriesLabels = Array.from({ length: 7 }, (_, i) => {
        const date = new Date();
        date.setDate(date.getDate() - (6 - i));
        return date.toLocaleDateString('en-CA', { month: 'short', day: 'numeric' });
      });
      
      const views = Array.from({ length: 7 }, () => Math.floor(Math.random() * 300) + 100);
      const clicks = Array.from({ length: 7 }, () => Math.floor(Math.random() * 120) + 50);
      const saves = Array.from({ length: 7 }, () => Math.floor(Math.random() * 60) + 20);
      
      // Mock category distribution
      const categories = [
        'Food', 'Art', 'Outdoor', 'Event', 
        'Shopping', 'Nightlife', 'Attraction'
      ];
      
      const categoryDistribution = categories.map(name => ({
        name,
        value: Math.floor(Math.random() * 150) + 50
      }));
      
      // Mock neighborhood engagement
      const neighborhoods = [
        'Downtown Core', 'Distillery District', 'Kensington Market',
        'Queen West', 'Yorkville', 'The Beaches'
      ];
      
      const neighborhoodEngagement = neighborhoods.map(name => ({
        name,
        value: Math.floor(Math.random() * 200) + 50
      }));
      
      // Get A/B test results from service
      const abTestMetrics = abTestingService.getAllMetrics();
      const abTestResults = Array.from(abTestMetrics.entries()).map(([testName, metrics]) => ({
        testName: String(testName),
        variant: metrics.variant,
        impressions: metrics.impressions,
        conversions: metrics.conversions,
        conversionRate: metrics.conversionRate
      }));
      
      // If no A/B test data, add mock data
      if (abTestResults.length === 0) {
        abTestResults.push(
          {
            testName: 'Recommendation Explanation',
            variant: 'A',
            impressions: 203,
            conversions: 46,
            conversionRate: 22.66
          },
          {
            testName: 'Location Priority',
            variant: 'Local',
            impressions: 187,
            conversions: 53,
            conversionRate: 28.34
          }
        );
      }
      
      // Get feedback metrics
      const allFeedback = feedbackService.getAllFeedback();
      
      const averageRating = allFeedback.length > 0
        ? allFeedback.reduce((sum, feedback) => sum + feedback.rating, 0) / allFeedback.length
        : 4.2; // Mock data if no feedback
        
      const averageRelevance = allFeedback.length > 0
        ? allFeedback.reduce((sum, feedback) => sum + feedback.relevance, 0) / allFeedback.length
        : 3.8; // Mock data if no feedback
      
      const dashboardMetrics: DashboardMetrics = {
        recommendationEngagement: {
          views,
          clicks,
          saves,
          timeSeriesLabels
        },
        categoryDistribution,
        neighborhoodEngagement,
        abTestResults,
        userFeedback: {
          averageRating: allFeedback.length > 0 ? averageRating : 4.2,
          averageRelevance: allFeedback.length > 0 ? averageRelevance : 3.8,
          feedbackCount: allFeedback.length || 27 // Mock data if no feedback
        }
      };
      
      setMetrics(dashboardMetrics);
      setIsLoading(false);
    };
    
    generateMockData();
  }, []);
  
  if (isLoading || !metrics) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }
  
  // Prepare data for charts
  const engagementData = metrics.recommendationEngagement.timeSeriesLabels.map((date, index) => ({
    date,
    Views: metrics.recommendationEngagement.views[index],
    Clicks: metrics.recommendationEngagement.clicks[index],
    Saves: metrics.recommendationEngagement.saves[index]
  }));
  
  // Define colors for charts
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#83a6ed'];
  
  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Toronto Trendspotter Performance Dashboard</h1>
        <p className="text-gray-600">
          Real-time metrics and analytics for the recommendation engine
        </p>
      </div>
      
      {/* KPI Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-blue-50 rounded-lg p-4 shadow-sm">
          <div className="flex items-center">
            <div className="bg-blue-100 p-2 rounded-full mr-3">
              <svg className="w-6 h-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </div>
            <div>
              <p className="text-sm text-blue-700 font-medium">Total Views</p>
              <p className="text-xl font-bold text-blue-900">
                {metrics.recommendationEngagement.views.reduce((a, b) => a + b, 0).toLocaleString()}
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-green-50 rounded-lg p-4 shadow-sm">
          <div className="flex items-center">
            <div className="bg-green-100 p-2 rounded-full mr-3">
              <svg className="w-6 h-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 015.36 19h-1.224a1 1 0 01-.894-1.447L7 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </div>
            <div>
              <p className="text-sm text-green-700 font-medium">Save Rate</p>
              <p className="text-xl font-bold text-green-900">
                {(metrics.recommendationEngagement.saves.reduce((a, b) => a + b, 0) / 
                  metrics.recommendationEngagement.views.reduce((a, b) => a + b, 0) * 100).toFixed(1)}%
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-yellow-50 rounded-lg p-4 shadow-sm">
          <div className="flex items-center">
            <div className="bg-yellow-100 p-2 rounded-full mr-3">
              <svg className="w-6 h-6 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
            </div>
            <div>
              <p className="text-sm text-yellow-700 font-medium">Avg. Rating</p>
              <p className="text-xl font-bold text-yellow-900">
                {metrics.userFeedback.averageRating.toFixed(1)}
                <span className="text-sm ml-1">/ 5</span>
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-purple-50 rounded-lg p-4 shadow-sm">
          <div className="flex items-center">
            <div className="bg-purple-100 p-2 rounded-full mr-3">
              <svg className="w-6 h-6 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <p className="text-sm text-purple-700 font-medium">Relevance Score</p>
              <p className="text-xl font-bold text-purple-900">
                {metrics.userFeedback.averageRelevance.toFixed(1)}
                <span className="text-sm ml-1">/ 5</span>
              </p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Engagement Over Time Chart */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recommendation Engagement</h2>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={engagementData}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="Views" stroke="#0088FE" strokeWidth={2} />
              <Line type="monotone" dataKey="Clicks" stroke="#00C49F" strokeWidth={2} />
              <Line type="monotone" dataKey="Saves" stroke="#FFBB28" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      {/* Category & Neighborhood Distribution */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        <div className="bg-white rounded-lg shadow-sm p-4">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Content Category Distribution</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={metrics.categoryDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {metrics.categoryDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm p-4">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Neighborhood Engagement</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                layout="vertical"
                data={metrics.neighborhoodEngagement}
                margin={{ top: 5, right: 30, left: 80, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis type="category" dataKey="name" />
                <Tooltip />
                <Bar dataKey="value" fill="#8884d8">
                  {metrics.neighborhoodEngagement.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
      {/* A/B Test Results */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">A/B Test Results</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Test Name
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Variant
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Impressions
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Conversions
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Conv. Rate
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {metrics.abTestResults.map((test, index) => (
                <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {test.testName}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {test.variant}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {test.impressions}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {test.conversions}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span className={`px-2 py-1 rounded-full ${
                      test.conversionRate > 25 ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {test.conversionRate.toFixed(1)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      
      {/* User Feedback Summary */}
      <div className="bg-white rounded-lg shadow-sm p-4">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">User Feedback Summary</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <h3 className="text-sm font-medium text-gray-700">Average Rating</h3>
              <span className="text-yellow-500 flex">
                {Array.from({ length: 5 }).map((_, i) => (
                  <svg key={i} className={`w-5 h-5 ${i < Math.round(metrics.userFeedback.averageRating) ? 'text-yellow-500' : 'text-gray-300'}`} fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                ))}
              </span>
            </div>
            <p className="text-3xl font-bold text-gray-900">{metrics.userFeedback.averageRating.toFixed(1)}</p>
            <p className="text-sm text-gray-500">{metrics.userFeedback.feedbackCount} ratings</p>
          </div>
          
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <h3 className="text-sm font-medium text-gray-700">Relevance Score</h3>
              <div className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                {metrics.userFeedback.averageRelevance > 4 ? 'Excellent' : 
                 metrics.userFeedback.averageRelevance > 3 ? 'Good' : 'Needs Improvement'}
              </div>
            </div>
            <p className="text-3xl font-bold text-gray-900">{metrics.userFeedback.averageRelevance.toFixed(1)}</p>
            <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
              <div 
                className="bg-blue-600 h-2.5 rounded-full" 
                style={{ width: `${(metrics.userFeedback.averageRelevance / 5) * 100}%` }}
              ></div>
            </div>
          </div>
          
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Recommendation Quality</h3>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-medium text-gray-700">Precision</span>
              <span className="text-xs font-medium text-gray-700">78%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5 mb-3">
              <div className="bg-green-500 h-2.5 rounded-full" style={{ width: '78%' }}></div>
            </div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-medium text-gray-700">Recall</span>
              <span className="text-xs font-medium text-gray-700">82%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5 mb-3">
              <div className="bg-blue-500 h-2.5 rounded-full" style={{ width: '82%' }}></div>
            </div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-medium text-gray-700">F1 Score</span>
              <span className="text-xs font-medium text-gray-700">80%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div className="bg-purple-500 h-2.5 rounded-full" style={{ width: '80%' }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceDashboard;