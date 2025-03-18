"""
Production configuration for the Business Lookup & Logistics Optimization Tool.
Contains settings optimized for production deployment.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Production configuration
DEBUG = False
SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key-change-in-production')

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///business_lookup.db')

# API keys
APOLLO_API_KEY = os.getenv('APOLLO_API_KEY')
VECTORSHIFT_API_KEY = os.getenv('VECTORSHIFT_API_KEY')
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
LINKEDIN_API_KEY = os.getenv('LINKEDIN_API_KEY')

# CORS settings
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

# Rate limiting
RATE_LIMIT = os.getenv('RATE_LIMIT', '100 per hour')

# Cache settings
CACHE_TYPE = os.getenv('CACHE_TYPE', 'SimpleCache')
CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'business_lookup_production.log')

# Location schedule
LOCATION_SCHEDULE = {
    "Monday": ["Waukesha", "West Milwaukee", "Jackson", "West Bend"],
    "Tuesday": ["Kenosha", "Racine"],
    "Wednesday": ["Madison"],
    "Thursday": [],  # Follow-up day
    "Friday": []     # Follow-up day
}

# Get location schedule
def get_location_schedule():
    """Get the location schedule."""
    return LOCATION_SCHEDULE
