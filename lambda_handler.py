"""
AWS Lambda handler for KOR.AI Surveillance Platform
Adapts Flask application to run on AWS Lambda with API Gateway
"""

import os
import sys
from mangum import Mangum

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import Flask app
from src.app import app

# Configure for Lambda environment
app.config['LAMBDA_ENVIRONMENT'] = True

# Create Lambda handler
handler = Mangum(app, lifespan="off")

def lambda_handler(event, context):
    """
    AWS Lambda entry point
    """
    return handler(event, context)