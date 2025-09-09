#!/usr/bin/env python3
"""
Test Word document export functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.word_document_exporter import WordDocumentExporter

def test_word_export():
    """Test Word document export"""
    
    print("🧪 Testing Word Document Export")
    print("=" * 50)
    
    # Create exporter
    exporter = WordDocumentExporter()
    
    # Sample travel report content
    sample_content = """
# Travel Plan - Paris, France

## Day 1: Arrival and City Center
- Arrive at Charles de Gaulle Airport (CDG)
- Check into hotel near Louvre
- Visit Eiffel Tower
- Dinner at local bistro

### Airport Distance Information
Distance from Charles de Gaulle Airport (CDG) to Eiffel Tower: 34.2 km (approximately 45m by car)
Distance from Charles de Gaulle Airport (CDG) to Louvre Museum: 32.1 km (approximately 42m by car)

## Day 2: Museums and Culture
- **Morning**: Louvre Museum
- **Afternoon**: Notre-Dame Cathedral
- **Evening**: Seine River cruise

## Car Rental Options
- Vehicle: Compact Car | Seats: 4 | Provider: Europcar | Price: 67 EUR
- Vehicle: Economy Car | Seats: 4 | Provider: Hertz | Price: 72 EUR

## Budget Breakdown
- **Hotel**: 120 EUR per night
- **Meals**: 50 EUR per day
- **Attractions**: 25 EUR per day
- **Transportation**: 15 EUR per day
"""
    
    # Query info
    query_info = {
        "startCity": "Paris",
        "endCity": "Paris",
        "startLocationCode": "CDG",
        "endLocationCode": "CDG"
    }
    
    try:
        # Create Word document
        doc_path = exporter.create_travel_report_doc(sample_content, query_info)
        
        print(f"✅ Word document created successfully!")
        print(f"   File path: {doc_path}")
        print(f"   File exists: {os.path.exists(doc_path)}")
        
        if os.path.exists(doc_path):
            file_size = os.path.getsize(doc_path)
            print(f"   File size: {file_size} bytes")
        
    except Exception as e:
        print(f"❌ Failed to create Word document: {e}")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_word_export()
