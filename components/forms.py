import streamlit as st
import os
import tempfile
import logging
import time
import datetime
import requests
from utils.resume_parser import process_resume

logger = logging.getLogger(__name__)

def check_parser_status():
    """Check and update the parsing status in session state."""
    if 'parser_job_id' in st.session_state:
        from utils.resume_parser import AirparserMakeIntegration
        parser = AirparserMakeIntegration()
        result = parser.check_parsing_status(st.session_state.parser_job_id)

        if result['status'] == 'completed':
            st.session_state.parsed_data = result.get('data', {})
            st.session_state.parser_status = 'completed'
        elif result['status'] == 'error':
            st.session_state.parser_status = 'error'
            st.session_state.parser_error = result.get('message', 'Unknown error')

def send_to_webhook(form_data, file_content=None):
    """Send form data to Make.com webhook"""
    webhook_url = os.getenv('MAKE_WEBHOOK_URL')
    if not webhook_url:
        st.error("Webhook URL not configured")
        return False

    files = {}
    if file_content:
        files = {'resume': ('resume.pdf', file_content, 'application/pdf')}

    try:
        response = requests.post(
            webhook_url,
            data=form_data,
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

        # File upload section
        st.markdown("### Resume Upload")
        st.info("✨ Upload your resume for intelligent parsing with Airparser!")
        uploaded_file = st.file_uploader(
            "Upload your resume (DOCX or PDF)",
            type=['docx', 'pdf'],
            key="resume_uploader",
            help="Upload your resume for Airparser analysis"
        )

        if uploaded_file is not None:
            st.info(f"File selected: {uploaded_file.name}")
            file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # Convert to MB
            if file_size > 10:  # 10MB limit
                st.warning(f"File size ({file_size:.1f}MB) exceeds 10MB limit")
            else:
                st.success(f"File size: {file_size:.1f}MB (Ready for processing)")

                if st.form_submit_button("Process Resume"):
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                            file_content = uploaded_file.getvalue()
                            tmp_file.write(file_content)
                            tmp_file_path = tmp_file.name
                            logger.debug(f"Saved uploaded file to {tmp_file_path}")

                            # Process with Airparser integration
                            result = process_resume(tmp_file_path, file_content, uploaded_file.name)
                            if result['status'] == 'error':
                                st.error(result['message'])
                            else:
                                st.session_state.parser_job_id = result['job_id']
                                st.session_state.parser_status = 'pending'
                                st.info("✨ Your resume has been submitted for parsing!")
                                st.info("Please wait while we process your document...")

                            # Clean up temporary file
                            os.unlink(tmp_file_path)
                            logger.debug("Cleaned up temporary file")

                    except Exception as e:
                        logger.error(f"Error processing file: {str(e)}")
                        st.error("Error processing your file. Please try again.")

        # Check parser status if a job is in progress
        if 'parser_status' in st.session_state:
            if st.session_state.parser_status == 'pending':
                check_parser_status()
                st.info("Processing your resume... Please wait.")
            elif st.session_state.parser_status == 'completed':
                st.success("✅ Resume parsing completed!")
                parsed_data = st.session_state.parsed_data

                # Auto-fill form fields with parsed data
                name = parsed_data.get('name', '')
                email = parsed_data.get('email', '')
                phone = parsed_data.get('phone', '')
            elif st.session_state.parser_status == 'error':
                st.error(f"Error parsing resume: {st.session_state.get('parser_error', 'Unknown error')}")

        # Manual input fields (auto-filled when parsing completes)
        first_name = st.text_input(
            "First Name",
            value=st.session_state.get('parsed_data', {}).get('first_name', ''),
            key="first_name_input"
        )

        last_name = st.text_input(
            "Last Name",
            value=st.session_state.get('parsed_data', {}).get('last_name', ''),
            key="last_name_input"
        )

        email = st.text_input(
            "Email",
            value=st.session_state.get('parsed_data', {}).get('email', ''),
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

        # File upload section placed here for better flow
        st.markdown("### Resume Upload")
        uploaded_file = st.file_uploader(
            "Upload your resume (DOCX or PDF)",
            type=['docx', 'pdf'],
            key="resume_uploader",
            help="Upload your resume for processing"
        )

        # Save button for manual edits
        if st.form_submit_button("Submit"):
            form_data = {
                'first_name': name.split()[0] if name else '',
                'last_name': ' '.join(name.split()[1:]) if name and len(name.split()) > 1 else '',
                'email': email,
                'phone': phone,
                'city': city,
                'state': state,
                'professional_level': prof_level,
                'date_created': current_time
            }

            file_content = None
            if uploaded_file:
                file_content = uploaded_file.getvalue()

            if send_to_webhook(form_data, file_content):
                st.success("✅ Information submitted successfully!")
            else:
                st.error("Failed to submit information. Please try again.")

def render_education():
    """Display education section with parsed data."""
    st.info("Education details will be populated from parsed resume data.")
    if 'parsed_data' in st.session_state and 'education' in st.session_state.parsed_data:
        st.write(st.session_state.parsed_data['education'])

def render_experience():
    """Display experience section with parsed data."""
    st.info("Experience details will be populated from parsed resume data.")
    if 'parsed_data' in st.session_state and 'experience' in st.session_state.parsed_data:
        st.write(st.session_state.parsed_data['experience'])

def render_skills():
    """Display skills section with parsed data."""
    st.info("Skills will be populated from parsed resume data.")
    if 'parsed_data' in st.session_state and 'skills' in st.session_state.parsed_data:
        st.write(st.session_state.parsed_data['skills'])