#!/usr/bin/env python3
"""
Setup configuration for Bayesian Market Surveillance System

This setup.py file establishes the project as a proper Python package with
single-source dependency management, eliminating the need for runtime sys.path 
modifications and avoiding dependency conflicts from multiple sources.

Key Features:
- Single-source dependency management (no requirements.txt conflicts)
- Proper version constraints with compatibility ranges
- Optional dependency groups for different use cases
- Professional package structure with entry points

Usage:
    # Development installation with dev dependencies
    pip install -e .[dev]
    
    # Production installation
    pip install .
    
    # With performance optimizations  
    pip install .[performance]
    
    # Run tests with proper package resolution
    python -m pytest tests/
    
    # Run validation scripts
    python -m validate_korbit_fixes
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    """Read README file for long description."""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Bayesian Market Surveillance System with Fan-In Intermediate Node Integration"

# All dependencies are defined directly in setup.py for clear precedence
# No external requirements.txt file to avoid conflicts and maintenance issues

setup(
    name="bayesian-market-surveillance",
    version="1.0.0",
    description="Bayesian Network-based Market Surveillance System with Fan-In Optimization",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Market Surveillance Team",
    author_email="surveillance@company.com",
    url="https://github.com/company/bayesian-market-surveillance",
    
    # Package configuration
    packages=find_packages(where="."),
    package_dir={"": "."},
    python_requires=">=3.8",
    
    # Dependencies - all defined here for clear precedence and conflict avoidance
    install_requires=[
        # Core scientific computing stack
        "numpy>=1.20.0,<2.0.0",
        "pandas>=1.3.0,<3.0.0",
        "scipy>=1.7.0,<2.0.0",
        
        # Bayesian Networks and graph operations
        "pgmpy>=0.1.19,<1.0.0",  # Bayesian Network library
        "networkx>=2.6,<4.0.0",  # Graph operations
        
        # Visualization and plotting
        "matplotlib>=3.3.0,<4.0.0",  # Plotting
        "seaborn>=0.11.0,<1.0.0",  # Statistical plotting
        
        # Machine learning and utilities
        "scikit-learn>=1.0.0,<2.0.0",  # Machine learning utilities
        "joblib>=1.0.0,<2.0.0",  # Parallel processing
        
        # Progress and configuration
        "tqdm>=4.60.0,<5.0.0",  # Progress bars
        "pyyaml>=5.4.0,<7.0.0",  # Configuration files
        "jsonschema>=3.2.0,<5.0.0",  # JSON validation
        
        # Type hints and compatibility
        "typing-extensions>=3.10.0,<5.0.0",  # Type hints
    ],
    
    # Optional dependencies with version constraints
    extras_require={
        "dev": [
            "pytest>=6.0.0,<8.0.0",
            "pytest-cov>=2.12.0,<5.0.0",
            "pytest-mock>=3.6.0,<4.0.0",
            "black>=21.0.0,<24.0.0",
            "flake8>=3.9.0,<7.0.0",
            "mypy>=0.910,<2.0.0",
            "isort>=5.9.0,<6.0.0",
            "pre-commit>=2.15.0,<4.0.0",
        ],
        "docs": [
            "sphinx>=4.0.0,<8.0.0",
            "sphinx-rtd-theme>=0.5.0,<3.0.0",
            "sphinx-autodoc-typehints>=1.12.0,<2.0.0",
        ],
        "performance": [
            "numba>=0.54.0,<1.0.0",
            "cython>=0.29.0,<4.0.0",
        ],
        "visualization": [
            "plotly>=5.0.0,<6.0.0",
            "dash>=2.0.0,<3.0.0",
            "graphviz>=0.17.0,<1.0.0",
        ]
    },
    
    # Entry points for command-line tools
    entry_points={
        "console_scripts": [
            "validate-korbit-fixes=validate_korbit_fixes:main",
            "run-surveillance=src.core.main:main",
            "bayesian-inference=src.core.bayesian_engine:main",
        ],
    },
    
    # Package data
    package_data={
        "src": [
            "config/*.yaml",
            "config/*.json",
            "data/templates/*.json",
            "models/bayesian/*/config/*.yaml",
        ],
    },
    
    # Include additional files
    include_package_data=True,
    
    # Metadata
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    
    keywords="bayesian networks, market surveillance, financial regulation, machine learning, fraud detection",
    
    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/company/bayesian-market-surveillance/issues",
        "Source": "https://github.com/company/bayesian-market-surveillance",
        "Documentation": "https://bayesian-market-surveillance.readthedocs.io/",
    },
    
    # Zip safety
    zip_safe=False,
)