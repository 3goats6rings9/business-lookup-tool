"""
Unit tests for the Business Lookup & Logistics Optimization Tool.
Tests individual components for functionality and correctness.
"""

import unittest
import os
import sys
import json
from unittest.mock import patch, MagicMock

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import Company, Industry, Address, Executive, Contact, Financials, TaxIndicators, TaxSavingPotential
from src.business_matcher import BusinessMatcher
from src.similarity_scorer import SimilarityScorer
from src.industry_discovery import IndustryDiscovery
from src.logistics_optimizer import LogisticsOptimizer


class TestBusinessMatcher(unittest.TestCase):
    """Test cases for the BusinessMatcher class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.matcher = BusinessMatcher()
        
        # Create test companies
        self.company1 = Company(
            id="company1",
            name="Test Manufacturing",
            description="A test manufacturing company",
            industry=Industry(primary="Manufacturing", naics_code="333", sic_code="3500"),
            address=Address(street="123 Main St", city="Milwaukee", state="WI", zip="53202"),
            financials=Financials(employee_count=50, estimated_revenue=5000000)
        )
        
        self.company2 = Company(
            id="company2",
            name="Similar Manufacturing",
            description="A similar manufacturing company",
            industry=Industry(primary="Manufacturing", naics_code="333", sic_code="3500"),
            address=Address(street="456 Oak St", city="Milwaukee", state="WI", zip="53202"),
            financials=Financials(employee_count=45, estimated_revenue=4500000)
        )
        
        self.company3 = Company(
            id="company3",
            name="Different Construction",
            description="A construction company",
            industry=Industry(primary="Construction", naics_code="236", sic_code="1500"),
            address=Address(street="789 Pine St", city="Madison", state="WI", zip="53703"),
            financials=Financials(employee_count=100, estimated_revenue=10000000)
        )
    
    def test_find_similar_companies(self):
        """Test finding similar companies."""
        # Mock the database search
        with patch.object(self.matcher, 'db_manager') as mock_db:
            mock_db.search_companies.return_value = [self.company2, self.company3]
            
            # Test finding similar companies
            similar_companies = self.matcher.find_similar_companies(self.company1)
            
            # Verify results
            self.assertEqual(len(similar_companies), 2)
            self.assertEqual(similar_companies[0].id, self.company2.id)  # Most similar should be first
            self.assertEqual(similar_companies[1].id, self.company3.id)
            
            # Verify database was called with correct parameters
            mock_db.search_companies.assert_called_once()
    
    def test_filter_by_industry(self):
        """Test filtering companies by industry."""
        companies = [self.company1, self.company2, self.company3]
        
        # Filter for manufacturing
        manufacturing_companies = self.matcher.filter_by_industry(companies, "Manufacturing")
        self.assertEqual(len(manufacturing_companies), 2)
        self.assertEqual(manufacturing_companies[0].id, self.company1.id)
        self.assertEqual(manufacturing_companies[1].id, self.company2.id)
        
        # Filter for construction
        construction_companies = self.matcher.filter_by_industry(companies, "Construction")
        self.assertEqual(len(construction_companies), 1)
        self.assertEqual(construction_companies[0].id, self.company3.id)
        
        # Filter for non-existent industry
        other_companies = self.matcher.filter_by_industry(companies, "Retail")
        self.assertEqual(len(other_companies), 0)
    
    def test_filter_by_size(self):
        """Test filtering companies by size."""
        companies = [self.company1, self.company2, self.company3]
        
        # Filter for companies with 50+ employees
        large_companies = self.matcher.filter_by_size(companies, min_employees=50)
        self.assertEqual(len(large_companies), 2)
        self.assertEqual(large_companies[0].id, self.company1.id)
        self.assertEqual(large_companies[1].id, self.company3.id)
        
        # Filter for companies with 75+ employees
        larger_companies = self.matcher.filter_by_size(companies, min_employees=75)
        self.assertEqual(len(larger_companies), 1)
        self.assertEqual(larger_companies[0].id, self.company3.id)
        
        # Filter for companies with 150+ employees
        very_large_companies = self.matcher.filter_by_size(companies, min_employees=150)
        self.assertEqual(len(very_large_companies), 0)
    
    def test_filter_by_location(self):
        """Test filtering companies by location."""
        companies = [self.company1, self.company2, self.company3]
        
        # Filter for companies in Milwaukee
        milwaukee_companies = self.matcher.filter_by_location(companies, "Milwaukee")
        self.assertEqual(len(milwaukee_companies), 2)
        self.assertEqual(milwaukee_companies[0].id, self.company1.id)
        self.assertEqual(milwaukee_companies[1].id, self.company2.id)
        
        # Filter for companies in Madison
        madison_companies = self.matcher.filter_by_location(companies, "Madison")
        self.assertEqual(len(madison_companies), 1)
        self.assertEqual(madison_companies[0].id, self.company3.id)
        
        # Filter for companies in Wisconsin (state level)
        wisconsin_companies = self.matcher.filter_by_location(companies, "WI")
        self.assertEqual(len(wisconsin_companies), 3)


class TestSimilarityScorer(unittest.TestCase):
    """Test cases for the SimilarityScorer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scorer = SimilarityScorer()
        
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
        
        self.company3 = Company(
            id="company3",
            name="Different Construction",
            description="A construction company",
            industry=Industry(primary="Construction", naics_code="236", sic_code="1500"),
            address=Address(street="789 Pine St", city="Madison", state="WI", zip="53703"),
            financials=Financials(employee_count=100, estimated_revenue=10000000, growth_rate=5),
            tax_indicators=TaxIndicators(
                recent_developments="",
                succession_planning="",
                government_contracts=""
            )
        )
    
    def test_score_company_similarity(self):
        """Test scoring similarity between companies."""
        # Test similarity between identical companies
        self_similarity = self.scorer.score_company_similarity(self.company1, self.company1)
        self.assertAlmostEqual(self_similarity, 1.0, places=1)
        
        # Test similarity between similar companies
        similar_similarity = self.scorer.score_company_similarity(self.company1, self.company2)
        self.assertGreater(similar_similarity, 0.7)  # Should be quite similar
        
        # Test similarity between different companies
        different_similarity = self.scorer.score_company_similarity(self.company1, self.company3)
        self.assertLess(different_similarity, 0.5)  # Should be less similar
    
    def test_score_tax_saving_potential(self):
        """Test scoring tax-saving potential."""
        # Test high potential
        potential1 = self.scorer.score_tax_saving_potential(self.company1)
        self.assertEqual(potential1, TaxSavingPotential.HIGH)
        
        # Test medium potential
        potential2 = self.scorer.score_tax_saving_potential(self.company2)
        self.assertEqual(potential2, TaxSavingPotential.MEDIUM)
        
        # Test low potential
        potential3 = self.scorer.score_tax_saving_potential(self.company3)
        self.assertEqual(potential3, TaxSavingPotential.LOW)
    
    def test_rank_companies_by_similarity(self):
        """Test ranking companies by similarity."""
        companies = [self.company1, self.company2, self.company3]
        
        # Rank by similarity to company1
        ranked = self.scorer.rank_companies_by_similarity(self.company1, companies)
        
        # Should return 2 companies (excluding the reference company)
        self.assertEqual(len(ranked), 2)
        
        # First should be company2 (most similar)
        self.assertEqual(ranked[0][0].id, self.company2.id)
        
        # Second should be company3 (least similar)
        self.assertEqual(ranked[1][0].id, self.company3.id)
    
    def test_rank_companies_by_tax_potential(self):
        """Test ranking companies by tax-saving potential."""
        companies = [self.company1, self.company2, self.company3]
        
        # Rank by tax potential
        ranked = self.scorer.rank_companies_by_tax_potential(companies)
        
        # Should return all 3 companies
        self.assertEqual(len(ranked), 3)
        
        # First should be company1 (HIGH potential)
        self.assertEqual(ranked[0][0].id, self.company1.id)
        self.assertEqual(ranked[0][1], TaxSavingPotential.HIGH)
        
        # Second should be company2 (MEDIUM potential)
        self.assertEqual(ranked[1][0].id, self.company2.id)
        self.assertEqual(ranked[1][1], TaxSavingPotential.MEDIUM)
        
        # Third should be company3 (LOW potential)
        self.assertEqual(ranked[2][0].id, self.company3.id)
        self.assertEqual(ranked[2][1], TaxSavingPotential.LOW)


class TestIndustryDiscovery(unittest.TestCase):
    """Test cases for the IndustryDiscovery class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.discovery = IndustryDiscovery()
        
        # Create test companies
        self.manufacturing_company = Company(
            id="company1",
            name="Test Manufacturing",
            description="A test manufacturing company with CNC machining",
            industry=Industry(primary="Manufacturing", naics_code="333", sic_code="3500"),
            address=Address(street="123 Main St", city="Milwaukee", state="WI", zip="53202"),
            financials=Financials(employee_count=50, estimated_revenue=5000000)
        )
        
        self.construction_company = Company(
            id="company2",
            name="Test Construction",
            description="A construction company specializing in commercial buildings",
            industry=Industry(primary="Construction", naics_code="236", sic_code="1500"),
            address=Address(street="456 Oak St", city="Milwaukee", state="WI", zip="53202"),
            financials=Financials(employee_count=75, estimated_revenue=7500000)
        )
        
        self.trucking_company = Company(
            id="company3",
            name="Test Trucking",
            description="A freight transportation and logistics company",
            industry=Industry(primary="Trucking", naics_code="484", sic_code="4200"),
            address=Address(street="789 Pine St", city="Madison", state="WI", zip="53703"),
            financials=Financials(employee_count=30, estimated_revenue=3000000)
        )
    
    def test_is_in_industry(self):
        """Test checking if a company is in a specific industry."""
        # Test manufacturing company
        self.assertTrue(self.discovery._is_in_industry(self.manufacturing_company, "manufacturing"))
        self.assertFalse(self.discovery._is_in_industry(self.manufacturing_company, "construction"))
        self.assertFalse(self.discovery._is_in_industry(self.manufacturing_company, "trucking"))
        
        # Test construction company
        self.assertFalse(self.discovery._is_in_industry(self.construction_company, "manufacturing"))
        self.assertTrue(self.discovery._is_in_industry(self.construction_company, "construction"))
        self.assertFalse(self.discovery._is_in_industry(self.construction_company, "trucking"))
        
        # Test trucking company
        self.assertFalse(self.discovery._is_in_industry(self.trucking_company, "manufacturing"))
        self.assertFalse(self.discovery._is_in_industry(self.trucking_company, "construction"))
        self.assertTrue(self.discovery._is_in_industry(self.trucking_company, "trucking"))
    
    def test_filter_companies_by_industry(self):
        """Test filtering companies by industry."""
        companies = [self.manufacturing_company, self.construction_company, self.trucking_company]
        
        # Filter for manufacturing
        manufacturing_companies = self.discovery.filter_companies_by_industry(companies, "manufacturing")
        self.assertEqual(len(manufacturing_companies), 1)
        self.assertEqual(manufacturing_companies[0].id, self.manufacturing_company.id)
        
        # Filter for construction
        construction_companies = self.discovery.filter_companies_by_industry(companies, "construction")
        self.assertEqual(len(construction_companies), 1)
        self.assertEqual(construction_companies[0].id, self.construction_company.id)
        
        # Filter for trucking
        trucking_companies = self.discovery.filter_companies_by_industry(companies, "trucking")
        self.assertEqual(len(trucking_companies), 1)
        self.assertEqual(trucking_companies[0].id, self.trucking_company.id)
    
    def test_get_industry_segments(self):
        """Test getting segments within an industry."""
        # Test manufacturing segments
        manufacturing_segments = self.discovery.get_industry_segments("manufacturing")
        self.assertIn("Industrial Machinery & Automation", manufacturing_segments)
        self.assertIn("Fabricators", manufacturing_segments)
        
        # Test construction segments
        construction_segments = self.discovery.get_industry_segments("construction")
        self.assertIn("General Contractors", construction_segments)
        self.assertIn("Engineering Firms", construction_segments)
        
        # Test trucking segments
        trucking_segments = self.discovery.get_industry_segments("trucking")
        self.assertIn("Freight Carriers", trucking_segments)
        self.assertIn("Warehousing & Distribution", trucking_segments)


class TestLogisticsOptimizer(unittest.TestCase):
    """Test cases for the LogisticsOptimizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.optimizer = LogisticsOptimizer()
        
        # Create test companies
        self.company1 = Company(
            id="company1",
            name="Milwaukee Company",
            address=Address(street="123 Main St", city="Milwaukee", state="WI", zip="53202"),
            location=MagicMock(latitude=43.0389, longitude=-87.9065, region="Milwaukee")
        )
        
        self.company2 = Company(
            id="company2",
            name="Waukesha Company",
            address=Address(street="456 Oak St", city="Waukesha", state="WI", zip="53186"),
            location=MagicMock(latitude=43.0117, longitude=-88.2315, region="Waukesha")
        )
        
        self.company3 = Company(
            id="company3",
            name="Kenosha Company",
            address=Address(street="789 Pine St", city="Kenosha", state="WI", zip="53140"),
            location=MagicMock(latitude=42.5847, longitude=-87.8212, region="Kenosha")
        )
        
        self.company4 = Company(
            id="company4",
            name="Madison Company",
            address=Address(street="101 Elm St", city="Madison", state="WI", zip="53703"),
            location=MagicMock(latitude=43.0731, longitude=-89.4012, region="Madison")
        )
    
    def test_cluster_companies_by_region(self):
        """Test clustering companies by region."""
        companies = [self.company1, self.company2, self.company3, self.company4]
        
        # Cluster companies
        clusters = self.optimizer.cluster_companies_by_region(companies)
        
        # Should have at least 2 clusters
        self.assertGreaterEqual(len(clusters), 2)
        
        # Companies in the same city should be in the same cluster
        for cluster_name, cluster_companies in clusters.items():
            if self.company1 in cluster_companies:
                # Milwaukee and Waukesha might be in the same cluster due to proximity
                if self.company2 in cluster_companies:
                    self.assertNotIn(self.company3, cluster_companies)  # Kenosha should be in a different cluster
                    self.assertNotIn(self.company4, cluster_companies)  # Madison should be in a different cluster
    
    def test_assign_companies_to_days(self):
        """Test assigning companies to specific days."""
        companies = [self.company1, self.company2, self.company3, self.company4]
        
        # Assign companies to days
        days = self.optimizer.assign_companies_to_days(companies)
        
        # Should have entries for all days
        self.assertIn("Monday", days)
        self.assertIn("Tuesday", days)
        self.assertIn("Wednesday", days)
        self.assertIn("Thursday", days)
        self.assertIn("Friday", days)
        
        # Milwaukee and Waukesha companies should be assigned to Monday
        self.assertIn(self.company1, days["Monday"])
        self.assertIn(self.company2, days["Monday"])
        
        # Kenosha company should be assigned to Tuesday
        self.assertIn(self.company3, days["Tuesday"])
        
        # Madison company should be assigned to Wednesday
        self.assertIn(self.company4, days["Wednesday"])
    
    def test_optimize_route(self):
        """Test optimizing a route for visiting companies."""
        companies = [self.company1, self.company2]
        
        # Optimize route
        route = self.optimizer.optimize_route(companies, "Milwaukee, WI")
        
        # Should have correct properties
        self.assertEqual(route.day, "Monday")
        self.assertEqual(len(route.companies), 2)
        self.assertGreater(route.total_distance, 0)
        self.assertGreater(route.estimated_travel_time, 0)
        
        # Should have an optimized order
        self.assertEqual(len(route.optimized_order), 3)  # Start + 2 companies + return to start
    
    def test_suggest_best_outreach_days(self):
        """Test suggesting best days for outreach."""
        companies = [self.company1, self.company2, self.company3, self.company4]
        
        # Get best outreach days
        best_days = self.optimizer.suggest_best_outreach_days(companies)
        
        # Should have entries for all weekdays
        self.assertIn("Monday", best_days)
        self.assertIn("Tuesday", best_days)
        self.assertIn("Wednesday", best_days)
        self.assertIn("Thursday", best_days)
        self.assertIn("Friday", best_days)
        
        # Tuesday should have the highest score
        self.assertEqual(max(best_days.items(), key=lambda x: x[1])[0], "Tuesday")


if __name__ == '__main__':
    unittest.main()
