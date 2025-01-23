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

        # CSS Styles
        st.markdown("""
        <style>
        /* Main container for requirements section */
        .requirements-container {
            margin-top: 0.5rem;
            padding: 0.5rem;
        }

        /* Text container */
        .requirement-text {
            flex: 1;
            margin: 0;
            line-height: 1.4;
            padding: 0.25rem 0;
            display: flex;
            align-items: center;
        }

        /* Checkbox container adjustment */
        .stCheckbox {
            margin: 0 !important;
            padding: 0 !important;
            transform: translateY(-2px) !important;
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

                # Requirements Section
                st.markdown("### Eligibility Requirements")
                with st.container():
                    st.markdown('<div class="requirements-container">', unsafe_allow_html=True)

                    # First Requirement
                    col1, col2 = st.columns([0.9, 0.1])
                    with col1:
                        st.markdown("""
                            <div class="requirement-text">
                            I have worked as a management consultant within the past two years.
                            </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.checkbox("", key="consultant_check", label_visibility="collapsed")

                    # Second Requirement
                    col1, col2 = st.columns([0.9, 0.1])
                    with col1:
                        st.markdown("""
                            <div class="requirement-text">
                            I am actively or passively seeking new employment opportunities.
                            </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.checkbox("", key="seeking_check", label_visibility="collapsed")

                    # Third Requirement
                    col1, col2 = st.columns([0.9, 0.1])
                    with col1:
                        st.markdown("""
                            <div class="requirement-text">
                            I commit to providing detailed feedback and suggestions.
                            </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.checkbox("", key="feedback_check", label_visibility="collapsed")

                    st.markdown('</div>', unsafe_allow_html=True)

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

                        if not all([st.session_state.get("consultant_check", False), 
                                  st.session_state.get("seeking_check", False), 
                                  st.session_state.get("feedback_check", False)]):
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
            <div style="text-align: center; padding: 1.5rem; margin-top: 2rem; font-size: 0.9rem; color: #666;">
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