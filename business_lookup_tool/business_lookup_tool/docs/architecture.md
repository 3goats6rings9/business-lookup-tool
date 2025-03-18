# System Architecture - Business Lookup & Logistics Optimization Tool

## Overview

This document outlines the system architecture for the AI-powered business lookup and logistics optimization tool. The system is designed to find similar companies in the same industry and region, identify businesses in target industries, and optimize outreach logistics.

## Architecture Diagram

```
+---------------------+     +----------------------+     +---------------------+
|                     |     |                      |     |                     |
|  User Interface     |     |  Core Application    |     |  Data Sources       |
|  ---------------    |     |  ----------------    |     |  ---------------    |
|  - Web Dashboard    |<--->|  - Business Matcher  |<--->|  - LinkedIn API     |
|  - Input Forms      |     |  - Industry Finder   |     |  - Yahoo Finance    |
|  - Results Display  |     |  - Logistics Planner |     |  - Apollo.io        |
|  - CSV Export       |     |  - Scoring Engine    |     |  - Google Maps      |
|                     |     |                      |     |                     |
+---------------------+     +----------------------+     +---------------------+
                                      ^
                                      |
                                      v
+---------------------+     +----------------------+     +---------------------+
|                     |     |                      |     |                     |
|  Data Processing    |     |  Data Storage        |     |  Output Generation  |
|  ---------------    |     |  ----------------    |     |  ---------------    |
|  - Data Cleaning    |<--->|  - Company Database  |<--->|  - Dashboard        |
|  - Normalization    |     |  - Industry Codes    |     |  - CSV Reports      |
|  - Enrichment       |     |  - Location Data     |     |  - Email Delivery   |
|  - Classification   |     |  - Contact Info      |     |  - CRM Integration  |
|                     |     |                      |     |                     |
+---------------------+     +----------------------+     +---------------------+
```

## Component Descriptions

### 1. User Interface
- **Web Dashboard**: Main interface for users to interact with the system
- **Input Forms**: Forms for entering company name, location, and industry filters
- **Results Display**: Visual representation of matched companies and logistics plans
- **CSV Export**: Functionality to export results in CSV format

### 2. Core Application
- **Business Matcher**: Matches similar companies based on industry, size, and location
- **Industry Finder**: Identifies companies in target industries when no specific company is entered
- **Logistics Planner**: Optimizes outreach routes and schedules based on location
- **Scoring Engine**: Calculates tax-saving potential scores for companies

### 3. Data Sources
- **LinkedIn API**: Retrieves company and people data from LinkedIn
- **Yahoo Finance**: Obtains company profile information and financial data
- **Apollo.io**: Gathers business intelligence and contact information
- **Google Maps**: Provides location data and route optimization

### 4. Data Processing
- **Data Cleaning**: Removes duplicates and invalid data
- **Normalization**: Standardizes data formats across different sources
- **Enrichment**: Adds additional information from multiple sources
- **Classification**: Categorizes companies by industry, size, and potential

### 5. Data Storage
- **Company Database**: Stores company information and attributes
- **Industry Codes**: Maps NAICS and SIC codes to industry categories
- **Location Data**: Stores geographical information for routing
- **Contact Info**: Maintains contact details for decision-makers

### 6. Output Generation
- **Dashboard**: Generates interactive dashboard for data visualization
- **CSV Reports**: Creates CSV reports with company information
- **Email Delivery**: Sends reports via email at scheduled times
- **CRM Integration**: Integrates with CRM systems for lead management

## Data Flow

1. User inputs company name, location, and optional industry filter
2. System queries data sources to retrieve company information
3. Data processing components clean, normalize, and enrich the data
4. Business matcher identifies similar companies based on criteria
5. Logistics planner optimizes routes based on company locations
6. Scoring engine calculates tax-saving potential for each company
7. Results are stored in the database and presented to the user
8. User can export results or schedule automated delivery

## API Integration Strategy

### LinkedIn API
- **Purpose**: Retrieve company details, employee counts, and executive information
- **Endpoints**: 
  - `/get_company_details`: Get company profile information
  - `/get_user_profile_by_username`: Get executive profiles
  - `/search_people`: Search for company executives

### Yahoo Finance API
- **Purpose**: Obtain financial data and company profiles
- **Endpoints**:
  - `/get_stock_profile`: Get company profile information including industry classification

### Apollo.io API
- **Purpose**: Gather business intelligence and contact information
- **Endpoints**: To be determined based on Apollo.io API documentation

### Google Maps API
- **Purpose**: Provide location data and route optimization
- **Endpoints**: To be determined based on Google Maps API documentation

## Data Models

### Company Model
```
Company {
    id: string
    name: string
    description: string
    address: {
        street: string
        city: string
        state: string
        zip: string
    }
    legal_structure: string  // LLC, S-Corp, C-Corp, Family-Owned
    industry: {
        primary: string
        naics_code: string
        sic_code: string
    }
    executives: [
        {
            name: string
            role: string
            linkedin_url: string
            business_history: string
            contact: {
                phone: string
                email: string
            }
        }
    ]
    financials: {
        employee_count: number
        estimated_revenue: number
        growth_rate: number
        capex_trends: string
        payroll_trends: string
    }
    tax_indicators: {
        recent_developments: string
        grants_subsidies: string
        government_contracts: string
        succession_planning: string
        financing_activity: string
        tax_saving_potential: string  // High, Medium, Low
    }
    location: {
        latitude: number
        longitude: number
        region: string  // Based on location schedule
    }
}
```

### Industry Model
```
Industry {
    id: string
    name: string
    naics_codes: [string]
    sic_codes: [string]
    subcategories: [string]
    target_segments: [string]
}
```

### Location Schedule Model
```
LocationSchedule {
    day: string
    regions: [string]
    is_followup: boolean
}
```

### Route Model
```
Route {
    day: string
    companies: [CompanyReference]
    total_distance: number
    estimated_travel_time: number
    optimized_order: [number]  // Indices of companies in optimized order
}
```

## Database Schema

The system will use a combination of SQL and NoSQL approaches:

1. **SQL Database**: For structured data with relationships
   - Companies table
   - Industries table
   - Executives table
   - Locations table

2. **NoSQL Database**: For flexible, document-based storage
   - Company profiles with nested attributes
   - Route optimization results
   - Tax-saving potential assessments

## Security Considerations

1. **API Key Management**: Secure storage of API keys in environment variables
2. **Data Encryption**: Encryption of sensitive data at rest and in transit
3. **Access Control**: Role-based access control for different user types
4. **Audit Logging**: Logging of all data access and modifications

## Scalability Considerations

1. **Caching**: Implementation of caching for frequently accessed data
2. **Asynchronous Processing**: Use of asynchronous tasks for data retrieval and processing
3. **Horizontal Scaling**: Design to allow for horizontal scaling of components
4. **Rate Limiting**: Respect API rate limits and implement backoff strategies

## Next Steps

1. Implement data models and database schema
2. Set up API clients for data sources
3. Develop core business matching algorithm
4. Create industry-specific discovery features
5. Build logistics optimization module
6. Integrate components and create user interface
7. Test and deploy the solution
