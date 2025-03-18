"""
Data collection module for the Business Lookup & Logistics Optimization Tool.
Implements the data collection pipeline for retrieving company information from various APIs.
"""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple

from src.api_clients import (
    LinkedInAPIClient, 
    YahooFinanceAPIClient, 
    ApolloAPIClient, 
    GoogleMapsAPIClient,
    VectorShiftAPIClient
)
from src.models import Company, Address, Industry, Executive, Contact, Financials, TaxIndicators, GeoLocation, LegalStructure
from src.config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataCollector:
    """Main data collection class that orchestrates data retrieval from multiple sources."""
    
    def __init__(self):
        """Initialize the data collector with API clients."""
        self.linkedin_client = LinkedInAPIClient()
        self.yahoo_finance_client = YahooFinanceAPIClient()
        self.apollo_client = ApolloAPIClient()
        # Note: Google Maps API key would need to be provided
        self.google_maps_client = None
        self.vectorshift_client = VectorShiftAPIClient()
        
    def collect_company_data(self, company_name: str, location: Optional[str] = None) -> Company:
        """
        Collect comprehensive company data from multiple sources.
        
        Args:
            company_name: Name of the company to search for
            location: Optional location to narrow down search
            
        Returns:
            Company object with collected data
        """
        logger.info(f"Collecting data for company: {company_name} in location: {location}")
        
        # Generate a unique ID for the company
        company_id = f"{company_name.lower().replace(' ', '-')}-{int(time.time())}"
        
        # Create a basic company object
        company = Company(
            id=company_id,
            name=company_name
        )
        
        # Collect data from LinkedIn
        linkedin_data = self._collect_from_linkedin(company_name)
        if linkedin_data:
            self._update_company_with_linkedin_data(company, linkedin_data)
        
        # Collect data from Yahoo Finance
        yahoo_data = self._collect_from_yahoo_finance(company_name)
        if yahoo_data:
            self._update_company_with_yahoo_data(company, yahoo_data)
        
        # Collect data from Apollo.io
        apollo_data = self._collect_from_apollo(company_name, location)
        if apollo_data:
            self._update_company_with_apollo_data(company, apollo_data)
        
        # Geocode the company address if available
        if company.address and self.google_maps_client:
            geocode_data = self._geocode_address(company.address)
            if geocode_data:
                company.location = geocode_data
        
        # Calculate tax saving potential
        company.tax_indicators.tax_saving_potential = company.calculate_tax_saving_potential()
        
        return company
    
    def find_similar_companies(self, company: Company, location: Optional[str] = None, limit: int = 10) -> List[Company]:
        """
        Find companies similar to the given company.
        
        Args:
            company: Reference company to find similar ones
            location: Optional location to narrow down search
            limit: Maximum number of similar companies to return
            
        Returns:
            List of similar Company objects
        """
        logger.info(f"Finding companies similar to: {company.name}")
        
        similar_companies = []
        
        # Use industry information to find similar companies
        if company.industry and company.industry.primary:
            # Search Apollo.io for companies in the same industry
            apollo_results = self._search_apollo_by_industry(
                company.industry.primary, 
                location or (company.address.city if company.address else None),
                limit
            )
            
            # Convert results to Company objects
            for result in apollo_results:
                similar_company = self._convert_apollo_result_to_company(result)
                if similar_company and similar_company.name != company.name:
                    similar_companies.append(similar_company)
        
        return similar_companies[:limit]
    
    def find_companies_by_industry(self, industry: str, location: Optional[str] = None, limit: int = 20) -> List[Company]:
        """
        Find companies in a specific industry.
        
        Args:
            industry: Industry to search for
            location: Optional location to narrow down search
            limit: Maximum number of companies to return
            
        Returns:
            List of Company objects in the specified industry
        """
        logger.info(f"Finding companies in industry: {industry} in location: {location}")
        
        # Search Apollo.io for companies in the specified industry
        apollo_results = self._search_apollo_by_industry(industry, location, limit)
        
        # Convert results to Company objects
        companies = []
        for result in apollo_results:
            company = self._convert_apollo_result_to_company(result)
            if company:
                companies.append(company)
        
        return companies[:limit]
    
    def _collect_from_linkedin(self, company_name: str) -> Dict[str, Any]:
        """Collect company data from LinkedIn."""
        try:
            logger.info(f"Collecting LinkedIn data for: {company_name}")
            result = self.linkedin_client.get_company_details(company_name)
            
            if "error" in result:
                logger.warning(f"LinkedIn API error: {result['error']}")
                return {}
                
            return result.get("data", {})
        except Exception as e:
            logger.error(f"Error collecting LinkedIn data: {e}")
            return {}
    
    def _collect_from_yahoo_finance(self, company_name: str) -> Dict[str, Any]:
        """Collect company data from Yahoo Finance."""
        try:
            logger.info(f"Collecting Yahoo Finance data for: {company_name}")
            # Note: This is a simplification. In reality, we would need to find the stock symbol first
            symbol = company_name.split()[0].upper()  # Just use the first word as a symbol for demonstration
            result = self.yahoo_finance_client.get_stock_profile(symbol)
            
            if "error" in result:
                logger.warning(f"Yahoo Finance API error: {result['error']}")
                return {}
                
            return result.get("quoteSummary", {}).get("result", [{}])[0].get("summaryProfile", {})
        except Exception as e:
            logger.error(f"Error collecting Yahoo Finance data: {e}")
            return {}
    
    def _collect_from_apollo(self, company_name: str, location: Optional[str] = None) -> Dict[str, Any]:
        """Collect company data from Apollo.io."""
        try:
            logger.info(f"Collecting Apollo.io data for: {company_name}")
            query = {
                "q_organization_name": company_name
            }
            
            if location:
                query["q_location"] = location
                
            result = self.apollo_client.search_organizations(query)
            
            if "error" in result:
                logger.warning(f"Apollo API error: {result['error']}")
                return {}
                
            # Get the first organization from results
            organizations = result.get("organizations", [])
            if not organizations:
                return {}
                
            return organizations[0]
        except Exception as e:
            logger.error(f"Error collecting Apollo data: {e}")
            return {}
    
    def _geocode_address(self, address: Address) -> Optional[GeoLocation]:
        """Geocode an address to get latitude and longitude."""
        if not self.google_maps_client:
            return None
            
        try:
            address_str = f"{address.street}, {address.city}, {address.state} {address.zip}"
            result = self.google_maps_client.geocode(address_str)
            
            if "error" in result:
                logger.warning(f"Google Maps API error: {result['error']}")
                return None
                
            results = result.get("results", [])
            if not results:
                return None
                
            location = results[0].get("geometry", {}).get("location", {})
            lat = location.get("lat")
            lng = location.get("lng")
            
            if lat and lng:
                return GeoLocation(
                    latitude=lat,
                    longitude=lng,
                    region=self._determine_region(address.city, address.state)
                )
                
            return None
        except Exception as e:
            logger.error(f"Error geocoding address: {e}")
            return None
    
    def _determine_region(self, city: str, state: str) -> str:
        """Determine the region based on city and state."""
        # Check if city is in any of the scheduled regions
        schedule = Config.get_location_schedule()
        
        for day, regions in schedule.items():
            if isinstance(regions, list):
                for region in regions:
                    if city in region or region in city:
                        return day
        
        # Default to the closest region based on state
        if state == "WI":
            return "Monday"  # Default Wisconsin to Monday
        
        return "Wednesday"  # Default to middle of the week
    
    def _update_company_with_linkedin_data(self, company: Company, data: Dict[str, Any]) -> None:
        """Update company object with LinkedIn data."""
        if not data:
            return
            
        company.description = data.get("description", company.description)
        company.website = data.get("website", company.website)
        
        # Update industry information
        if "industries" in data and data["industries"]:
            primary_industry = data["industries"][0]
            company.industry = Industry(
                primary=primary_industry,
                subcategories=data.get("industries", [])[1:] if len(data.get("industries", [])) > 1 else []
            )
        
        # Update employee count
        if "staffCount" in data:
            if not company.financials:
                company.financials = Financials()
            company.financials.employee_count = data.get("staffCount")
        
        # Update address if available
        if "locations" in data and data["locations"]:
            location = data["locations"][0]
            if "line1" in location and "city" in location and "state" in location and "postalCode" in location:
                company.address = Address(
                    street=location.get("line1", ""),
                    city=location.get("city", ""),
                    state=location.get("state", ""),
                    zip=location.get("postalCode", "")
                )
    
    def _update_company_with_yahoo_data(self, company: Company, data: Dict[str, Any]) -> None:
        """Update company object with Yahoo Finance data."""
        if not data:
            return
            
        company.description = data.get("longBusinessSummary", company.description)
        company.website = data.get("website", company.website)
        
        # Update industry information
        if "industry" in data:
            if not company.industry:
                company.industry = Industry(primary=data.get("industry", ""))
            else:
                company.industry.primary = data.get("industry", company.industry.primary)
                
            company.industry.naics_code = data.get("industryKey")
            company.industry.sic_code = data.get("sectorKey")
        
        # Update employee count
        if "fullTimeEmployees" in data:
            if not company.financials:
                company.financials = Financials()
            company.financials.employee_count = data.get("fullTimeEmployees")
        
        # Update address if available
        if all(key in data for key in ["address1", "city", "state", "zip"]):
            company.address = Address(
                street=data.get("address1", ""),
                city=data.get("city", ""),
                state=data.get("state", ""),
                zip=data.get("zip", "")
            )
        
        # Update executives if available
        if "companyOfficers" in data and data["companyOfficers"]:
            for officer in data["companyOfficers"]:
                executive = Executive(
                    name=officer.get("name", ""),
                    role=officer.get("title", ""),
                    contact=Contact()
                )
                company.executives.append(executive)
    
    def _update_company_with_apollo_data(self, company: Company, data: Dict[str, Any]) -> None:
        """Update company object with Apollo.io data."""
        if not data:
            return
            
        company.description = data.get("description", company.description)
        company.website = data.get("website", company.website)
        
        # Update industry information
        if "industry" in data:
            if not company.industry:
                company.industry = Industry(primary=data.get("industry", ""))
            else:
                company.industry.primary = data.get("industry", company.industry.primary)
        
        # Update employee count and estimated revenue
        if "estimated_num_employees" in data:
            if not company.financials:
                company.financials = Financials()
            company.financials.employee_count = data.get("estimated_num_employees")
        
        if "estimated_annual_revenue" in data:
            if not company.financials:
                company.financials = Financials()
            company.financials.estimated_revenue = data.get("estimated_annual_revenue")
        
        # Update address if available
        if "street_address" in data and "city" in data and "state" in data and "postal_code" in data:
            company.address = Address(
                street=data.get("street_address", ""),
                city=data.get("city", ""),
                state=data.get("state", ""),
                zip=data.get("postal_code", "")
            )
        
        # Update legal structure if available
        if "organization_type" in data:
            org_type = data.get("organization_type", "").upper()
            if "LLC" in org_type:
                company.legal_structure = LegalStructure.LLC
            elif "CORP" in org_type and "S" in org_type:
                company.legal_structure = LegalStructure.S_CORP
            elif "CORP" in org_type and "C" in org_type:
                company.legal_structure = LegalStructure.C_CORP
            elif "FAMILY" in org_type or "FAMILY" in data.get("description", "").upper():
                company.legal_structure = LegalStructure.FAMILY_OWNED
            elif "PARTNERSHIP" in org_type:
                company.legal_structure = LegalStructure.PARTNERSHIP
            elif "PROPRIETOR" in org_type:
                company.legal_structure = LegalStructure.SOLE_PROPRIETORSHIP
            else:
                company.legal_structure = LegalStructure.OTHER
        
        # Update executives if available
        if "contacts" in data and data["contacts"]:
            for contact in data["contacts"]:
                if contact.get("is_decision_maker", False):
                    executive = Executive(
                        name=f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip(),
                        role=contact.get("title", ""),
                        contact=Contact(
                            phone=contact.get("phone_number"),
                            email=contact.get("email"),
                            linkedin_url=contact.get("linkedin_url")
                        )
                    )
                    company.executives.append(executive)
    
    def _search_apollo_by_industry(self, industry: str, location: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search Apollo.io for companies in a specific industry."""
        try:
            query = {
                "q_industry_text": industry,
                "page": 1,
                "per_page": limit
            }
            
            if location:
                query["q_location"] = location
                
            # Add filters for employee count and revenue
            query["num_employees"] = [f"gte:{Config.MIN_EMPLOYEE_COUNT}"]
            
            result = self.apollo_client.search_organizations(query)
            
            if "error" in result:
                logger.warning(f"Apollo API error: {result['error']}")
                return []
                
            return result.get("organizations", [])
        except Exception as e:
            logger.error(f"Error searching Apollo by industry: {e}")
            return []
    
    def _convert_apollo_result_to_company(self, data: Dict[str, Any]) -> Optional[Company]:
        """Convert Apollo.io result to a Company object."""
        if not data or "name" not in data:
            return None
            
        company_id = f"{data['name'].lower().replace(' ', '-')}-{int(time.time())}"
        
        company = Company(
            id=company_id,
            name=data["name"]
        )
        
        # Update with Apollo data
        self._update_company_with_apollo_data(company, data)
        
        return company
