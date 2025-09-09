import streamlit as st
import requests
import datetime
import os

BASE_URL = "http://localhost:8000"

st.title("🌍 Travel Planner - Fixed Download")

# Input form
with st.form("travel_form"):
    user_input = st.text_input("Where do you want to travel?", placeholder="e.g. Plan a trip to Paris")
    submit = st.form_submit_button("Generate Travel Plan")

if submit and user_input:
    with st.spinner("Generating travel plan..."):
        try:
            # Get travel report
            response = requests.post(f"{BASE_URL}/query", json={"query": user_input})
            
            if response.status_code == 200:
                answer = response.json().get("answer", "")
                
                # Display the report
                st.markdown("## 🌍 Your Travel Plan")
                st.markdown(answer)
                
                # Prepare Word document data immediately
                st.markdown("---")
                
                export_payload = {
                    "content": answer,
                    "query_info": {"query": user_input}
                }
                
                # Generate Word document
                word_response = requests.post(f"{BASE_URL}/export-word", json=export_payload)
                
                if word_response.status_code == 200:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    filename = f"Travel_Plan_{timestamp}.docx"
                    
                    st.download_button(
                        label="📄 Download as Word Document",
                        data=word_response.content,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        type="primary"
                    )
                    
                else:
                    st.error("Could not generate Word document")
                    
            else:
                st.error("Failed to generate travel plan")
                
        except Exception as e:
            st.error(f"Error: {e}")

st.markdown("---")
st.markdown("**Note:** Make sure your server is running on port 8000")
st.markdown("```uvicorn main:app --reload --port 8000```")
