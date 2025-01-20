import os
import sys
import logging
from typing import Optional
import json
import requests
from datetime import datetime, timezone

# Configure logging first
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
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
    """Send form data to webhook with improved logging and validation."""
    try:
        # Get webhook URL from secrets or use default
        webhook_url = st.secrets["general"].get("MAKE_WEBHOOK_URL", "https://hooks.zapier.com/hooks/catch/274092/2km31m2/")
        logger.info(f"[{datetime.now(timezone.utc).isoformat()}] Initiating webhook submission...")

        # Validate webhook URL
        if not webhook_url:
            logger.error(f"[{datetime.now(timezone.utc).isoformat()}] Webhook URL not configured")
            return False

        # Add timestamp in ISO format with UTC timezone
        form_data['timestamp'] = datetime.now(timezone.utc).isoformat()

        # Prepare the payload with exactly the required fields
        payload = {
            "first_name": form_data.get("first_name", "").strip(),
            "last_name": form_data.get("last_name", "").strip(),
            "email": form_data.get("email", "").strip(),
            "level": form_data.get("professional_level", "").strip(),
            "timestamp": form_data["timestamp"]
        }

        # Debug logging of webhook details
        logger.debug(f"Webhook URL: {webhook_url}")
        logger.debug(f"Payload being sent: {json.dumps(payload, indent=2)}")

        # Format submission details for logging
        submission_details = (
            f"[{payload['first_name']}, {payload['last_name']}, "
            f"{payload['email']}, {payload['level']}, "
            f"Timestamp: {payload['timestamp']}"
        )

        # Handle file data
        files = None
        if file_data:
            file_name, file_content, file_type = file_data
            submission_details += f", Resume: {file_name}]"
            files = {
                'resume': (file_name, file_content, file_type)
            }
            logger.debug(f"File details - Name: {file_name}, Type: {file_type}, Size: {len(file_content)} bytes")
            logger.info(f"[{datetime.now(timezone.utc).isoformat()}] Resume file included: {file_name} ({len(file_content)} bytes)")
        else:
            submission_details += ", No Resume]"
            logger.warning(f"[{datetime.now(timezone.utc).isoformat()}] No resume file attached")

        logger.info(f"[{datetime.now(timezone.utc).isoformat()}] Preparing webhook submission: {submission_details}")

        # Additional debug logging right before the POST request
        logger.debug("==== WEBHOOK REQUEST DETAILS ====")
        logger.debug(f"URL: {webhook_url}")
        logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
        logger.debug(f"Files included: {True if files else False}")
        logger.debug("==============================")

        # Send request to webhook
        response = requests.post(
            webhook_url,
            data=payload,
            files=files,
            timeout=30
        )

        # Log the response for debugging
        logger.debug(f"Webhook Response Status: {response.status_code}")
        logger.debug(f"Webhook Response Content: {response.text}")

        if response.status_code == 200:
            logger.info(f"[{datetime.now(timezone.utc).isoformat()}] Webhook successfully triggered for submission: {submission_details}")
            return True
        else:
            error_msg = f"Status: {response.status_code}, Response: {response.text}"
            logger.error(f"[{datetime.now(timezone.utc).isoformat()}] Webhook failed for submission: {submission_details}. Error: {error_msg}")
            return False

    except Exception as e:
        error_msg = str(e)
        logger.error(f"[{datetime.now(timezone.utc).isoformat()}] Error sending data to webhook: {error_msg}")
        if 'submission_details' in locals():
            logger.error(f"[{datetime.now(timezone.utc).isoformat()}] Failed submission details: {submission_details}")
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
                if not all([first_name, last_name, email, level != "Select Level"]):
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
                }

                logger.info(f"Form submitted with data: {json.dumps(form_data, indent=2)}")

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