"""
Main script to run the Business Lookup & Logistics Optimization Tool.
"""

import os
import sys
import logging
from src.web_interface import app, run_app

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('business_lookup_tool.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("Starting Business Lookup & Logistics Optimization Tool")
    
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run the Flask application
    run_app(host='0.0.0.0', port=port, debug=False)
