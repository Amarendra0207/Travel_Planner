import os
import requests
from airportsdata import load as load_airports
from typing import Tuple, Optional, Dict, List
from dotenv import load_dotenv

class AirportDistanceCalculator:
    """Utility class for calculating distances from airports to various locations"""
    
    def __init__(self):
        load_dotenv()
        self.openroute_api_key = os.environ.get("MAP_KEY")
        self.airports_data = load_airports('IATA')
    
    def get_airport_coordinates(self, airport_code: str) -> Optional[Tuple[float, float]]:
        """Get latitude and longitude for an airport given its IATA code"""
        try:
            if airport_code.upper() in self.airports_data:
                airport_info = self.airports_data[airport_code.upper()]
                lat = airport_info.get('lat')
                lon = airport_info.get('lon')
                if lat and lon:
                    return (float(lat), float(lon))
            return None
        except Exception as e:
            print(f"Error getting airport coordinates for {airport_code}: {e}")
            return None
    
    def get_coordinates_from_address(self, address: str) -> Optional[Tuple[float, float]]:
        """Get coordinates from address using OpenRouteService Geocoding API"""
        try:
            url = "https://api.openrouteservice.org/geocode/search"
            headers = {"Authorization": self.openroute_api_key}
            
            # Improve address specificity
            enhanced_address = address
            if "Times Square" in address and "New York" in address:
                enhanced_address = "Times Square, Manhattan, New York City, NY, USA"
            elif "city center" in address.lower():
                city = address.split("city center")[0].strip()
                enhanced_address = f"downtown {city}, {city}"
                
            params = {
                "text": enhanced_address, 
                "size": 1,
                "boundary.country": "US" if "USA" in enhanced_address or any(state in enhanced_address.upper() for state in ["NY", "CA", "FL", "TX"]) else None
            }
            
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            
            response = requests.get(url, headers=headers, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get('features'):
                    coords = data['features'][0]['geometry']['coordinates']
                    return (float(coords[1]), float(coords[0]))  # Return as (lat, lon)
            return None
        except Exception as e:
            print(f"Error getting coordinates for {address}: {e}")
            return None
    
    def calculate_driving_distance(self, start_coords: Tuple[float, float], end_coords: Tuple[float, float]) -> Optional[float]:
        """Calculate driving distance in kilometers between two coordinate points"""
        try:
            url = "https://api.openrouteservice.org/v2/directions/driving-car"
            headers = {"Authorization": self.openroute_api_key}
            body = {
                "coordinates": [
                    [start_coords[1], start_coords[0]],  # [lon, lat]
                    [end_coords[1], end_coords[0]]
                ],
                "radiuses": [1000, 1000]  # Allow up to 1km radius to find routable points
            }
            response = requests.post(url, json=body, headers=headers, timeout=20)
            if response.status_code == 200:
                data = response.json()
                # distance in meters, convert to kilometers
                distance_km = data['features'][0]['properties']['segments'][0]['distance'] / 1000
                return round(distance_km, 2)
            elif response.status_code == 404:
                # Try with larger radius if 404 (routable point not found)
                body["radiuses"] = [5000, 5000]  # 5km radius
                response = requests.post(url, json=body, headers=headers, timeout=20)
                if response.status_code == 200:
                    data = response.json()
                    distance_km = data['features'][0]['properties']['segments'][0]['distance'] / 1000
                    return round(distance_km, 2)
                else:
                    # Fall back to straight-line distance calculation
                    return self._calculate_haversine_distance(start_coords, end_coords)
            return None
        except Exception as e:
            print(f"Error calculating distance: {e}")
            # Fall back to straight-line distance
            return self._calculate_haversine_distance(start_coords, end_coords)
    
    def _calculate_haversine_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """Calculate straight-line distance using Haversine formula as fallback"""
        import math
        
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in kilometers
        r = 6371
        
        distance = r * c
        return round(distance * 1.2, 2)  # Add 20% to approximate road distance
    
    def get_airport_to_attraction_distance(self, airport_code: str, attraction_address: str) -> Dict[str, any]:
        """
        Get comprehensive distance information from airport to attraction
        
        Returns:
            dict: Contains distance, travel time, airport info, and status
        """
        result = {
            "success": False,
            "airport_code": airport_code,
            "attraction": attraction_address,
            "distance_km": None,
            "travel_time": None,
            "airport_name": None,
            "error": None
        }
        
        # Get airport coordinates and info
        airport_coords = self.get_airport_coordinates(airport_code)
        if not airport_coords:
            result["error"] = f"Could not find airport with code {airport_code}"
            return result
        
        airport_info = self.airports_data.get(airport_code.upper(), {})
        result["airport_name"] = airport_info.get('name', airport_code)
        
        # Get attraction coordinates
        attraction_coords = self.get_coordinates_from_address(attraction_address)
        if not attraction_coords:
            result["error"] = f"Could not find coordinates for {attraction_address}"
            return result
        
        # Calculate distance
        distance = self.calculate_driving_distance(airport_coords, attraction_coords)
        if distance is not None:
            result["success"] = True
            result["distance_km"] = distance
            
            # Calculate travel time (assuming average speed of 50 km/h for city driving)
            travel_time_hours = distance / 50
            hours = int(travel_time_hours)
            minutes = int((travel_time_hours - hours) * 60)
            result["travel_time"] = f"{hours}h {minutes}m"
            
        else:
            result["error"] = "Could not calculate distance"
        
        return result
    
    def find_nearest_airports_to_city(self, city_name: str, limit: int = 3) -> List[Dict[str, any]]:
        """
        Find the nearest airports to a given city
        
        Args:
            city_name: Name of the city
            limit: Maximum number of airports to return
            
        Returns:
            List of airport information dictionaries
        """
        city_coords = self.get_coordinates_from_address(city_name)
        if not city_coords:
            return []
        
        airport_distances = []
        
        # Check a broader range of airports
        for airport_code, airport_info in self.airports_data.items():
            airport_coords = self.get_airport_coordinates(airport_code)
            if airport_coords:
                distance = self.calculate_driving_distance(city_coords, airport_coords)
                if distance and distance <= 200:  # Only consider airports within 200km
                    airport_distances.append({
                        "code": airport_code,
                        "name": airport_info.get('name', airport_code),
                        "city": airport_info.get('city', ''),
                        "country": airport_info.get('country', ''),
                        "distance_km": distance
                    })
        
        # Sort by distance and return top results
        airport_distances.sort(key=lambda x: x['distance_km'])
        return airport_distances[:limit]
    
    def format_distance_info(self, distance_data: Dict[str, any]) -> str:
        """Format distance information for display in travel reports"""
        if not distance_data["success"]:
            return f"Error: {distance_data['error']}"
        
        return (f"Distance from {distance_data['airport_name']} ({distance_data['airport_code']}) "
                f"to {distance_data['attraction']}: {distance_data['distance_km']} km "
                f"(approximately {distance_data['travel_time']} by car)")
