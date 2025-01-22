import os
import sys
import logging
from typing import Optional
import json
import requests
from datetime import datetime, timezone
import streamlit as st

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
    """Main application entry point with clean prototype layout."""
    st.set_page_config(
        page_title="ResumeRocket5a Prototype",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    # Custom styling
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

            .main {
                padding: 2rem;
                max-width: 1200px;
                margin: 0 auto;
            }

            h1, h2, h3 {
                font-family: 'Inter', sans-serif;
                color: #1E3A8A;
            }

            .limited-offer {
                background-color: #FEF3C7;
                padding: 1rem;
                border-radius: 0.5rem;
                border: 1px solid #F59E0B;
                margin: 1rem 0;
                text-align: center;
            }

            .section-card {
                background-color: #F8FAFC;
                padding: 1.5rem;
                border-radius: 0.5rem;
                margin: 1rem 0;
            }

            .footer {
                margin-top: 2rem;
                padding-top: 1rem;
                border-top: 1px solid #E2E8F0;
                text-align: center;
                color: #64748B;
            }
        </style>
    """, unsafe_allow_html=True)

    # Header with Project Introduction
    st.title("ResumeRocket5a Prototype")
    st.markdown("Transform your job search with AI-powered resume optimization")

    # Limited Offer Banner
    st.markdown("""
        <div class='limited-offer'>
            <strong>🚀 Limited Beta Access</strong><br>
            We're accepting only 50 users for our free beta program in exchange for detailed feedback.
            Join now to be part of this exclusive group!
        </div>
    """, unsafe_allow_html=True)

    # Project Background
    st.markdown("""
        <div class='section-card'>
            <h2>About Our Project</h2>
            <p>ResumeRocket5a is developed by industry professionals with over a decade of experience in 
            recruitment and HR technology. Our AI-powered platform analyzes and optimizes resumes based on 
            current industry standards and job market requirements.</p>
        </div>
    """, unsafe_allow_html=True)

    # Eligibility and Requirements
    st.markdown("""
        <div class='section-card'>
            <h2>Eligibility Requirements</h2>
            <ul>
                <li>Currently seeking employment or career advancement</li>
                <li>Have a resume in PDF or DOCX format</li>
                <li>Willing to provide detailed feedback on our service</li>
                <li>Must be 18 years or older</li>
            </ul>
            <p><em>Note: This is a prototype version for testing and feedback purposes only.</em></p>
        </div>
    """, unsafe_allow_html=True)

    # Application Form
    st.markdown("<h2>Submit Your Application</h2>", unsafe_allow_html=True)
    with st.form("resume_form"):
        col1, col2 = st.columns(2)

        with col1:
            first_name = st.text_input("First Name*")
        with col2:
            last_name = st.text_input("Last Name*")

        email = st.text_input("Email Address*")

        uploaded_file = st.file_uploader(
            "Upload Your Resume*",
            type=['pdf', 'docx'],
            help="Accepted formats: PDF, DOCX • Max size: 10MB"
        )

        submit = st.form_submit_button("Submit Application")

        if submit:
            if not all([first_name, last_name, email, uploaded_file]):
                st.error("Please fill in all required fields and upload your resume.")
            else:
                form_data = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'professional_level': "Individual Contributor",  # Set default value
                }
                logger.info(f"Form submitted with data: {json.dumps(form_data, indent=2)}")

                if send_to_webhook(form_data, (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)):
                    st.success("Application submitted successfully!")
                    st.balloons()
                else:
                    st.error("Failed to submit application. Please try again.")


    # Footer
    st.markdown("""
        <div class='footer'>
            <p>© 2025 ResumeRocket5a Prototype | Contact: support@resumerocket5a.example.com</p>
            <p><small>This is a prototype version for testing and feedback purposes only.</small></p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()