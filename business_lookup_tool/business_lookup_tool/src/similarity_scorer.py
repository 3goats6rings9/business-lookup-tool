"""
Company similarity scoring module for the Business Lookup & Logistics Optimization Tool.
Implements advanced scoring algorithms for company similarity and tax-saving potential.
"""

import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple

from src.models import Company, TaxSavingPotential

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimilarityScorer:
    """Class for scoring company similarity and tax-saving potential."""
    
    def __init__(self):
        """Initialize the similarity scorer."""
        # Weights for different similarity components
        self.similarity_weights = {
            'industry': 0.35,
            'size': 0.25,
            'location': 0.20,
            'legal_structure': 0.10,
            'growth': 0.10
        }
        
        # Weights for tax-saving potential components
        self.tax_potential_weights = {
            'growth_rate': 0.30,
            'hiring_expansion': 0.20,
            'equipment_upgrades': 0.20,
            'succession_planning': 0.15,
            'government_contracts': 0.15
        }
    
    def score_company_similarity(self, reference: Company, target: Company) -> float:
        """
        Calculate a comprehensive similarity score between two companies.
        
        Args:
            reference: Reference company
            target: Target company to compare against
            
        Returns:
            Similarity score (0-1)
        """
        scores = {}
        
        # Industry similarity
        scores['industry'] = self._score_industry_similarity(reference, target)
        
        # Size similarity
        scores['size'] = self._score_size_similarity(reference, target)
        
        # Location similarity
        scores['location'] = self._score_location_similarity(reference, target)
        
        # Legal structure similarity
        scores['legal_structure'] = self._score_legal_structure_similarity(reference, target)
        
        # Growth similarity
        scores['growth'] = self._score_growth_similarity(reference, target)
        
        # Calculate weighted average
        weighted_score = sum(scores[key] * self.similarity_weights[key] for key in scores)
        
        return weighted_score
    
    def score_tax_saving_potential(self, company: Company) -> TaxSavingPotential:
        """
        Calculate tax-saving potential score for a company.
        
        Args:
            company: Company to score
            
        Returns:
            TaxSavingPotential enum value
        """
        scores = {}
        
        # Growth rate score
        scores['growth_rate'] = self._score_growth_rate(company)
        
        # Hiring and payroll expansion score
        scores['hiring_expansion'] = self._score_hiring_expansion(company)
        
        # Equipment and facility upgrades score
        scores['equipment_upgrades'] = self._score_equipment_upgrades(company)
        
        # Succession and leadership transitions score
        scores['succession_planning'] = self._score_succession_planning(company)
        
        # Government contracting opportunities score
        scores['government_contracts'] = self._score_government_contracts(company)
        
        # Calculate weighted average
        weighted_score = sum(scores[key] * self.tax_potential_weights[key] for key in scores)
        
        # Determine potential based on score
        if weighted_score >= 0.7:
            return TaxSavingPotential.HIGH
        elif weighted_score >= 0.4:
            return TaxSavingPotential.MEDIUM
        else:
            return TaxSavingPotential.LOW
    
    def rank_companies_by_similarity(self, reference: Company, candidates: List[Company], top_n: int = 10) -> List[Tuple[Company, float]]:
        """
        Rank companies by similarity to a reference company.
        
        Args:
            reference: Reference company
            candidates: List of candidate companies to compare against
            top_n: Number of top matches to return
            
        Returns:
            List of tuples containing (company, similarity_score) sorted by score
        """
        # Calculate similarity scores for all candidates
        scored_companies = []
        for candidate in candidates:
            if candidate.id != reference.id:  # Skip the reference company itself
                score = self.score_company_similarity(reference, candidate)
                scored_companies.append((candidate, score))
        
        # Sort by score in descending order
        scored_companies.sort(key=lambda x: x[1], reverse=True)
        
        return scored_companies[:top_n]
    
    def rank_companies_by_tax_potential(self, companies: List[Company]) -> List[Tuple[Company, TaxSavingPotential]]:
        """
        Rank companies by tax-saving potential.
        
        Args:
            companies: List of companies to rank
            
        Returns:
            List of tuples containing (company, tax_potential) sorted by potential
        """
        # Calculate tax-saving potential for all companies
        scored_companies = []
        for company in companies:
            potential = self.score_tax_saving_potential(company)
            scored_companies.append((company, potential))
        
        # Sort by potential (HIGH > MEDIUM > LOW)
        potential_order = {
            TaxSavingPotential.HIGH: 3,
            TaxSavingPotential.MEDIUM: 2,
            TaxSavingPotential.LOW: 1
        }
        scored_companies.sort(key=lambda x: potential_order[x[1]], reverse=True)
        
        return scored_companies
    
    def _score_industry_similarity(self, company1: Company, company2: Company) -> float:
        """Score industry similarity between two companies."""
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
            
            # First digit match (major sector)
            if company1.industry.naics_code[0] == company2.industry.naics_code[0]:
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
    
    def _score_size_similarity(self, company1: Company, company2: Company) -> float:
        """Score size similarity between two companies."""
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
    
    def _score_location_similarity(self, company1: Company, company2: Company) -> float:
        """Score location similarity between two companies."""
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
        
        # Default to low similarity for different states
        return 0.2
    
    def _score_legal_structure_similarity(self, company1: Company, company2: Company) -> float:
        """Score legal structure similarity between two companies."""
        # If either company doesn't have legal structure, return medium similarity
        if not company1.legal_structure or not company2.legal_structure:
            return 0.5
        
        # If exact legal structure match, high similarity
        if company1.legal_structure == company2.legal_structure:
            return 1.0
        
        # Group similar legal structures
        corp_types = [
            "C-Corp", 
            "S-Corp"
        ]
        
        owner_operated_types = [
            "LLC", 
            "Family-Owned Business", 
            "Partnership", 
            "Sole Proprietorship"
        ]
        
        # If both are corporation types, medium-high similarity
        if (company1.legal_structure.value in corp_types and 
            company2.legal_structure.value in corp_types):
            return 0.8
        
        # If both are owner-operated types, medium-high similarity
        if (company1.legal_structure.value in owner_operated_types and 
            company2.legal_structure.value in owner_operated_types):
            return 0.7
        
        # Default to low similarity for different structure types
        return 0.3
    
    def _score_growth_similarity(self, company1: Company, company2: Company) -> float:
        """Score growth similarity between two companies."""
        # If either company doesn't have financials, return medium similarity
        if not company1.financials or not company2.financials:
            return 0.5
        
        # If both have growth rate, compare directly
        if (company1.financials.growth_rate is not None and 
            company2.financials.growth_rate is not None):
            
            # Calculate difference in growth rates
            diff = abs(company1.financials.growth_rate - company2.financials.growth_rate)
            
            # Convert difference to similarity score (0-1)
            # Smaller difference = higher similarity
            if diff <= 2:
                return 1.0
            elif diff <= 5:
                return 0.8
            elif diff <= 10:
                return 0.6
            elif diff <= 20:
                return 0.4
            else:
                return 0.2
        
        # Default to medium similarity if growth rates not available
        return 0.5
    
    def _score_growth_rate(self, company: Company) -> float:
        """Score growth rate for tax-saving potential."""
        if not company.financials or company.financials.growth_rate is None:
            return 0.3  # Default medium-low score if no data
        
        growth_rate = company.financials.growth_rate
        
        # Growth Rate (15%+ YoY)
        if growth_rate >= 15:
            return 1.0
        elif growth_rate >= 10:
            return 0.8
        elif growth_rate >= 5:
            return 0.5
        else:
            return 0.2
    
    def _score_hiring_expansion(self, company: Company) -> float:
        """Score hiring and payroll expansion for tax-saving potential."""
        if not company.financials:
            return 0.3  # Default medium-low score if no data
        
        # Check payroll trends for expansion indicators
        if company.financials.payroll_trends:
            payroll_trends = company.financials.payroll_trends.lower()
            
            # Strong indicators of hiring expansion
            strong_indicators = [
                'significant hiring', 
                'major expansion', 
                'doubled workforce',
                'rapid growth in employees',
                'aggressive hiring'
            ]
            
            # Moderate indicators of hiring expansion
            moderate_indicators = [
                'hiring', 
                'expansion', 
                'growing team',
                'adding staff',
                'increasing workforce'
            ]
            
            if any(indicator in payroll_trends for indicator in strong_indicators):
                return 1.0
            elif any(indicator in payroll_trends for indicator in moderate_indicators):
                return 0.7
        
        # If employee count is available and high, assume some hiring
        if company.financials.employee_count and company.financials.employee_count > 50:
            return 0.5
        
        return 0.2  # Low score if no clear indicators
    
    def _score_equipment_upgrades(self, company: Company) -> float:
        """Score equipment and facility upgrades for tax-saving potential."""
        if not company.financials or not company.financials.capex_trends:
            return 0.3  # Default medium-low score if no data
        
        capex_trends = company.financials.capex_trends.lower()
        
        # Strong indicators of equipment/facility upgrades
        strong_indicators = [
            'major investment', 
            'new facility', 
            'significant upgrade',
            'automation investment',
            'new manufacturing line',
            'facility expansion'
        ]
        
        # Moderate indicators of equipment/facility upgrades
        moderate_indicators = [
            'equipment purchase', 
            'upgrade', 
            'renovation',
            'expansion',
            'new equipment',
            'technology investment'
        ]
        
        if any(indicator in capex_trends for indicator in strong_indicators):
            return 1.0
        elif any(indicator in capex_trends for indicator in moderate_indicators):
            return 0.7
        
        return 0.2  # Low score if no clear indicators
    
    def _score_succession_planning(self, company: Company) -> float:
        """Score succession and leadership transitions for tax-saving potential."""
        if not company.tax_indicators or not company.tax_indicators.succession_planning:
            return 0.2  # Default low score if no data
        
        succession_planning = company.tax_indicators.succession_planning.lower()
        
        # Strong indicators of succession planning
        strong_indicators = [
            'leadership transition', 
            'succession plan', 
            'ownership transfer',
            'generational change',
            'retirement planning',
            'family business transition'
        ]
        
        # Moderate indicators of succession planning
        moderate_indicators = [
            'new leadership', 
            'management change', 
            'executive transition',
            'restructuring',
            'ownership changes'
        ]
        
        if any(indicator in succession_planning for indicator in strong_indicators):
            return 1.0
        elif any(indicator in succession_planning for indicator in moderate_indicators):
            return 0.7
        
        return 0.3  # Medium-low score if no clear indicators
    
    def _score_government_contracts(self, company: Company) -> float:
        """Score government contracting opportunities for tax-saving potential."""
        if not company.tax_indicators or not company.tax_indicators.government_contracts:
            return 0.2  # Default low score if no data
        
        government_contracts = company.tax_indicators.government_contracts.lower()
        
        # Strong indicators of government contracts
        strong_indicators = [
            'major government contract', 
            'federal contract award', 
            'multi-year government project',
            'significant public sector work',
            'primary government contractor'
        ]
        
        # Moderate indicators of government contracts
        moderate_indicators = [
            'government work', 
            'public sector', 
            'state contract',
            'municipal project',
            'government bid'
        ]
        
        if any(indicator in government_contracts for indicator in strong_indicators):
            return 1.0
        elif any(indicator in government_contracts for indicator in moderate_indicators):
            return 0.7
        
        return 0.3  # Medium-low score if no clear indicators
