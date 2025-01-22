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
        webhook_url = st.secrets["general"].get("MAKE_WEBHOOK_URL", "https://hooks.zapier.com/hooks/catch/274092/2km31m2/")
        logger.info(f"[{datetime.now(timezone.utc).isoformat()}] Initiating webhook submission...")

        if not webhook_url:
            logger.error(f"[{datetime.now(timezone.utc).isoformat()}] Webhook URL not configured")
            return False

        form_data['timestamp'] = datetime.now(timezone.utc).isoformat()

        payload = {
            "first_name": form_data.get("first_name", "").strip(),
            "last_name": form_data.get("last_name", "").strip(),
            "email": form_data.get("email", "").strip(),
            "timestamp": form_data["timestamp"]
        }

        logger.debug(f"Webhook URL: {webhook_url}")
        logger.debug(f"Payload being sent: {json.dumps(payload, indent=2)}")

        submission_details = (
            f"[{payload['first_name']}, {payload['last_name']}, "
            f"{payload['email']}, Timestamp: {payload['timestamp']}"
        )

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

        response = requests.post(
            webhook_url,
            data=payload,
            files=files,
            timeout=30
        )

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
    """Main application entry point with updated layout."""
    try:
        # Configure page
        st.set_page_config(
            page_title="ResumeRocket5 Prototype",
            layout="wide",
            initial_sidebar_state="collapsed"
        )

        # Custom CSS for clean, professional look
        st.markdown("""
            <style>
            .main {
                padding: 1rem;
            }
            .content-section {
                margin-bottom: 1rem;
                padding: 1rem;
                background-color: white;
                border-radius: 5px;
            }
            .info-text {
                font-size: 0.95rem;
                line-height: 1.5;
                margin-bottom: 1rem;
            }
            .requirements-list {
                margin: 0;
                padding-left: 1.2rem;
            }
            .requirements-list li {
                margin-bottom: 0.5rem;
            }
            .footer {
                margin-top: 2rem;
                padding: 1rem;
                background-color: #f7f7f7;
                border-radius: 5px;
                text-align: center;
                font-size: 0.9rem;
            }
            div[data-testid="stForm"] {
                background-color: white;
                padding: 1rem;
                border-radius: 5px;
            }
            div.stButton > button {
                width: 100%;
                margin-top: 1rem;
            }
            </style>
        """, unsafe_allow_html=True)

        # Header Section
        st.title("ResumeRocket5 Prototype")
        st.markdown("A specialized AI-powered resume analysis tool for management consultants, designed to enhance interview opportunities and enrich conversations with hiring managers.")

        # Create two columns for main content
        col1, col2 = st.columns([5, 7])

        # Left Column - Project Information
        with col1:
            st.markdown("""
                <div class='content-section'>
                    <h4>Limited Prototype Release</h4>
                    <p class='info-text'>This limited prototype release (50 users) will help us evaluate the tool's viability. 
                    While there's no monetary cost, we ask for your detailed feedback in exchange for the analysis - 
                    a mutual exchange of value that will shape the project's future direction.</p>

                    <h4>About Our Project</h4>
                    <p class='info-text'>This prototype emerged from extensive research into AI applications in consulting recruitment. 
                    As a 30-year executive recruiter specialized in management consulting, I've reviewed thousands of resumes across major 
                    firms and levels. We've combined this industry expertise with targeted AI capabilities to create a specialized 
                    analysis engine for management consultants' career documents.</p>

                    <h4>Eligibility Requirements</h4>
                    <ul class='requirements-list'>
                        <li>Must be a current management consultant or have worked as one within the past two years</li>
                        <li>Must be actively or passively seeking new employment opportunities</li>
                        <li>Must commit to providing detailed feedback and suggestions after using the tool</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)

        # Right Column - Application Form
        with col2:
            st.markdown("<div class='content-section'>", unsafe_allow_html=True)
            st.subheader("Enter Your Information")

            with st.form("beta_access_form"):
                first_name = st.text_input("First Name", key="first_name")
                last_name = st.text_input("Last Name", key="last_name")
                email = st.text_input("Email Address", key="email")

                uploaded_file = st.file_uploader(
                    "Upload Resume",
                    type=['pdf', 'docx'],
                    help="Limit 20MB per file • PDF, DOCX",
                    key="resume"
                )

                agree = st.checkbox("I commit to providing detailed feedback after using the tool")
                submit_button = st.form_submit_button("Submit Application")

                if submit_button:
                    if not all([first_name, last_name, email]):
                        st.error("Please fill in all required fields")
                        return

                    if not uploaded_file:
                        st.error("Please upload your resume")
                        return

                    if not agree:
                        st.error("Please agree to provide feedback to join the beta program")
                        return

                    form_data = {
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                    }

                    if send_to_webhook(form_data, (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)):
                        st.success("Your application has been submitted successfully! We'll be in touch soon.")
                        st.balloons()
                    else:
                        st.error("There was an error submitting your application. Please try again.")

            st.markdown("</div>", unsafe_allow_html=True)

        # Footer
        st.markdown("""
            <div class='footer'>
                <p>© 2025 ResumeRocket5 Prototype | Contact: support@resumerocket5.example.com</p>
                <small>This is a prototype version for demonstration purposes only. As with all AI-powered tools, 
                outputs may contain inaccuracies and should be reviewed carefully.</small>
            </div>
        """, unsafe_allow_html=True)

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