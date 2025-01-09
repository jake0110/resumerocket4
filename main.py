import os
import sys
import tempfile
import logging
from typing import Optional
import json
import requests
from datetime import datetime

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
    from openai import OpenAI
    logger.debug("Successfully imported all required packages")
except ImportError as e:
    logger.error(f"Failed to import required packages: {str(e)}")
    sys.exit(1)

def send_to_webhook(form_data: dict, file_data: Optional[tuple] = None) -> bool:
    """Send form data and file to Make.com webhook."""
    try:
        # Get webhook URL from secrets
        webhook_url = st.secrets.get("MAKE_WEBHOOK_URL")
        if not webhook_url:
            logger.error("Make.com webhook URL not configured")
            return False

        # Prepare the payload
        payload = {
            "first_name": form_data.get("first_name", ""),
            "last_name": form_data.get("last_name", ""),
            "email": form_data.get("email", ""),
            "phone": form_data.get("phone", ""),
            "city": form_data.get("city", ""),
            "state": form_data.get("state", ""),
            "professional_level": form_data.get("professional_level", ""),
            "date_created": datetime.now().isoformat()
        }

        files = None
        if file_data:
            files = {
                'resume': (file_data[0], file_data[1], file_data[2])
            }

        # Send request to webhook
        response = requests.post(
            webhook_url,
            data={"payload": json.dumps(payload)},
            files=files,
            timeout=30
        )

        if response.status_code == 200:
            logger.info("Successfully sent data to Make.com webhook")
            return True
        else:
            logger.error(f"Failed to send data to webhook. Status code: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"Error sending data to webhook: {str(e)}")
        return False

def test_openai_connection(api_key: Optional[str] = None) -> bool:
    """Test OpenAI API connection."""
    if not api_key:
        return False

    try:
        if not api_key.startswith('sk-'):
            st.error("Invalid API key format. Please enter a valid OpenAI API key.")
            return False

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": "Test connection"
            }],
            max_tokens=10
        )
        return True
    except Exception as e:
        logger.error(f"OpenAI API Error: {str(e)}")
        st.error(f"OpenAI API Error: {str(e)}")
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
        st.write("Upload your resume for intelligent analysis using Airparser and OpenAI")

        # Create a form for submission
        with st.form("resume_form"):
            st.subheader("Personal Information")
            col1, col2 = st.columns(2)

            with col1:
                first_name = st.text_input("First Name", key="first_name")
                last_name = st.text_input("Last Name", key="last_name")
                email = st.text_input("Email", key="email")
                phone = st.text_input("Phone", key="phone")
                city = st.text_input("City", key="city")

            with col2:
                states = ["Select State", "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
                state = st.selectbox("State", states, key="state")

                role_types = ["Select Role Type", "Entry Level", "Individual Contributor", "Team Lead", "Manager", "Director", "Vice President", "Executive"]
                professional_level = st.selectbox("Professional Level", role_types, key="professional_level")

                # File Upload Section
                uploaded_file = st.file_uploader(
                    "Upload your resume",
                    type=['docx', 'pdf'],
                    help="Upload a Word document (.docx) or PDF file"
                )

            # Submit button
            submit_button = st.form_submit_button("Submit Application")

            if submit_button:
                if not all([first_name, last_name, email, phone, city, state != "Select State", professional_level != "Select Role Type"]):
                    st.error("Please fill in all required fields")
                    return

                # Process form submission
                form_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "phone": phone,
                    "city": city,
                    "state": state,
                    "professional_level": professional_level
                }

                file_data = None
                if uploaded_file:
                    file_data = (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type
                    )

                # Send to webhook
                if send_to_webhook(form_data, file_data):
                    st.success("Application submitted successfully!")
                    st.balloons()
                else:
                    st.error("Failed to submit application. Please try again.")

        # OpenAI API Test Section (Optional)
        with st.expander("OpenAI API Configuration"):
            st.subheader("OpenAI API Test")
            api_key = st.text_input("Enter your OpenAI API Key", type="password")

            if st.button("Test Connection"):
                if test_openai_connection(api_key):
                    st.success("✅ OpenAI API connection verified")

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error("An unexpected error occurred. Please try again.")

if __name__ == "__main__":
    logger.debug("Starting main application...")
    main()