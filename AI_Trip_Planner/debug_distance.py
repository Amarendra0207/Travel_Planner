#!/usr/bin/env python3
"""
Debug distance calculation step by step
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.airport_distance_calculator import AirportDistanceCalculator
from dotenv import load_dotenv

def debug_distance():
    """Debug distance calculation step by step"""
    
    print("🔍 Debugging Distance Calculation")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Initialize calculator
    calc = AirportDistanceCalculator()
    
    # Step 1: Get JFK coordinates
    print("\n1️⃣ Getting JFK coordinates...")
    jfk_coords = calc.get_airport_coordinates("JFK")
    print(f"   JFK coordinates: {jfk_coords}")
    
    # Step 2: Get Times Square coordinates
    print("\n2️⃣ Getting Times Square coordinates...")
    ts_coords = calc.get_coordinates_from_address("Times Square, New York")
    print(f"   Times Square coordinates: {ts_coords}")
    
    # Step 3: Calculate distance if both coordinates are available
    if jfk_coords and ts_coords:
        print("\n3️⃣ Calculating distance...")
        distance = calc.calculate_driving_distance(jfk_coords, ts_coords)
        print(f"   Distance: {distance} km")
    else:
        print("\n❌ Cannot calculate distance - missing coordinates")
    
    print("\n✅ Debug completed!")

if __name__ == "__main__":
    debug_distance()
