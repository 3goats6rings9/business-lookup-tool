"""
Data normalization and cleaning module for the Business Lookup & Logistics Optimization Tool.
Provides functions for cleaning and normalizing data from various sources.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Union

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_company_name(name: str) -> str:
    """
    Clean and normalize company name.
    
    Args:
        name: Raw company name
        
    Returns:
        Cleaned company name
    """
    if not name:
        return ""
    
    # Remove common legal suffixes
    suffixes = [
        r'\bLLC\b', r'\bInc\.?\b', r'\bCorp\.?\b', r'\bLimited\b', 
        r'\bLtd\.?\b', r'\bL\.?P\.?\b', r'\bL\.?L\.?C\.?\b',
        r'\bP\.?C\.?\b', r'\bCo\.?\b'
    ]
    
    cleaned_name = name
    for suffix in suffixes:
        cleaned_name = re.sub(suffix, '', cleaned_name, flags=re.IGNORECASE)
    
    # Remove extra whitespace and punctuation
    cleaned_name = re.sub(r'\s+', ' ', cleaned_name)
    cleaned_name = cleaned_name.strip(' ,.-')
    
    return cleaned_name


def normalize_industry(industry: str) -> Dict[str, Any]:
    """
    Normalize industry name and map to standard categories.
    
    Args:
        industry: Raw industry name
        
    Returns:
        Dictionary with normalized industry information
    """
    if not industry:
        return {"primary": "", "category": "", "subcategory": ""}
    
    # Convert to lowercase for matching
    industry_lower = industry.lower()
    
    # Construction industry mapping
    construction_keywords = [
        'construction', 'contractor', 'builder', 'engineering', 
        'architect', 'hvac', 'electrical', 'plumbing', 'concrete',
        'framing', 'insulation', 'excavation', 'site prep',
        'modular', 'prefab', 'building materials', 'steel', 
        'lumber', 'glass', 'precast', 'fasteners', 'coatings'
    ]
    
    # Manufacturing industry mapping
    manufacturing_keywords = [
        'manufacturing', 'manufacturer', 'industrial', 'machinery',
        'automation', 'oem', 'supplier', 'component', 'fabricator',
        'fabrication', 'steel', 'plastic', 'composite', 'metal',
        'stamping', 'machining', 'aerospace', 'automotive',
        'equipment', 'robotics', 'cnc', 'injection molding',
        'food processing', 'packaging'
    ]
    
    # Trucking industry mapping
    trucking_keywords = [
        'trucking', 'logistics', 'freight', 'carrier', 'ltl', 'ftl',
        'last-mile', 'delivery', 'refrigerated', 'transport',
        'tanker', 'fleet', 'heavy equipment', 'warehousing',
        'distribution', 'supply chain', 'fleet maintenance',
        'intermodal', 'hazardous material'
    ]
    
    # Determine primary category
    if any(keyword in industry_lower for keyword in construction_keywords):
        category = "Construction"
        
        # Determine subcategory
        if any(kw in industry_lower for kw in ['general contractor', 'builder']):
            subcategory = "General Contractors"
        elif any(kw in industry_lower for kw in ['engineering', 'architect']):
            subcategory = "Engineering Firms"
        elif any(kw in industry_lower for kw in ['hvac', 'electrical', 'plumbing', 'concrete', 'framing', 'insulation']):
            subcategory = "Specialty Trade Contractors"
        elif any(kw in industry_lower for kw in ['excavation', 'site prep']):
            subcategory = "Excavation & Site Prep"
        elif any(kw in industry_lower for kw in ['modular', 'prefab']):
            subcategory = "Modular & Prefab Construction"
        elif any(kw in industry_lower for kw in ['building materials', 'steel', 'lumber', 'glass', 'precast', 'fasteners', 'coatings']):
            subcategory = "Building Materials Suppliers"
        else:
            subcategory = "Other Construction"
            
    elif any(keyword in industry_lower for keyword in manufacturing_keywords):
        category = "Manufacturing"
        
        # Determine subcategory
        if any(kw in industry_lower for kw in ['industrial machinery', 'automation']):
            subcategory = "Industrial Machinery & Automation"
        elif any(kw in industry_lower for kw in ['oem', 'supplier', 'component']):
            subcategory = "OEM Suppliers & Component Manufacturers"
        elif any(kw in industry_lower for kw in ['fabricator', 'fabrication', 'steel', 'plastic', 'composite', 'metal', 'stamping', 'machining']):
            subcategory = "Fabricators"
        elif any(kw in industry_lower for kw in ['aerospace', 'automotive', 'equipment']):
            subcategory = "Aerospace, Automotive & Heavy Equipment"
        elif any(kw in industry_lower for kw in ['robotics', 'cnc', 'automation']):
            subcategory = "Robotics & Automation"
        elif any(kw in industry_lower for kw in ['injection molding', 'composite']):
            subcategory = "Injection Molding & Composite Materials"
        elif any(kw in industry_lower for kw in ['food processing', 'packaging']):
            subcategory = "Food Processing & Packaging"
        else:
            subcategory = "Other Manufacturing"
            
    elif any(keyword in industry_lower for keyword in trucking_keywords):
        category = "Trucking & Logistics"
        
        # Determine subcategory
        if any(kw in industry_lower for kw in ['freight', 'carrier', 'ltl', 'ftl', 'last-mile', 'delivery']):
            subcategory = "Freight Carriers"
        elif any(kw in industry_lower for kw in ['refrigerated', 'tanker']):
            subcategory = "Refrigerated Transport & Tanker Fleets"
        elif any(kw in industry_lower for kw in ['heavy equipment']):
            subcategory = "Heavy Equipment Transporters"
        elif any(kw in industry_lower for kw in ['warehousing', 'distribution']):
            subcategory = "Warehousing & Distribution"
        elif any(kw in industry_lower for kw in ['logistics', 'supply chain']):
            subcategory = "Logistics Technology & Supply Chain"
        elif any(kw in industry_lower for kw in ['fleet maintenance']):
            subcategory = "Fleet Maintenance & Repair"
        elif any(kw in industry_lower for kw in ['intermodal', 'hazardous material']):
            subcategory = "Intermodal & Hazardous Material Haulers"
        else:
            subcategory = "Other Trucking & Logistics"
    else:
        category = "Other"
        subcategory = "Other"
    
    return {
        "primary": industry,
        "category": category,
        "subcategory": subcategory
    }


def normalize_employee_count(employee_count: Union[int, str, None]) -> Optional[int]:
    """
    Normalize employee count to an integer.
    
    Args:
        employee_count: Raw employee count (can be int, string, or range)
        
    Returns:
        Normalized employee count as integer
    """
    if employee_count is None:
        return None
    
    if isinstance(employee_count, int):
        return employee_count
    
    if isinstance(employee_count, str):
        # Handle ranges like "10-50"
        if '-' in employee_count:
            parts = employee_count.split('-')
            if len(parts) == 2:
                try:
                    lower = int(parts[0].strip())
                    upper = int(parts[1].strip())
                    return (lower + upper) // 2  # Return the average
                except ValueError:
                    pass
        
        # Handle "1,000+" format
        if '+' in employee_count:
            try:
                return int(employee_count.replace(',', '').replace('+', ''))
            except ValueError:
                pass
        
        # Handle simple numbers with commas
        try:
            return int(employee_count.replace(',', ''))
        except ValueError:
            pass
    
    logger.warning(f"Could not normalize employee count: {employee_count}")
    return None


def normalize_revenue(revenue: Union[float, str, None]) -> Optional[float]:
    """
    Normalize revenue to a float in dollars.
    
    Args:
        revenue: Raw revenue (can be float, string, or range)
        
    Returns:
        Normalized revenue as float
    """
    if revenue is None:
        return None
    
    if isinstance(revenue, (int, float)):
        return float(revenue)
    
    if isinstance(revenue, str):
        # Remove currency symbols and commas
        cleaned = revenue.replace('$', '').replace(',', '')
        
        # Handle ranges like "$1M-$5M"
        if '-' in cleaned:
            parts = cleaned.split('-')
            if len(parts) == 2:
                try:
                    lower = parse_revenue_with_suffix(parts[0].strip())
                    upper = parse_revenue_with_suffix(parts[1].strip())
                    if lower is not None and upper is not None:
                        return (lower + upper) / 2  # Return the average
                except ValueError:
                    pass
        
        # Handle single values with suffixes
        try:
            return parse_revenue_with_suffix(cleaned)
        except ValueError:
            pass
    
    logger.warning(f"Could not normalize revenue: {revenue}")
    return None


def parse_revenue_with_suffix(revenue_str: str) -> Optional[float]:
    """
    Parse revenue string with suffixes like K, M, B.
    
    Args:
        revenue_str: Revenue string with potential suffix
        
    Returns:
        Revenue as float
    """
    revenue_str = revenue_str.strip().upper()
    
    if revenue_str.endswith('K'):
        try:
            return float(revenue_str[:-1]) * 1000
        except ValueError:
            pass
    elif revenue_str.endswith('M'):
        try:
            return float(revenue_str[:-1]) * 1000000
        except ValueError:
            pass
    elif revenue_str.endswith('B'):
        try:
            return float(revenue_str[:-1]) * 1000000000
        except ValueError:
            pass
    else:
        try:
            return float(revenue_str)
        except ValueError:
            pass
    
    return None


def normalize_address(address: Dict[str, Any]) -> Dict[str, str]:
    """
    Normalize address components.
    
    Args:
        address: Dictionary with address components
        
    Returns:
        Normalized address dictionary
    """
    normalized = {}
    
    # Normalize street
    street = address.get('street') or address.get('address1') or address.get('street_address') or ''
    normalized['street'] = street.strip()
    
    # Normalize city
    city = address.get('city') or ''
    normalized['city'] = city.strip()
    
    # Normalize state
    state = address.get('state') or address.get('region') or ''
    # Convert state names to abbreviations if needed
    normalized['state'] = state.strip()
    
    # Normalize zip
    zip_code = address.get('zip') or address.get('postal_code') or address.get('zipcode') or ''
    # Format as 5-digit zip if possible
    if zip_code and len(zip_code) > 5 and '-' in zip_code:
        zip_code = zip_code.split('-')[0]
    normalized['zip'] = zip_code.strip()
    
    return normalized


def is_owner_operated(company_data: Dict[str, Any]) -> bool:
    """
    Determine if a company is likely owner-operated based on available data.
    
    Args:
        company_data: Dictionary with company information
        
    Returns:
        Boolean indicating if company is likely owner-operated
    """
    # Check employee count (owner-operated companies typically have fewer employees)
    employee_count = company_data.get('employee_count')
    if employee_count and isinstance(employee_count, (int, float)) and employee_count > 500:
        return False
    
    # Check executives for owner/founder titles
    executives = company_data.get('executives', [])
    for exec in executives:
        title = exec.get('role', '').lower()
        if any(term in title for term in ['owner', 'founder', 'president', 'ceo', 'principal']):
            return True
    
    # Check legal structure
    legal_structure = company_data.get('legal_structure', '')
    if isinstance(legal_structure, str) and any(term in legal_structure.lower() for term in ['llc', 'family', 'proprietor']):
        return True
    
    # Check company name for family indicators
    company_name = company_data.get('name', '').lower()
    if any(term in company_name for term in ['family', '& sons', '& son', 'brothers', '& co']):
        return True
    
    # Default to false if no clear indicators
    return False


def is_in_growth_mode(company_data: Dict[str, Any]) -> bool:
    """
    Determine if a company is likely in growth mode based on available data.
    
    Args:
        company_data: Dictionary with company information
        
    Returns:
        Boolean indicating if company is likely in growth mode
    """
    # Check growth rate
    growth_rate = company_data.get('growth_rate')
    if growth_rate and isinstance(growth_rate, (int, float)) and growth_rate >= 5:
        return True
    
    # Check for hiring indicators
    hiring_indicators = [
        'hiring', 'expanding', 'growth', 'new positions', 
        'job openings', 'career', 'join our team'
    ]
    
    description = company_data.get('description', '').lower()
    if any(indicator in description for indicator in hiring_indicators):
        return True
    
    # Check for expansion indicators in recent developments
    recent_dev = company_data.get('recent_developments', '').lower()
    expansion_indicators = [
        'expansion', 'new facility', 'new location', 'growing',
        'increased capacity', 'new equipment', 'investment'
    ]
    if recent_dev and any(indicator in recent_dev for indicator in expansion_indicators):
        return True
    
    # Check for financing activity
    financing = company_data.get('financing_activity', '').lower()
    if financing and any(term in financing for term in ['funding', 'investment', 'capital', 'loan', 'financing']):
        return True
    
    # Default to false if no clear indicators
    return False
