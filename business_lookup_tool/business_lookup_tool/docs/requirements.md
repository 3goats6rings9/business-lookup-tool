# Business Lookup & Logistics Optimization Tool Requirements

## Overview
This document outlines the requirements for an AI-powered business lookup and logistics optimization tool designed for targeted tax advisory lead generation. The system will enable users to input a company name and find similar companies in the same industry and region, identify businesses in target industries, and optimize outreach and logistics.

## Core Functionality

### 1. Input Section
- Company Name: Allow users to enter a business name
- Location: Allow users to input a city, state, or zip code
- Industry Filter (Optional): Enable selection from predefined industries (construction, manufacturing, steel, trucking, etc.)

### 2. Business Matching & Similar Companies
- API Lookup: Pull data from databases (Google Places API, Apollo.io, LinkedIn, Yahoo Finance)
- Find Similar Businesses: Based on industry classification (NAICS codes, SIC codes)
- Filter by Size & Revenue: Match ideal prospects ($2M+ revenue, owner-operated)

### 3. Industry-Specific Company Discovery
- Find companies in target industries (fabrication, trucking, etc.) when no specific company is entered
- Sort by size, revenue, and owner structure
- Focus on owner-operated B2B companies with 10+ employees in growth mode

### 4. Logistics & Route Optimization
- Cluster companies by region for efficient scheduling
- Suggest best outreach days based on prior response rates
- Integrate with Google Maps API for optimized appointment routes
- Support specific location schedule:
  - Monday: Waukesha to West Milwaukee to Jackson, including West Bend
  - Tuesday: Kenosha/Racine
  - Wednesday: West of Waukesha to Madison
  - Thursday & Friday: Follow-up days

## Target Industries & Business Segments

### Construction Industry
- General contractors
- Engineering firms (civil, structural, mechanical, electrical)
- Specialty trade contractors (HVAC, electrical, plumbing, concrete, framing, insulation)
- Excavation & site prep companies
- Modular & prefab construction
- Building materials suppliers (steel, lumber, glass, precast concrete, fasteners, coatings)

### Manufacturing Industry
- Industrial machinery & automation manufacturers
- OEM suppliers & component manufacturers
- Fabricators (steel, plastics, composites, metal stamping, precision machining)
- Aerospace, automotive, and heavy equipment suppliers
- Robotics, CNC machining, & automation technology manufacturers
- Injection molding & composite materials producers
- Food processing & packaging equipment manufacturers

### Trucking & Logistics Industry
- Freight carriers (LTL, FTL, last-mile delivery)
- Refrigerated transport & tanker fleets
- Heavy equipment transporters
- Warehousing & distribution centers
- Logistics technology & supply chain optimization firms
- Fleet maintenance & repair companies
- Intermodal & hazardous material haulers

## Required Data for Each Company

### Basic Company Information
1. Company Name
2. Business Description (Industry, core operations, specialization)
3. Company Address
4. Legal Structure (LLC, S-Corp, C-Corp, Family-Owned Business)

### Key Decision-Maker Details
5. Owner or Key Executive (Name, role, LinkedIn)
6. Owner's Business History (Prior companies owned, tenure at the company)
7. Contact Information (Phone, email)

### Company Financials & Growth Data
8. Employee Count & Estimated Revenue
9. Growth Rate (YoY revenue or employee growth trends)
10. Capital Expenditure (CapEx) Trends (Investments in equipment, facilities, automation)
11. Payroll Trends (Hiring increases or major workforce expansions)

### Indicators of Tax-Saving Potential
12. Recent Business Developments (expansion, new equipment purchases, leadership changes)
13. State or Federal Grants/Subsidies (Energy efficiency, infrastructure funding, R&D credits)
14. Government Contracts or Large Bids Won
15. Mergers, Acquisitions, or Succession Planning Needs
16. Debt & Financing Activity (Recent private equity, SBA loans, or growth financing rounds)

### Tax-Saving Potential Score
17. Score each company as High, Medium, or Low based on:
   - Growth Rate (15%+ YoY)
   - Hiring & Payroll Expansion
   - Equipment & Facility Upgrades
   - Succession & Leadership Transitions
   - Government Contracting Opportunities

## Output Format & Automation
- Generate a dashboard displaying all identified companies with structured data
- Provide a CSV file with at least 15-20 companies daily, ranked by tax-saving potential
- Deliver results via email or integrate into a CRM at 8:30 AM

## API Integration
- LinkedIn API for company and people data
- Yahoo Finance API for company profiles
- Google Maps API for location data and route optimization
- Apollo.io for business intelligence (API key provided: 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)
- VectorShift for AI integration (API key provided: sk_wEIuJDRtx8zuV38I3gqdkYNgBsDaL5GY7eTwynqU8rH4kPxo)
