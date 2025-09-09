#!/usr/bin/env python3
"""
Test script for distance calculation functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.airport_distance_calculator import AirportDistanceCalculator
from dotenv import load_dotenv

def test_distance_calculations():
    """Test the distance calculation features"""
    
    print("🧪 Testing Distance Calculation Features")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Initialize calculator
    calc = AirportDistanceCalculator()
    
    # Test 1: Airport to city center distance
    print("\n1️⃣ Testing Airport to City Center Distance:")
    distance_info = calc.get_airport_to_attraction_distance("DEL", "India Gate, New Delhi")
    print(calc.format_distance_info(distance_info))
    
    # Test 2: Find nearest airports to a city
    print("\n2️⃣ Testing Nearest Airports to City:")
    airports = calc.find_nearest_airports_to_city("London", limit=3)
    for airport in airports:
        print(f"✈️ {airport['name']} ({airport['code']}) - {airport['distance_km']} km")
    
    # Test 3: Airport coordinates
    print("\n3️⃣ Testing Airport Coordinates:")
    coords = calc.get_airport_coordinates("JFK")
    print(f"📍 JFK Airport coordinates: {coords}")
    
    # Test 4: Address to coordinates
    print("\n4️⃣ Testing Address to Coordinates:")
    coords = calc.get_coordinates_from_address("Times Square, New York")
    print(f"📍 Times Square coordinates: {coords}")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_distance_calculations()
