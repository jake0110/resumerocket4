import streamlit as st
import tempfile
import os
import base64
import logging
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Import local modules with detailed error handling
try:
    logger.info(f"Python path: {sys.path}")
    logger.info("Attempting to import local modules...")
    from utils.pdf_generator import generate_pdf
    logger.info("Successfully imported pdf_generator")
    from utils.resume_parser import ResumeParser
    logger.info("Successfully imported resume_parser")
    from components.forms import render_personal_info, render_education, render_experience, render_skills
    logger.info("Successfully imported form components")
    from components.preview import render_preview
    logger.info("Successfully imported preview component")
except ImportError as e:
    logger.error(f"Failed to import required modules: {str(e)}")
    logger.error(f"Current directory: {os.getcwd()}")
    logger.error(f"Directory contents: {os.listdir('.')}")
    raise
except Exception as e:
    logger.error(f"Unexpected error during imports: {str(e)}")
    raise

def main():
    try:
        logger.info("Starting Resume Builder application")
        st.set_page_config(
            page_title="Resume Builder",
            page_icon="📄",
            layout="wide"
        )
        logger.info("Page config set successfully")

        # Initialize session state
        if 'personal_info' not in st.session_state:
            st.session_state.personal_info = {}
        if 'education' not in st.session_state:
            st.session_state.education = [{}]
        if 'experience' not in st.session_state:
            st.session_state.experience = [{}]
        if 'skills' not in st.session_state:
            st.session_state.skills = []
        if 'parsed_resume' not in st.session_state:
            st.session_state.parsed_resume = None
        logger.info("Session state initialized")

        # Load custom CSS
        try:
            css_path = project_root / 'styles' / 'custom.css'
            with open(css_path) as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
                logger.info("Custom CSS loaded successfully")
        except FileNotFoundError as e:
            logger.warning(f"Custom styles not found at {css_path}: {str(e)}")
            pass

        st.title("Professional Resume Builder")

        # Create two columns: Form and Preview
        col1, col2 = st.columns([3, 2])

        with col1:
            st.header("Enter Your Information")

            # File Upload Section with parser integration
            uploaded_file = st.file_uploader(
                "Upload existing resume (DOCX)",
                type=['docx'],
                help="Upload your existing resume in DOCX format"
            )

            if uploaded_file is not None:
                try:
                    logger.info(f"Processing uploaded file: {uploaded_file.name}")
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name
                        logger.info(f"Saved uploaded file to {tmp_file_path}")

                    # Parse the resume
                    parser = ResumeParser()
                    parsed_content = parser.parse_docx(tmp_file_path)
                    logger.info("Successfully parsed resume content")

                    # Store parsed content in session state
                    st.session_state.parsed_resume = parsed_content
                    logger.info("Stored parsed content in session state")

                    # Update form fields with parsed content if available
                    if parsed_content.get('contact'):
                        st.session_state.personal_info = parsed_content['contact']
                    if parsed_content.get('education'):
                        st.session_state.education = parsed_content['education']
                    if parsed_content.get('experience'):
                        st.session_state.experience = parsed_content['experience']
                    if parsed_content.get('skills'):
                        st.session_state.skills = [
                            skill for category in parsed_content['skills'].values()
                            for skill in category
                        ]
                    logger.info("Updated session state with parsed content")

                    # Display parsed sections
                    with st.expander("📄 Parsed Resume Content", expanded=True):
                        st.json(parsed_content)

                    # Clean up temporary file
                    os.unlink(tmp_file_path)
                    logger.info("Cleaned up temporary file")

                except Exception as e:
                    logger.error(f"Error processing resume: {str(e)}")
                    st.error(f"Error processing resume: {str(e)}")

            # Template Selection
            template = st.selectbox(
                "Select Resume Template",
                ["Professional", "Modern", "Classic"],
                key="template"
            )

            # Tabs for different sections
            tabs = st.tabs(["Personal Info", "Education", "Experience", "Skills"])

            with tabs[0]:
                render_personal_info()

            with tabs[1]:
                render_education()

            with tabs[2]:
                render_experience()

            with tabs[3]:
                render_skills()

        with col2:
            st.header("Resume Preview")
            render_preview(template)

            if st.button("Generate PDF"):
                try:
                    pdf_bytes = generate_pdf(
                        st.session_state.personal_info,
                        st.session_state.education,
                        st.session_state.experience,
                        st.session_state.skills,
                        template
                    )

                    b64_pdf = base64.b64encode(pdf_bytes).decode()
                    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="resume.pdf">Download PDF</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    logger.info("Successfully generated PDF")
                except Exception as e:
                    logger.error(f"Error generating PDF: {str(e)}")
                    st.error(f"Error generating PDF: {str(e)}")

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        st.error("Failed to start the application. Please check the logs for details.")