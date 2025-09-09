#!/usr/bin/env python3
"""
Debug API responses
"""

import sys
import os
import requests
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

def debug_api():
    """Debug API responses"""
    
    print("🔍 Debugging API Responses")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    map_key = os.getenv("MAP_KEY")
    
    # Test geocoding with more specific address
    print("\n1️⃣ Testing Geocoding API...")
    url = "https://api.openrouteservice.org/geocode/search"
    headers = {"Authorization": map_key}
    params = {"text": "Times Square, Manhattan, New York City, NY, USA", "size": 1}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('features'):
                coords = data['features'][0]['geometry']['coordinates']
                print(f"   Coordinates: {coords[1]}, {coords[0]} (lat, lon)")
                print(f"   Full Address: {data['features'][0]['properties'].get('label', 'N/A')}")
            else:
                print("   No features found")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test directions API with known coordinates
    print("\n2️⃣ Testing Directions API...")
    jfk_coords = (40.63993, -73.77869)  # JFK
    nyc_coords = (40.7589, -73.9851)    # Times Square NYC (known coordinates)
    
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {"Authorization": map_key}
    body = {
        "coordinates": [
            [jfk_coords[1], jfk_coords[0]],  # [lon, lat] for JFK
            [nyc_coords[1], nyc_coords[0]]   # [lon, lat] for Times Square
        ]
    }
    
    try:
        response = requests.post(url, json=body, headers=headers, timeout=20)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            distance_m = data['features'][0]['properties']['segments'][0]['distance']
            distance_km = distance_m / 1000
            print(f"   Distance: {distance_km:.2f} km")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    print("\n✅ Debug completed!")

if __name__ == "__main__":
    debug_api()
