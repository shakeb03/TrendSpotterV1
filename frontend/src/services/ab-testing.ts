// File path: frontend/src/services/ab-testing.ts

/**
 * A/B Testing Service
 * 
 * This service provides utility functions for implementing A/B tests in the application.
 * It handles test variant assignment, tracking, and analytics.
 */

// Enum for test names to ensure consistency
export enum TestName {
    RECOMMENDATION_EXPLANATION = 'recommendation_explanation',
    HOMEPAGE_LAYOUT = 'homepage_layout',
    SEARCH_INTERFACE = 'search_interface',
    LOCATION_PRIORITY = 'location_priority'
  }
  
  // Interface for test definition
  interface Test {
    name: TestName;
    enabled: boolean;
    variants: string[];
    distribution?: number[]; // Optional weights for variant distribution (must sum to 1)
  }
  
  // Interface for tracked metrics
  interface TestMetrics {
    variant: string;
    impressions: number;
    conversions: number;
    conversionRate: number;
  }
  
  // Define available tests
  const AVAILABLE_TESTS: Test[] = [
    {
      name: TestName.RECOMMENDATION_EXPLANATION,
      enabled: true,
      variants: ['A', 'B'], // A: Simple explanation, B: Detailed explanation
    },
    {
      name: TestName.HOMEPAGE_LAYOUT,
      enabled: false, // Not active yet
      variants: ['Standard', 'LocationFirst', 'PersonalizedFirst'],
      distribution: [0.4, 0.3, 0.3] // 40% standard, 30% location-first, 30% personalized-first
    },
    {
      name: TestName.SEARCH_INTERFACE,
      enabled: true,
      variants: ['Basic', 'Advanced']
    },
    {
      name: TestName.LOCATION_PRIORITY,
      enabled: true,
      variants: ['Global', 'Local'] // Global: general recommendations, Local: Toronto-first
    }
  ];
  
  // Storage key for assigned variants
  const VARIANT_STORAGE_KEY = 'toronto_trendspotter_ab_tests';
  
  // Class for A/B testing
  class ABTestingService {
    // Map to store test variants for the current user
    private assignedVariants: Map<TestName, string> = new Map();
    
    // Map to store test metrics
    private testMetrics: Map<TestName, TestMetrics> = new Map();
    
    constructor() {
      // Load any previously assigned variants from localStorage
      this.loadAssignedVariants();
      
      // Assign variants for tests that don't have them yet
      this.assignMissingVariants();
    }
    
    /**
     * Load previously assigned test variants from localStorage
     */
    private loadAssignedVariants(): void {
      try {
        const savedVariants = localStorage.getItem(VARIANT_STORAGE_KEY);
        
        if (savedVariants) {
          const parsedVariants = JSON.parse(savedVariants);
          
          // Convert from object to Map
          Object.entries(parsedVariants).forEach(([testName, variant]) => {
            this.assignedVariants.set(testName as TestName, variant as string);
          });
        }
      } catch (err) {
        console.error('Error loading A/B test variants:', err);
      }
    }
    
    /**
     * Save assigned variants to localStorage
     */
    private saveAssignedVariants(): void {
      try {
        // Convert Map to object for storage
        const variantsObj: Record<string, string> = {};
        
        this.assignedVariants.forEach((variant, testName) => {
          variantsObj[testName] = variant;
        });
        
        localStorage.setItem(VARIANT_STORAGE_KEY, JSON.stringify(variantsObj));
      } catch (err) {
        console.error('Error saving A/B test variants:', err);
      }
    }
    
    /**
     * Assign variants for tests that don't have them yet
     */
    private assignMissingVariants(): void {
      AVAILABLE_TESTS.forEach(test => {
        // Skip if test is disabled
        if (!test.enabled) return;
        
        // Skip if variant is already assigned
        if (this.assignedVariants.has(test.name)) return;
        
        // Assign a variant based on distribution or randomly
        let variant: string = ''; // Initialize with empty string to fix TypeScript error
        
        if (test.distribution) {
          // Use weighted distribution
          const random = Math.random();
          let cumulativeWeight = 0;
          
          for (let i = 0; i < test.variants.length; i++) {
            cumulativeWeight += test.distribution[i];
            
            if (random <= cumulativeWeight) {
              variant = test.variants[i];
              break;
            }
          }
          
          // Fallback to last variant if something went wrong
          if (!variant) {
            variant = test.variants[test.variants.length - 1];
          }
        } else {
          // Use random assignment with equal distribution
          const randomIndex = Math.floor(Math.random() * test.variants.length);
          variant = test.variants[randomIndex];
        }
        
        // Set the assigned variant
        this.assignedVariants.set(test.name, variant);
        
        // Initialize metrics for this test
        this.testMetrics.set(test.name, {
          variant,
          impressions: 0,
          conversions: 0,
          conversionRate: 0
        });
      });
      
      // Save the assigned variants
      this.saveAssignedVariants();
    }
    
    /**
     * Get the variant assigned to a test for the current user
     * @param testName The name of the test
     * @returns The assigned variant, or null if the test is not enabled
     */
    public getVariant(testName: TestName): string | null {
      // Check if test is enabled
      const test = AVAILABLE_TESTS.find(t => t.name === testName);
      
      if (!test || !test.enabled) {
        return null;
      }
      
      // Return the assigned variant
      return this.assignedVariants.get(testName) || null;
    }
    
    /**
     * Track an impression for a test
     * @param testName The name of the test
     */
    public trackImpression(testName: TestName): void {
      // Check if test is enabled
      const test = AVAILABLE_TESTS.find(t => t.name === testName);
      
      if (!test || !test.enabled) {
        return;
      }
      
      // Get the metrics for this test
      const metrics = this.testMetrics.get(testName);
      
      if (!metrics) {
        return;
      }
      
      // Increment impressions
      metrics.impressions += 1;
      
      // Recalculate conversion rate
      if (metrics.impressions > 0) {
        metrics.conversionRate = (metrics.conversions / metrics.impressions) * 100;
      }
      
      // In a real app, you would send this event to your analytics service
      console.log(`A/B test impression: Test "${testName}", Variant "${metrics.variant}"`);
    }
    
    /**
     * Track a conversion for a test
     * @param testName The name of the test
     */
    public trackConversion(testName: TestName): void {
      // Check if test is enabled
      const test = AVAILABLE_TESTS.find(t => t.name === testName);
      
      if (!test || !test.enabled) {
        return;
      }
      
      // Get the metrics for this test
      const metrics = this.testMetrics.get(testName);
      
      if (!metrics) {
        return;
      }
      
      // Increment conversions
      metrics.conversions += 1;
      
      // Recalculate conversion rate
      if (metrics.impressions > 0) {
        metrics.conversionRate = (metrics.conversions / metrics.impressions) * 100;
      }
      
      // In a real app, you would send this event to your analytics service
      console.log(`A/B test conversion: Test "${testName}", Variant "${metrics.variant}"`);
    }
    
    /**
     * Get metrics for a test
     * @param testName The name of the test
     * @returns The metrics for the test, or null if the test is not enabled
     */
    public getMetrics(testName: TestName): TestMetrics | null {
      return this.testMetrics.get(testName) || null;
    }
    
    /**
     * Get metrics for all active tests
     * @returns A map of test names to metrics
     */
    public getAllMetrics(): Map<TestName, TestMetrics> {
      return new Map(this.testMetrics);
    }
  }
  
  // Export singleton instance
  export const abTestingService = new ABTestingService();
  
  // Export default for convenience
  export default abTestingService;