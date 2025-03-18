"""
Integration tests for the Business Lookup & Logistics Optimization Tool.
Tests interactions between components and end-to-end functionality.
"""

import unittest
import os
import sys
import json
from unittest.mock import patch, MagicMock

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import BusinessLookupApp
from src.models import Company, Industry, Address, Executive, Contact, Financials, TaxIndicators, TaxSavingPotential


class TestBusinessLookupApp(unittest.TestCase):
    """Test cases for the integrated BusinessLookupApp."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock for the data collector
        self.data_collector_patcher = patch('src.data_collector.DataCollector')
        self.mock_data_collector = self.data_collector_patcher.start()
        
        # Create a mock for the database manager
        self.db_manager_patcher = patch('src.database.DatabaseManager')
        self.mock_db_manager = self.db_manager_patcher.start()
        
        # Initialize the app with mocked dependencies
        self.app = BusinessLookupApp()
        
        # Create test companies
        self.company1 = Company(
            id="company1",
            name="Test Manufacturing",
            description="A test manufacturing company",
            industry=Industry(primary="Manufacturing", naics_code="333", sic_code="3500"),
            address=Address(street="123 Main St", city="Milwaukee", state="WI", zip="53202"),
            financials=Financials(employee_count=50, estimated_revenue=5000000, growth_rate=15),
            tax_indicators=TaxIndicators(
                recent_developments="Expanding operations",
                succession_planning="Owner planning retirement",
                government_contracts="Major government contract"
            )
        )
        
        self.company2 = Company(
            id="company2",
            name="Similar Manufacturing",
            description="A similar manufacturing company",
            industry=Industry(primary="Manufacturing", naics_code="333", sic_code="3500"),
            address=Address(street="456 Oak St", city="Milwaukee", state="WI", zip="53202"),
            financials=Financials(employee_count=45, estimated_revenue=4500000, growth_rate=10),
            tax_indicators=TaxIndicators(
                recent_developments="Purchased new equipment",
                succession_planning="",
                government_contracts=""
            )
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.data_collector_patcher.stop()
        self.db_manager_patcher.stop()
    
    def test_lookup_company_integration(self):
        """Test company lookup with integrated components."""
        # Configure mock data collector to return a test company
        self.app.data_collector.collect_company_data.return_value = self.company1
        
        # Look up a company
        company = self.app.lookup_company("Test Manufacturing", "Milwaukee")
        
        # Verify the result
        self.assertEqual(company.id, self.company1.id)
        self.assertEqual(company.name, self.company1.name)
        
        # Verify data collector was called with correct parameters
        self.app.data_collector.collect_company_data.assert_called_once_with("Test Manufacturing", "Milwaukee")
        
        # Verify company was saved to database
        self.app.db_manager.save_company.assert_called_once_with(self.company1)
    
    def test_find_similar_companies_integration(self):
        """Test finding similar companies with integrated components."""
        # Configure mock database manager to return test companies
        self.app.db_manager.search_companies.return_value = [self.company2]
        
        # Configure mock data collector to return no additional companies
        self.app.data_collector.find_similar_companies.return_value = []
        
        # Find similar companies
        similar_companies = self.app.find_similar_companies(self.company1, "Milwaukee")
        
        # Verify the result
        self.assertEqual(len(similar_companies), 1)
        self.assertEqual(similar_companies[0][0].id, self.company2.id)
        
        # Verify database manager was called with correct parameters
        self.app.db_manager.search_companies.assert_called_once()
        
        # Verify data collector was not called since enough companies were found in database
        self.app.data_collector.find_similar_companies.assert_not_called()
    
    def test_discover_companies_by_industry_integration(self):
        """Test discovering companies by industry with integrated components."""
        # Configure mock industry discovery to return test companies
        self.app.industry_discovery.discover_manufacturing_companies.return_value = [self.company1, self.company2]
        
        # Discover manufacturing companies
        companies = self.app.discover_companies_by_industry("manufacturing", "Milwaukee")
        
        # Verify the result
        self.assertEqual(len(companies), 2)
        self.assertEqual(companies[0].id, self.company1.id)
        self.assertEqual(companies[1].id, self.company2.id)
        
        # Verify industry discovery was called with correct parameters
        self.app.industry_discovery.discover_manufacturing_companies.assert_called_once_with(
            "Milwaukee", 10, True, True, 20
        )
    
    def test_optimize_logistics_integration(self):
        """Test logistics optimization with integrated components."""
        # Configure mock logistics optimizer to return test clusters and schedule
        self.app.logistics_optimizer.cluster_companies_by_region.return_value = {
            "Milwaukee": [self.company1, self.company2]
        }
        self.app.logistics_optimizer.generate_weekly_schedule.return_value = {
            "Monday": MagicMock(companies=[MagicMock(company_id=self.company1.id), MagicMock(company_id=self.company2.id)])
        }
        self.app.logistics_optimizer.suggest_best_outreach_days.return_value = {
            "Monday": 0.7, "Tuesday": 0.9
        }
        self.app.logistics_optimizer.generate_route_map.return_value = "/path/to/map.html"
        
        # Optimize logistics
        logistics_results = self.app.optimize_logistics([self.company1, self.company2])
        
        # Verify the result
        self.assertIn("clusters", logistics_results)
        self.assertIn("schedule", logistics_results)
        self.assertIn("best_days", logistics_results)
        self.assertIn("maps", logistics_results)
        
        # Verify logistics optimizer was called with correct parameters
        self.app.logistics_optimizer.cluster_companies_by_region.assert_called_once_with([self.company1, self.company2])
        self.app.logistics_optimizer.generate_weekly_schedule.assert_called_once_with([self.company1, self.company2])
        self.app.logistics_optimizer.suggest_best_outreach_days.assert_called_once_with([self.company1, self.company2])


class TestEndToEnd(unittest.TestCase):
    """End-to-end tests for the Business Lookup & Logistics Optimization Tool."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a real app instance
        self.app = BusinessLookupApp()
        
        # Create test data
        self.test_company_name = "Example Manufacturing"
        self.test_location = "Milwaukee, WI"
        self.test_industry = "manufacturing"
    
    @unittest.skip("Requires real API access and database")
    def test_end_to_end_lookup_and_similar(self):
        """Test end-to-end company lookup and finding similar companies."""
        # Look up a company
        company = self.app.lookup_company(self.test_company_name, self.test_location)
        
        # Verify company was found
        self.assertIsNotNone(company)
        self.assertEqual(company.name, self.test_company_name)
        
        # Find similar companies
        similar_companies = self.app.find_similar_companies(company, self.test_location)
        
        # Verify similar companies were found
        self.assertGreater(len(similar_companies), 0)
    
    @unittest.skip("Requires real API access and database")
    def test_end_to_end_industry_discovery(self):
        """Test end-to-end industry discovery."""
        # Discover companies in manufacturing industry
        companies = self.app.discover_companies_by_industry(self.test_industry, self.test_location)
        
        # Verify companies were found
        self.assertGreater(len(companies), 0)
        
        # Verify all companies are in the manufacturing industry
        for company in companies:
            self.assertEqual(company.industry.primary.lower(), self.test_industry)
    
    @unittest.skip("Requires real API access and database")
    def test_end_to_end_logistics_optimization(self):
        """Test end-to-end logistics optimization."""
        # First discover some companies
        companies = self.app.discover_companies_by_industry(self.test_industry, self.test_location)
        
        # Verify companies were found
        self.assertGreater(len(companies), 0)
        
        # Optimize logistics
        logistics_results = self.app.optimize_logistics(companies)
        
        # Verify logistics results
        self.assertIn("clusters", logistics_results)
        self.assertIn("schedule", logistics_results)
        self.assertIn("best_days", logistics_results)
        self.assertIn("maps", logistics_results)


if __name__ == '__main__':
    unittest.main()
