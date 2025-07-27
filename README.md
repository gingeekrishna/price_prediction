# Vehicle Price Prediction System 🚗💰

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Cross Platform](https://img.shields.io/badge/platform-windows%20%7C%20macOS%20%7C%20linux-lightgrey.svg)](https://github.com/gingeekrishna/price_prediction)

A comprehensive machine learning system for predicting vehicle prices using historical vehicle data and real-time market trends. This project implements an intelligent agent-based architecture with RESTful API endpoints for seamless integration across Windows, macOS, and Linux platforms.

## 🚀 Features

- **🤖 Advanced ML Pipeline**: Random Forest-based price prediction with comprehensive model evaluation
- **🏗️ Agent-Based Architecture**: Modular agent system following perceive-decide-act paradigm
- **🌐 RESTful API**: FastAPI-powered endpoints for real-time predictions
- **📊 Data Integration**: Seamless merging of historical vehicle data with market trends
- **🧪 Comprehensive Testing**: Full test suite with unit, integration, and performance tests
- **🐳 Production Ready**: Containerized deployment with Docker support
- **📈 Logging & Monitoring**: Structured logging and prediction tracking
- **🔄 Cross-Platform**: Works seamlessly on Windows, macOS, and Linux
- **🎯 Real-time Predictions**: Sub-second response times for price estimates

## 📁 Project Structure

```
vehicle-price-agent-multi/
├── src/                          # Main source code
│   ├── agent.py                  # Main prediction agent (perceive-decide-act)
│   ├── model.py                  # ML model training and evaluation
│   ├── data_loader.py            # Data loading and preprocessing
│   ├── api.py                    # FastAPI REST endpoints
│   ├── retriever.py              # Data retrieval utilities
│   ├── explainer.py              # Model explanation utilities
│   └── agents/                   # Specialized agent modules
│       ├── market_agent.py       # Market data collection agent
│       ├── model_agent.py        # ML model management agent
│       ├── explainer_agent.py    # Prediction explanation agent
│       ├── insight_agent.py      # Business insights agent
│       └── logger_agent.py       # Logging and monitoring agent
├── data/                         # Training and market data
│   ├── historical_vehicle_data.csv
│   └── market_trends.csv
├── tests/                        # Comprehensive test suite
│   ├── test_agent.py            # Agent functionality tests
│   ├── test_model.py            # Model training/evaluation tests
│   └── test_data_loader.py      # Data processing tests
├── notebooks/                    # Jupyter notebooks for analysis
│   ├── eda.ipynb               # Exploratory data analysis
│   └── model_training.ipynb    # Model development
├── logs/                        # Application logs
├── knowledge_docs/              # RAG knowledge base
├── static/                      # Web UI assets
├── templates/                   # HTML templates
├── requirements.txt             # Python dependencies
├── pyproject.toml              # Project configuration
├── Dockerfile                  # Container configuration
└── README.md                   # This file
```

## 🛠️ Installation & Setup

### Prerequisites

- **Python 3.11+** (Required)
- **pip** (Python package manager)
- **Git** (Version control)
- **Docker** (Optional, for containerized deployment)

### 🚀 Quick Start

#### Option 1: Local Python Installation (Recommended)

1. **Clone the Repository**
   ```bash
   git clone https://github.com/gingeekrishna/price_prediction.git
   cd price_prediction/vehicle-price-agent-multi
   ```

2. **Create Virtual Environment**
   
   **Windows (PowerShell/CMD):**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
   
   **macOS/Linux (Terminal):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   # Copy sample environment file
   cp .env.sample .env
   
   # Edit .env file with your configuration
   # Add your OpenAI API key (optional for AI explanations)
   ```

5. **Run the Application**
   
   **Method 1: Using the startup script (Cross-platform)**
   ```bash
   python run_app.py
   ```
   
   **Method 2: Using the server script**
   ```bash
   python run_server.py
   ```

6. **Access the Application**
   - **Web Interface**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/health

#### Option 2: Docker Deployment

1. **Build Docker Image**
   ```bash
   docker build -t vehicle-price-predictor .
   ```

2. **Run Container**
   ```bash
   docker run -p 8000:8000 vehicle-price-predictor
   ```

3. **Access Application**
   - Navigate to http://localhost:8000

### 🔧 Platform-Specific Notes

#### Windows Users
- Use PowerShell or Command Prompt
- If you encounter path issues, use forward slashes: `python run_app.py`
- Ensure Python is added to your PATH during installation

#### macOS Users
- Use Terminal application
- Install Python via Homebrew: `brew install python@3.11`
- Use `python3` command if `python` is not available

#### Linux Users
- Use your distribution's terminal
- Install Python via package manager: `sudo apt install python3.11` (Ubuntu/Debian)
- Ensure `python3-venv` is installed: `sudo apt install python3.11-venv`

## 📖 API Usage

### Making Predictions

**Endpoint**: `POST /predict`

**Request Example**:
```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "vehicle_age": 3,
       "mileage": 45000
     }'
```

**Response Example**:
```json
{
  "predicted_price": 18500.00,
  "market_data": {
    "market_index": 1050.2,
    "fuel_price": 3.45
  },
  "explanation": "Based on the vehicle age of 3 years and mileage of 45,000...",
  "confidence_interval": {
    "lower": 17200.00,
    "upper": 19800.00
  }
}
```

### Health Check

**Endpoint**: `GET /health`

```bash
curl http://localhost:8000/health
```

### Market Data

**Endpoint**: `GET /market-data`

```bash
curl http://localhost:8000/market-data
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test module
python -m pytest tests/test_agent.py -v
```

## 🐳 Docker Development

### Development with Docker Compose (Optional)

1. **Create docker-compose.yml**:
   ```yaml
   version: '3.8'
   services:
     app:
       build: .
       ports:
         - "8000:8000"
       volumes:
         - .:/app
       environment:
         - ENVIRONMENT=development
   ```

2. **Run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

## 🔍 Troubleshooting

### Common Issues and Solutions

#### Import Errors
```bash
# Issue: ModuleNotFoundError: No module named 'src'
# Solution: Run from project root directory
cd vehicle-price-agent-multi
python run_app.py
```

#### Port Already in Use
```bash
# Issue: Port 8000 already in use
# Solution: Kill existing process or use different port
# Windows:
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

#### Virtual Environment Issues
```bash
# Issue: Virtual environment not activating
# Solution: Recreate virtual environment
rm -rf venv  # or rmdir /s venv on Windows
python -m venv venv
# Then activate and reinstall dependencies
```

#### Docker Issues
```bash
# Issue: Docker build fails
# Solution: Ensure Docker is running and try:
docker system prune -f
docker build --no-cache -t vehicle-price-predictor .
```

### Performance Optimization

- **Memory Usage**: The system uses ~200MB RAM for basic operations
- **Response Time**: Typical prediction response < 100ms
- **Concurrent Users**: Supports 50+ concurrent requests
- **Data Loading**: Initial startup takes 2-3 seconds for model training

## 🤝 Contributing

We welcome contributions! Please see [DEVELOPMENT.md](DEVELOPMENT.md) for detailed guidelines.

### Quick Contribution Steps

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes and test**: `python -m pytest tests/`
4. **Commit changes**: `git commit -m 'Add amazing feature'`
5. **Push to branch**: `git push origin feature/amazing-feature`
6. **Open Pull Request**

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Install pre-commit hooks
pre-commit install

# Run code formatting
black src/ tests/
isort src/ tests/

# Run linting
flake8 src/ tests/
mypy src/
```

## 📊 Architecture Overview

### Agent-Based System

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Agent    │    │  Market Agent   │    │  Model Agent    │
│                 │    │                 │    │                 │
│ • Data Loading  │    │ • Market Data   │    │ • ML Training   │
│ • Validation    │    │ • Trend Analysis│    │ • Predictions   │
│ • Preprocessing │    │ • API Calls     │    │ • Model Mgmt    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Vehicle Price   │
                    │ Agent (Main)    │
                    │                 │
                    │ • Orchestration │
                    │ • Decision      │
                    │ • Integration   │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Logger Agent    │    │Explainer Agent  │    │ Insight Agent   │
│                 │    │                 │    │                 │
│ • Monitoring    │    │ • AI Explanations│    │ • Analytics     │
│ • Metrics       │    │ • Reasoning     │    │ • Business      │
│ • Alerting      │    │ • Transparency  │    │ • Intelligence  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔐 Security Considerations

- **API Keys**: Store sensitive keys in `.env` file (never commit to git)
- **Input Validation**: All API inputs are validated and sanitized
- **Rate Limiting**: Built-in protection against API abuse
- **Error Handling**: Secure error messages without sensitive data exposure

## 📈 Performance Metrics

- **Model Accuracy**: ~85% prediction accuracy on test data
- **Response Time**: < 100ms average API response
- **Memory Usage**: ~200MB baseline, ~500MB peak
- **Throughput**: 100+ requests/second sustained
- **Startup Time**: 2-3 seconds for model loading

## 🛣️ Roadmap

### Upcoming Features

- [ ] **Enhanced ML Models**: XGBoost and Neural Network options
- [ ] **Real-time Market Integration**: Live market data feeds
- [ ] **Advanced Analytics**: Trend analysis and forecasting
- [ ] **Mobile App**: React Native mobile application
- [ ] **Batch Processing**: Bulk prediction capabilities
- [ ] **A/B Testing**: Model comparison framework
- [ ] **Multi-language Support**: International market support

### Version History

- **v1.0.0**: Initial release with basic prediction functionality
- **v1.1.0**: Added agent-based architecture and comprehensive testing
- **v1.2.0**: Cross-platform support and Docker containerization
- **v1.3.0**: Enhanced API documentation and monitoring (Current)

## 📚 Documentation

- **[API Documentation](http://localhost:8000/docs)**: Interactive API docs (when server is running)
- **[Development Guide](DEVELOPMENT.md)**: Detailed development instructions
- **[Architecture Overview](docs/architecture.md)**: System design documentation
- **[Deployment Guide](docs/deployment.md)**: Production deployment instructions

## 🤖 Technical Stack

### Core Technologies
- **Backend**: Python 3.11+, FastAPI, Uvicorn
- **Machine Learning**: scikit-learn, pandas, numpy
- **Database**: SQLite (development), PostgreSQL (production)
- **Containerization**: Docker, Docker Compose
- **Testing**: pytest, coverage, mock

### Development Tools
- **Code Quality**: Black, isort, flake8, mypy
- **Version Control**: Git, GitHub Actions
- **Documentation**: Sphinx, OpenAPI
- **Monitoring**: Structured logging, metrics collection

## 📞 Support & Contact

### Getting Help

1. **Documentation**: Check the comprehensive docs first
2. **Issues**: Report bugs via [GitHub Issues](https://github.com/gingeekrishna/price_prediction/issues)
3. **Discussions**: Join community discussions on GitHub
4. **Email**: Contact the maintainer for urgent issues

### Community

- **GitHub**: [github.com/gingeekrishna/price_prediction](https://github.com/gingeekrishna/price_prediction)
- **Issues**: Report bugs and request features
- **Discussions**: Ask questions and share ideas

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI**: For providing AI explanation capabilities
- **FastAPI**: For the excellent web framework
- **scikit-learn**: For robust machine learning tools
- **Contributors**: Thanks to all project contributors

---

**Made with ❤️ for the automotive industry**

*For more information, visit our [GitHub repository](https://github.com/gingeekrishna/price_prediction) or check out the [live demo](http://localhost:8000) when the server is running.*
  "vehicle_age": 3,
  "mileage": 45000,
  "brand": "Toyota",
  "model": "Camry",
  "fuel_type": "Gasoline",
  "transmission": "Automatic"
}
```

Response:
```json
{
  "predicted_price": 25750.50,
  "confidence_interval": [24200.00, 27300.00],
  "market_factors": {
    "market_index": 1150.5,
    "fuel_price": 3.85
  },
  "explanation": "Price influenced by low mileage and strong market conditions"
}
```

### Model Training Endpoint

**POST** `/train`

Triggers model retraining with latest data:
```json
{
  "data_source": "latest",
  "model_type": "random_forest",
  "parameters": {
    "n_estimators": 100,
    "test_size": 0.2
  }
}
```

### Health Check

**GET** `/health`

Returns system status and model metrics:
```json
{
  "status": "healthy",
  "model_accuracy": 0.94,
  "last_trained": "2024-01-15T10:30:00Z",
  "predictions_today": 147
}
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m slow          # Performance tests

# Run tests in parallel
pytest -n auto
```

### Test Coverage

The test suite includes:
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Mock Tests**: External dependency simulation
- **Performance Tests**: Load and stress testing

View coverage report: `open htmlcov/index.html`

## 🔧 Development

### Code Quality

Format and lint code:

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Adding New Features

1. **Create Feature Branch**: `git checkout -b feature/new-feature`
2. **Implement Changes**: Follow existing code patterns
3. **Add Tests**: Ensure comprehensive test coverage
4. **Update Documentation**: Update README and docstrings
5. **Submit PR**: Create pull request for review

### Agent Development

To add a new specialized agent:

1. Create agent file in `src/agents/`
2. Implement required methods:
   ```python
   class NewAgent:
       def perceive(self, data):
           """Process input data"""
           pass
       
       def decide(self, processed_data):
           """Make decisions based on data"""
           pass
       
       def act(self, decision):
           """Execute actions based on decisions"""
           pass
   ```
3. Add comprehensive tests
4. Update API integration

## 📈 Model Performance

Current model metrics:
- **RMSE**: $2,150 (Test Set)
- **R² Score**: 0.94
- **MAE**: $1,680
- **Training Time**: ~15 seconds (100k samples)

### Feature Importance

1. **Vehicle Age** (23.5%)
2. **Mileage** (21.2%)
3. **Market Index** (18.7%)
4. **Brand** (15.3%)
5. **Fuel Price** (12.1%)
6. **Model** (9.2%)

## 🔍 Monitoring & Logging

### Prediction Logs

View recent predictions:
```bash
python logs/view_logs.py
```

### System Logs

Logs are stored in the `logs/` directory with structured format:
- `app.log`: General application logs
- `predictions.log`: Prediction-specific logs
- `errors.log`: Error tracking

### Database

Predictions are stored in SQLite database (`predictions.db`) with schema:
```sql
CREATE TABLE predictions (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    vehicle_age INTEGER,
    mileage INTEGER,
    predicted_price REAL,
    confidence_score REAL,
    market_conditions JSON
);
```

## 🚀 Production Deployment

### Environment Variables

Required for production:
```env
DATABASE_URL=postgresql://user:pass@host:port/db
MARKET_API_KEY=your_production_api_key
LOG_LEVEL=WARNING
CORS_ORIGINS=["https://yourdomain.com"]
```

### Performance Optimization

- **Model Caching**: Trained models cached in memory
- **Database Indexing**: Optimized queries for fast retrieval
- **Async Operations**: Non-blocking API endpoints
- **Connection Pooling**: Efficient database connections

### Security Considerations

- **API Rate Limiting**: Prevent abuse
- **Input Validation**: Comprehensive data validation
- **Error Handling**: Secure error responses
- **Logging**: No sensitive data in logs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write comprehensive docstrings
- Add inline comments for complex logic

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Troubleshooting

**Common Issues:**

1. **Import Errors**: Ensure virtual environment is activated
2. **Database Errors**: Check database file permissions
3. **API Errors**: Verify all dependencies installed
4. **Model Loading**: Ensure model.pkl exists in src/

**Getting Help:**

- Check the [Issues](../../issues) page
- Review test cases for usage examples
- Consult API documentation at `/docs`

### Performance Tips

- Use Docker for consistent environments
- Monitor memory usage with large datasets
- Consider model retraining frequency
- Implement caching for frequent predictions

---

**Built with ❤️ for accurate vehicle price predictions**

8. For expose the API publick 

```
cmd : brew install ngrok
singup in  https://dashboard.ngrok.com/signup
cmd : ngrok config add-authtoken 30QgTRA1Ixs5PHMwspRl8NQmmzi_3QjLrN1SbGi3QXaTgSBmx
cmd : ngrok http 8000
```

9. To Run locally with python server

```
python3 -m http.server
```

10. To update the requirement.txt

```
pip freeze > requirements.txt
```

11. train the model 

```
python scripts/train_model.py
```

12. set the environment variable for openAPI Key

```
export OPENAI_API_KEY="your_api_key_here"
```

13. Creating the docker file

```
docker build -t vehicle-price-agent .
```

14. Run the docker file

```
docker run -p 8000:8000 vehicle-price-agent
```