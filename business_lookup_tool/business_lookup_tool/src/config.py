"""
Configuration module for the Business Lookup & Logistics Optimization Tool.
Loads environment variables from .env file and provides access to configuration settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the application."""
    
    # API Keys
    APOLLO_API_KEY = os.getenv('APOLLO_API_KEY')
    VECTORSHIFT_API_KEY = os.getenv('VECTORSHIFT_API_KEY')
    
    # API Endpoints
    LINKEDIN_API_BASE_URL = os.getenv('LINKEDIN_API_BASE_URL', 'https://api.linkedin.com/v2')
    YAHOO_FINANCE_API_BASE_URL = os.getenv('YAHOO_FINANCE_API_BASE_URL', 'https://query1.finance.yahoo.com/v10/finance')
    
    # Application Settings
    DEFAULT_LOCATION = os.getenv('DEFAULT_LOCATION', 'Milwaukee')
    DEFAULT_INDUSTRY = os.getenv('DEFAULT_INDUSTRY', 'manufacturing')
    MIN_EMPLOYEE_COUNT = int(os.getenv('MIN_EMPLOYEE_COUNT', 10))
    MIN_REVENUE = int(os.getenv('MIN_REVENUE', 2000000))
    DAILY_COMPANY_TARGET = int(os.getenv('DAILY_COMPANY_TARGET', 20))
    
    # Location Schedule
    MONDAY_LOCATIONS = os.getenv('MONDAY_LOCATIONS', 'Waukesha,West Milwaukee,Jackson,West Bend').split(',')
    TUESDAY_LOCATIONS = os.getenv('TUESDAY_LOCATIONS', 'Kenosha,Racine').split(',')
    WEDNESDAY_LOCATIONS = os.getenv('WEDNESDAY_LOCATIONS', 'West Waukesha,Madison').split(',')
    THURSDAY_FRIDAY = os.getenv('THURSDAY_FRIDAY', 'Follow-up')
    
    # Output Settings
    OUTPUT_FORMAT = os.getenv('OUTPUT_FORMAT', 'csv,dashboard').split(',')
    OUTPUT_DELIVERY_TIME = os.getenv('OUTPUT_DELIVERY_TIME', '08:30')
    
    @classmethod
    def get_location_schedule(cls):
        """Return the weekly location schedule as a dictionary."""
        return {
            'Monday': cls.MONDAY_LOCATIONS,
            'Tuesday': cls.TUESDAY_LOCATIONS,
            'Wednesday': cls.WEDNESDAY_LOCATIONS,
            'Thursday': cls.THURSDAY_FRIDAY,
            'Friday': cls.THURSDAY_FRIDAY
        }
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration values are present."""
        required_keys = ['APOLLO_API_KEY', 'VECTORSHIFT_API_KEY']
        missing_keys = [key for key in required_keys if not getattr(cls, key)]
        
        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {', '.join(missing_keys)}")
        
        return True

# Validate configuration on module import
Config.validate_config()
