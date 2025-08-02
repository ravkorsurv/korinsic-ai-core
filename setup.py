#!/usr/bin/env python3
"""
Setup configuration for Bayesian Market Surveillance System

This setup.py file establishes the project as a proper Python package,
eliminating the need for runtime sys.path modifications and providing
proper import resolution.

Usage:
    # Development installation
    pip install -e .
    
    # Production installation
    pip install .
    
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

# Read requirements
def read_requirements():
    """Read requirements from requirements.txt if it exists."""
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

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
    
    # Dependencies
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
        "pgmpy>=0.1.19",  # Bayesian Network library
        "networkx>=2.6",  # Graph operations
        "matplotlib>=3.3.0",  # Plotting
        "seaborn>=0.11.0",  # Statistical plotting
        "scikit-learn>=1.0.0",  # Machine learning utilities
        "joblib>=1.0.0",  # Parallel processing
        "tqdm>=4.60.0",  # Progress bars
        "pyyaml>=5.4.0",  # Configuration files
        "jsonschema>=3.2.0",  # JSON validation
        "typing-extensions>=3.10.0",  # Type hints
    ] + read_requirements(),
    
    # Optional dependencies
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "pytest-mock>=3.6.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
            "isort>=5.9.0",
            "pre-commit>=2.15.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=0.5.0",
            "sphinx-autodoc-typehints>=1.12.0",
        ],
        "performance": [
            "numba>=0.54.0",
            "cython>=0.29.0",
        ],
        "visualization": [
            "plotly>=5.0.0",
            "dash>=2.0.0",
            "graphviz>=0.17.0",
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