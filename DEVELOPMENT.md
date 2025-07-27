# Development Guide

This guide provides comprehensive information for developers working on the Vehicle Price Prediction system.

## Table of Contents

1. [Development Setup](#development-setup)
2. [Code Structure](#code-structure)
3. [Testing Strategy](#testing-strategy)
4. [Code Quality Standards](#code-quality-standards)
5. [API Development](#api-development)
6. [Agent Development](#agent-development)
7. [Database Management](#database-management)
8. [Deployment](#deployment)
9. [Contributing](#contributing)

## Development Setup

### Prerequisites

- Python 3.9+
- Git
- Docker (optional, for containerized development)
- VS Code or PyCharm (recommended)

### Initial Setup

```bash
# Clone the repository
git clone <repository-url>
cd vehicle-price-agent-multi

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup pre-commit hooks
pip install pre-commit
pre-commit install

# Initialize database
python -c "from src.api import init_db; init_db()"
```

### IDE Configuration

#### VS Code Settings

Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"]
}
```

## Code Structure

### Architecture Overview

```
src/
├── agent.py              # Main prediction agent (perceive-decide-act)
├── model.py               # ML model training and utilities
├── data_loader.py         # Data loading and preprocessing
├── api.py                 # FastAPI REST endpoints
├── retriever.py           # Data retrieval utilities
├── explainer.py           # Model explanation utilities
└── agents/                # Specialized agent modules
    ├── market_agent.py    # Market data collection
    ├── model_agent.py     # ML model management
    ├── explainer_agent.py # Prediction explanations
    ├── insight_agent.py   # Business insights
    └── logger_agent.py    # Logging and monitoring
```

### Design Patterns

1. **Agent Pattern**: Each agent follows perceive-decide-act paradigm
2. **Factory Pattern**: Model creation and configuration
3. **Observer Pattern**: Event logging and monitoring
4. **Strategy Pattern**: Different prediction algorithms

### Coding Standards

- **Type Hints**: All functions must have type hints
- **Docstrings**: Google-style docstrings for all public methods
- **Error Handling**: Comprehensive exception handling
- **Logging**: Structured logging for debugging and monitoring

## Testing Strategy

### Test Categories

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete workflows
4. **Performance Tests**: Load and stress testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test types
pytest tests/ -m unit
pytest tests/ -m integration

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run tests in parallel
pytest tests/ -n auto

# Use the test runner script
python run_tests.py --type all --verbose
```

### Test Structure

```python
class TestClassName:
    """Test suite for ClassName functionality."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        return {...}
    
    def test_method_success(self, sample_data):
        """Test successful method execution."""
        # Arrange
        expected = "expected_result"
        
        # Act
        result = method_under_test(sample_data)
        
        # Assert
        assert result == expected
    
    def test_method_error_handling(self):
        """Test method handles errors appropriately."""
        with pytest.raises(ValueError, match="error message"):
            method_under_test(invalid_input)
```

### Mocking Guidelines

```python
from unittest.mock import Mock, patch

# Mock external dependencies
@patch('module.external_service')
def test_with_mocked_service(mock_service):
    mock_service.return_value = expected_data
    # Test implementation
```

## Code Quality Standards

### Formatting

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Check formatting
black --check src/ tests/
isort --check-only src/ tests/
```

### Linting

```bash
# Run flake8
flake8 src/ tests/

# Run type checking
mypy src/
```

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
```

## API Development

### Adding New Endpoints

1. **Define Pydantic Models**:
```python
class PredictionRequest(BaseModel):
    vehicle_age: int = Field(..., ge=0, le=50)
    mileage: int = Field(..., ge=0, le=500000)
    # Additional fields...
```

2. **Implement Endpoint**:
```python
@app.post("/predict", response_model=PredictionResponse)
async def predict_price(request: PredictionRequest):
    """Predict vehicle price based on input features."""
    try:
        # Implementation
        return PredictionResponse(...)
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")
```

3. **Add Tests**:
```python
def test_predict_endpoint(client):
    response = client.post("/predict", json={
        "vehicle_age": 3,
        "mileage": 45000
    })
    assert response.status_code == 200
    assert "predicted_price" in response.json()
```

### Error Handling

```python
from fastapi import HTTPException

# Standard error responses
raise HTTPException(
    status_code=400, 
    detail="Invalid input data"
)

raise HTTPException(
    status_code=500, 
    detail="Internal server error"
)
```

## Agent Development

### Creating New Agents

1. **Agent Base Structure**:
```python
class NewAgent:
    """Agent description and purpose."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize agent with configuration."""
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def perceive(self, data: Any) -> Any:
        """Process input data."""
        pass
    
    def decide(self, processed_data: Any) -> Any:
        """Make decisions based on processed data."""
        pass
    
    def act(self, decision: Any) -> Any:
        """Execute actions based on decisions."""
        pass
```

2. **Agent Integration**:
```python
# Register agent in main system
from src.agents.new_agent import NewAgent

agent = NewAgent(config)
```

### Agent Communication

Agents communicate through:
- **Event System**: Publish/subscribe pattern
- **Shared State**: Redis or database
- **Message Queues**: For asynchronous processing

## Database Management

### Schema Management

```python
# Define database models
class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    predicted_price = Column(Float)
    # Additional fields...
```

### Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Add new column"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Database Testing

```python
@pytest.fixture
def db_session():
    """Create test database session."""
    # Setup test database
    # Yield session
    # Cleanup
```

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ src/
COPY data/ data/

EXPOSE 8000
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Configuration

```bash
# Development
export ENVIRONMENT=development
export DEBUG=True

# Production
export ENVIRONMENT=production
export DEBUG=False
export DATABASE_URL=postgresql://...
```

### Health Checks

```python
@app.get("/health")
async def health_check():
    """Application health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }
```

## Contributing

### Workflow

1. **Create Feature Branch**:
```bash
git checkout -b feature/new-feature
```

2. **Implement Changes**:
   - Write code following standards
   - Add comprehensive tests
   - Update documentation

3. **Quality Checks**:
```bash
# Run all checks
make check-all

# Or individual checks
make format lint test
```

4. **Submit Pull Request**:
   - Provide clear description
   - Reference relevant issues
   - Ensure CI passes

### Code Review Guidelines

- **Functionality**: Does the code work as intended?
- **Testing**: Are there adequate tests?
- **Documentation**: Is the code well-documented?
- **Performance**: Any performance implications?
- **Security**: Any security concerns?

### Release Process

1. **Version Bump**: Update version numbers
2. **Changelog**: Update CHANGELOG.md
3. **Tag Release**: Create git tag
4. **Deploy**: Deploy to production environment

## Best Practices

### Performance

- **Caching**: Cache frequently accessed data
- **Database**: Use connection pooling
- **Async**: Use async/await for I/O operations
- **Profiling**: Profile bottlenecks

### Security

- **Input Validation**: Validate all inputs
- **Authentication**: Secure API endpoints
- **Secrets**: Use environment variables
- **Logging**: Don't log sensitive data

### Monitoring

- **Metrics**: Track key performance indicators
- **Logging**: Structured logging
- **Alerts**: Set up monitoring alerts
- **Tracing**: Distributed tracing for debugging

## Troubleshooting

### Common Issues

1. **Import Errors**: Check virtual environment activation
2. **Database Errors**: Verify database configuration
3. **Test Failures**: Check test dependencies
4. **Performance Issues**: Profile and optimize bottlenecks

### Debug Tools

```python
# Logging
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug message")

# Debugging
import pdb; pdb.set_trace()

# Profiling
import cProfile
cProfile.run('function_to_profile()')
```

### Getting Help

- Check existing issues and documentation
- Run tests to identify problems
- Use debugging tools to investigate
- Ask for help in team channels

---

This development guide should be updated as the project evolves. Always refer to the latest version in the repository.
