#!/usr/bin/env python3
"""
Kor.ai Surveillance Platform Server Runner

Simple script to start the surveillance platform server
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app import app
from src.utils.logger import setup_logger
from src.utils.config import Config

def main():
    """Main entry point for the server"""
    
    # Setup configuration and logging
    config = Config()
    logger = setup_logger()
    
    # Log startup information
    logger.info("=" * 60)
    logger.info("Starting Kor.ai Surveillance Platform")
    logger.info("=" * 60)
    logger.info(f"Environment: {config.get('environment')}")
    logger.info(f"Debug Mode: {config.get('debug')}")
    logger.info(f"Host: {config.get('host')}")
    logger.info(f"Port: {config.get('port')}")
    
    # Add Flask CORS support
    try:
        from flask_cors import CORS
        CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"])
    except ImportError:
        logger.warning("Flask-CORS not installed, CORS support disabled")
    
    # Start the server
    try:
        app.run(
            host=config.get('host'),
            port=config.get('port'),
            debug=config.get('debug'),
            threaded=True
        )
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()