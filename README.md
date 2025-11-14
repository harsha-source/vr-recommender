# VR App Recommendation System

A system that recommends Meta Quest VR apps based on user queries with likeliness scores, and stores all recommendations in MongoDB for analytics.

## Features

- **VR App Recommendations**: Get personalized VR app recommendations based on user interests
- **Likeliness Scoring**: Each app gets a score (0.0-1.0) indicating how well it matches the query
- **MongoDB Storage**: All recommendations are automatically stored for analytics
- **Comprehensive Analytics**: Analyze recommendation patterns, popular apps, and user interests

## Installation

### Prerequisites

- Python 3.9+
- MongoDB (local or cloud)
- OpenAI API key

### Quick Setup

1. **Clone and setup**:
   ```bash
   git clone <repository>
   cd vr_recommender
   ./setup.sh  # This will install MongoDB and dependencies
   ```

2. **Set environment variables**:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   export MONGODB_URI="mongodb://localhost:27017/"  # Optional, defaults to localhost
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Manual Setup

1. **Install MongoDB**:
   - macOS: `brew install mongodb-community`
   - Ubuntu: `sudo apt-get install mongodb`
   - Windows: Download from [MongoDB website](https://www.mongodb.com/try/download/community)

2. **Start MongoDB**:
   - macOS: `brew services start mongodb/brew/mongodb-community`
   - Linux: `sudo systemctl start mongod`

3. **Install Python dependencies**:
   ```bash
   pip install pymongo openai
   ```

## Usage

### Basic VR Recommendations

```python
from vr_recommender import HeinzLLMRecommender, StudentQuery

# Initialize recommender
recommender = HeinzLLMRecommender(
    api_key="your-openai-api-key",
    mongodb_uri="mongodb://localhost:27017/"  # Optional
)

# Create a student query
query = StudentQuery(
    query="I want to learn about machine learning and data science",
    interests=["machine learning", "data science", "programming"],
    background="Computer Science student"
)

# Get recommendations
recommendations = recommender.generate_vr_recommendation(query)
print(recommendations)
```

### Running the Demo

```bash
python vr_recommender.py
```

### Analytics

```bash
python analytics.py
```

## Analytics Features

The analytics system provides insights into:

- **Total Recommendations**: Count of all stored recommendations
- **Most Popular Apps**: Apps recommended most frequently
- **Category Analysis**: Which categories are most recommended
- **Interest Patterns**: Which interests lead to most recommendations
- **Query Analysis**: Patterns in user queries
- **High-Score Apps**: Apps that consistently get high likeliness scores
- **Time-based Analysis**: Recommendations over time

### Sample Analytics Output

```
================================================================================
VR RECOMMENDATION ANALYTICS SUMMARY
================================================================================

📊 Total Recommendations Stored: 15

🏆 TOP 10 MOST RECOMMENDED APPS:
--------------------------------------------------
   1. Neural Explorer VR        (8 times)
   2. PolicyVR                  (6 times)
   3. AI Visualization Studio  (5 times)
   4. CodeVR Workspace          (4 times)
   5. Virtual Town Hall         (3 times)

📂 TOP CATEGORIES BY RECOMMENDATIONS:
--------------------------------------------------
  1. Machine Learning          (12 recommendations)
  2. Public Policy             (9 recommendations)
  3. Programming               (7 recommendations)

🎯 TOP INTERESTS:
--------------------------------------------------
  1. machine learning          (8 queries)
  2. data science              (6 queries)
  3. public policy             (4 queries)
```

## Data Storage

Each recommendation is stored in MongoDB with the following structure:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "student_query": {
    "query": "I want to learn about machine learning",
    "interests": ["machine learning", "ai"],
    "background": "Computer Science student"
  },
  "recommendations": [
    {
      "app_name": "Neural Explorer VR",
      "likeliness_score": 1.0,
      "category": "Machine Learning"
    }
  ],
  "total_apps_recommended": 25,
  "high_score_apps": 5,
  "categories": ["Machine Learning", "Programming"]
}
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `MONGODB_URI`: MongoDB connection string (optional, defaults to localhost)

### MongoDB Configuration

The system uses the following MongoDB setup:
- Database: `vr_recommendations`
- Collection: `recommendations`

## VR App Categories

The system includes apps in these categories:

- **Data Science**: Virtualitics VR, DataVR, Spatial Analytics
- **Programming**: CodeVR Workspace, Immersed, Virtual Desktop
- **Public Policy**: PolicyVR, Virtual Town Hall, Spatial Meetings
- **Data Analytics**: DataViz VR, Tableau VR, Analytics Space
- **Machine Learning**: Neural Explorer VR, AI Visualization Studio
- **Cybersecurity**: Cyber Range VR, Security Training VR
- **Project Management**: Horizon Workrooms, Spatial, Arthur VR
- **Design Thinking**: Gravity Sketch, Tilt Brush, ShapesXR
- **Communication**: Spatial Meetings, Horizon Workrooms, MeetinVR
- **Finance**: Finance Simulator VR, Trading Floor VR

## Error Handling

The system gracefully handles:
- MongoDB connection failures (continues without storage)
- OpenAI API errors
- Invalid queries
- Missing dependencies

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

