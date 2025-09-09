import os
from typing import List
from langchain.tools import tool
from dotenv import load_dotenv
import requests
from airportsdata import load as load_airports

class DistanceCalculatorTool:
    def __init__(self):
        load_dotenv()
        self.openroute_api_key = os.environ.get("MAP_KEY")
        self.airports_data = load_airports('IATA')
        self.distance_tool_list = self._setup_tools()

    def _get_coordinates_from_address(self, address: str) -> tuple:
        """Get coordinates from address using OpenRouteService Geocoding API"""
        try:
            url = "https://api.openrouteservice.org/geocode/search"
            headers = {"Authorization": self.openroute_api_key}
            params = {"text": address, "size": 1}
            
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get('features'):
                    coords = data['features'][0]['geometry']['coordinates']
                    return (coords[1], coords[0])  # Return as (lat, lon)
            return None
        except Exception as e:
            print(f"Error getting coordinates for {address}: {e}")
            return None

    def _get_airport_coordinates(self, airport_code: str) -> tuple:
        """Get airport coordinates from IATA code"""
        try:
            if airport_code in self.airports_data:
                airport_info = self.airports_data[airport_code]
                lat = airport_info.get('lat')
                lon = airport_info.get('lon')
                if lat and lon:
                    return (lat, lon)
            return None
        except Exception as e:
            print(f"Error getting airport coordinates for {airport_code}: {e}")
            return None

    def _calculate_driving_distance(self, start_coords: tuple, end_coords: tuple) -> float:
        """Calculate driving distance using OpenRouteService"""
        try:
            url = "https://api.openrouteservice.org/v2/directions/driving-car"
            headers = {"Authorization": self.openroute_api_key}
            body = {
                "coordinates": [
                    [start_coords[1], start_coords[0]],  # [lon, lat]
                    [end_coords[1], end_coords[0]]
                ]
            }
            response = requests.post(url, json=body, headers=headers)
            if response.status_code == 200:
                data = response.json()
                # distance in meters, convert to kilometers
                distance_km = data['features'][0]['properties']['segments'][0]['distance'] / 1000
                return round(distance_km, 2)
            return None
        except Exception as e:
            print(f"Error calculating distance: {e}")
            return None

    def _setup_tools(self) -> List:
        """Setup all tools for distance calculation"""
        
        @tool
        def calculate_airport_to_attraction_distance(airport_code: str, attraction_address: str) -> str:
            """
            Calculate driving distance from airport to attraction/place.
            
            Args:
                airport_code (str): IATA airport code (e.g., 'JFK', 'LHR', 'DEL')
                attraction_address (str): Address or name of the attraction/place
            
            Returns:
                str: Distance information with travel details
            """
            # Get airport coordinates
            airport_coords = self._get_airport_coordinates(airport_code)
            if not airport_coords:
                return f"Could not find coordinates for airport {airport_code}"
            
            # Get attraction coordinates
            attraction_coords = self._get_coordinates_from_address(attraction_address)
            if not attraction_coords:
                return f"Could not find coordinates for {attraction_address}"
            
            # Calculate distance
            distance = self._calculate_driving_distance(airport_coords, attraction_coords)
            if distance is not None:
                # Estimate travel time (assuming average speed of 50 km/h)
                travel_time_hours = distance / 50
                hours = int(travel_time_hours)
                minutes = int((travel_time_hours - hours) * 60)
                
                airport_name = self.airports_data.get(airport_code, {}).get('name', airport_code)
                
                return (f"Distance from {airport_name} ({airport_code}) to {attraction_address}: "
                       f"{distance} km (approximately {hours}h {minutes}m by car)")
            else:
                return f"Could not calculate distance from {airport_code} to {attraction_address}"

        @tool
        def calculate_distance_between_places(place1: str, place2: str) -> str:
            """
            Calculate driving distance between two places/addresses.
            
            Args:
                place1 (str): First place/address
                place2 (str): Second place/address
            
            Returns:
                str: Distance information between the two places
            """
            # Get coordinates for both places
            coords1 = self._get_coordinates_from_address(place1)
            coords2 = self._get_coordinates_from_address(place2)
            
            if not coords1:
                return f"Could not find coordinates for {place1}"
            if not coords2:
                return f"Could not find coordinates for {place2}"
            
            # Calculate distance
            distance = self._calculate_driving_distance(coords1, coords2)
            if distance is not None:
                # Estimate travel time
                travel_time_hours = distance / 50
                hours = int(travel_time_hours)
                minutes = int((travel_time_hours - hours) * 60)
                
                return (f"Distance from {place1} to {place2}: "
                       f"{distance} km (approximately {hours}h {minutes}m by car)")
            else:
                return f"Could not calculate distance between {place1} and {place2}"

        @tool 
        def find_nearest_airport_to_city(city_name: str) -> str:
            """
            Find the nearest airport to a given city.
            
            Args:
                city_name (str): Name of the city
            
            Returns:
                str: Information about the nearest airport
            """
            city_coords = self._get_coordinates_from_address(city_name)
            if not city_coords:
                return f"Could not find coordinates for {city_name}"
            
            nearest_airport = None
            min_distance = float('inf')
            
            # Check major airports (limit search for performance)
            major_airports = ['JFK', 'LHR', 'CDG', 'DXB', 'NRT', 'LAX', 'ORD', 'DEL', 'BOM', 'SIN']
            
            for airport_code in major_airports:
                airport_coords = self._get_airport_coordinates(airport_code)
                if airport_coords:
                    distance = self._calculate_driving_distance(city_coords, airport_coords)
                    if distance and distance < min_distance:
                        min_distance = distance
                        nearest_airport = airport_code
            
            if nearest_airport:
                airport_name = self.airports_data.get(nearest_airport, {}).get('name', nearest_airport)
                return f"Nearest major airport to {city_name}: {airport_name} ({nearest_airport}) - {min_distance} km away"
            else:
                return f"Could not find nearest airport to {city_name}"

        return [calculate_airport_to_attraction_distance, calculate_distance_between_places, find_nearest_airport_to_city]
