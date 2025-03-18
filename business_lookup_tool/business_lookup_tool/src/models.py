"""
Data models for the Business Lookup & Logistics Optimization Tool.
Defines the structure of data objects used throughout the application.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union
from enum import Enum
from datetime import datetime


class LegalStructure(Enum):
    """Enum representing different legal structures of companies."""
    LLC = "LLC"
    S_CORP = "S-Corp"
    C_CORP = "C-Corp"
    FAMILY_OWNED = "Family-Owned Business"
    PARTNERSHIP = "Partnership"
    SOLE_PROPRIETORSHIP = "Sole Proprietorship"
    OTHER = "Other"


class TaxSavingPotential(Enum):
    """Enum representing tax saving potential levels."""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class Address:
    """Address information for a company."""
    street: str
    city: str
    state: str
    zip: str
    country: str = "USA"


@dataclass
class Industry:
    """Industry classification for a company."""
    primary: str
    naics_code: Optional[str] = None
    sic_code: Optional[str] = None
    subcategories: List[str] = field(default_factory=list)


@dataclass
class Contact:
    """Contact information for an executive."""
    phone: Optional[str] = None
    email: Optional[str] = None
    linkedin_url: Optional[str] = None


@dataclass
class Executive:
    """Information about a company executive."""
    name: str
    role: str
    contact: Contact = field(default_factory=Contact)
    business_history: Optional[str] = None
    tenure: Optional[str] = None


@dataclass
class Financials:
    """Financial information about a company."""
    employee_count: Optional[int] = None
    estimated_revenue: Optional[float] = None
    growth_rate: Optional[float] = None
    capex_trends: Optional[str] = None
    payroll_trends: Optional[str] = None


@dataclass
class TaxIndicators:
    """Tax-related indicators for a company."""
    recent_developments: Optional[str] = None
    grants_subsidies: Optional[str] = None
    government_contracts: Optional[str] = None
    succession_planning: Optional[str] = None
    financing_activity: Optional[str] = None
    tax_saving_potential: TaxSavingPotential = TaxSavingPotential.LOW


@dataclass
class GeoLocation:
    """Geographical location information."""
    latitude: float
    longitude: float
    region: Optional[str] = None


@dataclass
class Company:
    """Main company data model."""
    id: str
    name: str
    description: Optional[str] = None
    address: Optional[Address] = None
    legal_structure: Optional[LegalStructure] = None
    industry: Optional[Industry] = None
    executives: List[Executive] = field(default_factory=list)
    financials: Financials = field(default_factory=Financials)
    tax_indicators: TaxIndicators = field(default_factory=TaxIndicators)
    location: Optional[GeoLocation] = None
    website: Optional[str] = None
    last_updated: datetime = field(default_factory=datetime.now)
    
    def calculate_tax_saving_potential(self) -> TaxSavingPotential:
        """Calculate tax saving potential based on company attributes."""
        score = 0
        
        # Growth rate (15%+ YoY)
        if self.financials.growth_rate and self.financials.growth_rate >= 15:
            score += 3
        elif self.financials.growth_rate and self.financials.growth_rate >= 10:
            score += 2
        elif self.financials.growth_rate and self.financials.growth_rate >= 5:
            score += 1
        
        # Hiring & Payroll Expansion
        if self.financials.payroll_trends and "expansion" in self.financials.payroll_trends.lower():
            score += 2
        
        # Equipment & Facility Upgrades
        if self.financials.capex_trends and any(term in self.financials.capex_trends.lower() 
                                               for term in ["equipment", "facility", "upgrade", "expansion"]):
            score += 2
        
        # Succession & Leadership Transitions
        if self.tax_indicators.succession_planning and self.tax_indicators.succession_planning.strip():
            score += 2
        
        # Government Contracting Opportunities
        if self.tax_indicators.government_contracts and self.tax_indicators.government_contracts.strip():
            score += 1
        
        # Determine potential based on score
        if score >= 6:
            return TaxSavingPotential.HIGH
        elif score >= 3:
            return TaxSavingPotential.MEDIUM
        else:
            return TaxSavingPotential.LOW


@dataclass
class IndustryCategory:
    """Industry category with related codes and segments."""
    id: str
    name: str
    naics_codes: List[str] = field(default_factory=list)
    sic_codes: List[str] = field(default_factory=list)
    subcategories: List[str] = field(default_factory=list)
    target_segments: List[str] = field(default_factory=list)


@dataclass
class LocationSchedule:
    """Schedule for location-based outreach."""
    day: str
    regions: List[str] = field(default_factory=list)
    is_followup: bool = False


@dataclass
class CompanyReference:
    """Reference to a company for use in routes."""
    company_id: str
    name: str
    address: str
    priority: int = 0


@dataclass
class Route:
    """Optimized route for company outreach."""
    day: str
    companies: List[CompanyReference] = field(default_factory=list)
    total_distance: float = 0.0
    estimated_travel_time: float = 0.0
    optimized_order: List[int] = field(default_factory=list)
    
    def add_company(self, company: Company, priority: int = 0) -> None:
        """Add a company to the route."""
        if not company.address:
            return
            
        address_str = f"{company.address.street}, {company.address.city}, {company.address.state} {company.address.zip}"
        company_ref = CompanyReference(
            company_id=company.id,
            name=company.name,
            address=address_str,
            priority=priority
        )
        self.companies.append(company_ref)
        # Reset optimization when companies change
        self.optimized_order = list(range(len(self.companies)))


@dataclass
class SearchCriteria:
    """Search criteria for finding companies."""
    company_name: Optional[str] = None
    location: Optional[str] = None
    industry: Optional[str] = None
    min_employees: int = 10
    min_revenue: float = 2000000
    owner_operated: bool = True
    growth_mode: bool = False
