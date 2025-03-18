"""
API client interfaces for the Business Lookup & Logistics Optimization Tool.
Defines the interfaces for interacting with external APIs.
"""

import requests
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from src.config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIClient(ABC):
    """Abstract base class for API clients."""
    
    @abstractmethod
    def make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to the API endpoint."""
        pass


class LinkedInAPIClient(APIClient):
    """Client for interacting with LinkedIn API."""
    
    def __init__(self):
        """Initialize the LinkedIn API client."""
        self.base_url = Config.LINKEDIN_API_BASE_URL
        
    def make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to the LinkedIn API."""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"LinkedIn API request failed: {e}")
            return {"error": str(e)}
    
    def get_company_details(self, company_name: str) -> Dict[str, Any]:
        """Get company details from LinkedIn."""
        return self.make_request("get_company_details", {"username": company_name})
    
    def get_user_profile(self, username: str) -> Dict[str, Any]:
        """Get user profile from LinkedIn."""
        return self.make_request("get_user_profile_by_username", {"username": username})
    
    def search_people(self, keywords: str, company: Optional[str] = None, title: Optional[str] = None) -> Dict[str, Any]:
        """Search for people on LinkedIn."""
        params = {"keywords": keywords}
        if company:
            params["company"] = company
        if title:
            params["keywordTitle"] = title
        return self.make_request("search_people", params)


class YahooFinanceAPIClient(APIClient):
    """Client for interacting with Yahoo Finance API."""
    
    def __init__(self):
        """Initialize the Yahoo Finance API client."""
        self.base_url = Config.YAHOO_FINANCE_API_BASE_URL
        
    def make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to the Yahoo Finance API."""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Yahoo Finance API request failed: {e}")
            return {"error": str(e)}
    
    def get_stock_profile(self, symbol: str, region: str = "US") -> Dict[str, Any]:
        """Get stock profile from Yahoo Finance."""
        return self.make_request("get_stock_profile", {"symbol": symbol, "region": region})


class ApolloAPIClient(APIClient):
    """Client for interacting with Apollo.io API."""
    
    def __init__(self):
        """Initialize the Apollo API client."""
        self.api_key = Config.APOLLO_API_KEY
        self.base_url = "https://api.apollo.io/v1"
        
    def make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to the Apollo API."""
        url = f"{self.base_url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Apollo API request failed: {e}")
            return {"error": str(e)}
    
    def search_organizations(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Search for organizations in Apollo."""
        return self.make_request("organizations/search", query)
    
    def get_organization(self, organization_id: str) -> Dict[str, Any]:
        """Get organization details from Apollo."""
        return self.make_request(f"organizations/{organization_id}")
    
    def search_people(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Search for people in Apollo."""
        return self.make_request("people/search", query)


class GoogleMapsAPIClient(APIClient):
    """Client for interacting with Google Maps API."""
    
    def __init__(self, api_key: str):
        """Initialize the Google Maps API client."""
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api"
        
    def make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to the Google Maps API."""
        url = f"{self.base_url}/{endpoint}"
        if params is None:
            params = {}
        params["key"] = self.api_key
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Google Maps API request failed: {e}")
            return {"error": str(e)}
    
    def geocode(self, address: str) -> Dict[str, Any]:
        """Geocode an address to get coordinates."""
        return self.make_request("geocode/json", {"address": address})
    
    def distance_matrix(self, origins: List[str], destinations: List[str]) -> Dict[str, Any]:
        """Get distance matrix between origins and destinations."""
        return self.make_request("distancematrix/json", {
            "origins": "|".join(origins),
            "destinations": "|".join(destinations)
        })
    
    def directions(self, origin: str, destination: str, waypoints: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get directions from origin to destination with optional waypoints."""
        params = {
            "origin": origin,
            "destination": destination
        }
        if waypoints:
            params["waypoints"] = "optimize:true|" + "|".join(waypoints)
        
        return self.make_request("directions/json", params)


class VectorShiftAPIClient(APIClient):
    """Client for interacting with VectorShift API."""
    
    def __init__(self):
        """Initialize the VectorShift API client."""
        self.api_key = Config.VECTORSHIFT_API_KEY
        self.base_url = "https://api.vectorshift.ai/v1"
        
    def make_request(self, endpoint: str, params: Dict[str, Any] = None, method: str = "GET", data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to the VectorShift API."""
        url = f"{self.base_url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                headers["Content-Type"] = "application/json"
                response = requests.post(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"VectorShift API request failed: {e}")
            return {"error": str(e)}
    
    def analyze_company(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze company data using VectorShift AI."""
        return self.make_request("analyze", method="POST", data=company_data)
