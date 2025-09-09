import streamlit as st
import requests
import datetime
import os

# from exception.exceptions import TradingBotException
import sys

BASE_URL = "http://localhost:8000"  # Backend endpoint

st.set_page_config(
    page_title="🌍 Travel Planner Agentic Application",
    page_icon="🌍",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title("🌍 Travel Planner Agentic Application")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize download state
if "last_report" not in st.session_state:
    st.session_state.last_report = None
if "last_query" not in st.session_state:
    st.session_state.last_query = None
if "budget_preference" not in st.session_state:
    st.session_state.budget_preference = None
if "current_budget_selection" not in st.session_state:
    st.session_state.current_budget_selection = None
if "current_travel_query" not in st.session_state:
    st.session_state.current_travel_query = ""
if "report_generated" not in st.session_state:
    st.session_state.report_generated = False
if "generation_timestamp" not in st.session_state:
    st.session_state.generation_timestamp = None

# Display chat history
st.header("How can I help you in planning a trip? Let me know where do you want to visit.")

# Travel query and budget preference form
with st.form(key="query_form", clear_on_submit=False):  # Changed to False to prevent clearing
    # Travel query input first
    st.subheader("✈️ Tell me about your trip")
    user_input = st.text_input(
        "Enter your travel query", 
        placeholder="e.g. Plan a trip to Goa for 5 days",
        value=st.session_state.current_travel_query  # Use session state value
    )
    
    # Update session state when input changes
    if user_input != st.session_state.current_travel_query:
        st.session_state.current_travel_query = user_input
    
    st.markdown("---")
    
    # Budget preference selector below input
    st.markdown("**💰 Select Your Budget Preference**")
    
    budget_options = [
        "💰 Budget Friendly - Good value for money",
        "🏷️ Cheapest - Ultra budget-friendly options", 
        "💎 Luxurious - Premium experiences"
    ]
    
    # Determine the current index based on session state
    current_index = None
    if st.session_state.current_budget_selection in budget_options:
        current_index = budget_options.index(st.session_state.current_budget_selection)
    
    budget_option = st.radio(
        "Choose the type of travel experience you prefer:",
        budget_options,
        index=current_index,  # Use session state to persist selection
        horizontal=True
    )
    
    # Update session state when selection changes
    if budget_option != st.session_state.current_budget_selection:
        st.session_state.current_budget_selection = budget_option
    
    st.markdown("<br>", unsafe_allow_html=True)
    submit_button = st.form_submit_button("🚀 Generate Travel Plan", type="primary")

if submit_button and user_input.strip():
    # Validate that budget preference is selected
    if st.session_state.current_budget_selection is None:
        st.error("⚠️ Please select a budget preference before generating your travel plan.")
    else:
        try:
            # Extract budget preference (remove emoji and extra text for backend)
            budget_map = {
                "💰 Budget Friendly - Good value for money": "budget_friendly",
                "🏷️ Cheapest - Ultra budget-friendly options": "cheapest", 
                "💎 Luxurious - Premium experiences": "luxurious"
            }
            budget_preference = budget_map.get(st.session_state.current_budget_selection, "budget_friendly")
            
            # Show thinking spinner while backend processes
            with st.spinner("Bot is thinking..."):
                payload = {
                    "question": user_input,
                    "budget_preference": budget_preference
                }
                response = requests.post(f"{BASE_URL}/query", json=payload)

            if response.status_code == 200:
                answer = response.json().get("answer", "No answer returned.")
                # Store in session state for persistent display
                st.session_state.last_report = answer
                st.session_state.last_query = user_input
                st.session_state.budget_preference = st.session_state.current_budget_selection  # Store the full display text
                st.session_state.report_generated = True
                st.session_state.generation_timestamp = datetime.datetime.now().strftime('%Y-%m-%d at %H:%M')
                # Keep the current travel query in session state for persistence
                st.session_state.current_travel_query = user_input
            else:
                st.error(" Bot failed to respond: " + response.text)

        except Exception as e:
            st.error(f"The response failed due to {e}")
elif submit_button and not user_input.strip():
    st.error("⚠️ Please enter your travel query.")

# Display the report content persistently (outside form submission)
if st.session_state.get('report_generated', False) and st.session_state.get('last_report'):
    st.markdown("---")
    
    # Display the travel report
    budget_display = st.session_state.get('budget_preference', 'Budget Friendly')
    markdown_content = f"""# 🌍 AI Travel Plan

**Generated:** {st.session_state.get('generation_timestamp', 'Unknown')}  
**Budget Preference:** {budget_display}  
**Created by:** Atriyo's Travel Agent

---

{st.session_state.last_report}

---

<small><i>This travel plan was generated by AI. Please verify all information, especially prices, operating hours, and travel requirements before your trip.</i></small>
"""
    st.markdown(markdown_content, unsafe_allow_html=True)

# Download functionality - separate section to prevent interference
if st.session_state.get('report_generated', False) and st.session_state.get('last_report'):
    st.markdown("---")
    st.markdown("### 📥 Export Options")
    
    # Simple download button that doesn't interfere with content
    if st.button("📄 Download as Word Document", type="primary", key="download_word"):
        try:
            # Prepare export request
            export_payload = {
                "content": st.session_state.last_report,
                "query_info": {
                    "query": st.session_state.last_query,
                    "budget_preference": st.session_state.get('budget_preference', 'Budget Friendly'),
                    "generation_timestamp": st.session_state.get('generation_timestamp', 'Unknown')
                }
            }
            
            # Call export endpoint to get the Word document
            export_response = requests.post(f"{BASE_URL}/export-word", json=export_payload)
            
            if export_response.status_code == 200:
                # Create download with timestamp
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"AI_Travel_Report_{timestamp}.docx"
                
                st.download_button(
                    label="💾 Click to Save Document",
                    data=export_response.content,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key="actual_download"
                )
                st.success("✅ Document ready for download! Click the button above to save.")
            else:
                st.error("❌ Failed to generate Word document")
                
        except Exception as e:
            st.error(f"❌ Export failed: {e}")