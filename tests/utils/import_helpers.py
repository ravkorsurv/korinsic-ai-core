"""
Import helpers for test modules.

This module provides proper import utilities to replace brittle sys.path manipulation
and improve test module portability and reliability.
"""

import os
import sys
from pathlib import Path
from typing import Optional


def setup_src_imports(src_relative_path: str = "../../src") -> Path:
    """
    Set up imports from the src directory in a more robust way.
    
    Args:
        src_relative_path: Relative path to src directory from calling file
        
    Returns:
        Path object pointing to the src directory
        
    Raises:
        ImportError: If src directory cannot be found
    """
    # Get the directory of the calling file
    caller_frame = sys._getframe(1)
    caller_file = caller_frame.f_globals.get('__file__')
    
    if caller_file is None:
        raise ImportError("Cannot determine caller file location")
    
    caller_dir = Path(caller_file).parent
    src_dir = (caller_dir / src_relative_path).resolve()
    
    if not src_dir.exists():
        raise ImportError(f"Source directory not found: {src_dir}")
    
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    
    return src_dir


def safe_import(module_name: str, package: Optional[str] = None):
    """
    Safely import a module with better error handling.
    
    Args:
        module_name: Name of the module to import
        package: Package context for relative imports
        
    Returns:
        The imported module
        
    Raises:
        ImportError: If module cannot be imported with helpful error message
    """
    try:
        if package:
            return __import__(module_name, fromlist=[package])
        else:
            return __import__(module_name)
    except ImportError as e:
        raise ImportError(
            f"Failed to import {module_name}: {e}\n"
            f"Ensure the module exists and dependencies are installed."
        ) from e


def get_project_root() -> Path:
    """
    Get the project root directory by looking for common markers.
    
    Returns:
        Path object pointing to the project root
        
    Raises:
        RuntimeError: If project root cannot be determined
    """
    current_dir = Path(__file__).parent
    
    # Look for common project root markers
    markers = ['.git', 'pyproject.toml', 'setup.py', 'requirements.txt', '.korbit-config.yaml']
    
    while current_dir != current_dir.parent:
        if any((current_dir / marker).exists() for marker in markers):
            return current_dir
        current_dir = current_dir.parent
    
    raise RuntimeError("Could not determine project root directory")


def setup_project_imports() -> Path:
    """
    Set up imports from project root in a robust way.
    
    Returns:
        Path object pointing to the project root
    """
    project_root = get_project_root()
    src_dir = project_root / "src"
    
    if src_dir.exists() and str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    
    return project_root