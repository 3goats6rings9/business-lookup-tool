from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, template_folder='../templates', static_folder='../static')

@app.route('/')
def index():
    """Render the main page of the application."""
    return render_template('index.html')

@app.route('/company-lookup')
def company_lookup():
    """Render the company lookup page."""
    return render_template('company_lookup.html')

@app.route('/industry-discovery')
def industry_discovery():
    """Render the industry discovery page."""
    return render_template('industry_discovery.html')

@app.route('/logistics-optimization')
def logistics_optimization():
    """Render the logistics optimization page."""
    return render_template('logistics_optimization.html')

@app.route('/api/health')
def health_check():
    """API endpoint to check if the service is running."""
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
