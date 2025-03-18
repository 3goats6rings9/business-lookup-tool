"""
Logistics optimization module for the Business Lookup & Logistics Optimization Tool.
Implements features for regional clustering, route optimization, and scheduling.
"""

import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import folium
from geopy.distance import geodesic
from sklearn.cluster import DBSCAN

from src.models import Company, Route, CompanyReference, LocationSchedule
from src.config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LogisticsOptimizer:
    """Class for logistics optimization and route planning."""
    
    def __init__(self):
        """Initialize the logistics optimizer."""
        self.location_schedule = Config.get_location_schedule()
    
    def cluster_companies_by_region(self, companies: List[Company]) -> Dict[str, List[Company]]:
        """
        Cluster companies by region based on location.
        
        Args:
            companies: List of companies to cluster
            
        Returns:
            Dictionary mapping regions to lists of companies
        """
        logger.info(f"Clustering {len(companies)} companies by region")
        
        # Filter companies with valid location data
        companies_with_location = [c for c in companies if c.location and c.location.latitude and c.location.longitude]
        
        if not companies_with_location:
            logger.warning("No companies with valid location data for clustering")
            return {}
        
        # Extract coordinates for clustering
        coordinates = np.array([[c.location.latitude, c.location.longitude] for c in companies_with_location])
        
        # Perform DBSCAN clustering
        # eps is the maximum distance between two samples to be considered in the same cluster (in degrees)
        # min_samples is the minimum number of samples in a cluster
        clustering = DBSCAN(eps=0.05, min_samples=2).fit(coordinates)
        
        # Get cluster labels for each company
        labels = clustering.labels_
        
        # Group companies by cluster
        clusters = {}
        for i, label in enumerate(labels):
            if label == -1:
                # -1 means noise (not part of any cluster)
                region = "Other"
            else:
                region = f"Cluster_{label}"
            
            if region not in clusters:
                clusters[region] = []
            
            clusters[region].append(companies_with_location[i])
        
        return clusters
    
    def assign_companies_to_days(self, companies: List[Company]) -> Dict[str, List[Company]]:
        """
        Assign companies to specific days based on location schedule.
        
        Args:
            companies: List of companies to assign
            
        Returns:
            Dictionary mapping days to lists of companies
        """
        logger.info(f"Assigning {len(companies)} companies to days based on location schedule")
        
        # Initialize days
        days = {day: [] for day in self.location_schedule.keys()}
        
        for company in companies:
            if not company.address or not company.address.city:
                continue
            
            assigned = False
            company_city = company.address.city.lower()
            
            # Check each day's regions
            for day, regions in self.location_schedule.items():
                if isinstance(regions, list):
                    for region in regions:
                        region_lower = region.lower()
                        if region_lower in company_city or company_city in region_lower:
                            days[day].append(company)
                            assigned = True
                            break
                
                if assigned:
                    break
            
            # If not assigned to any specific day, add to Thursday (follow-up day)
            if not assigned:
                days["Thursday"].append(company)
        
        return days
    
    def optimize_route(self, companies: List[Company], start_location: str) -> Route:
        """
        Optimize route for visiting companies.
        
        Args:
            companies: List of companies to visit
            start_location: Starting location address
            
        Returns:
            Optimized route
        """
        logger.info(f"Optimizing route for {len(companies)} companies from {start_location}")
        
        if not companies:
            return Route(day="", companies=[], total_distance=0, estimated_travel_time=0)
        
        # Determine day based on first company's location
        day = "Monday"  # Default
        if companies[0].location and companies[0].location.region:
            day = companies[0].location.region
        
        # Create route
        route = Route(day=day)
        
        # Add companies to route
        for company in companies:
            route.add_company(company)
        
        # If no companies with valid addresses, return empty route
        if not route.companies:
            return route
        
        # Calculate distances between all points
        distances = self._calculate_distance_matrix(route.companies, start_location)
        
        # Solve TSP (Traveling Salesman Problem) using a greedy approach
        optimized_order = self._solve_tsp_greedy(distances)
        route.optimized_order = optimized_order
        
        # Calculate total distance and estimated travel time
        total_distance = 0
        for i in range(len(optimized_order) - 1):
            from_idx = optimized_order[i]
            to_idx = optimized_order[i + 1]
            total_distance += distances[from_idx][to_idx]
        
        route.total_distance = total_distance
        
        # Estimate travel time (assuming average speed of 30 mph)
        route.estimated_travel_time = total_distance / 30  # in hours
        
        return route
    
    def _calculate_distance_matrix(self, companies: List[CompanyReference], start_location: str) -> List[List[float]]:
        """
        Calculate distance matrix between all companies.
        
        Args:
            companies: List of company references
            start_location: Starting location address
            
        Returns:
            Distance matrix
        """
        # Add start location to the list of addresses
        addresses = [start_location] + [company.address for company in companies]
        n = len(addresses)
        
        # Initialize distance matrix
        distances = [[0 for _ in range(n)] for _ in range(n)]
        
        # Calculate distances between all pairs of addresses
        for i in range(n):
            for j in range(i + 1, n):
                # In a real implementation, this would use Google Maps Distance Matrix API
                # For now, we'll use a placeholder distance calculation
                distance = self._calculate_distance(addresses[i], addresses[j])
                distances[i][j] = distance
                distances[j][i] = distance  # Distance matrix is symmetric
        
        return distances
    
    def _calculate_distance(self, address1: str, address2: str) -> float:
        """
        Calculate distance between two addresses.
        
        Args:
            address1: First address
            address2: Second address
            
        Returns:
            Distance in miles
        """
        # In a real implementation, this would use geocoding and geodesic distance
        # For now, we'll return a placeholder distance
        return 10.0  # miles
    
    def _solve_tsp_greedy(self, distances: List[List[float]]) -> List[int]:
        """
        Solve Traveling Salesman Problem using a greedy approach.
        
        Args:
            distances: Distance matrix
            
        Returns:
            Optimized order of indices
        """
        n = len(distances)
        
        # Start from the first location (index 0)
        current = 0
        unvisited = set(range(1, n))
        tour = [current]
        
        # Greedy algorithm: always visit the closest unvisited location
        while unvisited:
            closest = min(unvisited, key=lambda x: distances[current][x])
            tour.append(closest)
            unvisited.remove(closest)
            current = closest
        
        # Return to the starting point
        tour.append(0)
        
        return tour
    
    def generate_weekly_schedule(self, companies: List[Company]) -> Dict[str, Route]:
        """
        Generate a weekly schedule for visiting companies.
        
        Args:
            companies: List of companies to schedule
            
        Returns:
            Dictionary mapping days to routes
        """
        logger.info(f"Generating weekly schedule for {len(companies)} companies")
        
        # Assign companies to days based on location schedule
        companies_by_day = self.assign_companies_to_days(companies)
        
        # Optimize route for each day
        routes = {}
        for day, day_companies in companies_by_day.items():
            if day_companies:
                # Use a central location as the starting point for each day
                if day == "Monday":
                    start_location = "Waukesha, WI"
                elif day == "Tuesday":
                    start_location = "Kenosha, WI"
                elif day == "Wednesday":
                    start_location = "Madison, WI"
                else:
                    start_location = "Milwaukee, WI"
                
                routes[day] = self.optimize_route(day_companies, start_location)
            else:
                routes[day] = Route(day=day)
        
        return routes
    
    def generate_route_map(self, route: Route, start_location: str, output_path: str) -> str:
        """
        Generate an interactive map for a route.
        
        Args:
            route: Route to visualize
            start_location: Starting location address
            output_path: Path to save the map HTML file
            
        Returns:
            Path to the generated map file
        """
        logger.info(f"Generating route map for {len(route.companies)} companies")
        
        # Create a map centered at the starting location
        # In a real implementation, this would use geocoding to get coordinates
        # For now, we'll use placeholder coordinates for Milwaukee
        map_center = [43.0389, -87.9065]  # Milwaukee coordinates
        route_map = folium.Map(location=map_center, zoom_start=10)
        
        # Add starting location marker
        folium.Marker(
            location=map_center,
            popup="Start: " + start_location,
            icon=folium.Icon(color="green", icon="play")
        ).add_to(route_map)
        
        # Add company markers in optimized order
        for i, idx in enumerate(route.optimized_order[1:-1], 1):  # Skip start/end
            company = route.companies[idx - 1]  # Adjust index (first is start location)
            
            # In a real implementation, this would use geocoding to get coordinates
            # For now, we'll use placeholder coordinates with small offsets
            lat = map_center[0] + (i * 0.01)
            lng = map_center[1] + (i * 0.01)
            
            folium.Marker(
                location=[lat, lng],
                popup=f"{i}. {company.name}",
                icon=folium.Icon(color="blue")
            ).add_to(route_map)
        
        # Add lines connecting the points in order
        points = [map_center]  # Start with starting location
        for idx in route.optimized_order[1:-1]:
            company = route.companies[idx - 1]
            # Use placeholder coordinates with offsets
            i = route.optimized_order.index(idx)
            lat = map_center[0] + (i * 0.01)
            lng = map_center[1] + (i * 0.01)
            points.append([lat, lng])
        points.append(map_center)  # End at starting location
        
        folium.PolyLine(
            points,
            color="blue",
            weight=2.5,
            opacity=1
        ).add_to(route_map)
        
        # Add route information
        route_info = f"""
        <h3>Route Information</h3>
        <p>Day: {route.day}</p>
        <p>Companies: {len(route.companies)}</p>
        <p>Total Distance: {route.total_distance:.1f} miles</p>
        <p>Estimated Travel Time: {route.estimated_travel_time:.1f} hours</p>
        """
        
        folium.Marker(
            location=[map_center[0] - 0.03, map_center[1] - 0.03],
            popup=folium.Popup(route_info, max_width=300),
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(route_map)
        
        # Save the map
        route_map.save(output_path)
        
        return output_path
    
    def suggest_best_outreach_days(self, companies: List[Company], historical_data: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """
        Suggest best days for outreach based on historical response rates.
        
        Args:
            companies: List of companies for outreach
            historical_data: Optional historical response rates by day
            
        Returns:
            Dictionary mapping days to suggested outreach priority scores
        """
        logger.info(f"Suggesting best outreach days for {len(companies)} companies")
        
        # If historical data is provided, use it
        if historical_data:
            return historical_data
        
        # Otherwise, use default response rates
        # These would typically be based on actual historical data
        default_rates = {
            "Monday": 0.7,    # Good day, people are fresh
            "Tuesday": 0.9,   # Best day, people are settled in but not yet mid-week
            "Wednesday": 0.8, # Good day, mid-week productivity
            "Thursday": 0.7,  # Decent day, but people may be looking toward weekend
            "Friday": 0.5     # Worst day, people are focused on finishing for the weekend
        }
        
        return default_rates
