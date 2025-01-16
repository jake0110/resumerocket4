import streamlit as st
import os
import tempfile
import logging
import time
import datetime
import requests

logger = logging.getLogger(__name__)

def send_to_webhook(form_data, file_content=None):
    """Send form data to Zapier webhook"""
    webhook_url = "https://hooks.zapier.com/hooks/catch/274092/2k4qlhg/"
    if not webhook_url:
        st.error("Webhook URL not configured")
        return False

    # Prepare payload according to the specified structure
    payload = {
        "first_name": form_data.get("first_name", ""),
        "last_name": form_data.get("last_name", ""),
        "email": form_data.get("email", ""),
        "level": form_data.get("professional_level", "")
    }

    files = {}
    if file_content:
        files = {'resume': ('resume.pdf', file_content, 'application/pdf')}

    try:
        response = requests.post(
            webhook_url,
            json=payload,
            files=files,
            timeout=30
        )
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error sending to webhook: {str(e)}")
        return False

def render_personal_info():
    """Render the personal information form with file upload."""
    with st.form("personal_info_form"):
        st.subheader("Personal Information")

        # Add timestamp
        current_time = datetime.datetime.now().isoformat()

        # Manual input fields
        first_name = st.text_input(
            "First Name",
            key="first_name_input"
        )

        last_name = st.text_input(
            "Last Name", 
            key="last_name_input"
        )

        email = st.text_input(
            "Email",
            key="email_input"
        )

        # Professional level dropdown
        level_options = [
            'Individual Contributor', 
            'Manager', 
            'Client Manager', 
            'Selling Principal/Partner', 
            'Practice Leader'
        ]
        prof_level = st.selectbox(
            "Professional Level",
            options=level_options,
            index=0,
            key="prof_level"
        )

        # File upload section
        st.markdown("### Resume Upload")
        st.info("✨ Upload your resume (PDF or DOCX format)")
        uploaded_file = st.file_uploader(
            "Upload your resume (DOCX or PDF)",
            type=['docx', 'pdf'],
            key="resume_uploader",
            help="Upload your resume"
        )

        if uploaded_file is not None:
            st.info(f"File selected: {uploaded_file.name}")
            file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # Convert to MB
            if file_size > 10:  # 10MB limit
                st.warning(f"File size ({file_size:.1f}MB) exceeds 10MB limit")
            else:
                st.success(f"File size: {file_size:.1f}MB (Ready for processing)")

        # Save button for form submission
        if st.form_submit_button("Submit"):
            if not all([first_name, last_name, email, prof_level]):
                st.error("Please fill in all required fields")
                return

            if not uploaded_file:
                st.error("Please upload your resume")
                return

            form_data = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'professional_level': prof_level,
                'date_created': current_time
            }

            file_content = None
            if uploaded_file:
                file_content = uploaded_file.getvalue()

            if send_to_webhook(form_data, file_content):
                st.success("✅ Information submitted successfully!")
                st.balloons()
            else:
                st.error("Failed to submit information. Please try again.")

def render_education():
    """Display education section."""
    st.info("Education section")

def render_experience():
    """Display experience section."""
    st.info("Experience section")

def render_skills():
    """Display skills section."""
    st.info("Skills section")

def check_parser_status():
    """Placeholder for parser status check"""
    pass #No functionality needed here as per new design