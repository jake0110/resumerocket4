import os
import sys
import logging
from typing import Optional
import json
import requests
import datetime

# Configure logging first
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

logger.debug("Starting application...")

# Import required packages with error handling
try:
    logger.debug("Importing required packages...")
    import streamlit as st
    logger.debug("Successfully imported all required packages")
except ImportError as e:
    logger.error(f"Failed to import required packages: {str(e)}")
    sys.exit(1)

def send_to_webhook(form_data: dict, file_data: Optional[tuple] = None) -> bool:
    """Send form data to Make.com webhook."""
    try:
        # Get webhook URL from secrets
        webhook_url = st.secrets["general"]["MAKE_WEBHOOK_URL"]
        if not webhook_url:
            logger.error("Make.com webhook URL not configured")
            return False

        logger.debug(f"Preparing to send data to webhook")

        # Prepare the payload with exact field names matching Google Sheets
        payload = {
            "first_name": form_data.get("first_name", ""),
            "last_name": form_data.get("last_name", ""),
            "email": form_data.get("email", ""),
            "phone": form_data.get("phone", ""),
            "city": form_data.get("city", ""),
            "state": form_data.get("state", "")
        }

        files = None
        if file_data:
            files = {
                'resume': (file_data[0], file_data[1], file_data[2])
            }
            # Add file-related fields
            payload["_filename_"] = file_data[0]
            payload["_name_"] = os.path.splitext(file_data[0])[0]
            payload["_download_url_"] = ""  # Will be populated by Make.com

        logger.debug("Sending request to webhook")
        # Send request to webhook
        response = requests.post(
            webhook_url,
            json=payload,  # Send as JSON directly
            files=files,
            timeout=30
        )

        logger.debug(f"Webhook response status code: {response.status_code}")
        logger.debug(f"Webhook response content: {response.text}")

        if response.status_code == 200:
            logger.info("Successfully sent data to Make.com webhook")
            return True
        else:
            logger.error(f"Failed to send data to webhook. Status code: {response.status_code}")
            logger.error(f"Response content: {response.text}")
            return False

    except Exception as e:
        logger.error(f"Error sending data to webhook: {str(e)}")
        return False

def main():
    """Main application entry point."""
    try:
        logger.debug("Setting up Streamlit page configuration...")
        # Configure page
        st.set_page_config(
            page_title="ResumeRocket5 - Resume Analyzer",
            layout="wide"
        )

        st.title("ResumeRocket5 - Resume Analyzer")
        st.write("Enter your information below")

        # Create a form for submission
        with st.form("personal_info_form"):
            st.subheader("Personal Information")

            col1, col2 = st.columns(2)

            with col1:
                first_name = st.text_input("First Name", key="first_name")
                last_name = st.text_input("Last Name", key="last_name")
                email = st.text_input("Email", key="email")

            with col2:
                phone = st.text_input("Phone", key="phone")
                city = st.text_input("City", key="city")
                states = [
                    "Select", "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", 
                    "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
                    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", 
                    "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", 
                    "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
                ]
                state = st.selectbox("State", states, key="state")

            # File Upload Section
            uploaded_file = st.file_uploader(
                "Upload your resume",
                type=['docx', 'pdf'],
                help="Upload a Word document (.docx) or PDF file",
                key="_filename_"
            )

            # Submit button
            submit_button = st.form_submit_button("Submit Application")

            if submit_button:
                if not all([
                    first_name, last_name, email, phone, city, 
                    state != "Select"
                ]):
                    st.error("Please fill in all required fields")
                    return

                # Process form submission with debug logging
                form_data = {
                    'first_name': st.session_state.get("first_name", ""),
                    'last_name': st.session_state.get("last_name", ""),
                    'email': st.session_state.get("email", ""),
                    'phone': st.session_state.get("phone", ""),
                    'city': st.session_state.get("city", ""),
                    'state': st.session_state.get("state", ""),
                    'professional_level': st.session_state.get("prof_level", "Entry Level"),
                    'date_created': datetime.datetime.now().isoformat()
                }

                logger.debug(f"Preparing to send payload: {json.dumps(form_data)}")
                
                files = None
                if uploaded_file:
                    files = {
                        'resume': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
                    }

                try:
                    webhook_url = st.secrets["general"]["MAKE_WEBHOOK_URL"]
                    response = requests.post(
                        webhook_url,
                        json=form_data,
                        files=files,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                    st.success("Application submitted successfully!")
                    st.balloons()
                else:
                    st.error("Failed to submit application. Please try again.")

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error("An unexpected error occurred. Please try again.")

if __name__ == "__main__":
    logger.debug("Starting main application...")
    main()