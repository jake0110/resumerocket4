import streamlit as st
import tempfile
import os
import base64
import logging
import sys
from pathlib import Path

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,  # Change to DEBUG for more verbose logging
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Add the project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))
logger.debug(f"Added {project_root} to Python path")
logger.debug(f"Current Python path: {sys.path}")

try:
    # Import local modules
    logger.debug("Attempting to import local modules...")
    from utils.pdf_generator import generate_pdf
    from utils.resume_parser import ResumeParser
    from components.preview import render_preview
    from components.forms import render_personal_info, render_education, render_experience, render_skills
    logger.debug("Successfully imported all local modules")
except Exception as e:
    logger.error(f"Failed to import modules: {str(e)}", exc_info=True)
    raise

def main():
    try:
        logger.info("Starting Resume Builder application")
        st.set_page_config(
            page_title="Resume Builder",
            page_icon="📄",
            layout="wide"
        )

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

        logger.debug("Session state initialized")

        # Load custom CSS
        try:
            css_path = project_root / 'styles' / 'custom.css'
            logger.debug(f"Loading CSS from {css_path}")
            with open(css_path) as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        except Exception as e:
            logger.warning(f"Could not load custom CSS: {str(e)}")

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
                        logger.debug(f"Saved uploaded file to {tmp_file_path}")

                    # Parse the resume
                    parser = ResumeParser()
                    parsed_content = parser.parse_docx(tmp_file_path)
                    logger.info("Successfully parsed resume content")
                    logger.debug(f"Parsed content: {parsed_content}")

                    # Store parsed content in session state
                    st.session_state.parsed_resume = parsed_content

                    # Update form fields with parsed content if available
                    if parsed_content.get('contact'):
                        st.session_state.personal_info = parsed_content['contact']
                    if parsed_content.get('education'):
                        st.session_state.education = parsed_content['education']
                    if parsed_content.get('experience'):
                        st.session_state.experience = parsed_content['experience']
                    if parsed_content.get('skills'):
                        st.session_state.skills = parsed_content['skills']

                    # Display success message
                    st.success("✅ Resume successfully parsed! Form fields have been updated.")

                    # Clean up temporary file
                    os.unlink(tmp_file_path)
                    logger.debug("Cleaned up temporary file")

                except Exception as e:
                    logger.error(f"Error processing resume: {str(e)}", exc_info=True)
                    st.error(f"Error processing resume: {str(e)}")

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
            template = st.selectbox(
                "Select Resume Template",
                ["Professional", "Modern", "Classic"],
                key="template"
            )
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
                except Exception as e:
                    logger.error(f"Error generating PDF: {str(e)}", exc_info=True)
                    st.error(f"Error generating PDF: {str(e)}")

    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()