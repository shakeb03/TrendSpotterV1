# Toronto Trendspotter

A machine learning-powered tool that analyzes Pinterest-like user behavior and local Toronto trends to recommend hyper-relevant visual content to users.

## Overview

Toronto Trendspotter is a recommendation engine that combines visual content analysis with location-based trends to provide Toronto users with personalized recommendations. The system analyzes user interactions with visual content (similar to Pinterest pins) and incorporates local Toronto events, businesses, and seasonal activities to create a hyper-relevant discovery experience.

## Features

- **Pinterest-like Data Analysis**: Processes user interactions with visual content
- **Toronto-Specific Recommendations**: Incorporates local events, businesses, and seasonal activities
- **Machine Learning Models**: Uses collaborative filtering and content-based approaches
- **A/B Testing Framework**: Tests different recommendation strategies
- **Interactive UI**: Pinterest-inspired interface for visual content discovery
- **Performance Dashboard**: Visualizes recommendation metrics and system performance

## Technical Architecture

The project consists of four main components:

1. **Data Collection & Preprocessing**:
   - Scrapes Pinterest-like engagement data
   - Integrates Toronto-specific datasets
   - Preprocesses and transforms data for ML models

2. **Machine Learning Models**:
   - Recommendation system using collaborative filtering
   - Content-based filtering with NLP for pin descriptions
   - Location-aware recommendations prioritizing Toronto content

3. **A/B Testing Framework**:
   - Tests different recommendation strategies
   - Simulates user feedback to improve accuracy

4. **Visualization & User Interface**:
   - Pinterest-style UI for content discovery
   - Performance dashboard for metrics visualization

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/toronto-trendspotter.git
cd toronto-trendspotter

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and database configuration

# Initialize database
python src/utils/initialize_db.py
```

## Usage

```bash
# Start the API server
python run_api.py

# In a separate terminal, start the frontend
cd frontend
npm install
npm start
```

Visit `http://localhost:3000` to access the Toronto Trendspotter interface.

## Development

### Project Structure

```
toronto-trendspotter/
├── data/                      # For datasets and raw data
│   ├── raw/                   # Original scraped data
│   └── processed/             # Cleaned and processed data
├── notebooks/                 # Jupyter notebooks for exploration
├── src/                       # Source code
│   ├── api/                   # API endpoints
│   │   └── recommendation_api.py   # FastAPI implementation
│   ├── data/                  # Data collection and processing
│   │   ├── collectors/        # Data collection modules
│   │   ├── models/            # Data models
│   │   └── processing/        # Feature extraction
│   ├── models/                # ML models
│   │   ├── collaborative_filtering.py
│   │   ├── content_based.py
│   │   └── hybrid_recommender.py
│   └── utils/                 # Utility functions
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API communication
│   │   └── utils/             # Utility functions
├── tests/                     # Unit tests
├── docs/                      # Documentation
├── requirements.txt           # Python dependencies
└── README.md                  # Project overview
```

### Running Tests

```bash
# Backend tests
pytest

# Frontend tests
cd frontend
npm test
```

## Key Components

- **ContentCard**: Pinterest-style visual content display
- **TorontoMap**: Interactive neighborhood-based discovery
- **RecommendationSection**: Dynamically loaded recommendation groups
- **SeasonalTheme**: Season-aware content highlighting
- **PerformanceDashboard**: Real-time recommendation analytics

## Recommendation Engine

The heart of Toronto Trendspotter is its sophisticated recommendation engine, which uses a hybrid approach combining:

1. **Collaborative Filtering**: Identifies patterns in user-item interactions
2. **Content-Based Analysis**: Extracts and utilizes features from images and text
3. **Location-Aware Recommendations**: Prioritizes content from neighborhoods users prefer
4. **Seasonal Relevance**: Adjusts recommendations based on time of year and seasonal events

## License

[MIT License](LICENSE)
