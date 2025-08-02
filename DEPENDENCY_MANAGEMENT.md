# Dependency Management

## 🎯 **Single-Source Dependency Management**

This project follows a **single-source dependency management approach** using only `setup.py` to avoid conflicts and maintenance issues. All dependencies are defined in one place with clear version constraints.

---

## 📦 **Dependency Categories**

### **Core Dependencies (`install_requires`)**
Required for basic functionality - installed automatically with the package:

```python
# Core scientific computing stack - relaxed for performance improvements
"numpy>=1.20.0"                  # Numerical operations - allow latest optimizations
"pandas>=1.3.0"                  # Data manipulation - allow performance improvements  
"scipy>=1.7.0"                   # Scientific computing - allow algorithm optimizations

# Bayesian Networks and graph operations  
"pgmpy>=0.1.19,<1.0.0"           # Bayesian Network library - keep bound (API stability)
"networkx>=2.6"                  # Graph operations - stable API, allow latest

# Visualization and plotting - stable APIs, allow improvements
"matplotlib>=3.3.0"              # Basic plotting - mature API
"seaborn>=0.11.0"                # Statistical plotting - stable API

# Machine learning and utilities
"scikit-learn>=1.0.0"            # ML utilities - stable API since 1.0
"joblib>=1.0.0"                  # Parallel processing - stable, allow latest

# Progress and configuration - stable utilities
"tqdm>=4.60.0"                   # Progress bars - stable API
"pyyaml>=5.4.0"                  # YAML configuration - stable API
"jsonschema>=3.2.0,<5.0.0"       # JSON validation - keep bound (API changes)
"typing-extensions>=3.10.0"      # Type hints - backward compatible
```

### **Development Dependencies (`extras_require["dev"]`)**
For development, testing, and code quality:

```bash
pip install -e .[dev]
```

Includes:
- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting  
- **pytest-mock**: Mocking utilities
- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Type checking
- **isort**: Import sorting
- **pre-commit**: Git hooks

### **Documentation Dependencies (`extras_require["docs"]`)**
For building documentation:

```bash
pip install -e .[docs]
```

### **Performance Dependencies (`extras_require["performance"]`)**
For enhanced performance:

```bash
pip install -e .[performance]
```

### **Visualization Dependencies (`extras_require["visualization"]`)**
For advanced visualization:

```bash
pip install -e .[visualization]
```

---

## 🔧 **Installation Commands**

### **Basic Installation**
```bash
# Production installation
pip install .

# Development installation (recommended)
pip install -e .
```

### **With Optional Dependencies**
```bash
# Development setup
pip install -e .[dev]

# Full installation with all extras
pip install -e .[dev,docs,performance,visualization]

# Specific combinations
pip install -e .[dev,performance]
```

---

## 📋 **Version Constraint Strategy**

### **Constraint Strategy**
- **Core scientific libraries**: Only minimum versions (allow performance improvements)
- **Framework/API libraries**: Conservative bounds (prevent breaking changes)
- **Example**: `numpy>=1.20.0` vs `pgmpy>=0.1.19,<1.0.0`

### **Rationale**
1. **Minimum versions** ensure required features are available
2. **Scientific libraries** (NumPy, Pandas, SciPy) get frequent performance improvements
3. **Framework libraries** may have breaking API changes requiring bounds
4. **Balanced approach** maximizes performance while maintaining stability

### **Version Selection Criteria**
- **Minimum**: Oldest version that provides required functionality
- **Maximum**: Next major version to avoid breaking changes
- **Testing**: All constraints tested in CI/CD pipeline

---

## 🚫 **What We DON'T Use**

### **No requirements.txt**
- **Why**: Dual dependency sources create conflicts and maintenance issues
- **Instead**: All dependencies in `setup.py` for single source of truth

### **No Pipfile/poetry.lock**
- **Why**: Adds complexity for library packages
- **Instead**: Standard setuptools approach for maximum compatibility

### **No version pinning**
- **Why**: Libraries should specify ranges, not exact versions
- **Instead**: Compatible version ranges allowing flexibility

---

## 🔄 **Dependency Updates**

### **Regular Update Process**
1. **Review**: Check for new versions of dependencies
2. **Test**: Ensure compatibility with new versions
3. **Update**: Modify version constraints in `setup.py`
4. **Validate**: Run full test suite
5. **Document**: Update changelog with dependency changes

### **Security Updates**
- **Monitor**: Use tools like `safety` or `pip-audit`
- **Priority**: Security updates take precedence
- **Testing**: Immediate testing after security updates

### **Breaking Changes**
- **Major versions**: Review breaking changes before updating
- **Testing**: Comprehensive testing with new major versions
- **Documentation**: Update code if APIs change

---

## 🧪 **Testing Dependencies**

### **Compatibility Testing**
```bash
# Test with minimum versions
pip install numpy==1.20.0 pandas==1.3.0 scipy==1.7.0
python -m pytest

# Test with latest versions  
pip install --upgrade numpy pandas scipy
python -m pytest
```

### **Dependency Conflict Detection**
```bash
# Check for conflicts
pip check

# Detailed dependency tree
pip list --format=freeze
```

---

## 📊 **Dependency Monitoring**

### **Tools for Monitoring**
- **pip-audit**: Security vulnerability scanning
- **safety**: Security database checking
- **pip-outdated**: Check for outdated packages

### **Automated Checks**
```bash
# Security scan
pip-audit

# Outdated packages
pip list --outdated

# Dependency conflicts
pip check
```

---

## 🎯 **Best Practices**

### **✅ DO**
- Define all dependencies in `setup.py`
- Use version ranges, not exact pins
- Group dependencies logically in extras_require
- Test with both minimum and maximum supported versions
- Monitor for security updates regularly
- Document dependency changes in changelog

### **❌ DON'T**
- Create requirements.txt files
- Pin exact versions in library setup.py
- Use multiple dependency sources
- Ignore security updates
- Use overly broad version ranges
- Skip testing after dependency updates

---

## 🚀 **Production Deployment**

### **Installation in Production**
```bash
# Clean production installation
pip install bayesian-market-surveillance

# With performance optimizations
pip install bayesian-market-surveillance[performance]
```

### **Docker Deployment**
```dockerfile
# Use specific Python version
FROM python:3.11-slim

# Install package
RUN pip install bayesian-market-surveillance[performance]

# Run application
CMD ["python", "-m", "src.core.main"]
```

### **Environment Isolation**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install in isolated environment
pip install -e .[dev]
```

---

## 📋 **Summary**

**Single-Source Approach Benefits**:
- ✅ **No conflicts**: One source of truth for all dependencies
- ✅ **Easy maintenance**: Update versions in one place
- ✅ **Clear precedence**: No ambiguity about which versions to use
- ✅ **Professional standard**: Follows Python packaging best practices
- ✅ **CI/CD friendly**: Simple dependency resolution

**This approach ensures reliable, maintainable dependency management for enterprise-grade deployment.**