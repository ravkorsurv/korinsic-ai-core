"""
Core Package for Korinsic AI Surveillance Platform.

This package contains the core business logic and processing components
for the financial market surveillance system. It provides the foundational
architecture for market abuse detection and analysis.

Components:
- **Bayesian Engine**: Core Bayesian inference engine for risk calculation
- **Data Processor**: Trading data ingestion, validation, and preprocessing
- **Alert Generator**: Risk-based alert creation and management
- **Evidence Mapper**: Evidence collection and sufficiency analysis
- **Risk Calculator**: Multi-model risk aggregation and scoring
- **Regulatory Services**: Compliance reporting and explainability

Architecture:
The core package follows a layered architecture with clear separation of concerns:
1. **Data Layer**: Raw data processing and validation
2. **Model Layer**: Bayesian inference and risk calculation
3. **Service Layer**: Business logic and workflow orchestration
4. **API Layer**: External interfaces and response formatting

Design Principles:
- Modularity: Each component has a single responsibility
- Extensibility: Easy to add new detection models
- Reliability: Comprehensive error handling and logging
- Compliance: Built-in regulatory reporting capabilities
- Performance: Optimized for high-throughput analysis

Version: 1.0.0 - Core surveillance platform capabilities
Compliance: Designed for MiFID II, MAR, EMIR regulatory requirements
"""
