"""
Web interface module for the Business Lookup & Logistics Optimization Tool.
Implements a Flask web application for user interaction.
"""

import os
import json
from typing import Dict, Any, List, Optional
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

from src.app import BusinessLookupApp
from src.models import SearchCriteria, TaxSavingPotential

# Initialize Flask app
app = Flask(__name__, 
            static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'),
            template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'))
CORS(app)

# Initialize business lookup application
business_app = BusinessLookupApp()

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/api/lookup', methods=['POST'])
def lookup_company():
    """API endpoint for looking up a company."""
    data = request.json
    company_name = data.get('company_name')
    location = data.get('location')
    
    if not company_name:
        return jsonify({'error': 'Company name is required'}), 400
    
    try:
        company = business_app.lookup_company(company_name, location)
        
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Convert company object to JSON-serializable dict
        company_dict = {
            'id': company.id,
            'name': company.name,
            'description': company.description,
            'website': company.website,
            'legal_structure': company.legal_structure.value if company.legal_structure else None,
            'address': {
                'street': company.address.street,
                'city': company.address.city,
                'state': company.address.state,
                'zip': company.address.zip
            } if company.address else None,
            'industry': {
                'primary': company.industry.primary,
                'naics_code': company.industry.naics_code,
                'sic_code': company.industry.sic_code
            } if company.industry else None,
            'executives': [
                {
                    'name': exec.name,
                    'role': exec.role,
                    'contact': {
                        'phone': exec.contact.phone,
                        'email': exec.contact.email,
                        'linkedin_url': exec.contact.linkedin_url
                    } if exec.contact else None
                } for exec in company.executives
            ],
            'financials': {
                'employee_count': company.financials.employee_count,
                'estimated_revenue': company.financials.estimated_revenue,
                'growth_rate': company.financials.growth_rate
            } if company.financials else None,
            'tax_indicators': {
                'tax_saving_potential': company.tax_indicators.tax_saving_potential.value if company.tax_indicators and company.tax_indicators.tax_saving_potential else None
            } if company.tax_indicators else None
        }
        
        return jsonify({'company': company_dict})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/similar', methods=['POST'])
def find_similar_companies():
    """API endpoint for finding similar companies."""
    data = request.json
    company_id = data.get('company_id')
    location = data.get('location')
    limit = int(data.get('limit', 10))
    
    if not company_id:
        return jsonify({'error': 'Company ID is required'}), 400
    
    try:
        # Get the reference company
        company = business_app.db_manager.get_company(company_id)
        
        if not company:
            return jsonify({'error': 'Reference company not found'}), 404
        
        # Find similar companies
        similar_companies = business_app.find_similar_companies(company, location, limit)
        
        # Convert results to JSON-serializable format
        results = []
        for similar_company, score in similar_companies:
            company_dict = {
                'id': similar_company.id,
                'name': similar_company.name,
                'description': similar_company.description,
                'industry': similar_company.industry.primary if similar_company.industry else None,
                'address': f"{similar_company.address.city}, {similar_company.address.state}" if similar_company.address else None,
                'employee_count': similar_company.financials.employee_count if similar_company.financials else None,
                'similarity_score': score
            }
            results.append(company_dict)
        
        return jsonify({'similar_companies': results})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/discover', methods=['POST'])
def discover_companies():
    """API endpoint for discovering companies by industry."""
    data = request.json
    industry = data.get('industry')
    location = data.get('location')
    min_employees = int(data.get('min_employees', 10))
    owner_operated = data.get('owner_operated', True)
    growth_mode = data.get('growth_mode', True)
    limit = int(data.get('limit', 20))
    
    if not industry:
        return jsonify({'error': 'Industry is required'}), 400
    
    try:
        # Discover companies
        companies = business_app.discover_companies_by_industry(
            industry, location, min_employees, owner_operated, growth_mode, limit
        )
        
        # Convert results to JSON-serializable format
        results = []
        for company in companies:
            company_dict = {
                'id': company.id,
                'name': company.name,
                'description': company.description,
                'industry': company.industry.primary if company.industry else None,
                'address': f"{company.address.city}, {company.address.state}" if company.address else None,
                'employee_count': company.financials.employee_count if company.financials else None,
                'tax_saving_potential': company.tax_indicators.tax_saving_potential.value if company.tax_indicators and company.tax_indicators.tax_saving_potential else None
            }
            results.append(company_dict)
        
        return jsonify({'companies': results})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logistics', methods=['POST'])
def optimize_logistics():
    """API endpoint for optimizing logistics."""
    data = request.json
    company_ids = data.get('company_ids', [])
    
    if not company_ids:
        return jsonify({'error': 'At least one company ID is required'}), 400
    
    try:
        # Get companies
        companies = []
        for company_id in company_ids:
            company = business_app.db_manager.get_company(company_id)
            if company:
                companies.append(company)
        
        if not companies:
            return jsonify({'error': 'No valid companies found'}), 404
        
        # Optimize logistics
        logistics_results = business_app.optimize_logistics(companies)
        
        # Convert results to JSON-serializable format
        schedule_dict = {}
        for day, route in logistics_results['schedule'].items():
            schedule_dict[day] = {
                'companies': [
                    {
                        'id': company_ref.company_id,
                        'name': company_ref.name,
                        'address': company_ref.address
                    } for company_ref in route.companies
                ],
                'total_distance': route.total_distance,
                'estimated_travel_time': route.estimated_travel_time,
                'optimized_order': route.optimized_order
            }
        
        best_days_dict = {day: score for day, score in logistics_results['best_days'].items()}
        
        maps_dict = {day: os.path.basename(map_path) for day, map_path in logistics_results['maps'].items()}
        
        return jsonify({
            'schedule': schedule_dict,
            'best_days': best_days_dict,
            'maps': maps_dict
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export', methods=['POST'])
def export_companies():
    """API endpoint for exporting companies to CSV."""
    data = request.json
    company_ids = data.get('company_ids', [])
    
    if not company_ids:
        return jsonify({'error': 'At least one company ID is required'}), 400
    
    try:
        # Get companies
        companies = []
        for company_id in company_ids:
            company = business_app.db_manager.get_company(company_id)
            if company:
                companies.append(company)
        
        if not companies:
            return jsonify({'error': 'No valid companies found'}), 404
        
        # Export to CSV
        output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'export.csv')
        csv_path = business_app.export_companies_to_csv(companies, output_path)
        
        return jsonify({'csv_path': os.path.basename(csv_path)})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/data/<path:filename>')
def get_data_file(filename):
    """Serve data files."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    return send_from_directory(data_dir, filename)

def run_app(host='0.0.0.0', port=5000, debug=True):
    """Run the Flask application."""
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_app()
