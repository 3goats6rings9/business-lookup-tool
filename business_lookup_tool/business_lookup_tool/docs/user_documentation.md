# Business Lookup & Logistics Optimization Tool - User Documentation

## Overview

The Business Lookup & Logistics Optimization Tool is a comprehensive system designed to help tax advisory professionals identify and target owner-operated B2B companies in construction, manufacturing, and trucking industries. The tool provides capabilities for:

1. Finding similar companies in the same industry and region
2. Identifying businesses in target industries
3. Optimizing outreach logistics and travel planning

This documentation provides instructions for installation, configuration, and usage of the tool.

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Features](#features)
   - [Company Lookup](#company-lookup)
   - [Industry Discovery](#industry-discovery)
   - [Logistics Optimization](#logistics-optimization)
4. [API Reference](#api-reference)
5. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Internet connection for API access

### Steps

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/business-lookup-tool.git
   cd business-lookup-tool
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file in the root directory
   - Add your API keys (see [Configuration](#configuration))

4. Run the application:
   ```
   python run.py
   ```

5. Access the web interface:
   - Open a browser and navigate to `http://localhost:5000`

## Configuration

The tool requires API keys for various data sources. Create a `.env` file in the root directory with the following variables:

```
APOLLO_API_KEY=your_apollo_api_key
VECTORSHIFT_API_KEY=your_vectorshift_api_key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
LINKEDIN_API_KEY=your_linkedin_api_key
```

### Location Schedule Configuration

The default location schedule is:
- Monday: Waukesha to West Milwaukee to Jackson, including West Bend
- Tuesday: Kenosha/Racine
- Wednesday: West of Waukesha to Madison
- Thursday & Friday: Follow-up days

To customize this schedule, modify the `location_schedule` in `src/config.py`.

## Features

### Company Lookup

The Company Lookup feature allows you to search for a specific company by name and location, and find similar companies in the same industry and region.

#### How to Use:

1. Navigate to the "Company Lookup" tab
2. Enter a company name (required)
3. Enter a location (optional, improves accuracy)
4. Click "Search"
5. View company details and tax-saving potential
6. Explore similar companies in the results section
7. Add companies to the logistics optimization by clicking "Add to Logistics"

#### Example:

Input:
- Company Name: XYZ Steel Fabrication
- Location: Milwaukee

Output:
- Company details (industry, size, revenue, etc.)
- Tax-saving potential score
- List of similar steel fabrication companies in the Milwaukee area

### Industry Discovery

The Industry Discovery feature allows you to find companies in specific target industries based on various criteria.

#### How to Use:

1. Navigate to the "Industry Discovery" tab
2. Select an industry (Construction, Manufacturing, or Trucking)
3. Enter a location (optional)
4. Set minimum employee count (default: 10)
5. Select business type filters (Owner-Operated, Growth Mode)
6. Click "Discover"
7. View discovered companies in the results section
8. Export results to CSV by clicking "Export to CSV"
9. Add companies to logistics optimization by clicking "Add to Logistics"

#### Example:

Input:
- Industry: Manufacturing
- Location: Milwaukee
- Min. Employees: 10
- Owner-Operated: Yes
- Growth Mode: Yes

Output:
- List of manufacturing companies in Milwaukee
- Each company includes details and tax-saving potential
- Option to export results to CSV

### Logistics Optimization

The Logistics Optimization feature helps plan efficient routes for visiting selected companies based on your location schedule.

#### How to Use:

1. Select companies from Company Lookup or Industry Discovery
2. Navigate to the "Logistics Optimization" tab
3. Click "Optimize Logistics"
4. View the weekly schedule organized by day
5. Explore route maps for each day
6. Check best outreach days based on response rates

#### Example:

Input:
- Selected companies from previous searches

Output:
- Weekly schedule with companies grouped by day
- Optimized route for each day
- Total distance and estimated travel time
- Interactive maps showing the route
- Chart showing best days for outreach

## API Reference

The tool provides several API endpoints for programmatic access:

### `/api/lookup` (POST)

Look up a company by name and location.

Parameters:
- `company_name` (required): Name of the company
- `location` (optional): Location of the company

### `/api/similar` (POST)

Find companies similar to a reference company.

Parameters:
- `company_id` (required): ID of the reference company
- `location` (optional): Location to search in
- `limit` (optional): Maximum number of results (default: 10)

### `/api/discover` (POST)

Discover companies in a specific industry.

Parameters:
- `industry` (required): Industry to search for
- `location` (optional): Location to search in
- `min_employees` (optional): Minimum number of employees (default: 10)
- `owner_operated` (optional): Whether to target owner-operated businesses (default: true)
- `growth_mode` (optional): Whether to target businesses in growth mode (default: true)
- `limit` (optional): Maximum number of results (default: 20)

### `/api/logistics` (POST)

Optimize logistics for visiting selected companies.

Parameters:
- `company_ids` (required): Array of company IDs to include in the optimization

### `/api/export` (POST)

Export selected companies to CSV.

Parameters:
- `company_ids` (required): Array of company IDs to export

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Verify your API keys in the `.env` file
   - Check your internet connection
   - Ensure you haven't exceeded API rate limits

2. **No Results Found**
   - Try broadening your search criteria
   - Check for typos in company names or locations
   - Try a different industry or location

3. **Application Won't Start**
   - Verify all dependencies are installed
   - Check for error messages in the console
   - Ensure the required ports are available

### Getting Help

If you encounter issues not covered in this documentation, please:
1. Check the logs in `business_lookup_tool.log`
2. Contact support at support@example.com
3. Submit an issue on the GitHub repository

---

© 2025 Business Lookup & Logistics Optimization Tool
