import streamlit as st
import tempfile
import os
import base64
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import local modules after logging setup
try:
    from utils.pdf_generator import generate_pdf
    from utils.resume_parser import ResumeParser
    from components.forms import render_personal_info, render_education, render_experience, render_skills
    from components.preview import render_preview
    logger.info("Successfully imported all required modules")
except Exception as e:
    logger.error(f"Error importing modules: {str(e)}")
    raise

def main():
    try:
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

        # Load custom CSS
        try:
            with open('styles/custom.css') as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        except FileNotFoundError:
            logger.warning("Custom styles not found. Using default styling.")

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
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name
                        logger.info(f"Saved uploaded file to {tmp_file_path}")

                    # Parse the resume
                    parser = ResumeParser()
                    parsed_content = parser.parse_docx(tmp_file_path)
                    logger.info("Successfully parsed resume content")

                    # Store parsed content
                    st.session_state.parsed_resume = parsed_content

                    # Display parsed sections
                    with st.expander("📄 Parsed Resume Content", expanded=True):
                        for section, content in parsed_content['sections'].items():
                            if content and section != 'unknown':
                                st.subheader(f"📌 {section.title()}")
                                for item in content:
                                    st.write(f"• {item}")

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
        logger.info("Starting Resume Builder application")
        main()
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        st.error("Failed to start the application. Please check the logs for details.")