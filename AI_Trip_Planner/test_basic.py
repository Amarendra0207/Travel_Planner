#!/usr/bin/env python3
"""
Simple test script for distance calculation functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.airport_distance_calculator import AirportDistanceCalculator
from dotenv import load_dotenv

def test_basic_functionality():
    """Test basic functionality without API calls"""
    
    print("🧪 Testing Basic Distance Calculation Features")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Initialize calculator
    calc = AirportDistanceCalculator()
    
    # Test 1: Airport coordinates lookup (no API call needed)
    print("\n1️⃣ Testing Airport Coordinates Lookup:")
    coords = calc.get_airport_coordinates("DEL")
    print(f"📍 DEL (Delhi) Airport coordinates: {coords}")
    
    coords = calc.get_airport_coordinates("JFK")
    print(f"📍 JFK (New York) Airport coordinates: {coords}")
    
    coords = calc.get_airport_coordinates("LHR")
    print(f"📍 LHR (London) Airport coordinates: {coords}")
    
    # Test 2: Check MAP_KEY
    print(f"\n2️⃣ MAP_KEY Status:")
    map_key = os.getenv("MAP_KEY")
    if map_key:
        print(f"✅ MAP_KEY found: {map_key[:10]}...{map_key[-10:]}")
    else:
        print("❌ MAP_KEY not found in environment variables")
    
    # Test 3: Test one simple geocoding call
    print(f"\n3️⃣ Testing Simple Geocoding (with timeout):")
    try:
        import requests
        url = "https://api.openrouteservice.org/geocode/search"
        headers = {"Authorization": map_key}
        params = {"text": "New York", "size": 1}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"📡 API Response Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ OpenRouteService API is working")
        else:
            print(f"❌ API Error: {response.text}")
    except Exception as e:
        print(f"❌ API Connection Error: {e}")
    
    print("\n✅ Basic test completed!")

if __name__ == "__main__":
    test_basic_functionality()
