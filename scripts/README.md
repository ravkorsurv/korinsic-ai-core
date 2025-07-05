# Kor.ai Surveillance Platform - Scripts

This directory contains utility scripts for development, deployment, data management, and maintenance.

## Directory Structure

- **development/**: Scripts for local development and testing
- **deployment/**: Scripts for deployment and production management
- **data/**: Scripts for data generation, import/export, and processing
- **maintenance/**: Scripts for system maintenance and monitoring

## Development Scripts

### `development/run_server.py`
Main server runner script for local development.

```bash
python scripts/development/run_server.py
```

### `development/sample_request.py`
Script for testing API endpoints with sample data.

```bash
python scripts/development/sample_request.py
```

### `development/demo_e2e.py`
End-to-end demonstration script.

```bash
python scripts/development/demo_e2e.py
```

### `development/github_app_config.js`
GitHub app configuration for CI/CD integration.

### `development/github_commit_service.js`
GitHub commit service for automated workflows.

## Data Scripts

### `data/kor_ai_dynamodb_implementation.py`
DynamoDB implementation and data model management.

```bash
python scripts/data/kor_ai_dynamodb_implementation.py
```

## Usage Guidelines

1. **Development Scripts**: Use for local development and testing
2. **Deployment Scripts**: Use for production deployment and management
3. **Data Scripts**: Use for data processing and model management
4. **Maintenance Scripts**: Use for system maintenance and monitoring

## Adding New Scripts

When adding new scripts:
1. Place them in the appropriate subdirectory
2. Include proper documentation and usage examples
3. Add executable permissions if needed
4. Follow the existing naming conventions
5. Update this README with the new script information

## Environment Setup

Make sure you have the required dependencies installed:

```bash
pip install -r requirements.txt
```

For development scripts, you may need additional development dependencies.