#!/usr/bin/env python3
"""
Test the complete API with distance information
"""

import requests
import json

def test_api_with_distance():
    """Test the API with distance information"""
    
    print("🧪 Testing Complete API with Distance Information")
    print("=" * 60)
    
    # Test request
    url = "http://127.0.0.1:8001/query"
    
    payload = {
        "query": "Plan a 2-day trip to New York City",
        "startLocationCode": "JFK",
        "endLocationCode": "JFK",
        "startCity": "New York",
        "endCity": "New York"
    }
    
    print(f"\n📤 Sending request:")
    print(f"   URL: {url}")
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=120)  # 2 minute timeout
        
        print(f"\n📥 Response:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "")
            print(f"   Content Length: {len(answer)} characters")
            
            # Check if distance information is included
            distance_keywords = ["distance", "km", "airport", "📍", "✈️"]
            found_keywords = [kw for kw in distance_keywords if kw.lower() in answer.lower()]
            
            print(f"\n🔍 Distance Information Check:")
            print(f"   Found keywords: {found_keywords}")
            
            if found_keywords:
                print("   ✅ Distance information appears to be included!")
            else:
                print("   ❌ Distance information may be missing")
            
            # Show first 500 characters of response
            print(f"\n📄 First 500 characters of response:")
            print("   " + "="*50)
            print("   " + answer[:500].replace('\n', '\n   '))
            if len(answer) > 500:
                print("   ... (truncated)")
            print("   " + "="*50)
            
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   Exception: {e}")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_api_with_distance()
