# Kor.ai – Surveillance Platform Core

Kor.ai is an AI-powered surveillance platform built to detect market abuse risks such as insider dealing and spoofing, with a focus on commodities and energy trading. This repository contains the core logic, Bayesian inference engine, data mapping, and service orchestration for alert generation.

---

## 📁 Project Structure

The codebase follows a professional enterprise architecture with clear separation of concerns:

```
kor-ai-core/
├── src/                          # Core application source code
│   ├── app.py                   # Main Flask application entry point
│   ├── api/                     # API layer with versioning
│   │   └── v1/                  # API version 1
│   │       ├── routes/          # API endpoints by functional area
│   │       ├── middleware/      # Request/response middleware
│   │       └── schemas/         # Request/response schemas
│   ├── core/                    # Core business logic
│   │   ├── engines/            # Analytical engines
│   │   ├── processors/         # Data processing components
│   │   └── services/           # Business service layer
│   ├── models/                  # Data models and ML models
│   │   ├── bayesian/           # Bayesian inference models
│   │   ├── data/               # Data model definitions
│   │   └── shared/             # Shared model components
│   └── utils/                  # Utility functions and helpers
├── tests/                       # Comprehensive test suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   ├── e2e/                    # End-to-end tests
│   ├── performance/            # Performance tests
│   ├── fixtures/               # Test data fixtures
│   └── utils/                  # Test utilities and helpers
├── config/                     # Configuration management
│   ├── base.json              # Base configuration
│   ├── development.json       # Development environment
│   ├── production.json        # Production environment
│   ├── testing.json           # Testing environment
│   ├── models/                # Model-specific configurations
│   └── deployment/            # Deployment configurations
├── docs/                       # Documentation
│   ├── api/                   # API documentation
│   ├── models/                # Model documentation
│   ├── deployment/            # Deployment guides
│   ├── development/           # Development guides
│   └── architecture/          # Architecture documentation
├── scripts/                    # Utility scripts
│   ├── development/           # Development scripts
│   ├── deployment/            # Deployment scripts
│   ├── data/                  # Data management scripts
│   └── maintenance/           # Maintenance scripts
├── deployment/                 # Deployment configurations
├── archive/                   # Archived/legacy files
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container configuration
├── .env.example              # Environment configuration template
└── pytest.ini               # Test configuration
```

---

## 🧭 Navigating the Codebase

### Core Components

**Entry Point:** `src/app.py`
- Main Flask application
- CORS configuration
- API route registration
- Server initialization

**API Layer:** `src/api/v1/`
- **Routes:** Organized by functional area (analysis, alerts, health)
- **Middleware:** Request validation, error handling, logging
- **Schemas:** Request/response validation and documentation

**Business Logic:** `src/core/`
- **Engines:** Bayesian inference engine, risk calculation
- **Processors:** Data processing pipeline, evidence mapping
- **Services:** High-level business logic coordination

**Models:** `src/models/`
- **Bayesian:** Probabilistic models for risk detection
- **Data:** Data structure definitions and validators
- **Shared:** Common model components and utilities

### Key Files to Understand

1. **`src/app.py`** - Application entry point
2. **`src/api/v1/routes/analysis.py`** - Main API endpoints
3. **`src/core/engines/bayesian_engine.py`** - Core inference engine
4. **`src/models/bayesian/insider_dealing/model.py`** - Insider dealing model
5. **`config/base.json`** - Base configuration
6. **`tests/conftest.py`** - Test configuration and fixtures

### Development Workflow

1. **Configuration:** Start with `config/` files for environment setup
2. **API Testing:** Use `scripts/development/` for testing endpoints
3. **Model Development:** Work in `src/models/bayesian/` for new models
4. **Testing:** Use `tests/` with comprehensive test utilities
5. **Documentation:** Update `docs/` for changes

---

## 🐳 Containerization

### Docker Configuration

**Dockerfile** is configured for production deployment:

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "src/app.py"]
```

### Build and Run

```bash
# Build the container
docker build -t kor-ai-core .

# Run in development mode
docker run -p 5000:5000 -e ENVIRONMENT=development kor-ai-core

# Run in production mode
docker run -p 5000:5000 -e ENVIRONMENT=production -e DATABASE_URL=... kor-ai-core
```

### Environment Variables

Key environment variables for containerized deployment:

- `ENVIRONMENT`: `development|production|testing`
- `PORT`: Server port (default: 5000)
- `HOST`: Server host (default: 0.0.0.0)
- `DATABASE_URL`: Database connection string
- `REDIS_URL`: Redis connection string
- `LOG_LEVEL`: Logging level
- `INSIDER_HIGH_THRESHOLD`: Risk threshold configuration
- `SPOOFING_HIGH_THRESHOLD`: Risk threshold configuration

### Docker Compose (Optional)

For local development with dependencies:

```yaml
version: '3.8'
services:
  kor-ai-core:
    build: .
    ports:
      - "5000:5000"
    environment:
      - ENVIRONMENT=development
    depends_on:
      - redis
      - postgres
  redis:
    image: redis:alpine
  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=korai
      - POSTGRES_USER=korai
      - POSTGRES_PASSWORD=korai
```

---

## 🌿 Branch Strategy & Development Workflow

### Branch Structure

**Main Branches:**
- `main` - Production-ready code, stable releases
- `develop` - Integration branch for features (optional)

**Feature Branches:**
- `feature/[feature-name]` - New features
- `bugfix/[bug-description]` - Bug fixes
- `hotfix/[urgent-fix]` - Production hotfixes
- `refactor/[refactor-description]` - Code refactoring
- `docs/[documentation-update]` - Documentation updates

### Development Workflow

1. **Feature Development:**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/new-detection-model
   # ... make changes ...
   git add .
   git commit -m "Add spoofing detection model"
   git push origin feature/new-detection-model
   # Create PR to main
   ```

2. **Bug Fixes:**
   ```bash
   git checkout -b bugfix/fix-bayesian-inference
   # ... fix bug ...
   git push origin bugfix/fix-bayesian-inference
   # Create PR to main
   ```

3. **Hotfixes:**
   ```bash
   git checkout main
   git checkout -b hotfix/critical-security-fix
   # ... fix critical issue ...
   git push origin hotfix/critical-security-fix
   # Create PR to main with urgent label
   ```

### Pull Request Process

1. **Create PR** with descriptive title and description
2. **Code Review** by team members
3. **Tests** must pass (automated CI/CD)
4. **Documentation** updated if needed
5. **Merge** to main after approval

### Branch Cleanup

**Active Branches:**
- `main` - Keep (production)
- `cursor/suggest-structural-improvements-without-disruption-4682` - Merge to main then delete

**Branches to Clean Up:**
- `cursor/confirm-task-completion-731a` - Delete (completed task)
- `cursor/create-comprehensive-data-model-54a0` - Delete (integrated)
- `cursor/write-complete-code-f9b6` - Delete (integrated)
- `init/github-pr-bot-service` - Keep for reference or archive

---

## 🚀 Quick Start

### 1. Installation

```bash
git clone https://github.com/your-org/kor-ai-core.git
cd kor-ai-core

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit configuration as needed
nano .env
```

### 3. Run the Server

```bash
# Using the development script
python scripts/development/run_server.py

# Or run tests first
python scripts/development/run_tests.py

# Or directly
python src/app.py
```

The server will start on `http://localhost:5000`

### 4. Test the API

```bash
# Run comprehensive tests
python scripts/development/run_tests.py --mode all

# Or test specific components
python scripts/development/run_tests.py --mode unit
```

---

## 📖 API Endpoints

### Health Check
```http
GET /health
```

### Analyze Trading Data
```http
POST /api/v1/analyze
Content-Type: application/json

{
  "trades": [...],
  "orders": [...],
  "trader_info": {...},
  "material_events": [...],
  "market_data": {...}
}
```

### Batch Analysis
```http
POST /api/v1/analyze/batch
Content-Type: application/json

{
  "datasets": [
    {
      "id": "dataset_1",
      "trades": [...],
      "orders": [...],
      ...
    }
  ]
}
```

### Real-time Analysis
```http
POST /api/v1/analyze/realtime
Content-Type: application/json

{
  "stream_data": {...},
  "analysis_config": {...}
}
```

### Get Alert History
```http
GET /api/v1/alerts/history?limit=100&type=INSIDER_DEALING
```

---

## ⚙️ Configuration Management

The platform uses an advanced configuration system with environment-specific settings:

### Configuration Structure
```
config/
├── base.json              # Base configuration
├── development.json       # Development overrides  
├── production.json        # Production overrides
├── testing.json          # Testing overrides
├── models/                # Model configurations
│   └── bayesian_models.json
└── deployment/            # Deployment configurations
```

### Environment Variables

Override configuration with environment variables:

- `ENVIRONMENT`: development/production/testing (default: development)
- `DEBUG`: Enable debug mode
- `PORT`: Server port (default: 5000)
- `HOST`: Server host (default: 0.0.0.0)
- `LOG_LEVEL`: Logging level (DEBUG/INFO/WARNING/ERROR)
- `DATABASE_URL`: Database connection string
- `REDIS_URL`: Redis connection string
- `INSIDER_HIGH_THRESHOLD`: High risk threshold for insider dealing
- `SPOOFING_HIGH_THRESHOLD`: High risk threshold for spoofing

### Configuration Usage

```python
from src.utils.config import ConfigManager

config = ConfigManager()
# Access configuration with dot notation
db_host = config.get('database.host')
# Environment-specific values
debug_mode = config.get('debug', default=False)
```

---

## 🧠 Bayesian Models

### Model Architecture

The platform uses a sophisticated Bayesian inference system located in `src/models/bayesian/`:

**Insider Dealing Model** (`src/models/bayesian/insider_dealing/`)
- **Nodes**: MaterialInfo, TradingActivity, Timing, PriceImpact, Risk
- **Features**: Access to material information, unusual trading patterns, suspicious timing
- **Inference**: Variable elimination using pgmpy

**Spoofing Model** (Future - `src/models/bayesian/spoofing/`)
- **Nodes**: OrderPattern, CancellationRate, PriceMovement, VolumeRatio, Risk
- **Features**: Layered orders, high cancellation rates, volume imbalances

**Shared Components** (`src/models/bayesian/shared/`)
- **Node Library**: Common node definitions and utilities
- **Model Builder**: Framework for constructing Bayesian networks
- **Fallback Logic**: Handling missing evidence

### Model Registry

```python
from src.models.bayesian.registry import BayesianModelRegistry

registry = BayesianModelRegistry()
model = registry.get_model('insider_dealing')
result = model.analyze(evidence)
```

---

## 📊 Evidence Sufficiency Index (ESI)

The Evidence Sufficiency Index (ESI) measures how well-supported risk scores are based on:

- **Node Activation Ratio**: Proportion of active nodes in the Bayesian network
- **Mean Confidence Score**: Average confidence level of inputs
- **Fallback Ratio**: Proportion of nodes using fallback priors
- **Contribution Entropy**: Distribution evenness of node contributions
- **Cross-Cluster Diversity**: Evidence spread across node groups

### ESI Integration

```json
{
  "evidence_sufficiency_index": 0.84,
  "esi_badge": "Strong",
  "risk_scores": {
    "insider_dealing": {
      "overall_score": 0.73,
      "confidence": "High"
    }
  }
}
```

---

## 🧪 Testing Framework

### Test Organization

**Unit Tests** (`tests/unit/`)
- Individual component testing
- Mock-based isolation
- Fast execution

**Integration Tests** (`tests/integration/`)
- Component interaction testing
- Database integration
- API endpoint testing

**End-to-End Tests** (`tests/e2e/`)
- Full workflow testing
- Real scenario simulation
- Performance validation

**Performance Tests** (`tests/performance/`)
- Load testing
- Memory usage analysis
- Response time measurement

### Test Utilities

**Test Fixtures** (`tests/fixtures/`)
- Sample data sets
- Mock configurations
- Test scenarios

**Test Helpers** (`tests/utils/`)
- Custom assertions
- Data generators
- Mock factories

### Running Tests

```bash
# Run all tests
python scripts/development/run_tests.py

# Run specific test types
python scripts/development/run_tests.py --mode unit
python scripts/development/run_tests.py --mode integration
python scripts/development/run_tests.py --mode e2e

# Run with coverage
python scripts/development/run_tests.py --mode coverage
```

---

## 📊 Monitoring & Logging

**Structured Logging** (`src/utils/logger.py`)
- JSON format for production
- Environment-specific configuration
- Multiple log levels and handlers

**Configuration-Driven Logging**
- File rotation and cleanup
- Separate error logs
- Performance metrics logging

**Usage:**
```python
from src.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Risk analysis completed", extra={"risk_score": 0.85})
```

---

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Follow** the coding standards and add tests
4. **Update** documentation if needed
5. **Commit** your changes (`git commit -m 'Add amazing feature'`)
6. **Push** to the branch (`git push origin feature/amazing-feature`)
7. **Create** a Pull Request with detailed description

### Code Standards

- Follow PEP 8 for Python code
- Add type hints where appropriate
- Include docstrings for functions and classes
- Write comprehensive tests
- Update configuration if needed

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Review the documentation in `docs/`
- Check the development guides in `docs/development/`
- Contact the development team

---

## 🔮 Roadmap

- [ ] Enhanced ML models with deep learning
- [ ] Real-time streaming data processing
- [ ] Advanced visualization dashboard  
- [ ] Integration with major trading platforms
- [ ] Regulatory reporting automation
- [ ] Multi-language support
- [ ] Cloud-native deployment options
- [ ] Advanced model explainability features
