# Toronto Trendspotter

![Toronto Trendspotter](https://images.unsplash.com/photo-1610509659326-b35b9b15bf51?fm=jpg&q=60&w=3000&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8dG9yb250byUyMHNreWxpbmV8ZW58MHx8MHx8fDA%3D)

## A Machine Learning-Powered Local Content Discovery Platform

Toronto Trendspotter is an advanced recommendation engine that delivers personalized content discovery for Toronto's events, places, and experiences. By leveraging collaborative filtering, content-based analysis, and location-aware algorithms, the platform creates hyper-relevant recommendations tailored to individual preferences and local context.

### [Live Demo](https://trendspotter-v1.vercel.app/) | [GitHub Repository](https://github.com/shakeb03/TrendSpotterV1)

> **Note:** The current version uses a curated mock dataset. Integration with live data sources is in progress.

## Features

* **Personalized Recommendations**: Multi-model hybrid recommendation system that learns from user preferences, content similarity, and interaction patterns
* **Location-Aware Discovery**: Neighborhood-specific content recommendations that prioritize local relevance
* **Seasonal Adaptations**: Content suggestions that adapt based on Toronto's seasons and upcoming events
* **Interactive Map Exploration**: Visual discovery through an interactive neighborhood map
* **A/B Testing Framework**: Built-in experimentation platform to continuously optimize recommendations
* **Responsive UI**: Fully responsive design for seamless experience across devices

## Technical Architecture

### System Overview

Toronto Trendspotter implements a comprehensive recommendation engine using multiple algorithms that work together to provide highly relevant content suggestions.

![System Architecture](https://via.placeholder.com/800x400?text=Toronto+Trendspotter+Architecture)

### Backend Architecture

The backend is built on a Python foundation with FastAPI and organized in a modular architecture:

#### Recommendation Engine

The core of the system is a sophisticated hybrid recommendation engine that combines three distinct approaches:

1. **Collaborative Filtering (35%)**

   * Item-based approach that finds patterns across user interactions
   * Identifies content that users with similar preferences have enjoyed
   * Reduces cold start problems by leveraging collective wisdom

2. **Content-Based Filtering (30%)**

   * Analyzes content features (text, categories, visual elements)
   * Creates feature vectors for similarity calculations
   * Incorporates NLP for text understanding and feature extraction

3. **Location-Based Enhancements (25%)**

   * Toronto-specific location model for neighborhood relevance
   * Geospatial awareness for proximity recommendations
   * Neighborhood affinity modeling based on user preferences

4. **Temporal/Seasonal Adjustments (10%)**

   * Seasonal boosting for time-relevant content
   * Event proximity factoring based on dates
   * Trending content identification

The recommendation pipeline follows these stages:

1. **Data Collection & Preprocessing**
2. **Feature Engineering & Extraction**
3. **User Profiling**
4. **Model Training & Hybridization**
5. **Content Ranking & Serving**
6. **Feedback Collection & Model Refinement**

#### Database Design

The system uses MongoDB Atlas for flexible document storage with the following collections:

* `users`: User profiles and preferences
* `content`: Content items (pins, events, places)
* `interactions`: User-content interaction tracking
* `toronto_events`: Toronto-specific event data
* `feature_vectors`: Computed feature vectors for ML models
* `ml_models`: Model metadata and parameters

#### API Layer

The recommendation API is built with FastAPI and provides endpoints for:

* User-specific recommendations
* Location-based content discovery
* Similar content retrieval
* Trending and popular content
* Interaction logging

### Frontend Architecture

The React frontend is built with TypeScript and organized using a component-based architecture:

* **Context Providers**: Global state management (user authentication, preferences)
* **Page Components**: Full page views for main application routes
* **Feature Components**: Reusable UI components for content display, search, maps
* **Service Layer**: API integration, data fetching, and client-side utilities
* **Utility Functions**: Formatting, data processing, and helper functions

#### Key Frontend Technologies

* **React & TypeScript**: Type-safe component development
* **React Router**: Application routing
* **React Query**: Data fetching, caching, and state management
* **Leaflet**: Interactive map integration
* **Recharts**: Data visualization for analytics
* **Tailwind CSS**: Utility-first styling

### ML Pipeline

The machine learning pipeline incorporates:

1. **Text Processing**: NLP techniques for content understanding
2. **Feature Engineering**: Extraction of relevant features from content
3. **Model Training**: Collaborative and content-based models
4. **Model Evaluation**: Metrics calculation and performance assessment
5. **Hybrid Blending**: Weighted combination of model outputs
6. **Location Enhancement**: Toronto-specific geographic boosting
7. **Seasonal Adjustment**: Time-based relevance scoring

### Deployment Architecture

* **Backend**: Hosted on Render with auto-scaling capabilities
* **Frontend**: Deployed on Vercel for global CDN distribution
* **Database**: MongoDB Atlas for cloud-based document storage
* **CI/CD**: GitHub Actions for automated testing and deployment

## Development Setup

### Prerequisites

* Python 3.9+
* Node.js 16+
* MongoDB Atlas account

### Backend Setup

1. Clone the repository

   ```bash
   git clone https://github.com/shakeb03/TrendSpotterV1.git
   cd TrendSpotterV1
   ```

2. Set up a virtual environment

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables

   ```bash
   cp .env.example .env
   # Edit .env with your MongoDB connection string and settings
   ```

5. Run the database initialization

   ```bash
   python src/utils/initialize_db.py
   ```

6. Start the API server

   ```bash
   python run_api.py
   ```

### Frontend Setup

1. Navigate to the frontend directory

   ```bash
   cd frontend
   ```

2. Install dependencies

   ```bash
   npm install
   ```

3. Configure environment variables

   ```bash
   cp .env.example .env
   # Set REACT_APP_API_BASE_URL to your backend URL
   ```

4. Start the development server

   ```bash
   npm start
   ```

## Machine Learning Insights

Toronto Trendspotter demonstrates several advanced ML techniques:

1. **Hybrid Recommender Systems**: Weighted combination of multiple recommendation strategies
2. **Feature Vector Creation**: Extraction of meaningful features from heterogeneous data
3. **Similarity Computation**: Cosine similarity for content relationships
4. **Cold Start Handling**: Multiple strategies to provide quality recommendations for new users
5. **Contextual Boosting**: Location and temporal factors incorporated into recommendation scoring
6. **A/B Testing Framework**: Experimental design for algorithm optimization

## Project Structure

```
📆
├─ src
│  ├─ api/                  # API endpoints
│  ├─ data/                 # Data processing
│  │  ├─ collectors/        # Data collection
│  │  ├─ processing/        # Feature extraction
│  │  └─ schemas/           # Data models
│  ├─ models/               # ML recommendation models
│  └─ utils/                # Utilities and tools
├─ frontend
│  ├─ src/
│  │  ├─ components/        # UI components
│  │  ├─ context/           # React context providers
│  │  ├─ pages/             # Page components
│  │  ├─ services/          # API integration
│  │  └─ utils/             # Utilities
├─ docs/                    # Documentation
└─ tests/                   # Test suite
```

## Future Enhancements

* Integration with real-time Toronto event APIs
* Enhanced visual content recommendations
* Advanced personalization features
* Mobile application development
* Social sharing capabilities
* Community contribution features


## About the Author

This project was developed to showcase expertise in machine learning, recommendation systems, and full-stack development. It demonstrates:

* **Machine Learning Engineering**: Building production-ready recommendation algorithms
* **Full-Stack Development**: End-to-end implementation from data processing to user interface
* **Location-Based Services**: Geographic context integration
* **Data Engineering**: Feature extraction and processing pipeline
* **UI/UX Design**: Responsive, intuitive interface design

As a portfolio piece, Toronto Trendspotter highlights how recommendation systems can be tailored to local contexts while maintaining scalable architecture principles similar to those used by companies like Pinterest.

**Connect with me on [LinkedIn](https://www.linkedin.com/in/shakeb03/) if you'd like to discuss the project or collaborate.**

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

© 2025 Toronto Trendspotter. All rights reserved.
