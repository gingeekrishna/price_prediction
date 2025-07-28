# Vehicle Price Prediction System - High Level Design (HLD)

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [System Components](#system-components)
4. [Data Flow](#data-flow)
5. [Multi-Agent System Design](#multi-agent-system-design)
6. [API Design](#api-design)
7. [Database Design](#database-design)
8. [Technology Stack](#technology-stack)
9. [Performance Requirements](#performance-requirements)
10. [Security Considerations](#security-considerations)
11. [Deployment Architecture](#deployment-architecture)
12. [Scalability & Future Enhancements](#scalability--future-enhancements)

---

## System Overview

### Purpose
The Vehicle Price Prediction System is a multi-agent AI-powered application that provides accurate vehicle price predictions using machine learning models, market data analysis, and intelligent explanations.

### Key Features
- **Accurate Price Prediction**: ML-based price estimation using Random Forest algorithm
- **Multi-Agent Architecture**: Specialized agents for different functionalities
- **AI-Powered Explanations**: Intelligent reasoning for price predictions
- **Market Analysis**: Real-time market trends and insights
- **RESTful API**: Standard API interface with comprehensive documentation
- **Web Interface**: User-friendly web application
- **Comprehensive Logging**: Full audit trail and performance monitoring

### Business Value
- Helps users make informed decisions about vehicle purchases
- Provides transparent pricing with detailed explanations
- Offers market insights and investment advice
- Ensures consistency in price evaluation

---

## Architecture

### 4-Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                             │
├─────────────────────────────────────────────────────────────┤
│ Web Browser │ API Clients │ Mobile Apps │ Swagger UI       │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  API GATEWAY LAYER                          │
├─────────────────────────────────────────────────────────────┤
│ FastAPI Server │ CORS │ Error Handling │ Static Files      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│              BUSINESS LOGIC LAYER                           │
│                (Multi-Agent System)                         │
├─────────────────────────────────────────────────────────────┤
│ Main Agent │ Model Agent │ Market Agent │ Explainer Agent  │
│ Insight Agent │ Logger Agent │ Data Processing Pipeline    │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                               │
├─────────────────────────────────────────────────────────────┤
│ Historical Data │ Market Data │ ML Model │ SQLite DB        │
│ FAISS Index │ Knowledge Docs │ External APIs               │
└─────────────────────────────────────────────────────────────┘
```

### Design Principles
- **Separation of Concerns**: Each layer has distinct responsibilities
- **Modularity**: Components are loosely coupled and highly cohesive
- **Scalability**: Architecture supports horizontal and vertical scaling
- **Maintainability**: Clear structure for easy updates and debugging
- **Extensibility**: Easy to add new features and agents

---

## System Components

### 1. Client Layer
| Component | Technology | Purpose |
|-----------|------------|---------|
| Web Browser | HTML/CSS/JavaScript | Primary user interface |
| API Clients | HTTP/REST | Programmatic access |
| Swagger UI | OpenAPI 3.0 | API documentation and testing |
| Mobile Apps | Future Enhancement | Mobile access |

### 2. API Gateway Layer
| Component | Technology | Purpose |
|-----------|------------|---------|
| FastAPI Server | FastAPI + Uvicorn | Main application server |
| CORS Middleware | FastAPI CORS | Cross-origin request handling |
| Error Handler | Custom Middleware | Centralized error management |
| Static Files | FastAPI StaticFiles | Static content serving |
| Template Engine | Jinja2 | Dynamic HTML rendering |

### 3. Business Logic Layer (Multi-Agent System)
| Agent | Responsibility | Input | Output |
|-------|----------------|-------|--------|
| **Main Agent** | Orchestration & coordination | User request | Final response |
| **Model Agent** | ML prediction execution | Vehicle features | Price prediction |
| **Market Agent** | Market data processing | Raw data sources | Market insights |
| **Explainer Agent** | AI-powered explanations | Prediction context | Human-readable explanation |
| **Insight Agent** | Strategic recommendations | Market data + prediction | Investment advice |
| **Logger Agent** | Audit & monitoring | All system activities | Logs & metrics |

### 4. Data Layer
| Component | Type | Technology | Purpose |
|-----------|------|------------|---------|
| Historical Vehicle Data | File | CSV | Training data |
| Market Trends | File | CSV | Market analysis |
| ML Model | File | Pickle | Trained Random Forest |
| Predictions Database | Database | SQLite | Audit trail |
| Vector Database | Index | FAISS | Similarity search |
| Knowledge Base | Files | Text | Domain knowledge |

---

## Data Flow

### 1. Request Processing Flow
```
User Input → API Request → Main Agent → Agent Coordination → Response Assembly → User Display
```

### 2. Detailed Processing Steps

#### Step 1: Input Validation
- Validate vehicle parameters (age, mileage, make, model)
- Check data types and ranges
- Sanitize input data

#### Step 2: Data Loading & Processing
- Load historical vehicle data (`historical_vehicle_data.csv`)
- Load market trends data (`market_trends.csv`)
- Merge datasets on date column
- Handle missing values and outliers

#### Step 3: Feature Engineering
- Extract features: vehicle_age, mileage, market_index, fuel_price
- Normalize and scale numerical features
- Encode categorical variables

#### Step 4: ML Prediction
- Load Random Forest model (`model.pkl`)
- Validate 4 input features
- Generate price prediction with confidence score

#### Step 5: Market Analysis
- Fetch current market trends
- Calculate market adjustments
- Analyze seasonal factors
- Assess fuel price impact

#### Step 6: AI Explanation Generation
- Use FAISS vector search for similar cases
- Generate human-readable explanations
- Explain feature importance
- Provide reasoning for price

#### Step 7: Insights & Recommendations
- Generate market recommendations
- Provide price trend analysis
- Offer investment advice
- Assess risk factors

#### Step 8: Logging & Monitoring
- Log prediction details to SQLite database
- Record performance metrics
- Track user interactions
- Monitor system health

#### Step 9: Response Assembly
- Aggregate all agent outputs
- Format JSON response
- Include confidence scores
- Validate response structure

---

## Multi-Agent System Design

### Architecture Pattern: Orchestrator Pattern
The Main Agent acts as a central orchestrator, coordinating specialized agents using the **Perceive-Decide-Act** pattern.

### Agent Communication
```
Main Agent (Orchestrator)
    ├── Model Agent (Price Prediction)
    ├── Market Agent (Data Processing)
    ├── Explainer Agent (AI Explanations)
    ├── Insight Agent (Recommendations)
    └── Logger Agent (Monitoring)
```

### Design Patterns Used
- **Orchestrator Pattern**: Central coordination by Main Agent
- **Observer Pattern**: Logger Agent monitors all activities
- **Strategy Pattern**: Different prediction strategies
- **Factory Pattern**: Agent creation and initialization
- **Chain of Responsibility**: Sequential data processing
- **Command Pattern**: Agent task execution
- **Facade Pattern**: Simplified API interface

### Error Handling Strategy
- **Graceful Degradation**: System continues operating with reduced functionality
- **Fallback Mechanisms**: Default values for missing data
- **Circuit Breaker**: Protection against external API failures
- **Retry Logic**: Automatic retry for transient failures
- **Comprehensive Logging**: Detailed error tracking

---

## API Design

### REST Endpoints

#### Core Endpoints
| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| GET | `/` | Web interface | - | HTML page |
| POST | `/predict` | Price prediction | Vehicle data | Prediction response |
| GET | `/health` | Health check | - | System status |
| GET | `/docs` | API documentation | - | Swagger UI |

#### Prediction Request Format
```json
{
    "vehicle_age": 5,
    "mileage": 50000,
    "make": "Toyota",
    "model": "Camry"
}
```

#### Prediction Response Format
```json
{
    "predicted_price": 16712.50,
    "confidence": 0.85,
    "explanation": "Based on the vehicle's age of 5 years and mileage of 50,000...",
    "market_data": {
        "market_index": 1.05,
        "fuel_price": 3.45,
        "trend": "stable"
    },
    "recommendation": "Good value for money. Consider purchasing.",
    "insights": {
        "price_trend": "stable",
        "market_position": "competitive",
        "investment_advice": "reasonable investment"
    },
    "timestamp": "2025-07-28T12:00:00Z",
    "prediction_id": "pred_123456"
}
```

### API Standards
- **RESTful Design**: Standard HTTP methods and status codes
- **JSON Format**: Consistent JSON request/response format
- **OpenAPI 3.0**: Complete API documentation
- **Error Handling**: Standardized error responses
- **Versioning**: API version management strategy

---

## Database Design

### SQLite Database Schema

#### predictions Table
```sql
CREATE TABLE predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prediction_id VARCHAR(50) UNIQUE NOT NULL,
    vehicle_age INTEGER NOT NULL,
    mileage INTEGER NOT NULL,
    make VARCHAR(50),
    model VARCHAR(50),
    predicted_price DECIMAL(10,2) NOT NULL,
    confidence DECIMAL(3,2),
    market_index DECIMAL(5,2),
    fuel_price DECIMAL(5,2),
    explanation TEXT,
    recommendation TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    response_time_ms INTEGER,
    user_session VARCHAR(100),
    ip_address VARCHAR(45)
);
```

#### system_metrics Table
```sql
CREATE TABLE system_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name VARCHAR(50) NOT NULL,
    metric_value DECIMAL(10,4),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    agent_name VARCHAR(50)
);
```

#### error_logs Table
```sql
CREATE TABLE error_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    error_type VARCHAR(50),
    error_message TEXT,
    stack_trace TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    severity VARCHAR(20),
    component VARCHAR(50)
);
```

### FAISS Vector Database
- **Purpose**: Store embeddings for similarity search
- **Index Type**: Flat index for exact search
- **Dimension**: 384 (sentence-transformer embeddings)
- **Storage**: Binary format (.faiss) with metadata (.pkl)

---

## Technology Stack

### Backend Technologies
| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Web Framework** | FastAPI | 0.104+ | REST API development |
| **ASGI Server** | Uvicorn | 0.24+ | High-performance server |
| **Machine Learning** | scikit-learn | 1.3+ | ML model training/inference |
| **Data Processing** | pandas | 2.1+ | Data manipulation |
| **Numerical Computing** | numpy | 1.24+ | Mathematical operations |
| **AI/LLM Framework** | LangChain | 0.0.340+ | AI agent orchestration |
| **Vector Database** | FAISS | 1.7+ | Similarity search |
| **Database** | SQLite | 3.40+ | Data persistence |
| **ORM** | SQLAlchemy | 2.0+ | Database abstraction |

### Frontend Technologies
| Component | Technology | Purpose |
|-----------|------------|---------|
| **Template Engine** | Jinja2 | Dynamic HTML generation |
| **Styling** | CSS3 | User interface styling |
| **Interactivity** | Vanilla JavaScript | Client-side functionality |
| **API Documentation** | Swagger UI | Interactive API docs |

### Development & Deployment
| Component | Technology | Purpose |
|-----------|------------|---------|
| **Containerization** | Docker | Application packaging |
| **Environment Management** | Python venv | Dependency isolation |
| **Package Management** | pip | Python package management |
| **Version Control** | Git | Source code management |

---

## Performance Requirements

### Response Time Targets
| Operation | Target | Acceptable | Maximum |
|-----------|--------|------------|---------|
| Price Prediction | < 200ms | < 500ms | < 1000ms |
| Data Loading | < 100ms | < 300ms | < 500ms |
| API Response | < 300ms | < 700ms | < 1500ms |
| Web Page Load | < 500ms | < 1000ms | < 2000ms |

### Throughput Requirements
- **Concurrent Users**: 50-100 simultaneous users
- **Requests per Second**: 100-200 RPS
- **Daily Predictions**: 10,000-50,000 predictions
- **Data Processing**: 1000 records/second

### Resource Requirements
| Resource | Minimum | Recommended | Maximum |
|----------|---------|-------------|---------|
| **CPU** | 2 cores | 4 cores | 8 cores |
| **RAM** | 4 GB | 8 GB | 16 GB |
| **Storage** | 10 GB | 20 GB | 50 GB |
| **Network** | 10 Mbps | 100 Mbps | 1 Gbps |

### Model Performance
- **Training RMSE**: 658.05
- **Test RMSE**: 2670.00
- **Prediction Accuracy**: ~85% confidence
- **Model Size**: ~50 MB (serialized)
- **Features**: 4 (vehicle_age, mileage, market_index, fuel_price)

---

## Security Considerations

### Input Validation
- **Data Type Validation**: Ensure correct data types
- **Range Validation**: Check numerical ranges
- **SQL Injection Prevention**: Parameterized queries
- **XSS Protection**: Input sanitization

### Authentication & Authorization
- **Future Enhancement**: User authentication system
- **API Keys**: For programmatic access
- **Rate Limiting**: Prevent abuse
- **CORS Configuration**: Controlled cross-origin access

### Data Protection
- **Data Encryption**: At rest and in transit
- **PII Handling**: Minimal personal data collection
- **Audit Logging**: Complete activity tracking
- **Backup Strategy**: Regular data backups

### Infrastructure Security
- **Container Security**: Secure Docker images
- **Network Security**: Firewall configuration
- **Environment Variables**: Secure configuration management
- **Regular Updates**: Security patch management

---

## Deployment Architecture

### Local Development
```
Developer Machine
├── Python Virtual Environment
├── Local SQLite Database
├── Local File Storage
└── Development Server (Uvicorn)
```

### Production Deployment Options

#### Option 1: Single Server Deployment
```
Production Server
├── Docker Container
│   ├── FastAPI Application
│   ├── SQLite Database
│   └── Static Files
├── Reverse Proxy (Nginx)
└── SSL Certificate
```

#### Option 2: Cloud Deployment
```
Cloud Infrastructure
├── Application Server (Docker)
├── Database Service (PostgreSQL)
├── File Storage (S3/Azure Blob)
├── Load Balancer
└── CDN (Static Files)
```

#### Option 3: Microservices (Future)
```
Kubernetes Cluster
├── API Gateway Service
├── Prediction Service
├── Data Processing Service
├── Database Service
└── Monitoring Service
```

### Deployment Process
1. **Code Build**: Create Docker image
2. **Testing**: Run automated tests
3. **Staging**: Deploy to staging environment
4. **Validation**: Perform integration tests
5. **Production**: Deploy to production
6. **Monitoring**: Monitor system health

---

## Scalability & Future Enhancements

### Horizontal Scaling
- **Load Balancing**: Multiple application instances
- **Database Scaling**: Read replicas and sharding
- **Caching**: Redis for frequently accessed data
- **CDN**: Content delivery network for static files

### Vertical Scaling
- **CPU Optimization**: Async processing
- **Memory Optimization**: Efficient data structures
- **Storage Optimization**: Database indexing
- **Network Optimization**: Connection pooling

### Future Enhancements

#### Phase 1: Core Improvements
- **Real-time Market Data**: Live API integration
- **Advanced ML Models**: Deep learning models
- **User Authentication**: User account system
- **Mobile Application**: iOS/Android apps

#### Phase 2: AI Enhancement
- **GPT Integration**: Advanced natural language explanations
- **Computer Vision**: Image-based vehicle assessment
- **Predictive Analytics**: Market trend forecasting
- **Recommendation Engine**: Personalized suggestions

#### Phase 3: Enterprise Features
- **Multi-tenancy**: Support multiple organizations
- **Advanced Analytics**: Business intelligence dashboard
- **API Management**: Rate limiting, quotas, analytics
- **Compliance**: GDPR, SOX compliance features

#### Phase 4: Advanced Capabilities
- **Blockchain Integration**: Transparent vehicle history
- **IoT Integration**: Real-time vehicle data
- **Marketplace Integration**: Direct buying/selling
- **AI Agents Marketplace**: Third-party agent plugins

### Technology Evolution
- **Cloud Native**: Kubernetes-based deployment
- **Event-Driven**: Message queues for async processing
- **Serverless**: Function-as-a-Service components
- **Edge Computing**: Regional data processing

---

## Monitoring & Observability

### Application Monitoring
- **Health Checks**: Endpoint availability monitoring
- **Performance Metrics**: Response time, throughput
- **Error Tracking**: Exception monitoring and alerting
- **Business Metrics**: Prediction accuracy, user satisfaction

### Infrastructure Monitoring
- **Resource Utilization**: CPU, memory, disk usage
- **Network Monitoring**: Bandwidth, latency
- **Database Performance**: Query performance, connection pools
- **Container Metrics**: Docker container health

### Logging Strategy
- **Structured Logging**: JSON format with consistent fields
- **Log Levels**: DEBUG, INFO, WARN, ERROR, CRITICAL
- **Centralized Logging**: Aggregated log collection
- **Log Retention**: Configurable retention policies

### Alerting
- **Performance Alerts**: Response time degradation
- **Error Alerts**: High error rates
- **Resource Alerts**: Resource exhaustion
- **Business Alerts**: Prediction accuracy drops

---

## Conclusion

This High-Level Design document provides a comprehensive overview of the Vehicle Price Prediction System architecture. The multi-agent design enables modular development, easy maintenance, and future scalability. The system is built with modern technologies and follows industry best practices for security, performance, and reliability.

The architecture supports the current requirements while providing a solid foundation for future enhancements and scaling. Regular reviews and updates of this document will ensure it remains aligned with the evolving system requirements and technology landscape.

---

*Document Version: 1.0*  
*Last Updated: July 28, 2025*  
*Next Review Date: January 28, 2026*
