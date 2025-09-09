import streamlit as st
import requests
import datetime
import os

# Simple test for Word document download
st.title("🧪 Word Download Test")

BASE_URL = "http://localhost:8000"

# Test content
test_content = """
# Test Travel Report

## Destination: Paris

### Day 1
- Visit Eiffel Tower
- Lunch at Café de Flore

### Airport Distance Information
Distance from Charles de Gaulle Airport (CDG) to Eiffel Tower: 34.2 km (approximately 45m by car)

## Car Rental Options
- Vehicle: Compact Car | Seats: 4 | Provider: Europcar | Price: 67 EUR
"""

if st.button("🧪 Test Word Download"):
    try:
        st.info("Generating Word document...")
        
        # Prepare export request
        export_payload = {
            "content": test_content,
            "query_info": {
                "query": "Test Paris trip"
            }
        }
        
        # Call export endpoint
        response = requests.post(f"{BASE_URL}/export-word", json=export_payload, timeout=30)
        
        st.write(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            # Create filename
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"Test_Travel_Report_{timestamp}.docx"
            
            st.success("✅ Document generated successfully!")
            
            # Create download button
            st.download_button(
                label="📄 Download Test Document",
                data=response.content,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
        else:
            st.error(f"❌ Failed: {response.status_code}")
            st.error(f"Error: {response.text}")
            
    except Exception as e:
        st.error(f"❌ Exception: {e}")

st.markdown("---")
st.markdown("**Instructions:**")
st.markdown("1. Make sure your server is running on port 8000")
st.markdown("2. Click the test button above")
st.markdown("3. If successful, you should see a download button")
