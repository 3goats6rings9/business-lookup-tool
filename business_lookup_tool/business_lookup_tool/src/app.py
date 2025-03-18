"""
Main application module for the Business Lookup & Logistics Optimization Tool.
Integrates all components and provides the core application functionality.
"""

import logging
import os
from typing import Dict, Any, List, Optional, Tuple

from src.config import Config
from src.data_collector import DataCollector
from src.business_matcher import BusinessMatcher
from src.similarity_scorer import SimilarityScorer
from src.industry_discovery import IndustryDiscovery
from src.logistics_optimizer import LogisticsOptimizer
from src.database import DatabaseManager
from src.models import Company, SearchCriteria, TaxSavingPotential

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BusinessLookupApp:
    """Main application class that integrates all components."""
    
    def __init__(self):
        """Initialize the application with all components."""
        self.data_collector = DataCollector()
        self.business_matcher = BusinessMatcher()
        self.similarity_scorer = SimilarityScorer()
        self.industry_discovery = IndustryDiscovery()
        self.logistics_optimizer = LogisticsOptimizer()
        self.db_manager = DatabaseManager()
        
        # Create data directory if it doesn't exist
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        os.makedirs(data_dir, exist_ok=True)
    
    def lookup_company(self, company_name: str, location: Optional[str] = None) -> Optional[Company]:
        """
        Look up a company by name and location.
        
        Args:
            company_name: Name of the company to look up
            location: Optional location to narrow down search
            
        Returns:
            Company object if found, None otherwise
        """
        logger.info(f"Looking up company: {company_name} in location: {location}")
        
        # First check if company exists in database
        # This would require a search by name functionality in the database manager
        
        # If not found in database, collect data from external sources
        company = self.data_collector.collect_company_data(company_name, location)
        
        # Save to database if found
        if company:
            self.db_manager.save_company(company)
        
        return company
    
    def find_similar_companies(self, company: Company, location: Optional[str] = None, limit: int = 10) -> List[Tuple[Company, float]]:
        """
        Find companies similar to the given company.
        
        Args:
            company: Reference company to find similar ones
            location: Optional location to narrow down search
            limit: Maximum number of similar companies to return
            
        Returns:
            List of tuples containing (company, similarity_score)
        """
        logger.info(f"Finding companies similar to: {company.name}")
        
        # First check database for potential matches
        search_criteria = {}
        if company.industry and company.industry.primary:
            search_criteria['industry'] = company.industry.primary
        if location:
            search_criteria['location'] = location
        elif company.address and company.address.city:
            search_criteria['location'] = company.address.city
        
        candidate_companies = self.db_manager.search_companies(search_criteria, limit=100)
        
        # If not enough candidates in database, collect more from external sources
        if len(candidate_companies) < 20:
            external_companies = self.data_collector.find_similar_companies(company, location, limit=20)
            
            # Save external companies to database
            for ext_company in external_companies:
                self.db_manager.save_company(ext_company)
                candidate_companies.append(ext_company)
        
        # Use similarity scorer to rank companies
        similar_companies = self.similarity_scorer.rank_companies_by_similarity(company, candidate_companies, limit)
        
        return similar_companies
    
    def discover_companies_by_industry(self, industry: str, location: Optional[str] = None, 
                                      min_employees: int = 10, owner_operated: bool = True, 
                                      growth_mode: bool = True, limit: int = 20) -> List[Company]:
        """
        Discover companies in a specific industry.
        
        Args:
            industry: Industry to search for
            location: Optional location to narrow down search
            min_employees: Minimum number of employees
            owner_operated: Whether to target owner-operated businesses
            growth_mode: Whether to target businesses in growth mode
            limit: Maximum number of companies to return
            
        Returns:
            List of companies in the specified industry
        """
        logger.info(f"Discovering companies in industry: {industry} in location: {location}")
        
        # Map industry to specific discovery method
        if industry.lower() == "construction":
            companies = self.industry_discovery.discover_construction_companies(
                location, min_employees, owner_operated, growth_mode, limit
            )
        elif industry.lower() == "manufacturing":
            companies = self.industry_discovery.discover_manufacturing_companies(
                location, min_employees, owner_operated, growth_mode, limit
            )
        elif industry.lower() == "trucking":
            companies = self.industry_discovery.discover_trucking_companies(
                location, min_employees, owner_operated, growth_mode, limit
            )
        else:
            # Generic industry search
            search_criteria = {
                'industry': industry,
                'min_employees': min_employees
            }
            if location:
                search_criteria['location'] = location
            
            companies = self.db_manager.search_companies(search_criteria, limit=limit)
            
            # Filter for owner-operated and growth mode if requested
            if owner_operated:
                companies = self.industry_discovery.filter_owner_operated_companies(companies)
            if growth_mode:
                companies = self.industry_discovery.filter_growth_mode_companies(companies)
        
        # Calculate tax-saving potential for each company
        for company in companies:
            company.tax_indicators.tax_saving_potential = self.similarity_scorer.score_tax_saving_potential(company)
        
        return companies
    
    def optimize_logistics(self, companies: List[Company]) -> Dict[str, Any]:
        """
        Optimize logistics for visiting a list of companies.
        
        Args:
            companies: List of companies to visit
            
        Returns:
            Dictionary with logistics optimization results
        """
        logger.info(f"Optimizing logistics for {len(companies)} companies")
        
        # Cluster companies by region
        clusters = self.logistics_optimizer.cluster_companies_by_region(companies)
        
        # Generate weekly schedule
        schedule = self.logistics_optimizer.generate_weekly_schedule(companies)
        
        # Suggest best outreach days
        best_days = self.logistics_optimizer.suggest_best_outreach_days(companies)
        
        # Generate route maps
        maps = {}
        for day, route in schedule.items():
            if route.companies:
                # Use a central location as the starting point for each day
                if day == "Monday":
                    start_location = "Waukesha, WI"
                elif day == "Tuesday":
                    start_location = "Kenosha, WI"
                elif day == "Wednesday":
                    start_location = "Madison, WI"
                else:
                    start_location = "Milwaukee, WI"
                
                map_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', f'route_map_{day}.html')
                maps[day] = self.logistics_optimizer.generate_route_map(route, start_location, map_path)
        
        return {
            'clusters': clusters,
            'schedule': schedule,
            'best_days': best_days,
            'maps': maps
        }
    
    def export_companies_to_csv(self, companies: List[Company], output_path: Optional[str] = None) -> str:
        """
        Export companies to a CSV file.
        
        Args:
            companies: List of companies to export
            output_path: Optional path for the output file
            
        Returns:
            Path to the generated CSV file
        """
        if not output_path:
            output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'companies.csv')
        
        success = self.db_manager.export_to_csv(companies, output_path)
        
        if success:
            return output_path
        else:
            raise Exception("Failed to export companies to CSV")
    
    def rank_companies_by_tax_potential(self, companies: List[Company]) -> List[Tuple[Company, TaxSavingPotential]]:
        """
        Rank companies by tax-saving potential.
        
        Args:
            companies: List of companies to rank
            
        Returns:
            List of tuples containing (company, tax_potential) sorted by potential
        """
        return self.similarity_scorer.rank_companies_by_tax_potential(companies)
