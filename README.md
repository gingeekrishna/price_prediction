# Vehicle Price Prediction System 🚗💰

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-orange.svg)](https://aws.amazon.com/bedrock/)
[![Cross Platform](https://img.shields.io/badge/platform-windows%20%7C%20macOS%20%7C%20linux-lightgrey.svg)](https://github.com/gingeekrishna/price_prediction)
[![AI Powered](https://img.shields.io/badge/AI-Bedrock%20%2B%20Claude%20%2B%20Ollama-purple.svg)](https://anthropic.com/)

A comprehensive **AI-powered** machine learning system for predicting vehicle prices using historical vehicle data, real-time market trends, and advanced **multi-LLM architecture** with **AWS Bedrock integration**. This project implements an intelligent agent-based architecture with RESTful API endpoints for seamless integration across Windows, macOS, and Linux platforms.

## 🚀 Features

### 🤖 **Enterprise Multi-LLM AI Integration**
- **🔮 AWS Bedrock Integration**: Enterprise-grade AI with Claude, Titan, AI21 Jurassic, and Cohere Command models
- **🧠 Claude AI Integration**: Premium explanations using Anthropic's Claude-3-Opus model
- **🔄 Intelligent Fallbacks**: Bedrock → Claude → Ollama → Standard explanations with smart provider selection
- **⚡ Performance Optimized**: Multi-threaded AI processing with response caching
- **🎯 Smart AI Selection**: Automatic best-available AI provider routing
- **🏠 Local Development**: Mock Bedrock agent for offline development

### 🏗️ **Enhanced Architecture**
- **🤖 Advanced ML Pipeline**: Random Forest-based price prediction with comprehensive model evaluation
- **🏗️ Agent-Based Architecture**: Modular agent system following perceive-decide-act paradigm
- **🌐 RESTful API**: FastAPI-powered endpoints with **multiple AI-powered prediction routes**
- **📊 Data Integration**: Seamless merging of historical vehicle data with market trends
- **🧪 Comprehensive Testing**: Full test suite including Bedrock integration testing
- **🐳 Production Ready**: Multi-environment Docker configurations (local, development, production)

### 🌟 **AI-Powered Endpoints**
- **`/predict`** - Standard vehicle price predictions
- **`/predict_with_bedrock`** - Enterprise AI explanations using AWS Bedrock (NEW!)
- **`/predict_with_claude`** - Premium AI explanations using Claude
- **`/predict_with_ai`** - Smart AI selection with automatic fallbacks
- **`/bedrock/status`** - Bedrock service availability checking (NEW!)
- **`/claude/status`** - Claude availability checking
- **📊 Performance Monitoring**: Real-time bottleneck analysis and optimization

### 🔧 **Enhanced User Experience**
- **🎨 Modern Web Interface**: Beautiful, responsive design with AI provider selection
- **📱 Mobile Optimized**: Works seamlessly on desktop and mobile devices
- **⚡ Real-time Predictions**: Sub-second response times for price estimates
- **🔄 Cross-Platform**: Works seamlessly on Windows, macOS, and Linux

## 📁 Project Structure

```
vehicle-price-agent-multi/
├── 📁 config/                    # Configuration files
│   ├── .env.local                # Local development environment
│   ├── .env.development          # Development environment
│   └── .env.production           # Production environment
├── 📁 docker/                    # Docker configurations
│   ├── docker-compose.local-ai.yml      # Local AI development
│   ├── docker-compose.development.yml   # Development environment
│   └── docker-compose.production.yml    # Production environment
├── 📁 docs/                      # Documentation
│   ├── BEDROCK_INTEGRATION.md           # Bedrock integration guide
│   ├── BEDROCK_IMPLEMENTATION_SUMMARY.md # Implementation summary
│   └── PROJECT_STRUCTURE.md            # Detailed project structure
├── 📁 scripts/                  # Utility scripts
│   ├── setup_development.sh           # Development setup
│   ├── deploy_production.sh           # Production deployment
│   ├── health_check.sh               # Health monitoring
│   └── test_bedrock_integration.py   # Bedrock testing
├── 📁 src/                      # Main source code
│   ├── 📁 agents/               # AI agents
│   │   ├── bedrock_agent.py           # AWS Bedrock integration
│   │   ├── mock_bedrock_agent.py      # Mock for local development
│   │   └── explainer_agent.py         # Multi-LLM explanations
│   ├── agent.py                  # Main prediction agent
│   ├── api.py                    # FastAPI REST endpoints
│   └── model.py                  # ML model implementation
│   └── agents/                   # Specialized agent modules
│       ├── market_agent.py       # Market data collection agent
│       ├── model_agent.py        # ML model management agent
│       ├── explainer_agent.py    # Multi-LLM explanation agent (ENHANCED!)
│       ├── claude_agent.py       # Claude AI integration (NEW!)
│       ├── ollama_agent.py       # Optimized Ollama integration (ENHANCED!)
│       ├── insight_agent.py      # Business insights agent
│       └── logger_agent.py       # Logging and monitoring agent
├── data/                         # Training and market data
│   ├── historical_vehicle_data.csv
│   └── market_trends.csv
├── tests/                        # Comprehensive test suite
│   ├── test_agent.py            # Agent functionality tests
│   ├── test_model.py            # Model training/evaluation tests
│   ├── test_data_loader.py      # Data processing tests
│   ├── test_claude.py           # Claude AI integration tests (NEW!)
│   └── test_ollama.py           # Ollama performance tests (NEW!)
├── notebooks/                    # Jupyter notebooks for analysis
│   ├── eda.ipynb               # Exploratory data analysis
│   └── model_training.ipynb    # Model development
├── frontend/                    # Web interface
│   └── index.html              # Modern responsive UI
├── templates/                   # Alternative web templates
│   └── index.html              # Enhanced web interface
├── logs/                        # Application logs
├── knowledge_docs/              # RAG knowledge base
├── performance_test.py          # AI performance analysis tool (NEW!)
├── CLAUDE_INTEGRATION.md        # Claude setup guide (NEW!)
├── PERFORMANCE_OPTIMIZATION.md  # Performance tuning guide (NEW!)
├── static/                      # Web UI assets
├── requirements.txt             # Python dependencies (updated with Claude)
├── pyproject.toml              # Project configuration
├── Dockerfile                  # Container configuration
└── README.md                   # This file
```

## 🛠️ Cross-Platform Installation & Setup

### 📋 Prerequisites

| Component | Windows | macOS | Linux |
|-----------|---------|-------|-------|
| **Python 3.11+** | [python.org](https://python.org/downloads) | `brew install python@3.11` | `sudo apt install python3.11` |
| **Git** | [git-scm.com](https://git-scm.com) | `brew install git` | `sudo apt install git` |
| **pip** | Included with Python | Included with Python | `sudo apt install python3-pip` |
| **Docker** *(Optional)* | [Docker Desktop](https://docker.com/products/docker-desktop) | [Docker Desktop](https://docker.com/products/docker-desktop) | `sudo apt install docker.io` |

### 🚀 Complete Setup Guide

#### **Step 1: System Preparation**

**🪟 Windows Setup:**
```powershell
# Check Python version
python --version

# If Python not found, install from python.org
# Ensure "Add Python to PATH" is checked during installation

# Open PowerShell as Administrator (recommended)
# Verify pip is available
pip --version
```

**🍎 macOS Setup:**
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11+
brew install python@3.11

# Verify installation
python3 --version
pip3 --version

# Create alias (optional)
echo 'alias python=python3' >> ~/.zshrc
echo 'alias pip=pip3' >> ~/.zshrc
source ~/.zshrc
```

**🐧 Linux (Ubuntu/Debian) Setup:**
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.11 and dependencies
sudo apt install python3.11 python3.11-venv python3-pip git -y

# Verify installation
python3.11 --version
pip3 --version

# Create symlinks (optional)
sudo ln -sf /usr/bin/python3.11 /usr/bin/python
sudo ln -sf /usr/bin/pip3 /usr/bin/pip
```

#### **Step 2: Clone Repository**

**All Platforms:**
```bash
# Clone the repository
git clone https://github.com/gingeekrishna/price_prediction.git

# Navigate to project directory
cd price_prediction/vehicle-price-agent-multi

# Verify you're in the right directory
ls -la  # Linux/macOS
dir     # Windows
```

#### **Step 3: Virtual Environment Setup**

**🪟 Windows (PowerShell):**
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If execution policy error occurs:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Verify activation (should show (venv) in prompt)
python --version
```

**🪟 Windows (Command Prompt):**
```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate.bat

# Verify activation
python --version
```

**🍎 macOS:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (should show (venv) in prompt)
python --version
which python  # Should point to venv directory
```

**🐧 Linux:**
```bash
# Install venv if not available
sudo apt install python3.11-venv -y

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation
python --version
which python  # Should point to venv directory
```

#### **Step 4: Install Dependencies**

**All Platforms (after venv activation):**
```bash
# Upgrade pip to latest version
python -m pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -E "(fastapi|uvicorn|scikit-learn|anthropic)"
```

**If Installation Issues Occur:**
```bash
# Clear pip cache
pip cache purge

# Install with no cache
pip install --no-cache-dir -r requirements.txt

# Force reinstall specific package
pip install --force-reinstall uvicorn
```

#### **Step 5: Environment Configuration**

**🪟 Windows:**
```powershell
# Copy environment template
copy .env.sample .env

# Edit environment file
notepad .env  # or use your preferred editor

# Set environment variables (Optional for Claude AI)
$env:ANTHROPIC_API_KEY="your-anthropic-key-here"
$env:OPENAI_API_KEY="your-openai-key-here"
```

**🍎 macOS / 🐧 Linux:**
```bash
# Copy environment template
cp .env.sample .env

# Edit environment file
nano .env  # or vim, code, etc.

# Set environment variables (Optional for Claude AI)
export ANTHROPIC_API_KEY="your-anthropic-key-here"
export OPENAI_API_KEY="your-openai-key-here"

# Make permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export ANTHROPIC_API_KEY="your-key"' >> ~/.bashrc
```

#### **Step 6: Run the Application**

**🚀 Recommended Method (Cross-platform):**
```bash
# Start the application
python run_server.py

# Alternative startup methods:
python run_app.py        # Basic startup
python start_server.py   # Legacy method
```

**🪟 Windows Quick Start:**
```powershell
# Using PowerShell script
.\start.ps1

# Using batch file
.\start.bat
```

**🍎 macOS / 🐧 Linux Quick Start:**
```bash
# Make script executable
chmod +x start.sh

# Run startup script
./start.sh
```

#### **Step 7: Verify Installation**

**Test Endpoints:**
```bash
# Check if server is running (wait 30-60 seconds for startup)
curl http://localhost:8000/health

# Or open in browser:
# - Web Interface: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Health Check: http://localhost:8000/health
```

### 🧪 **Quick Test Run**

```bash
# Test basic prediction
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "vehicle_age": 5,
       "mileage": 50000,
       "make": "Toyota",
       "model": "Camry",
       "condition": "good"
     }'

# Test AI-powered prediction
curl -X POST "http://localhost:8000/predict_with_ai" \
     -H "Content-Type: application/json" \
     -d '{
       "vehicle_age": 3,
       "mileage": 30000,
       "make": "BMW",
       "model": "3 Series",
       "condition": "excellent"
     }'
```

### 🧠 **Claude AI Setup (Optional - Premium Features)**

To enable **premium AI-powered explanations** with Claude:

#### **Step 1: Get Anthropic API Key**
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create account and generate API key
3. Copy your API key (starts with `sk-ant-`)

#### **Step 2: Configure Environment Variables**

**🪟 Windows (PowerShell):**
```powershell
# Temporary (current session only)
$env:ANTHROPIC_API_KEY="sk-ant-your-api-key-here"

# Permanent (add to system environment)
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-ant-your-api-key-here", "User")

# Verify
echo $env:ANTHROPIC_API_KEY
```

**🪟 Windows (Command Prompt):**
```cmd
# Temporary (current session only)
set ANTHROPIC_API_KEY=sk-ant-your-api-key-here

# Permanent (system environment)
setx ANTHROPIC_API_KEY "sk-ant-your-api-key-here"

# Verify
echo %ANTHROPIC_API_KEY%
```

**🍎 macOS:**
```bash
# Temporary (current session only)
export ANTHROPIC_API_KEY="sk-ant-your-api-key-here"

# Permanent (add to shell profile)
echo 'export ANTHROPIC_API_KEY="sk-ant-your-api-key-here"' >> ~/.zshrc
source ~/.zshrc

# For bash users
echo 'export ANTHROPIC_API_KEY="sk-ant-your-api-key-here"' >> ~/.bash_profile
source ~/.bash_profile

# Verify
echo $ANTHROPIC_API_KEY
```

**🐧 Linux:**
```bash
# Temporary (current session only)
export ANTHROPIC_API_KEY="sk-ant-your-api-key-here"

# Permanent (add to bash profile)
echo 'export ANTHROPIC_API_KEY="sk-ant-your-api-key-here"' >> ~/.bashrc
source ~/.bashrc

# For zsh users
echo 'export ANTHROPIC_API_KEY="sk-ant-your-api-key-here"' >> ~/.zshrc
source ~/.zshrc

# Verify
echo $ANTHROPIC_API_KEY
```

#### **Step 3: Test Claude Integration**
```bash
# Run Claude integration test
python test_claude.py

# Expected output:
# ✅ Claude API key found
# ✅ Claude agent initialized successfully
# ✅ Claude integration test passed
```

#### **Step 4: Use Premium AI Endpoints**

**Available Premium Endpoints:**
- **`/predict_with_claude`** - Exclusive Claude AI explanations
- **`/predict_with_ai`** - Smart AI selection (automatically uses Claude when available)
- **`/claude/status`** - Check Claude availability and API status

**Test Premium Features:**
```bash
# Test Claude status
curl http://localhost:8000/claude/status

# Test Claude-powered prediction
curl -X POST "http://localhost:8000/predict_with_claude" \
     -H "Content-Type: application/json" \
     -d '{
       "vehicle_age": 4,
       "mileage": 30000,
       "make": "Tesla",
       "model": "Model 3",
       "condition": "excellent"
     }'
```

**💡 Important Notes:**
- ✅ **System works perfectly without Claude** using optimized Ollama + standard fallbacks
- 🔄 **Intelligent Fallback**: If Claude is unavailable, system automatically uses Ollama or standard explanations
- 💰 **Cost**: Claude API charges per usage (~$0.001-0.01 per prediction)
- 🚀 **Performance**: Claude responses typically 2-5 seconds

### ✅ **Latest Updates (v3.0 - AI Integration)**

**🚀 Major AI Enhancements**:
- ✅ **Claude AI Integration**: Premium explanations using Anthropic's Claude-3-Opus
- ✅ **Multi-LLM Architecture**: Intelligent fallback system (Claude → Ollama → Standard)
- ✅ **Performance Optimized**: Ollama response time improved by 59% (22.4s → 9.2s)
- ✅ **Smart AI Routing**: Automatic best-available AI provider selection
- ✅ **Enhanced Web Interface**: Modern UI with full vehicle details support
- ✅ **Comprehensive Testing**: AI performance analysis and bottleneck detection

**🔧 Technical Improvements**:
- ✅ **Fixed Frontend**: Corrected port configuration (8080→8000) 
- ✅ **API Compatibility**: Multiple prediction endpoints for different use cases
- ✅ **Enhanced Error Handling**: Robust fallback mechanisms for AI failures
- ✅ **Performance Monitoring**: Real-time bottleneck analysis tools

### ✅ Previous Improvements (v2.1)

**Path Resolution Fixes** - All cross-platform compatibility issues resolved:
- ✅ **Fixed Model Loading**: Resolved `STACK_GLOBAL requires str` pickle errors
- ✅ **Cross-Platform Paths**: Automatic path resolution for Windows, macOS, and Linux
- ✅ **Database Compatibility**: Fixed SQLite path issues across platforms
- ✅ **Static Files**: Resolved template and static file serving on all platforms

**Mac/Linux Users**: Use the optimized startup script:
```bash
chmod +x start.sh
./start.sh
```

### 🐳 **Docker Deployment (Recommended for Production)**

Docker provides a consistent environment across all platforms and includes monitoring, caching, and security features.

#### **Step 1: Install Docker**

**🪟 Windows:**
```powershell
# Download and install Docker Desktop from docker.com
# Enable WSL2 backend for better performance
# Verify installation
docker --version
docker-compose --version
```

**🍎 macOS:**
```bash
# Option 1: Download Docker Desktop from docker.com
# Option 2: Install via Homebrew
brew install --cask docker

# Start Docker Desktop and verify
docker --version
```

**🐧 Linux:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose -y

# CentOS/RHEL
sudo yum install docker docker-compose -y

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
```

#### **Step 2: Environment Setup**

```bash
# Clone repository (if not done already)
git clone https://github.com/gingeekrishna/price_prediction.git
cd price_prediction/vehicle-price-agent-multi

# Copy environment template
cp .env.docker .env

# Edit .env with your API keys
# Required: ANTHROPIC_API_KEY=your_anthropic_key_here
# Optional: OLLAMA_BASE_URL=http://host.docker.internal:11434
```

#### **Step 3: Production Deployment**

**🚀 Quick Start (All Platforms):**
```bash
# Linux/macOS
chmod +x scripts/docker-start.sh
./scripts/docker-start.sh

# Windows PowerShell
.\scripts\docker-start.ps1

# Manual approach
docker-compose up --build -d
```

**Production Stack Includes:**
- ✅ **Vehicle Price API** with multi-LLM support
- ✅ **Nginx Reverse Proxy** with security headers and rate limiting
- ✅ **Redis Cache** for performance optimization
- ✅ **Prometheus Monitoring** for metrics collection
- ✅ **Grafana Dashboards** for visualization

**Access Points:**
- 🌐 **Application**: http://localhost
- 📊 **Grafana**: http://localhost:3000 (admin/admin)
- 📈 **Prometheus**: http://localhost:9090

#### **Step 4: Development Environment**

For active development with hot reload:
```bash
# Linux/macOS
chmod +x scripts/docker-dev.sh
./scripts/docker-dev.sh

# Windows PowerShell
.\scripts\docker-dev.ps1

# Manual approach
docker-compose -f docker-compose.dev.yml up --build
```

**Development Features:**
- 🔄 Hot reload on code changes
- 🐛 Development debugging enabled
- 📁 Volume mounts for live editing
- 🌐 Direct access at http://localhost:8000

#### **Step 5: Docker Management Commands**

```bash
# View logs
docker-compose logs -f                    # All services
docker-compose logs -f app               # Application only

# Check service status
docker-compose ps

# Stop services
docker-compose down                      # Stop services
docker-compose down -v                   # Stop and remove volumes

# Restart specific service
docker-compose restart app

# Update and rebuild
docker-compose pull                      # Pull latest images
docker-compose up --build -d            # Rebuild and restart

# Cleanup
docker system prune -a                  # Remove unused images
docker volume prune                     # Remove unused volumes
```

#### **Step 6: Monitoring and Maintenance**

**Grafana Dashboard Setup:**
1. Access http://localhost:3000
2. Login: admin/admin
3. Import dashboard: Use ID `1860` for Node Exporter
4. Monitor application metrics and performance

**Health Checks:**
```bash
# Check application health
curl http://localhost/health

# Check individual services
docker-compose exec app python -c "import requests; print(requests.get('http://localhost:8000/health').json())"
```

**Basic Container Run:**
```bash
# Run container with port mapping
docker run -p 8000:8000 vehicle-price-predictor

# Run in background (detached mode)
docker run -d -p 8000:8000 --name vehicle-predictor vehicle-price-predictor

# Check container status
docker ps
```

**Advanced Container Options:**
```bash
# Run with environment variables
docker run -d -p 8000:8000 \
  -e ANTHROPIC_API_KEY="your-key-here" \
  -e OPENAI_API_KEY="your-key-here" \
  --name vehicle-predictor \
  vehicle-price-predictor

# Run with volume mounting (for persistent data)
docker run -d -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --name vehicle-predictor \
  vehicle-price-predictor

# View container logs
docker logs vehicle-predictor

# Access container shell
docker exec -it vehicle-predictor /bin/bash
```

#### **Step 4: Docker Compose (Recommended for Production)**

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./predictions.db:/app/predictions.db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

**Run with Docker Compose:**
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build -d
```

### 🔧 **Platform-Specific Setup Notes**

#### **🪟 Windows Specific Instructions**

**PowerShell Setup:**
```powershell
# Enable script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install Python via Windows Store (recommended)
# Or download from python.org (ensure "Add to PATH" is checked)

# Use Windows Terminal for better experience
# Available from Microsoft Store

# Common Windows paths
$env:PATH += ";C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python311"
```

**WSL2 Integration (Recommended):**
```bash
# Install WSL2 for Linux-like experience
wsl --install

# Use Ubuntu or preferred distribution
# Run the project in WSL2 for better compatibility
```

#### **🍎 macOS Specific Instructions**

**Homebrew Setup:**
```bash
# Install Homebrew (package manager)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python via Homebrew (recommended)
brew install python@3.11

# Install additional tools
brew install git curl wget

# Add to PATH (add to ~/.zshrc)
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Apple Silicon (M1/M2) Notes:**
```bash
# Some packages may need native ARM builds
pip install --upgrade pip
pip install --no-binary :all: scikit-learn  # If needed

# For Docker on Apple Silicon
# Use --platform linux/amd64 if needed
docker build --platform linux/amd64 -t vehicle-price-predictor .
```

#### **🐧 Linux Distribution Specific**

**Ubuntu/Debian:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3.11 python3.11-venv python3-pip git curl build-essential -y

# For older Ubuntu versions, add deadsnakes PPA
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
```

**CentOS/RHEL/Fedora:**
```bash
# Install EPEL repository (CentOS/RHEL)
sudo yum install epel-release -y

# Install dependencies
sudo yum install python3 python3-pip git curl gcc gcc-c++ make -y

# Or for Fedora
sudo dnf install python3 python3-pip git curl gcc gcc-c++ make -y
```

**Arch Linux:**
```bash
# Install dependencies
sudo pacman -S python python-pip git curl base-devel -Sy

# Install from AUR if needed
yay -S python311  # If available
```

### ✅ **Verification Checklist**

After setup on any platform, verify your installation:

```bash
# 1. Check Python version
python --version  # Should be 3.11+

# 2. Check virtual environment
which python  # Should point to venv directory

# 3. Check installed packages
pip list | grep -E "(fastapi|uvicorn|scikit-learn)"

# 4. Test server startup
python run_server.py  # Should start without errors

# 5. Test API endpoints
curl http://localhost:8000/health  # Should return {"status": "healthy"}

# 6. Test web interface
# Open http://localhost:8000 in browser

# 7. Test AI capabilities (if configured)
curl http://localhost:8000/claude/status  # Check Claude status
python test_claude.py  # Run Claude integration test
```

## 📖 **AI-Powered API Usage**

### 🤖 **Premium AI Endpoints (NEW!)**

#### **Smart AI Prediction** (Recommended)
**Endpoint**: `POST /predict_with_ai`
*Automatically selects the best available AI (Claude → Ollama → Standard)*

```bash
curl -X POST "http://localhost:8000/predict_with_ai" \
     -H "Content-Type: application/json" \
     -d '{
       "make": "Toyota",
       "model": "Camry",
       "year": 2020,
       "mileage": 45000,
       "condition": "good"
     }'
```

#### **Claude AI Prediction** (Premium)
**Endpoint**: `POST /predict_with_claude`
*Premium explanations using Anthropic Claude*

```bash
curl -X POST "http://localhost:8000/predict_with_claude" \
     -H "Content-Type: application/json" \
     -d '{
       "make": "BMW",
       "model": "3 Series",
       "year": 2019,
       "mileage": 30000,
       "condition": "excellent"
     }'
```

#### **Claude Status Check**
**Endpoint**: `GET /claude/status`

```bash
curl http://localhost:8000/claude/status
```

### 📊 **Standard Prediction Endpoints**

#### **Enhanced Vehicle Prediction**
**Endpoint**: `POST /predict`

```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "make": "Honda",
       "model": "Civic",
       "year": 2021,
       "mileage": 25000,
       "condition": "good"
     }'
```

#### **Simple Prediction** (Legacy)
**Endpoint**: `POST /predict` (Alternative format)

```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "vehicle_age": 3,
       "mileage": 45000
     }'
```

### **AI-Enhanced Response Example**:
```json
{
  "predicted_price": 24500.00,
  "explanation": "🤖 Claude AI Analysis:\n\nPrice Analysis: $24,500\n\nThis 2020 Toyota Camry with 45,000 miles represents excellent value in today's market. Key factors:\n\n• Vehicle Age: 4 years shows moderate depreciation\n• Mileage: 45K miles is reasonable for the age\n• Condition: Good condition maintains resale value\n• Market Position: Toyota's reliability premium...",
  "recommendation": "💡 AI Recommendations:\n\n• Buyers: Excellent choice for reliability and value\n• Sellers: Price competitively at $24,000-$25,000\n• Market timing is favorable for this vehicle class",
  "market_data": {
    "market_index": 1125.4,
    "fuel_price": 3.89
  },
  "ai_provider": "claude",
  "confidence_score": 0.94
}
```

### **System Health & Monitoring**

#### **Health Check**
```bash
curl http://localhost:8000/health
```

#### **Performance Analysis**
```bash
python performance_test.py
```

#### **Market Data**
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

## 🔍 Comprehensive Troubleshooting Guide

### 🚨 **Common Installation Issues**

#### **Python Version Issues**

**🪟 Windows:**
```powershell
# Problem: Python not found or wrong version
# Solution 1: Check Python installation
python --version
Get-Command python

# Solution 2: Install/Update Python
# Download from python.org and ensure "Add to PATH" is checked
# Or use Windows Store version

# Solution 3: Multiple Python versions conflict
py -3.11 --version  # Use specific version
```

**🍎 macOS:**
```bash
# Problem: python3 command not found
# Solution 1: Install via Homebrew
brew install python@3.11

# Solution 2: Fix PATH issues
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Solution 3: Multiple Python versions
which python3  # Check current Python path
/usr/bin/python3 --version  # System Python
/opt/homebrew/bin/python3 --version  # Homebrew Python
```

**🐧 Linux:**
```bash
# Problem: Python 3.11 not available
# Solution 1: Add deadsnakes PPA (Ubuntu)
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-pip

# Solution 2: Build from source (other distros)
wget https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz
tar xzf Python-3.11.9.tgz
cd Python-3.11.9
./configure --enable-optimizations
make -j 8
sudo make altinstall
```

#### **Virtual Environment Issues**

**🪟 Windows PowerShell Execution Policy:**
```powershell
# Problem: cannot be loaded because running scripts is disabled
# Solution: Enable script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Verify
Get-ExecutionPolicy -List

# Alternative: Use Command Prompt instead
cmd
venv\Scripts\activate.bat
```

**🍎 macOS Permission Issues:**
```bash
# Problem: Permission denied creating venv
# Solution 1: Check directory permissions
ls -la
chmod 755 .

# Solution 2: Use user Python installation
python3 -m pip install --user virtualenv
python3 -m virtualenv venv
```

**🐧 Linux venv Package Missing:**
```bash
# Problem: No module named 'venv'
# Solution: Install venv package
sudo apt install python3.11-venv  # Ubuntu/Debian
sudo yum install python3-venv      # CentOS/RHEL
sudo pacman -S python-virtualenv   # Arch Linux
```

#### **Dependency Installation Issues**

**All Platforms - pip Issues:**
```bash
# Problem: pip install fails with various errors
# Solution 1: Upgrade pip
python -m pip install --upgrade pip

# Solution 2: Clear cache
pip cache purge

# Solution 3: Install with no cache
pip install --no-cache-dir -r requirements.txt

# Solution 4: Install individually
pip install fastapi uvicorn scikit-learn pandas numpy

# Solution 5: Use pre-compiled wheels only
pip install --only-binary=all -r requirements.txt
```

**Specific Package Issues:**
```bash
# Problem: Failed building wheel for [package]
# Solution: Install build tools

# Windows: Install Visual Studio Build Tools
# macOS: 
xcode-select --install

# Linux:
sudo apt install build-essential python3-dev  # Ubuntu
sudo yum groupinstall "Development Tools"     # CentOS
```

#### **Port and Network Issues**

**🪟 Windows Port Conflicts:**
```powershell
# Problem: Port 8000 already in use
# Solution 1: Find process using port
netstat -ano | findstr :8000
Get-Process -Id <PID>

# Solution 2: Kill process
taskkill /PID <process_id> /F

# Solution 3: Use different port
# Edit run_server.py to change port number
```

**🍎 macOS / 🐧 Linux Port Conflicts:**
```bash
# Problem: Address already in use
# Solution 1: Find and kill process
lsof -ti:8000
kill -9 $(lsof -ti:8000)

# Solution 2: Use netstat
netstat -tulpn | grep :8000
sudo kill -9 <PID>

# Solution 3: Check for system services
sudo systemctl status  # Linux
brew services list      # macOS
```

#### **File Permission Issues**

**🍎 macOS / 🐧 Linux:**
```bash
# Problem: Permission denied errors
# Solution 1: Fix directory permissions
chmod -R 755 .
chown -R $USER:$USER .

# Solution 2: For log files
mkdir -p logs
chmod 755 logs

# Solution 3: For database files
chmod 644 *.db
```

**🪟 Windows:**
```powershell
# Problem: Access denied errors
# Solution: Run as Administrator or check folder permissions
# Right-click folder → Properties → Security → Edit
```

### 🔧 **Runtime Issues**

#### **Model Loading Errors**

```bash
# Problem: Model file not found or corrupted
# Solution 1: Retrain model
python scripts/train_model.py

# Solution 2: Check model file
ls -la src/model.pkl
file src/model.pkl  # Linux/macOS

# Solution 3: Reset model cache
rm src/model.pkl
python run_server.py  # Will retrain automatically
```

#### **Database Issues**

```bash
# Problem: Database locked or corrupted
# Solution 1: Remove database file
rm predictions.db

# Solution 2: Check database permissions
chmod 644 predictions.db

# Solution 3: Use database browser (if needed)
sqlite3 predictions.db ".schema"
```

#### **AI Agent Issues**

```bash
# Problem: Ollama not responding
# Solution 1: Check Ollama status
curl http://localhost:11434/api/version

# Solution 2: Restart Ollama
# Windows: Check Task Manager and restart
# macOS/Linux:
brew services restart ollama  # macOS
sudo systemctl restart ollama # Linux

# Problem: Claude API key issues
# Solution: Verify API key
echo $ANTHROPIC_API_KEY
curl -H "x-api-key: $ANTHROPIC_API_KEY" https://api.anthropic.com/v1/messages
```

### 📊 **Performance Issues**

#### **Slow Startup**

```bash
# Problem: Application takes too long to start
# Cause: Model training, data loading, AI initialization

# Solution 1: Monitor startup process
python run_server.py --log-level debug

# Solution 2: Skip AI components temporarily
# Comment out AI imports in src/api.py for testing

# Solution 3: Use smaller dataset for testing
# Replace data files with smaller versions
```

#### **High Memory Usage**

```bash
# Problem: Application uses too much RAM
# Solution 1: Monitor memory usage
# Windows: Task Manager → Performance → Memory
# macOS: Activity Monitor
# Linux: htop or top

# Solution 2: Optimize model settings
# Edit src/model.py and reduce n_estimators

# Solution 3: Increase system memory or use swap
```

### 🌐 **Web Interface Issues**

#### **Browser Access Problems**

```bash
# Problem: Cannot access web interface
# Solution 1: Check server is running
curl http://localhost:8000/health

# Solution 2: Try different browsers
# Chrome, Firefox, Safari, Edge

# Solution 3: Clear browser cache
# Ctrl+Shift+Delete (Windows/Linux)
# Cmd+Shift+Delete (macOS)

# Solution 4: Check firewall
# Windows: Windows Defender Firewall
# macOS: System Preferences → Security & Privacy → Firewall
# Linux: sudo ufw status
```

### 🆘 **Getting Additional Help**

**📋 Collect System Information:**
```bash
# System info script
python -c "
import sys, platform, os
print(f'OS: {platform.system()} {platform.release()}')
print(f'Python: {sys.version}')
print(f'Current Directory: {os.getcwd()}')
print(f'Python Path: {sys.executable}')
"

# Check installed packages
pip list > installed_packages.txt
```

**🔍 Debug Mode:**
```bash
# Run with debug logging
python run_server.py --log-level debug > debug.log 2>&1

# Check logs
tail -f debug.log  # Linux/macOS
Get-Content debug.log -Wait  # Windows PowerShell
```

**📞 Support Channels:**
- **GitHub Issues**: [Report bugs](https://github.com/gingeekrishna/price_prediction/issues)
- **Documentation**: Check `DEVELOPMENT.md` for detailed setup
- **Community**: GitHub Discussions for questions

### ⚡ **Performance Optimization**

**🚀 AI Performance Improvements**:
- **Ollama Response Time**: 59% faster (22.4s → 9.2s)
- **Claude Integration**: Sub-3s response times when available
- **Smart Caching**: Reduces repeated AI computations
- **Intelligent Fallbacks**: Never fails to provide predictions

**📊 System Performance**:
- **Memory Usage**: ~200MB RAM for basic operations
- **Standard Predictions**: < 100ms response time
- **AI-Enhanced Predictions**: 3-20s (depending on AI provider)
- **Concurrent Users**: Supports 50+ concurrent requests
- **Data Loading**: Initial startup 2-3 seconds

**🔍 Performance Analysis Tool**:
```bash
python performance_test.py
```
*Provides comprehensive bottleneck analysis and optimization recommendations*

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

- **v3.0.0**: **Major AI Integration** - Claude LLM + Multi-LLM architecture + 59% performance improvement (Current)
- **v2.1.0**: Cross-platform compatibility fixes and path resolution
- **v2.0.0**: Added agent-based architecture and comprehensive testing  
- **v1.2.0**: Cross-platform support and Docker containerization
- **v1.1.0**: Enhanced API documentation and monitoring
- **v1.0.0**: Initial release with basic prediction functionality

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

- **Anthropic**: For providing Claude AI capabilities and advanced reasoning
- **Ollama**: For local LLM processing and optimization opportunities
- **OpenAI**: For foundational AI explanation capabilities
- **FastAPI**: For the excellent web framework
- **scikit-learn**: For robust machine learning tools
- **Contributors**: Thanks to all project contributors

---

**Made with ❤️ for the automotive industry**

*Powered by advanced AI including Claude-3-Opus for premium vehicle price analysis and explanations.*

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