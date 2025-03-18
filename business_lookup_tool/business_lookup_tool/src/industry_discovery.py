"""
Industry-specific discovery module for the Business Lookup & Logistics Optimization Tool.
Implements features for targeting specific industries like construction, manufacturing, and trucking.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple, Set

from src.models import Company, Industry, SearchCriteria
from src.data_normalizer import normalize_industry, is_owner_operated, is_in_growth_mode
from src.business_matcher import BusinessMatcher
from src.similarity_scorer import SimilarityScorer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IndustryDiscovery:
    """Class for industry-specific company discovery."""
    
    def __init__(self):
        """Initialize the industry discovery module."""
        self.business_matcher = BusinessMatcher()
        self.similarity_scorer = SimilarityScorer()
        self.industry_keywords = self._initialize_industry_keywords()
        self.industry_naics_codes = self._initialize_industry_naics_codes()
    
    def _initialize_industry_keywords(self) -> Dict[str, List[str]]:
        """Initialize industry-specific keywords for targeting."""
        keywords = {
            "construction": [
                "contractor", "builder", "construction", "engineering", "architect",
                "hvac", "electrical", "plumbing", "concrete", "framing", "insulation",
                "excavation", "site prep", "modular", "prefab", "building materials",
                "steel", "lumber", "glass", "precast", "fasteners", "coatings"
            ],
            "manufacturing": [
                "manufacturer", "manufacturing", "industrial", "machinery", "automation",
                "oem", "supplier", "component", "fabricator", "fabrication", "steel",
                "plastic", "composite", "metal", "stamping", "machining", "aerospace",
                "automotive", "equipment", "robotics", "cnc", "injection molding",
                "food processing", "packaging"
            ],
            "trucking": [
                "trucking", "logistics", "freight", "carrier", "ltl", "ftl", "last-mile",
                "delivery", "refrigerated", "transport", "tanker", "fleet", "heavy equipment",
                "warehousing", "distribution", "supply chain", "fleet maintenance",
                "intermodal", "hazardous material"
            ]
        }
        return keywords
    
    def _initialize_industry_naics_codes(self) -> Dict[str, List[str]]:
        """Initialize industry-specific NAICS codes for targeting."""
        naics_codes = {
            "construction": [
                "23", "236", "237", "238",  # Construction
                "2361", "2362",  # Construction of Buildings
                "2371", "2372", "2373", "2379",  # Heavy and Civil Engineering Construction
                "2381", "2382", "2383", "2389"  # Specialty Trade Contractors
            ],
            "manufacturing": [
                "31", "32", "33",  # Manufacturing
                "331", "332", "333", "334", "335", "336", "337", "339",  # Specific Manufacturing Sectors
                "3311", "3312", "3313", "3314", "3315",  # Primary Metal Manufacturing
                "3321", "3322", "3323", "3324", "3325", "3326", "3327", "3328", "3329"  # Fabricated Metal Product Manufacturing
            ],
            "trucking": [
                "48", "484", "4841", "4842",  # Truck Transportation
                "493", "4931",  # Warehousing and Storage
                "49311", "49312", "49313", "49319"  # Specific Warehousing and Storage
            ]
        }
        return naics_codes
    
    def discover_construction_companies(self, location: Optional[str] = None, min_employees: int = 10, 
                                        owner_operated: bool = True, growth_mode: bool = True, 
                                        limit: int = 20) -> List[Company]:
        """
        Discover companies in the construction industry.
        
        Args:
            location: Optional location to narrow down search
            min_employees: Minimum number of employees
            owner_operated: Whether to target owner-operated businesses
            growth_mode: Whether to target businesses in growth mode
            limit: Maximum number of companies to return
            
        Returns:
            List of construction companies matching criteria
        """
        logger.info(f"Discovering construction companies in location: {location}")
        
        criteria = SearchCriteria(
            industry="construction",
            location=location,
            min_employees=min_employees,
            owner_operated=owner_operated,
            growth_mode=growth_mode
        )
        
        return self._discover_companies_by_industry("construction", criteria, limit)
    
    def discover_manufacturing_companies(self, location: Optional[str] = None, min_employees: int = 10, 
                                         owner_operated: bool = True, growth_mode: bool = True, 
                                         limit: int = 20) -> List[Company]:
        """
        Discover companies in the manufacturing industry.
        
        Args:
            location: Optional location to narrow down search
            min_employees: Minimum number of employees
            owner_operated: Whether to target owner-operated businesses
            growth_mode: Whether to target businesses in growth mode
            limit: Maximum number of companies to return
            
        Returns:
            List of manufacturing companies matching criteria
        """
        logger.info(f"Discovering manufacturing companies in location: {location}")
        
        criteria = SearchCriteria(
            industry="manufacturing",
            location=location,
            min_employees=min_employees,
            owner_operated=owner_operated,
            growth_mode=growth_mode
        )
        
        return self._discover_companies_by_industry("manufacturing", criteria, limit)
    
    def discover_trucking_companies(self, location: Optional[str] = None, min_employees: int = 10, 
                                    owner_operated: bool = True, growth_mode: bool = True, 
                                    limit: int = 20) -> List[Company]:
        """
        Discover companies in the trucking and logistics industry.
        
        Args:
            location: Optional location to narrow down search
            min_employees: Minimum number of employees
            owner_operated: Whether to target owner-operated businesses
            growth_mode: Whether to target businesses in growth mode
            limit: Maximum number of companies to return
            
        Returns:
            List of trucking companies matching criteria
        """
        logger.info(f"Discovering trucking companies in location: {location}")
        
        criteria = SearchCriteria(
            industry="trucking",
            location=location,
            min_employees=min_employees,
            owner_operated=owner_operated,
            growth_mode=growth_mode
        )
        
        return self._discover_companies_by_industry("trucking", criteria, limit)
    
    def _discover_companies_by_industry(self, industry_type: str, criteria: SearchCriteria, limit: int) -> List[Company]:
        """
        Generic method to discover companies by industry type.
        
        Args:
            industry_type: Type of industry to target
            criteria: Search criteria
            limit: Maximum number of companies to return
            
        Returns:
            List of companies matching criteria
        """
        # This would typically query the database or API
        # For now, we'll return a placeholder implementation
        
        # In a real implementation, this would:
        # 1. Query the database or API for companies matching the industry
        # 2. Filter by location if provided
        # 3. Filter by minimum employee count
        # 4. Filter for owner-operated businesses if requested
        # 5. Filter for businesses in growth mode if requested
        # 6. Sort by relevance or tax-saving potential
        # 7. Return the top N results
        
        # Placeholder for demonstration
        return []
    
    def filter_companies_by_industry(self, companies: List[Company], industry_type: str) -> List[Company]:
        """
        Filter a list of companies to include only those in a specific industry.
        
        Args:
            companies: List of companies to filter
            industry_type: Type of industry to filter for
            
        Returns:
            Filtered list of companies
        """
        filtered_companies = []
        
        for company in companies:
            if self._is_in_industry(company, industry_type):
                filtered_companies.append(company)
        
        return filtered_companies
    
    def _is_in_industry(self, company: Company, industry_type: str) -> bool:
        """
        Determine if a company is in a specific industry.
        
        Args:
            company: Company to check
            industry_type: Type of industry to check for
            
        Returns:
            Boolean indicating if company is in the industry
        """
        if not company.industry:
            return False
        
        # Check primary industry
        if company.industry.primary:
            normalized = normalize_industry(company.industry.primary)
            if normalized["category"].lower() == industry_type.lower():
                return True
        
        # Check NAICS code if available
        if company.industry.naics_code and industry_type in self.industry_naics_codes:
            for code_prefix in self.industry_naics_codes[industry_type]:
                if company.industry.naics_code.startswith(code_prefix):
                    return True
        
        # Check description for industry keywords
        if company.description and industry_type in self.industry_keywords:
            description_lower = company.description.lower()
            for keyword in self.industry_keywords[industry_type]:
                if keyword in description_lower:
                    return True
        
        return False
    
    def get_industry_segments(self, industry_type: str) -> List[str]:
        """
        Get segments within a specific industry.
        
        Args:
            industry_type: Type of industry
            
        Returns:
            List of industry segments
        """
        segments = {
            "construction": [
                "General Contractors",
                "Engineering Firms",
                "Specialty Trade Contractors",
                "Excavation & Site Prep",
                "Modular & Prefab Construction",
                "Building Materials Suppliers"
            ],
            "manufacturing": [
                "Industrial Machinery & Automation",
                "OEM Suppliers & Component Manufacturers",
                "Fabricators",
                "Aerospace, Automotive & Heavy Equipment",
                "Robotics & Automation",
                "Injection Molding & Composite Materials",
                "Food Processing & Packaging"
            ],
            "trucking": [
                "Freight Carriers",
                "Refrigerated Transport & Tanker Fleets",
                "Heavy Equipment Transporters",
                "Warehousing & Distribution",
                "Logistics Technology & Supply Chain",
                "Fleet Maintenance & Repair",
                "Intermodal & Hazardous Material Haulers"
            ]
        }
        
        return segments.get(industry_type, [])
    
    def filter_companies_by_segment(self, companies: List[Company], industry_type: str, segment: str) -> List[Company]:
        """
        Filter companies by industry segment.
        
        Args:
            companies: List of companies to filter
            industry_type: Type of industry
            segment: Specific segment within the industry
            
        Returns:
            Filtered list of companies
        """
        filtered_companies = []
        
        for company in companies:
            if self._is_in_industry(company, industry_type) and self._is_in_segment(company, segment):
                filtered_companies.append(company)
        
        return filtered_companies
    
    def _is_in_segment(self, company: Company, segment: str) -> bool:
        """
        Determine if a company is in a specific industry segment.
        
        Args:
            company: Company to check
            segment: Segment to check for
            
        Returns:
            Boolean indicating if company is in the segment
        """
        if not company.industry or not company.description:
            return False
        
        # Check if normalized industry subcategory matches segment
        if company.industry.primary:
            normalized = normalize_industry(company.industry.primary)
            if normalized["subcategory"] == segment:
                return True
        
        # Check description for segment keywords
        description_lower = company.description.lower()
        segment_lower = segment.lower()
        
        # Create segment-specific keywords
        segment_keywords = []
        
        # General Contractors
        if segment_lower == "general contractors":
            segment_keywords = ["general contractor", "builder", "construction company"]
        
        # Engineering Firms
        elif segment_lower == "engineering firms":
            segment_keywords = ["engineering firm", "engineer", "architectural", "design firm"]
        
        # Specialty Trade Contractors
        elif segment_lower == "specialty trade contractors":
            segment_keywords = ["specialty", "trade", "hvac", "electrical", "plumbing", "concrete", "framing", "insulation"]
        
        # And so on for other segments...
        
        for keyword in segment_keywords:
            if keyword in description_lower:
                return True
        
        return False
    
    def filter_owner_operated_companies(self, companies: List[Company]) -> List[Company]:
        """
        Filter for owner-operated companies.
        
        Args:
            companies: List of companies to filter
            
        Returns:
            Filtered list of owner-operated companies
        """
        return [company for company in companies if is_owner_operated({
            "employee_count": company.financials.employee_count if company.financials else None,
            "executives": [{"role": exec.role} for exec in company.executives] if company.executives else [],
            "legal_structure": company.legal_structure.value if company.legal_structure else "",
            "name": company.name
        })]
    
    def filter_growth_mode_companies(self, companies: List[Company]) -> List[Company]:
        """
        Filter for companies in growth mode.
        
        Args:
            companies: List of companies to filter
            
        Returns:
            Filtered list of companies in growth mode
        """
        return [company for company in companies if is_in_growth_mode({
            "growth_rate": company.financials.growth_rate if company.financials else None,
            "description": company.description or "",
            "recent_developments": company.tax_indicators.recent_developments if company.tax_indicators else "",
            "financing_activity": company.tax_indicators.financing_activity if company.tax_indicators else ""
        })]
