"""
Business matching module for the Business Lookup & Logistics Optimization Tool.
Implements algorithms for finding similar companies and scoring company similarity.
"""

import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.models import Company, Industry
from src.data_normalizer import normalize_industry, clean_company_name

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BusinessMatcher:
    """Business matching class for finding similar companies."""
    
    def __init__(self):
        """Initialize the business matcher."""
        self.industry_codes = self._load_industry_codes()
        self.vectorizer = TfidfVectorizer(stop_words='english')
    
    def _load_industry_codes(self) -> Dict[str, Dict[str, Any]]:
        """
        Load industry codes mapping (NAICS and SIC).
        
        Returns:
            Dictionary mapping industry codes to information
        """
        # This would typically load from a file or database
        # For now, we'll use a simplified version with key industries
        
        industry_codes = {
            # Construction industry codes
            "23": {
                "code_type": "NAICS",
                "name": "Construction",
                "subcategories": {
                    "236": "Construction of Buildings",
                    "237": "Heavy and Civil Engineering Construction",
                    "238": "Specialty Trade Contractors"
                }
            },
            "1521": {
                "code_type": "SIC",
                "name": "General Contractors-Single-Family Houses",
                "naics_equivalent": "236115"
            },
            "1541": {
                "code_type": "SIC",
                "name": "General Contractors-Industrial Buildings and Warehouses",
                "naics_equivalent": "236210"
            },
            
            # Manufacturing industry codes
            "31-33": {
                "code_type": "NAICS",
                "name": "Manufacturing",
                "subcategories": {
                    "331": "Primary Metal Manufacturing",
                    "332": "Fabricated Metal Product Manufacturing",
                    "333": "Machinery Manufacturing",
                    "336": "Transportation Equipment Manufacturing"
                }
            },
            "3411": {
                "code_type": "SIC",
                "name": "Metal Cans",
                "naics_equivalent": "332431"
            },
            "3441": {
                "code_type": "SIC",
                "name": "Fabricated Structural Metal",
                "naics_equivalent": "332312"
            },
            
            # Trucking industry codes
            "484": {
                "code_type": "NAICS",
                "name": "Truck Transportation",
                "subcategories": {
                    "4841": "General Freight Trucking",
                    "4842": "Specialized Freight Trucking"
                }
            },
            "4212": {
                "code_type": "SIC",
                "name": "Local Trucking Without Storage",
                "naics_equivalent": "484110"
            },
            "4213": {
                "code_type": "SIC",
                "name": "Trucking, Except Local",
                "naics_equivalent": "484121"
            }
        }
        
        return industry_codes
    
    def find_similar_companies(self, company: Company, candidate_companies: List[Company], top_n: int = 10) -> List[Tuple[Company, float]]:
        """
        Find companies similar to the given company.
        
        Args:
            company: Reference company to find similar ones
            candidate_companies: List of candidate companies to compare against
            top_n: Number of top matches to return
            
        Returns:
            List of tuples containing (company, similarity_score)
        """
        logger.info(f"Finding companies similar to: {company.name}")
        
        # Filter out the reference company itself
        candidates = [c for c in candidate_companies if c.id != company.id]
        
        if not candidates:
            return []
        
        # Calculate similarity scores
        similarity_scores = []
        for candidate in candidates:
            score = self.calculate_similarity_score(company, candidate)
            similarity_scores.append((candidate, score))
        
        # Sort by similarity score (descending)
        similarity_scores.sort(key=lambda x: x[1], reverse=True)
        
        return similarity_scores[:top_n]
    
    def calculate_similarity_score(self, company1: Company, company2: Company) -> float:
        """
        Calculate similarity score between two companies.
        
        Args:
            company1: First company
            company2: Second company
            
        Returns:
            Similarity score (0-1)
        """
        # Calculate individual similarity components
        industry_similarity = self.calculate_industry_similarity(company1, company2)
        size_similarity = self.calculate_size_similarity(company1, company2)
        location_similarity = self.calculate_location_similarity(company1, company2)
        description_similarity = self.calculate_description_similarity(company1, company2)
        
        # Weighted average of similarity components
        weights = {
            'industry': 0.4,
            'size': 0.2,
            'location': 0.2,
            'description': 0.2
        }
        
        similarity_score = (
            weights['industry'] * industry_similarity +
            weights['size'] * size_similarity +
            weights['location'] * location_similarity +
            weights['description'] * description_similarity
        )
        
        return similarity_score
    
    def calculate_industry_similarity(self, company1: Company, company2: Company) -> float:
        """
        Calculate industry similarity between two companies.
        
        Args:
            company1: First company
            company2: Second company
            
        Returns:
            Industry similarity score (0-1)
        """
        # If either company doesn't have industry information, return low similarity
        if not company1.industry or not company2.industry:
            return 0.1
        
        # If primary industries match exactly, high similarity
        if company1.industry.primary == company2.industry.primary:
            return 1.0
        
        # If NAICS or SIC codes match, high similarity
        if (company1.industry.naics_code and company2.industry.naics_code and 
            company1.industry.naics_code == company2.industry.naics_code):
            return 0.9
        
        if (company1.industry.sic_code and company2.industry.sic_code and 
            company1.industry.sic_code == company2.industry.sic_code):
            return 0.9
        
        # Check for partial NAICS code match (first 2-3 digits)
        if (company1.industry.naics_code and company2.industry.naics_code):
            naics1 = company1.industry.naics_code[:2]
            naics2 = company2.industry.naics_code[:2]
            if naics1 == naics2:
                return 0.8
        
        # Normalize industries and check for category/subcategory match
        industry1 = normalize_industry(company1.industry.primary)
        industry2 = normalize_industry(company2.industry.primary)
        
        if industry1['category'] == industry2['category']:
            if industry1['subcategory'] == industry2['subcategory']:
                return 0.8
            else:
                return 0.6
        
        # Check for overlapping subcategories
        subcategories1 = set(company1.industry.subcategories)
        subcategories2 = set(company2.industry.subcategories)
        
        if subcategories1 and subcategories2:
            overlap = subcategories1.intersection(subcategories2)
            if overlap:
                return 0.5 + (0.3 * len(overlap) / max(len(subcategories1), len(subcategories2)))
        
        # Default to low similarity
        return 0.2
    
    def calculate_size_similarity(self, company1: Company, company2: Company) -> float:
        """
        Calculate size similarity between two companies based on employee count and revenue.
        
        Args:
            company1: First company
            company2: Second company
            
        Returns:
            Size similarity score (0-1)
        """
        # If either company doesn't have financials, return medium similarity
        if not company1.financials or not company2.financials:
            return 0.5
        
        employee_similarity = 0.5
        revenue_similarity = 0.5
        
        # Calculate employee count similarity
        if (company1.financials.employee_count is not None and 
            company2.financials.employee_count is not None):
            
            # Use logarithmic scale for employee count comparison
            log_emp1 = np.log10(max(10, company1.financials.employee_count))
            log_emp2 = np.log10(max(10, company2.financials.employee_count))
            
            # Calculate similarity based on ratio of smaller to larger
            ratio = min(log_emp1, log_emp2) / max(log_emp1, log_emp2)
            employee_similarity = ratio
        
        # Calculate revenue similarity
        if (company1.financials.estimated_revenue is not None and 
            company2.financials.estimated_revenue is not None):
            
            # Use logarithmic scale for revenue comparison
            log_rev1 = np.log10(max(10000, company1.financials.estimated_revenue))
            log_rev2 = np.log10(max(10000, company2.financials.estimated_revenue))
            
            # Calculate similarity based on ratio of smaller to larger
            ratio = min(log_rev1, log_rev2) / max(log_rev1, log_rev2)
            revenue_similarity = ratio
        
        # Weighted average of employee and revenue similarity
        return 0.6 * employee_similarity + 0.4 * revenue_similarity
    
    def calculate_location_similarity(self, company1: Company, company2: Company) -> float:
        """
        Calculate location similarity between two companies.
        
        Args:
            company1: First company
            company2: Second company
            
        Returns:
            Location similarity score (0-1)
        """
        # If either company doesn't have address, return low similarity
        if not company1.address or not company2.address:
            return 0.1
        
        # If exact address match, highest similarity
        if (company1.address.street == company2.address.street and
            company1.address.city == company2.address.city and
            company1.address.state == company2.address.state):
            return 1.0
        
        # If same city and state, high similarity
        if (company1.address.city == company2.address.city and
            company1.address.state == company2.address.state):
            return 0.9
        
        # If same state and zip code prefix matches, medium-high similarity
        if (company1.address.state == company2.address.state and
            company1.address.zip and company2.address.zip and
            company1.address.zip[:3] == company2.address.zip[:3]):
            return 0.8
        
        # If same state, medium similarity
        if company1.address.state == company2.address.state:
            return 0.6
        
        # If states are adjacent, low-medium similarity
        # This would require a mapping of adjacent states
        
        # Default to low similarity for different states
        return 0.2
    
    def calculate_description_similarity(self, company1: Company, company2: Company) -> float:
        """
        Calculate description similarity between two companies using text analysis.
        
        Args:
            company1: First company
            company2: Second company
            
        Returns:
            Description similarity score (0-1)
        """
        # If either company doesn't have a description, return low similarity
        if not company1.description or not company2.description:
            return 0.3
        
        try:
            # Create document corpus
            corpus = [company1.description, company2.description]
            
            # Transform corpus to TF-IDF features
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating description similarity: {e}")
            return 0.3
    
    def match_by_industry_code(self, naics_code: str = None, sic_code: str = None) -> List[str]:
        """
        Find matching industries based on NAICS or SIC code.
        
        Args:
            naics_code: NAICS code to match
            sic_code: SIC code to match
            
        Returns:
            List of matching industry names
        """
        matches = []
        
        if naics_code:
            # Check for exact NAICS code match
            for code, info in self.industry_codes.items():
                if info["code_type"] == "NAICS" and code == naics_code:
                    matches.append(info["name"])
                    break
                
                # Check subcategories
                if "subcategories" in info:
                    for subcode, subname in info["subcategories"].items():
                        if subcode == naics_code:
                            matches.append(subname)
                            break
        
        if sic_code:
            # Check for exact SIC code match
            for code, info in self.industry_codes.items():
                if info["code_type"] == "SIC" and code == sic_code:
                    matches.append(info["name"])
                    break
        
        return matches
    
    def get_industry_by_name(self, industry_name: str) -> List[Dict[str, Any]]:
        """
        Find industry codes based on industry name.
        
        Args:
            industry_name: Industry name to search for
            
        Returns:
            List of matching industry information
        """
        matches = []
        industry_name_lower = industry_name.lower()
        
        for code, info in self.industry_codes.items():
            if industry_name_lower in info["name"].lower():
                matches.append({
                    "code": code,
                    "code_type": info["code_type"],
                    "name": info["name"]
                })
            
            # Check subcategories
            if "subcategories" in info:
                for subcode, subname in info["subcategories"].items():
                    if industry_name_lower in subname.lower():
                        matches.append({
                            "code": subcode,
                            "code_type": info["code_type"],
                            "name": subname,
                            "parent_name": info["name"]
                        })
        
        return matches
