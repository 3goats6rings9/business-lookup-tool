"""
Database module for the Business Lookup & Logistics Optimization Tool.
Provides functionality for storing and retrieving company data.
"""

import os
import json
import csv
import sqlite3
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from src.models import Company, Address, Industry, Executive, Contact, Financials, TaxIndicators, GeoLocation, LegalStructure, TaxSavingPotential

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database file path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'companies.db')


class DatabaseManager:
    """Database manager for storing and retrieving company data."""
    
    def __init__(self, db_path: str = DB_PATH):
        """Initialize the database manager."""
        self.db_path = db_path
        self._create_tables_if_not_exist()
    
    def _create_tables_if_not_exist(self):
        """Create database tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Companies table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            website TEXT,
            legal_structure TEXT,
            last_updated TEXT
        )
        ''')
        
        # Addresses table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS addresses (
            company_id TEXT PRIMARY KEY,
            street TEXT,
            city TEXT,
            state TEXT,
            zip TEXT,
            country TEXT,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
        ''')
        
        # Industries table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS industries (
            company_id TEXT PRIMARY KEY,
            primary_industry TEXT,
            naics_code TEXT,
            sic_code TEXT,
            subcategories TEXT,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
        ''')
        
        # Executives table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS executives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id TEXT,
            name TEXT,
            role TEXT,
            business_history TEXT,
            tenure TEXT,
            phone TEXT,
            email TEXT,
            linkedin_url TEXT,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
        ''')
        
        # Financials table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS financials (
            company_id TEXT PRIMARY KEY,
            employee_count INTEGER,
            estimated_revenue REAL,
            growth_rate REAL,
            capex_trends TEXT,
            payroll_trends TEXT,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
        ''')
        
        # Tax indicators table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tax_indicators (
            company_id TEXT PRIMARY KEY,
            recent_developments TEXT,
            grants_subsidies TEXT,
            government_contracts TEXT,
            succession_planning TEXT,
            financing_activity TEXT,
            tax_saving_potential TEXT,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
        ''')
        
        # Locations table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            company_id TEXT PRIMARY KEY,
            latitude REAL,
            longitude REAL,
            region TEXT,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_company(self, company: Company) -> bool:
        """
        Save a company to the database.
        
        Args:
            company: Company object to save
            
        Returns:
            Boolean indicating success
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Save company basic info
            cursor.execute('''
            INSERT OR REPLACE INTO companies (id, name, description, website, legal_structure, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                company.id,
                company.name,
                company.description,
                company.website,
                company.legal_structure.value if company.legal_structure else None,
                datetime.now().isoformat()
            ))
            
            # Save address if available
            if company.address:
                cursor.execute('''
                INSERT OR REPLACE INTO addresses (company_id, street, city, state, zip, country)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    company.id,
                    company.address.street,
                    company.address.city,
                    company.address.state,
                    company.address.zip,
                    company.address.country
                ))
            
            # Save industry if available
            if company.industry:
                cursor.execute('''
                INSERT OR REPLACE INTO industries (company_id, primary_industry, naics_code, sic_code, subcategories)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    company.id,
                    company.industry.primary,
                    company.industry.naics_code,
                    company.industry.sic_code,
                    json.dumps(company.industry.subcategories)
                ))
            
            # Save executives if available
            if company.executives:
                # First delete existing executives for this company
                cursor.execute('DELETE FROM executives WHERE company_id = ?', (company.id,))
                
                # Then insert new executives
                for executive in company.executives:
                    cursor.execute('''
                    INSERT INTO executives (company_id, name, role, business_history, tenure, phone, email, linkedin_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        company.id,
                        executive.name,
                        executive.role,
                        executive.business_history,
                        executive.tenure,
                        executive.contact.phone if executive.contact else None,
                        executive.contact.email if executive.contact else None,
                        executive.contact.linkedin_url if executive.contact else None
                    ))
            
            # Save financials if available
            if company.financials:
                cursor.execute('''
                INSERT OR REPLACE INTO financials (company_id, employee_count, estimated_revenue, growth_rate, capex_trends, payroll_trends)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    company.id,
                    company.financials.employee_count,
                    company.financials.estimated_revenue,
                    company.financials.growth_rate,
                    company.financials.capex_trends,
                    company.financials.payroll_trends
                ))
            
            # Save tax indicators if available
            if company.tax_indicators:
                cursor.execute('''
                INSERT OR REPLACE INTO tax_indicators (company_id, recent_developments, grants_subsidies, government_contracts, succession_planning, financing_activity, tax_saving_potential)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    company.id,
                    company.tax_indicators.recent_developments,
                    company.tax_indicators.grants_subsidies,
                    company.tax_indicators.government_contracts,
                    company.tax_indicators.succession_planning,
                    company.tax_indicators.financing_activity,
                    company.tax_indicators.tax_saving_potential.value if company.tax_indicators.tax_saving_potential else None
                ))
            
            # Save location if available
            if company.location:
                cursor.execute('''
                INSERT OR REPLACE INTO locations (company_id, latitude, longitude, region)
                VALUES (?, ?, ?, ?)
                ''', (
                    company.id,
                    company.location.latitude,
                    company.location.longitude,
                    company.location.region
                ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error saving company to database: {e}")
            return False
    
    def get_company(self, company_id: str) -> Optional[Company]:
        """
        Get a company from the database by ID.
        
        Args:
            company_id: ID of the company to retrieve
            
        Returns:
            Company object if found, None otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get company basic info
            cursor.execute('SELECT * FROM companies WHERE id = ?', (company_id,))
            company_row = cursor.fetchone()
            
            if not company_row:
                return None
            
            # Create company object
            company = Company(
                id=company_row['id'],
                name=company_row['name'],
                description=company_row['description'],
                website=company_row['website'],
                legal_structure=LegalStructure(company_row['legal_structure']) if company_row['legal_structure'] else None
            )
            
            # Get address
            cursor.execute('SELECT * FROM addresses WHERE company_id = ?', (company_id,))
            address_row = cursor.fetchone()
            if address_row:
                company.address = Address(
                    street=address_row['street'],
                    city=address_row['city'],
                    state=address_row['state'],
                    zip=address_row['zip'],
                    country=address_row['country']
                )
            
            # Get industry
            cursor.execute('SELECT * FROM industries WHERE company_id = ?', (company_id,))
            industry_row = cursor.fetchone()
            if industry_row:
                company.industry = Industry(
                    primary=industry_row['primary_industry'],
                    naics_code=industry_row['naics_code'],
                    sic_code=industry_row['sic_code'],
                    subcategories=json.loads(industry_row['subcategories']) if industry_row['subcategories'] else []
                )
            
            # Get executives
            cursor.execute('SELECT * FROM executives WHERE company_id = ?', (company_id,))
            executive_rows = cursor.fetchall()
            for row in executive_rows:
                executive = Executive(
                    name=row['name'],
                    role=row['role'],
                    business_history=row['business_history'],
                    tenure=row['tenure'],
                    contact=Contact(
                        phone=row['phone'],
                        email=row['email'],
                        linkedin_url=row['linkedin_url']
                    )
                )
                company.executives.append(executive)
            
            # Get financials
            cursor.execute('SELECT * FROM financials WHERE company_id = ?', (company_id,))
            financials_row = cursor.fetchone()
            if financials_row:
                company.financials = Financials(
                    employee_count=financials_row['employee_count'],
                    estimated_revenue=financials_row['estimated_revenue'],
                    growth_rate=financials_row['growth_rate'],
                    capex_trends=financials_row['capex_trends'],
                    payroll_trends=financials_row['payroll_trends']
                )
            
            # Get tax indicators
            cursor.execute('SELECT * FROM tax_indicators WHERE company_id = ?', (company_id,))
            tax_row = cursor.fetchone()
            if tax_row:
                company.tax_indicators = TaxIndicators(
                    recent_developments=tax_row['recent_developments'],
                    grants_subsidies=tax_row['grants_subsidies'],
                    government_contracts=tax_row['government_contracts'],
                    succession_planning=tax_row['succession_planning'],
                    financing_activity=tax_row['financing_activity'],
                    tax_saving_potential=TaxSavingPotential(tax_row['tax_saving_potential']) if tax_row['tax_saving_potential'] else TaxSavingPotential.LOW
                )
            
            # Get location
            cursor.execute('SELECT * FROM locations WHERE company_id = ?', (company_id,))
            location_row = cursor.fetchone()
            if location_row:
                company.location = GeoLocation(
                    latitude=location_row['latitude'],
                    longitude=location_row['longitude'],
                    region=location_row['region']
                )
            
            conn.close()
            return company
        except Exception as e:
            logger.error(f"Error retrieving company from database: {e}")
            return None
    
    def search_companies(self, criteria: Dict[str, Any] = None, limit: int = 100) -> List[Company]:
        """
        Search for companies in the database.
        
        Args:
            criteria: Dictionary of search criteria
            limit: Maximum number of results to return
            
        Returns:
            List of Company objects matching the criteria
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = '''
            SELECT c.id FROM companies c
            LEFT JOIN addresses a ON c.id = a.company_id
            LEFT JOIN industries i ON c.id = i.company_id
            LEFT JOIN financials f ON c.id = f.company_id
            LEFT JOIN tax_indicators t ON c.id = t.company_id
            WHERE 1=1
            '''
            
            params = []
            
            if criteria:
                if 'name' in criteria and criteria['name']:
                    query += ' AND c.name LIKE ?'
                    params.append(f'%{criteria["name"]}%')
                
                if 'industry' in criteria and criteria['industry']:
                    query += ' AND i.primary_industry LIKE ?'
                    params.append(f'%{criteria["industry"]}%')
                
                if 'location' in criteria and criteria['location']:
                    query += ' AND (a.city LIKE ? OR a.state LIKE ? OR a.zip LIKE ?)'
                    params.extend([f'%{criteria["location"]}%', f'%{criteria["location"]}%', f'%{criteria["location"]}%'])
                
                if 'min_employees' in criteria and criteria['min_employees']:
                    query += ' AND f.employee_count >= ?'
                    params.append(criteria['min_employees'])
                
                if 'min_revenue' in criteria and criteria['min_revenue']:
                    query += ' AND f.estimated_revenue >= ?'
                    params.append(criteria['min_revenue'])
                
                if 'tax_potential' in criteria and criteria['tax_potential']:
                    query += ' AND t.tax_saving_potential = ?'
                    params.append(criteria['tax_potential'])
            
            query += ' ORDER BY c.name LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            companies = []
            for row in rows:
                company = self.get_company(row['id'])
                if company:
                    companies.append(company)
            
            conn.close()
            return companies
        except Exception as e:
            logger.error(f"Error searching companies in database: {e}")
            return []
    
    def export_to_csv(self, companies: List[Company], output_path: str) -> bool:
        """
        Export companies to a CSV file.
        
        Args:
            companies: List of Company objects to export
            output_path: Path to the output CSV file
            
        Returns:
            Boolean indicating success
        """
        try:
            with open(output_path, 'w', newline='') as csvfile:
                fieldnames = [
                    'Company Name', 'Business Description', 'Address', 'Legal Structure',
                    'Owner/Key Executive', 'Role', 'Contact Info', 'LinkedIn',
                    'Employee Count', 'Estimated Revenue', 'Growth Rate',
                    'Recent Developments', 'Tax Saving Potential'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for company in companies:
                    # Get primary executive
                    executive = company.executives[0] if company.executives else None
                    
                    # Format address
                    address = ""
                    if company.address:
                        address = f"{company.address.street}, {company.address.city}, {company.address.state} {company.address.zip}"
                    
                    # Format contact info
                    contact_info = ""
                    if executive and executive.contact:
                        if executive.contact.phone:
                            contact_info += f"Phone: {executive.contact.phone}"
                        if executive.contact.email:
                            if contact_info:
                                contact_info += ", "
                            contact_info += f"Email: {executive.contact.email}"
                    
                    writer.writerow({
                        'Company Name': company.name,
                        'Business Description': company.description or "",
                        'Address': address,
                        'Legal Structure': company.legal_structure.value if company.legal_structure else "",
                        'Owner/Key Executive': executive.name if executive else "",
                        'Role': executive.role if executive else "",
                        'Contact Info': contact_info,
                        'LinkedIn': executive.contact.linkedin_url if executive and executive.contact else "",
                        'Employee Count': company.financials.employee_count if company.financials else "",
                        'Estimated Revenue': f"${company.financials.estimated_revenue:,.2f}" if company.financials and company.financials.estimated_revenue else "",
                        'Growth Rate': f"{company.financials.growth_rate}%" if company.financials and company.financials.growth_rate else "",
                        'Recent Developments': company.tax_indicators.recent_developments if company.tax_indicators else "",
                        'Tax Saving Potential': company.tax_indicators.tax_saving_potential.value if company.tax_indicators and company.tax_indicators.tax_saving_potential else "Low"
                    })
            
            return True
        except Exception as e:
            logger.error(f"Error exporting companies to CSV: {e}")
            return False
