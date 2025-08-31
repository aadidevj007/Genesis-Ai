# Generative Recommendation Engine

A comprehensive recommendation engine that creates realistic customer personas and product suggestions, simulating entire shopping sessions for market simulation and behavioral analysis.

## Features

### 🎯 Core Functionality
- **Personalized Recommendations**: Collaborative filtering and content-based recommendation algorithms
- **Customer Personas**: 9 different persona types with realistic shopping behaviors
- **Shopping Session Simulation**: Generate realistic shopping sessions for behavioral analysis
- **Product Offers**: Dynamic offer generation based on user preferences and product characteristics
- **Market Simulation**: Simulate entire shopping journeys for market research

### 📊 Data Management
- **1000+ Users**: Realistic user profiles with diverse demographics and preferences
- **1000+ Products**: Comprehensive product catalog across 8 categories
- **Purchase History**: Detailed transaction data for analysis
- **MongoDB Integration**: Scalable NoSQL database for flexible data storage

### 🤖 AI-Powered Features
- **Multi-Algorithm Recommendations**: Combines collaborative filtering, content-based, and trending algorithms
- **Persona-Based Suggestions**: Tailored recommendations for new users based on persona type
- **Behavioral Analysis**: Deep insights into shopping patterns and preferences
- **Dynamic Scoring**: Real-time recommendation scoring with multiple factors

## Architecture

```
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   └── database.py          # MongoDB connection
│   ├── models/
│   │   ├── user.py              # User data models
│   │   ├── product.py           # Product data models
│   │   └── purchase.py          # Purchase data models
│   ├── services/
│   │   ├── recommendation_service.py  # Core recommendation logic
│   │   └── persona_service.py         # Persona generation and analysis
│   └── utils/
│       └── data_generator.py    # Sample data generation
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Main React application
│   │   ├── main.jsx             # React entry point
│   │   └── index.css            # Styling
│   └── package.json             # Frontend dependencies
├── data/
│   └── scripts/
│       └── generate_data.py     # Data generation script
└── docker-compose.yml           # Container orchestration
```

## Persona Types

The system supports 9 different customer personas:

1. **Budget Conscious**: Price-sensitive, researches before buying
2. **Luxury Lover**: Premium products, impulse buyer
3. **Tech Enthusiast**: Early adopter, technology-focused
4. **Fashion Forward**: Trend follower, style-conscious
5. **Practical Buyer**: Needs-based, reliable products
6. **Impulse Shopper**: Spontaneous purchases, discount-sensitive
7. **Research Heavy**: Detailed analysis, quality-focused
8. **Brand Loyal**: Specific brand preferences
9. **Trend Follower**: Popular items, social influence

## Product Categories

- **Electronics**: Smartphones, laptops, tablets, accessories, gaming
- **Fashion**: Clothing, shoes, accessories, jewelry
- **Home & Garden**: Furniture, kitchen, decor, garden, tools
- **Books**: Fiction, non-fiction, academic, children's, cookbooks
- **Sports**: Fitness, outdoor, team sports, equipment, clothing
- **Beauty**: Skincare, makeup, haircare, fragrances, tools
- **Toys**: Educational, action figures, board games, puzzles, dolls
- **Automotive**: Parts, accessories, tools, electronics, maintenance

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 16+ (for frontend development)
- Python 3.11+ (for backend development)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd recommendation-engine
```

### 2. Start Services
```bash
# Start MongoDB and backend
docker-compose up -d mongodb mongo-express

# Start backend (in a new terminal)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Generate Sample Data
```bash
# Generate 1000 users, 1000 products, and purchase history
curl -X POST http://localhost:8000/generate-data
```

### 4. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### 5. Access Applications
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MongoDB Express**: http://localhost:8081

## API Endpoints

### Users
- `GET /users` - Get all users
- `GET /users/{user_id}` - Get specific user
- `POST /users` - Create new user

### Products
- `GET /products` - Get all products (with filters)
- `GET /products/{product_id}` - Get specific product
- `POST /products` - Create new product

### Recommendations
- `GET /recommendations/{user_id}` - Get personalized recommendations
- `GET /recommendations/new-user` - Get recommendations for new users

### Persona & Analysis
- `GET /persona/shopping-session/{user_id}` - Generate shopping session
- `GET /persona/analyze/{user_id}` - Analyze user behavior

### Data Management
- `POST /generate-data` - Generate sample data
- `GET /purchases/{user_id}` - Get user purchase history

## Recommendation Algorithms

### 1. Collaborative Filtering
- Finds users with similar purchase patterns
- Recommends products bought by similar users
- Weight: 40% of final score

### 2. Content-Based Filtering
- Matches user preferences with product attributes
- Considers category, price range, and interests
- Weight: 40% of final score

### 3. Trending Products
- Recommends popular products based on recent sales
- Considers ratings and review counts
- Weight: 20% of final score

### 4. Persona-Based (New Users)
- Uses persona type to determine preferences
- Considers income level and demographic factors
- Provides initial recommendations for new users

## Shopping Session Simulation

The system can generate realistic shopping sessions including:

- **Session Events**: Browse, search, view product, add to cart, purchase
- **Behavioral Patterns**: Based on persona type and user characteristics
- **Purchase Probability**: Calculated using multiple factors
- **Time Analysis**: Realistic session duration and event timing

## Data Generation

The system generates realistic data using:

- **Faker Library**: For names, emails, addresses
- **Persona Templates**: For consistent user behavior patterns
- **Category Mapping**: For realistic product categorization
- **Price Ranges**: Based on category and persona type
- **Purchase Patterns**: Realistic buying behavior simulation

## Configuration

### Environment Variables
```bash
MONGODB_URL=mongodb://admin:password123@localhost:27017/
```

### MongoDB Collections
- `users`: User profiles and preferences
- `products`: Product catalog and metadata
- `purchases`: Transaction history and details

## Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Running Tests
```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

## Deployment

### Docker Deployment
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Considerations
- Use environment variables for sensitive data
- Implement proper authentication and authorization
- Set up monitoring and logging
- Configure backup strategies for MongoDB
- Use load balancers for high availability

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the example implementations

---

**Note**: This is a demonstration system. For production use, implement proper security measures, authentication, and data validation.
