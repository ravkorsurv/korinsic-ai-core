# Kor.ai Surveillance Platform - Configuration

This directory contains configuration files for the Kor.ai Surveillance Platform.

## Files

### `bayesian_model_config.json`
Main configuration file for Bayesian models including:
- Model parameters
- Risk thresholds
- Node definitions
- Probability distributions

### `bayesian_model_config_backup.json`
Backup of the original Bayesian model configuration file (preserved for reference).

## Configuration Structure

Configuration files should follow the environment-specific naming convention:
- `base.json`: Base configuration shared across environments
- `development.json`: Development environment overrides
- `production.json`: Production environment overrides
- `testing.json`: Testing environment overrides

## Model Configuration

Model configurations include:
- **Risk Thresholds**: Configurable thresholds for different risk levels
- **Node Definitions**: Bayesian network node configurations
- **Evidence Weights**: Weights for different types of evidence
- **Fallback Values**: Default values when evidence is missing

## Usage

The application loads configuration files based on the environment:

```python
from utils.config import Config

config = Config()
thresholds = config.get_risk_thresholds()
```

## Environment Variables

Configuration can be overridden by environment variables:
- `INSIDER_HIGH_THRESHOLD`: High risk threshold for insider dealing
- `SPOOFING_HIGH_THRESHOLD`: High risk threshold for spoofing
- `LOG_LEVEL`: Logging level
- `DEBUG`: Debug mode

## Adding New Configuration

When adding new configuration:
1. Add to the appropriate environment file
2. Document the configuration option
3. Provide reasonable default values
4. Test with different environments
5. Update this README

## Security

- Never commit secrets or sensitive data
- Use environment variables for sensitive configuration
- Encrypt sensitive configuration files if needed
- Regularly rotate any secrets or keys