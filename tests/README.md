# Person-Centric Surveillance Test Suite

This directory contains comprehensive tests for the Person-Centric Surveillance System, covering all components from entity resolution to regulatory explainability.

## 🧪 Test Structure

### Test Categories

- **Unit Tests** (`@pytest.mark.unit`): Test individual components in isolation
- **Integration Tests** (`@pytest.mark.integration`): Test component interactions
- **End-to-End Tests** (`@pytest.mark.e2e`): Test complete workflows
- **Performance Tests** (`@pytest.mark.performance`): Test system performance and scalability
- **Regulatory Tests** (`@pytest.mark.regulatory`): Test regulatory compliance features

### Test Files

- `test_person_centric_surveillance.py` - Main test suite with comprehensive coverage
- `test_regulatory_compliance.py` - Specialized regulatory compliance tests
- `conftest.py` - Shared fixtures and test configuration

## 🚀 Running Tests

### Prerequisites

```bash
# Install pytest and dependencies
pip install pytest pytest-cov pytest-html pytest-xdist

# Or install from requirements file (if available)
pip install -r requirements-test.txt
```

### Quick Start

```bash
# Run all tests
python3 scripts/run_tests.py --all

# Run unit tests only
python3 scripts/run_tests.py --unit

# Run tests with coverage
python3 scripts/run_tests.py --all --coverage

# Run tests in parallel
python3 scripts/run_tests.py --all --parallel
```

### Test Runner Options

The `scripts/run_tests.py` script provides various testing options:

```bash
# Test Categories
python3 scripts/run_tests.py --unit           # Unit tests
python3 scripts/run_tests.py --integration    # Integration tests
python3 scripts/run_tests.py --e2e            # End-to-end tests
python3 scripts/run_tests.py --regulatory     # Regulatory compliance tests
python3 scripts/run_tests.py --performance    # Performance tests

# Specific Components
python3 scripts/run_tests.py --component entity_resolution
python3 scripts/run_tests.py --component evidence_aggregation
python3 scripts/run_tests.py --component cross_typology
python3 scripts/run_tests.py --component alert_generation
python3 scripts/run_tests.py --component explainability

# Specific Risk Typologies
python3 scripts/run_tests.py --typology insider_dealing
python3 scripts/run_tests.py --typology spoofing
python3 scripts/run_tests.py --typology market_manipulation

# Execution Options
python3 scripts/run_tests.py --quick          # Fast tests only
python3 scripts/run_tests.py --smoke          # Smoke tests
python3 scripts/run_tests.py --failed         # Re-run failed tests
python3 scripts/run_tests.py --parallel       # Parallel execution
python3 scripts/run_tests.py --coverage       # Generate coverage report

# Utilities
python3 scripts/run_tests.py --check          # Check test environment
python3 scripts/run_tests.py --list           # List available tests
python3 scripts/run_tests.py --report         # Generate comprehensive report
```

### Direct pytest Usage

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m "unit or integration"
pytest -m "not slow"

# Run specific test files
pytest tests/test_person_centric_surveillance.py
pytest tests/test_regulatory_compliance.py

# Run specific test classes or methods
pytest tests/test_person_centric_surveillance.py::TestEntityResolution
pytest tests/test_person_centric_surveillance.py::TestEntityResolution::test_identity_matcher_name_similarity

# Run with coverage
pytest --cov=src --cov-report=html

# Run in parallel (requires pytest-xdist)
pytest -n auto

# Run with verbose output
pytest -v

# Stop on first failure
pytest -x
```

## 📊 Test Coverage

The test suite aims for comprehensive coverage of:

### Core Components
- ✅ Entity Resolution (`TestEntityResolution`)
- ✅ Person Evidence Aggregation (`TestPersonEvidenceAggregator`) 
- ✅ Person-Centric Bayesian Nodes (`TestPersonCentricNodes`)
- ✅ Cross-Typology Engine (`TestCrossTypologyEngine`)
- ✅ Alert Generation (`TestPersonCentricAlertGenerator`)
- ✅ Regulatory Explainability (`TestRegulatoryExplainability`)

### Risk Typologies
- Insider Dealing Detection
- Spoofing Detection
- Market Manipulation Detection
- Front Running Detection
- Wash Trading Detection
- Cross-Desk Collusion Detection

### Regulatory Frameworks
- STOR (Suspicious Transaction and Order Reporting)
- MAR (Market Abuse Regulation) Articles 8 & 12
- MiFID II Article 17
- Cross-jurisdictional compliance

### Data Quality & Performance
- Missing data handling
- Invalid data filtering
- Large dataset processing
- Concurrent processing
- Memory usage optimization

## 🏗️ Test Architecture

### TestDataFactory
Provides consistent test data creation:
- `create_sample_trade_data()` - Generate realistic trade data
- `create_sample_person_profile()` - Create person profiles
- `create_sample_cross_typology_signal()` - Generate cross-typology signals
- `create_test_config()` - Provide test configuration

### Test Fixtures (conftest.py)
- `test_config` - Test configuration
- `sample_trade_data` - Sample trading data
- `high_risk_scenario_data` - High-risk test scenarios
- `performance_test_data` - Large datasets for performance testing
- Mock services for isolated testing

### Test Utilities
- `TestUtils.assert_valid_probability()` - Validate probability values
- `TestUtils.assert_alert_structure()` - Validate alert format
- `TestUtils.assert_person_profile_structure()` - Validate person profiles

## 🎯 Test Scenarios

### High-Risk Scenarios
- Insider dealing with confidential information access
- Cross-account coordination patterns
- Large volume trades before announcements
- Suspicious communication timing

### Low-Risk Scenarios
- Normal trading patterns
- Standard communication flows
- Routine market making activities

### Edge Cases
- Missing or incomplete data
- Invalid data formats
- Network timeouts and failures
- Memory constraints

### Performance Scenarios
- 10,000+ trades processing
- Multiple concurrent persons
- Cross-account pattern detection at scale
- Real-time alert generation

## 📈 Performance Benchmarks

Expected performance targets:
- **Throughput**: > 100 trades/second processing
- **Memory**: < 500MB for 10,000 trades
- **Latency**: < 30 seconds for full pipeline
- **Scalability**: Linear scaling up to 100 concurrent persons

## 🔍 Debugging Tests

### Common Issues
1. **Import Errors**: Ensure `src/` is in Python path
2. **Missing Dependencies**: Install test requirements
3. **Configuration Issues**: Check test config files
4. **Mock Failures**: Verify mock setups in fixtures

### Debug Commands
```bash
# Run single test with detailed output
pytest tests/test_person_centric_surveillance.py::TestEntityResolution::test_identity_matcher_name_similarity -v -s

# Run with pdb debugger
pytest --pdb

# Show local variables on failure
pytest --tb=long

# Capture stdout/stderr
pytest -s
```

## 📋 Test Reporting

### Coverage Reports
- HTML: `htmlcov/index.html`
- Terminal: Coverage summary in test output
- XML: `coverage.xml` for CI/CD integration

### Test Reports
- HTML: `reports/test_report.html`
- JUnit XML: `reports/junit.xml`
- Performance: Duration reports in test output

## 🚨 Continuous Integration

The test suite is designed for CI/CD integration:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    python3 scripts/run_tests.py --all --coverage --parallel
    
- name: Upload Coverage
  uses: codecov/codecov-action@v1
  with:
    file: ./coverage.xml
```

## 🔧 Adding New Tests

### Test Structure
```python
class TestNewComponent:
    """Test new component functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.config = TestDataFactory.create_test_config()
        # Setup component
    
    def test_basic_functionality(self):
        """Test basic component functionality"""
        # Arrange
        # Act
        # Assert
    
    @pytest.mark.integration
    def test_integration_scenario(self):
        """Test integration with other components"""
        # Test integration logic
    
    @pytest.mark.performance
    def test_performance_scenario(self):
        """Test performance characteristics"""
        # Test performance
```

### Test Markers
Use appropriate markers for test categorization:
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.regulatory` - Regulatory compliance tests

## 📞 Support

For test-related issues:
1. Check test output for specific error messages
2. Verify test environment with `python3 scripts/run_tests.py --check`
3. Review test configuration in `pytest.ini` and `conftest.py`
4. Run individual tests to isolate issues
5. Check mock configurations and test data

## 🎉 Test Results

A successful test run should show:
- ✅ All test categories passing
- 📊 Coverage > 80%
- ⚡ Performance within benchmarks
- 🔒 Regulatory compliance validated
- 📋 Clean audit trails generated

Example successful output:
```
==================== test session starts ====================
collected 156 items

tests/test_person_centric_surveillance.py::TestEntityResolution::test_identity_matcher_name_similarity PASSED
tests/test_person_centric_surveillance.py::TestEntityResolution::test_identity_graph_person_creation PASSED
...
tests/test_regulatory_compliance.py::TestSTORCompliance::test_stor_eligibility_criteria PASSED

==================== 156 passed in 45.23s ====================

Coverage: 87%
🎉 All requested tests completed successfully!
```