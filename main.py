import os
import sys
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
    logger.debug("Successfully imported all required packages")
except ImportError as e:
    logger.error(f"Failed to import required packages: {str(e)}")
    sys.exit(1)

def send_to_webhook(form_data: dict, file_data: Optional[tuple] = None) -> bool:
    """Send form data to Zapier webhook."""
    try:
        # Get webhook URL from secrets
        webhook_url = "https://hooks.zapier.com/hooks/catch/274092/2k4qlhg/"
        if not webhook_url:
            logger.error("Zapier webhook URL not configured")
            return False

        logger.debug(f"Preparing to send data to webhook")

        # Prepare the payload according to specified structure
        payload = {
            "first_name": form_data.get("first_name", ""),
            "last_name": form_data.get("last_name", ""),
            "email": form_data.get("email", ""),
            "level": form_data.get("professional_level", ""),
            "resume": "" #Added to match required structure.  Content will be added via files.
        }

        files = None
        if file_data:
            files = {
                'resume': (file_data[0], file_data[1], file_data[2])
            }

        logger.debug(f"Sending data to webhook: {json.dumps(payload)}")
        logger.debug(f"File included: {True if files else False}")

        # Send request to webhook
        response = requests.post(
            webhook_url,
            json=payload,
            files=files,
            timeout=30
        )

        logger.debug(f"Webhook response status code: {response.status_code}")
        logger.debug(f"Webhook response content: {response.text}")

        if response.status_code == 200:
            logger.info("Successfully sent data to Zapier webhook")
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
        # Configure page
        st.set_page_config(
            page_title="ResumeRocket5 - Resume Analyzer",
            layout="wide"
        )

        st.title("ResumeRocket5 - Resume Analyzer")
        st.write("Please fill out the form below")

        # Create form with required fields
        with st.form("resume_form"):
            col1, col2 = st.columns(2)

            with col1:
                first_name = st.text_input("First Name", key="first_name")
                last_name = st.text_input("Last Name", key="last_name")

            with col2:
                email = st.text_input("Email", key="email")
                level_options = [
                    "Select Level",
                    "Individual Contributor",
                    "Manager",
                    "Client Manager",
                    "Selling Principal/Partner",
                    "Practice Leader"
                ]
                level = st.selectbox("Professional Level", level_options, key="level")

            # File Upload Section
            uploaded_file = st.file_uploader(
                "Upload your resume",
                type=['docx', 'pdf'],
                help="Upload a Word document (.docx) or PDF file",
                key="resume"
            )

            # Submit button
            submit_button = st.form_submit_button("Submit Application")

            if submit_button:
                # Validate form
                if not all([
                    first_name,
                    last_name,
                    email,
                    level != "Select Level"
                ]):
                    st.error("Please fill in all required fields")
                    return

                if not uploaded_file:
                    st.error("Please upload your resume")
                    return

                # Process form data
                form_data = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'professional_level': level,
                    'date_created': datetime.now().isoformat()
                }

                logger.info(f"Form submitted successfully: {form_data}")

                if send_to_webhook(form_data, (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)):
                    st.success("Application submitted successfully!")
                    st.balloons()
                else:
                    st.error("Failed to submit application. Please try again.")

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error("An unexpected error occurred. Please try again.")

if __name__ == "__main__":
    try:
        logger.debug("Starting main application...")
        main()
    except Exception as e:
        logger.error(f"Application failed to start: {str(e)}")
        st.error("Application failed to start. Please try again.")