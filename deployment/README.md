# Kor.ai Surveillance Platform - Deployment

This directory contains deployment configurations and related files for the Kor.ai Surveillance Platform.

## Files

### `amplify.yml`
AWS Amplify deployment configuration for frontend and API hosting.

Contains build settings, environment variables, and deployment phases for:
- Frontend build process
- API deployment
- Environment-specific configurations

## Deployment Options

### AWS Amplify
The platform is configured for deployment on AWS Amplify with:
- Automated builds from git commits
- Environment-specific deployments
- Integrated CI/CD pipeline

### Local Development
For local development, use:
```bash
python scripts/development/run_server.py
```

### Docker Deployment
Docker deployment configurations and scripts can be added here for containerized deployments.

## Configuration Management

Deployment configurations should be:
1. Environment-specific (dev/staging/prod)
2. Properly secured (no hardcoded secrets)
3. Documented with usage instructions
4. Version controlled

## Environment Variables

Make sure to set up the following environment variables:
- `ENVIRONMENT`: development/staging/production
- `DEBUG`: Enable debug mode
- `PORT`: Server port (default: 5000)
- `INSIDER_HIGH_THRESHOLD`: High risk threshold for insider dealing
- `SPOOFING_HIGH_THRESHOLD`: High risk threshold for spoofing
- `LOG_LEVEL`: Logging level (DEBUG/INFO/WARNING/ERROR)

## Adding New Deployment Configurations

When adding new deployment configurations:
1. Use environment-specific naming
2. Include proper documentation
3. Test thoroughly before production use
4. Update this README with new configurations
