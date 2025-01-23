import streamlit as st
import os
import sys
import logging
from typing import Optional
import json
import requests
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

def send_to_webhook(form_data: dict, file_data: Optional[tuple] = None) -> bool:
    """Send form data to webhook with improved logging and validation."""
    try:
        webhook_url = st.secrets["general"].get("MAKE_WEBHOOK_URL", "https://hooks.zapier.com/hooks/catch/274092/2km31m2/")
        logger.info(f"[{datetime.now(timezone.utc).isoformat()}] Initiating webhook submission...")

        if not webhook_url:
            logger.error("Webhook URL not configured")
            return False

        form_data['timestamp'] = datetime.now(timezone.utc).isoformat()

        payload = {
            "first_name": form_data.get("first_name", "").strip(),
            "last_name": form_data.get("last_name", "").strip(),
            "email": form_data.get("email", "").strip(),
            "timestamp": form_data["timestamp"]
        }

        files = None
        if file_data:
            file_name, file_content, file_type = file_data
            files = {
                'resume': (file_name, file_content, file_type)
            }
            logger.debug(f"File details - Name: {file_name}, Type: {file_type}, Size: {len(file_content)} bytes")

        response = requests.post(
            webhook_url,
            data=payload,
            files=files,
            timeout=30
        )

        if response.status_code == 200:
            logger.info("Webhook submission successful")
            return True
        else:
            logger.error(f"Webhook failed. Status: {response.status_code}, Response: {response.text}")
            return False

    except Exception as e:
        logger.error(f"Error sending data to webhook: {str(e)}")
        return False

def main():
    """Main application entry point"""
    try:
        # Configure page
        st.set_page_config(
            page_title="ResumeRocket5 Prototype",
            layout="wide",
            initial_sidebar_state="collapsed"
        )

        # Custom CSS
        st.markdown("""
            <style>
            .main {
                padding: 2rem;
                max-width: 1200px;
                margin: 0 auto;
            }
            .stApp {
                background-color: #f8f9fa;
            }
            .content-box {
                background-color: white;
                padding: 1.5rem;
                border-radius: 8px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                margin-bottom: 1.5rem;
            }
            .section-title {
                font-size: 1.2rem;
                font-weight: 600;
                margin-bottom: 1rem;
                color: #1E1E1E;
            }
            .section-text {
                font-size: 1rem;
                line-height: 1.6;
                color: #4A4A4A;
                margin-bottom: 1.5rem;
            }
            .footer {
                text-align: center;
                padding: 1.5rem;
                margin-top: 2rem;
                font-size: 0.9rem;
                color: #666;
                background-color: #f8f9fa;
                border-radius: 8px;
            }
            /* Custom checkbox container */
            .checkbox-container {
                display: flex;
                align-items: center;
                justify-content: flex-end; /* Align checkbox to the right */
                padding: 10px 15px;
                margin: 8px 0;
                background-color: #ffffff;
                border-radius: 6px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                transition: all 0.2s ease;
            }
            .checkbox-container:hover {
                box-shadow: 0 2px 5px rgba(0,0,0,0.15);
            }
            .checkbox-label {
                flex-grow: 1;
                padding-right: 15px;
                font-size: 0.95rem;
                color: #2C3E50;
            }
            /* Make the checkbox itself more prominent */
            .stCheckbox > label > div[role="checkbox"] {
                transform: scale(1.2);
            }
            /* Hide the default checkbox text */
            .stCheckbox label p {
                display: none !important;
            }
            </style>
        """, unsafe_allow_html=True)

        # Header
        st.title("ResumeRocket5 Prototype")
        st.markdown("A specialized AI-powered resume analysis tool for management consultants, designed to enhance interview opportunities and enrich conversations with hiring managers.")

        # Create two columns for main content
        left_col, right_col = st.columns([6, 4])

        # Left Column - Content
        with left_col:
            with st.container():
                # About Our Project
                st.markdown("### About Our Project")
                st.write(
                    "This project emerged from research conducted in artificial intelligence, its application to human "
                    "resources and recruiting, combined with expertise gained from decades of recruiting in the management "
                    "consulting field. The prototype brings together deep industry knowledge with AI-based language analysis "
                    "to produce an analysis engine that sits at the leading edge of what AI can offer management consulting "
                    "job seekers.\n\n"
                    "This limited prototype release (50 users) will help us evaluate the tool's viability. While there's no "
                    "monetary cost, we ask for your detailed feedback in exchange for the analysis - a mutual exchange of "
                    "value that will shape the project's future direction."
                )

                # Eligibility Requirements
                st.markdown("### Eligibility Requirements")
                st.markdown('<div class="checkbox-container">'
                          '<div class="checkbox-label">I am a current management consultant or have worked as one within the past two years</div>'
                          f'{st.checkbox("", key="is_consultant", label_visibility="collapsed", value=True)}</div>', 
                          unsafe_allow_html=True)

                st.markdown('<div class="checkbox-container">'
                          '<div class="checkbox-label">I am actively or passively seeking new employment opportunities</div>'
                          f'{st.checkbox("", key="is_job_seeking", label_visibility="collapsed", value=True)}</div>', 
                          unsafe_allow_html=True)

                st.markdown('<div class="checkbox-container">'
                          '<div class="checkbox-label">I commit to providing detailed feedback and suggestions after using the tool</div>'
                          f'{st.checkbox("", key="will_provide_feedback", label_visibility="collapsed", value=True)}</div>', 
                          unsafe_allow_html=True)

        # Right Column - Form
        with right_col:
            with st.container():
                st.markdown("### Enter Your Information")

                with st.form("beta_access_form", clear_on_submit=False):
                    first_name = st.text_input("First Name")
                    last_name = st.text_input("Last Name")
                    email = st.text_input("Email Address")

                    uploaded_file = st.file_uploader(
                        "Upload Resume",
                        type=['pdf', 'docx'],
                        help="Limit 20MB per file • PDF, DOCX"
                    )

                    submit_button = st.form_submit_button("Upload Document")

                    if submit_button:
                        if not all([first_name, last_name, email]):
                            st.error("Please fill in all required fields")
                            return

                        if not uploaded_file:
                            st.error("Please upload your resume")
                            return

                        if not all([st.session_state.is_consultant, st.session_state.is_job_seeking, st.session_state.will_provide_feedback]):
                            st.error("Please confirm all eligibility requirements")
                            return

                        form_data = {
                            'first_name': first_name,
                            'last_name': last_name,
                            'email': email,
                        }

                        if send_to_webhook(form_data, (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)):
                            st.success("""
                                Message received! You will receive analysis by email shortly. 
                                If it does not arrive within 15 minutes, please check your spam folder.
                            """)
                            st.balloons()
                        else:
                            st.error("There was an error submitting your application. Please try again.")

        # Footer
        st.markdown("""
            <div class="footer">
                © 2025 ResumeRocket5 Prototype | Contact: support@resumerocket5.example.com<br>
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