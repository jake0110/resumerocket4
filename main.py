import streamlit as st
import tempfile
import os
import logging
from utils.resume_parser import ResumeParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Streamlit app
st.set_page_config(
    page_title="Resume Builder",
    page_icon="📝",
    layout="wide"
)

# Updated roles list
ROLES = [
    "Individual Contributor",
    "Manager",
    "Client Manager",
    "Selling Partner or Principal",
    "Practice Leader"
]

# Main UI elements
st.title("Resume Builder")
st.markdown("""
Upload your resume and fill in your information:
- Personal details
- Professional experience
- Education history
- Skills and qualifications
""")

# Initialize session state for storing resume data
if 'personal_info' not in st.session_state:
    st.session_state.personal_info = {}
if 'education' not in st.session_state:
    st.session_state.education = []
if 'experience' not in st.session_state:
    st.session_state.experience = []
if 'skills' not in st.session_state:
    st.session_state.skills = []

# Contact Information Form
with st.form("contact_info"):
    st.subheader("Contact Information")
    name = st.text_input("Full Name*", key="name")
    email = st.text_input("Email Address*", key="email")
    phone = st.text_input("Phone Number (Optional)", key="phone")

    # Role Selection with updated options
    role = st.selectbox(
        "Select Role*",
        options=ROLES,
        key="role"
    )

    # File upload
    uploaded_file = st.file_uploader(
        "Upload your resume (DOCX)*",
        type=['docx'],
        help="Upload your resume in DOCX format"
    )

    submit_button = st.form_submit_button("Process Resume")

# Process the uploaded resume
if submit_button and uploaded_file and name and email and role:
    try:
        with st.spinner("Processing your resume..."):
            # Save uploaded file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

                try:
                    # Parse resume
                    parser = ResumeParser()
                    parsed_content = parser.parse_docx(tmp_file_path)

                    # Store parsed content in session state
                    if parsed_content.get('contact'):
                        st.session_state.personal_info = parsed_content['contact']
                    if parsed_content.get('education'):
                        st.session_state.education = parsed_content['education']
                    if parsed_content.get('experience'):
                        st.session_state.experience = parsed_content['experience']
                    if parsed_content.get('skills'):
                        st.session_state.skills = parsed_content['skills']

                    st.success("Resume processed successfully!")

                    # Clean up temporary file
                    os.unlink(tmp_file_path)

                except Exception as e:
                    logger.error(f"Error processing resume: {str(e)}")
                    st.error("Error processing resume. Please ensure you've uploaded a valid DOCX file.")
                    if os.path.exists(tmp_file_path):
                        os.unlink(tmp_file_path)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        st.error("An unexpected error occurred. Please try again.")

elif submit_button:
    if not name:
        st.error("Please enter your name")
    if not email:
        st.error("Please enter your email")
    if not role:
        st.error("Please select a role")
    if not uploaded_file:
        st.error("Please upload your resume")