#!/usr/bin/env python3
"""
Test script to verify budget preference integration
"""

import requests
import json

def test_budget_integration():
    """Test budget preference integration with FastAPI backend"""
    
    base_url = "http://localhost:8000"
    
    # Test data for different budget preferences
    test_cases = [
        {
            "name": "Cheapest Plan",
            "payload": {
                "question": "Plan a 3-day trip to Paris",
                "budget_preference": "cheapest"
            }
        },
        {
            "name": "Budget Friendly Plan", 
            "payload": {
                "question": "Plan a 3-day trip to Paris",
                "budget_preference": "budget_friendly"
            }
        },
        {
            "name": "Luxurious Plan",
            "payload": {
                "question": "Plan a 3-day trip to Paris", 
                "budget_preference": "luxurious"
            }
        }
    ]
    
    print("🧪 Testing Budget Preference Integration...")
    print("=" * 60)
    
    for test_case in test_cases:
        print(f"\n🎯 Testing: {test_case['name']}")
        print(f"Budget Preference: {test_case['payload']['budget_preference']}")
        print("-" * 40)
        
        try:
            # Send request to FastAPI backend
            response = requests.post(f"{base_url}/query", json=test_case['payload'])
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("answer", "No answer returned")
                
                # Check if budget preference influenced the response
                budget_keywords = {
                    "cheapest": ["hostel", "budget", "cheap", "affordable", "free", "backpack"],
                    "budget_friendly": ["3-star", "moderate", "value", "mid-range"],
                    "luxurious": ["luxury", "premium", "4-star", "5-star", "high-end", "boutique"]
                }
                
                expected_keywords = budget_keywords[test_case['payload']['budget_preference']]
                found_keywords = [kw for kw in expected_keywords if kw.lower() in answer.lower()]
                
                print(f"✅ Request successful!")
                print(f"📊 Found budget-related keywords: {found_keywords}")
                print(f"📝 Response length: {len(answer)} characters")
                
                # Show first 200 characters of response
                preview = answer[:200] + "..." if len(answer) > 200 else answer
                print(f"🔍 Preview: {preview}")
                
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        print("\n")
    
    print("🏁 Budget Integration Testing Complete!")

if __name__ == "__main__":
    test_budget_integration()
