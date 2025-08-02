# Vehicle Price Prediction - Project Structure

## Overview
This document outlines the organized project structure for the Vehicle Price Prediction system with comprehensive AWS Bedrock integration and multi-LLM support.

## Directory Structure

```
vehicle-price-agent-multi/
├── 📁 config/                    # Configuration files
│   ├── .env.local                # Local development environment
│   ├── .env.development          # Development environment
│   └── .env.production           # Production environment
│
├── 📁 data/                      # Data files
│   ├── historical_vehicle_data.csv
│   └── market_trends.csv
│
├── 📁 docker/                    # Docker configurations
│   ├── docker-compose.local-ai.yml      # Local AI development
│   ├── docker-compose.development.yml   # Development environment
│   ├── docker-compose.production.yml    # Production environment
│   └── Dockerfile                       # Application container
│
├── 📁 docs/                      # Documentation
│   ├── BEDROCK_INTEGRATION.md           # Bedrock integration guide
│   ├── BEDROCK_IMPLEMENTATION_SUMMARY.md # Implementation summary
│   ├── DEVELOPMENT.md                   # Development guide
│   ├── HIGH_LEVEL_DESIGN.md            # System design
│   └── PROJECT_STRUCTURE.md            # This file
│
├── 📁 faiss_index/              # Vector search index
│   ├── index.faiss
│   └── index.pkl
│
├── 📁 knowledge_docs/           # Knowledge base
│   └── pricing_notes.txt
│
├── 📁 logs/                     # Application logs
│   └── view_logs.py
│
├── 📁 notebooks/                # Jupyter notebooks
│   ├── eda.ipynb               # Exploratory data analysis
│   └── model_training.ipynb    # Model training
│
├── 📁 scripts/                  # Utility scripts
│   ├── build_faiss_index.py           # Index building
│   ├── deploy_production.sh           # Production deployment
│   ├── health_check.sh               # Health monitoring
│   ├── run_tests.sh                  # Test execution
│   ├── setup_development.sh          # Development setup
│   ├── setup_local_ai.sh            # Local AI setup
│   ├── test_bedrock_integration.py   # Bedrock testing
│   └── train_model.py               # Model training
│
├── 📁 src/                      # Source code
│   ├── 📁 agents/               # AI agents
│   │   ├── bedrock_agent.py           # AWS Bedrock integration
│   │   ├── explainer_agent.py         # Explanation generation
│   │   ├── insight_agent.py           # Market insights
│   │   ├── logger_agent.py            # Logging agent
│   │   ├── market_agent.py            # Market analysis
│   │   ├── market_data_agent.py       # Market data handling
│   │   ├── mock_bedrock_agent.py      # Mock Bedrock for local dev
│   │   └── model_agent.py             # ML model agent
│   │
│   ├── agent.py                 # Main agent orchestrator
│   ├── api.py                   # FastAPI application
│   ├── data_loader.py           # Data loading utilities
│   ├── demo_agent.py            # Demo functionality
│   ├── explainer.py             # Explanation logic
│   ├── model.py                 # ML model implementation
│   ├── predict.py               # Prediction logic
│   ├── retriever.py             # Information retrieval
│   └── mock.py                  # Mock services
│
├── 📁 static/                   # Static web files
│   └── index.html
│
├── 📁 templates/                # HTML templates
│   ├── index.html
│   └── logs.html
│
├── 📁 tests/                    # Test files
│   ├── test_agent.py
│   ├── test_data_loader.py
│   └── test_model.py
│
├── 📄 pyproject.toml           # Python project configuration
├── 📄 requirements.txt         # Python dependencies
├── 📄 README.md               # Project overview
├── 📄 run_app.py              # Application runner
├── 📄 run_server.py           # Server runner
├── 📄 run_tests.py            # Test runner
├── 📄 setup.cfg               # Setup configuration
├── 📄 start_server.py         # Server startup
├── 📄 start.bat               # Windows startup script
├── 📄 start.ps1               # PowerShell startup script
└── 📄 start.sh                # Unix startup script
```

## Key Components

### 🤖 AI Agents (`src/agents/`)
- **bedrock_agent.py**: AWS Bedrock integration with multi-model support
- **mock_bedrock_agent.py**: Local development mock for Bedrock
- **explainer_agent.py**: Multi-LLM explanation generation
- **model_agent.py**: ML model predictions
- **market_agent.py**: Market analysis and trends

### 🐳 Docker Infrastructure (`docker/`)
- **docker-compose.local-ai.yml**: Local development with Ollama
- **docker-compose.development.yml**: Development environment
- **docker-compose.production.yml**: Production deployment

### ⚙️ Configuration (`config/`)
- **Environment-specific settings**: Local, development, production
- **AWS Bedrock configuration**: Credentials and model settings
- **Service endpoints**: Database, Redis, AI services

### 📜 Scripts (`scripts/`)
- **setup_development.sh**: Development environment setup
- **deploy_production.sh**: Production deployment
- **health_check.sh**: Service health monitoring
- **test_bedrock_integration.py**: Bedrock functionality testing

### 📚 Documentation (`docs/`)
- **Architecture guides**: High-level design and implementation
- **Integration guides**: Bedrock setup and configuration
- **Development guides**: Setup and contribution guidelines

## Usage Patterns

### Local Development
```bash
# Setup local development environment
./scripts/setup_development.sh

# Run with local AI (Ollama)
docker-compose -f docker/docker-compose.local-ai.yml up

# Run tests
./scripts/run_tests.sh
```

### Production Deployment
```bash
# Deploy to production
./scripts/deploy_production.sh

# Monitor health
./scripts/health_check.sh
```

### Multi-LLM Configuration
The system supports intelligent fallback across multiple LLM providers:
1. **AWS Bedrock** (Primary) - Claude, Titan, Jurassic, Command
2. **Claude API** (Secondary) - Direct Anthropic integration
3. **Ollama** (Local) - Local model hosting
4. **Standard** (Fallback) - Basic responses

## Benefits of This Structure

### 🎯 **Organization**
- Clear separation of concerns
- Logical grouping of related files
- Easy navigation and maintenance

### 🔧 **Development**
- Environment-specific configurations
- Automated setup scripts
- Comprehensive testing framework

### 🚀 **Deployment**
- Docker-based containerization
- Production-ready configurations
- Health monitoring and logging

### 🤖 **AI Integration**
- Multi-provider LLM support
- Local development capabilities
- Fallback mechanisms for reliability

This structure provides a robust foundation for developing, testing, and deploying a production-grade vehicle price prediction system with comprehensive AI capabilities.
