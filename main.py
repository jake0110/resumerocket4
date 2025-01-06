import os
import sys
import tempfile
import logging
import traceback
import streamlit as st
from utils.resume_parser import ResumeParser

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    try:
        st.set_page_config(
            page_title="ResumeRocket5 - Resume Parser",
            layout="wide"
        )

        st.title("ResumeRocket5 - Resume Parser")
        st.write("Upload your resume and get structured information with AI-powered analysis")

        # File upload
        uploaded_file = st.file_uploader(
            "Upload your resume",
            type=['docx'],
            help="Upload a Word document (.docx)"
        )

        if uploaded_file:
            logger.info(f"Processing uploaded file: {uploaded_file.name}")

            try:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                    logger.info(f"Saved temporary file at: {tmp_file_path}")

                # Initialize parser and parse document
                parser = ResumeParser()
                parsed_data = parser.parse_docx(tmp_file_path)

                if parsed_data:
                    st.success("Resume successfully parsed!")

                    # Display Contact Information
                    st.subheader("Contact Information")
                    contact_info = parsed_data.get('contact', {})

                    if contact_info.get('name'):
                        st.write(f"**Name:** {contact_info['name']}")
                    if contact_info.get('email'):
                        st.write(f"**Email:** {contact_info['email']}")
                    if contact_info.get('phone'):
                        st.write(f"**Phone:** {contact_info['phone']}")

                    # Check for missing fields
                    missing = []
                    for field in ['name', 'email', 'phone']:
                        if not contact_info.get(field):
                            missing.append(field)
                    if missing:
                        st.warning(f"Missing information: {', '.join(missing)}")
                        logger.warning(f"Missing fields in contact info: {missing}")

                    # Display Experience
                    if parsed_data.get('experience'):
                        st.subheader("Experience")
                        for exp in parsed_data['experience']:
                            with st.expander(exp.get('company', 'Experience Entry')):
                                st.write(f"**Position:** {exp.get('position', '')}")
                                st.write(f"**Duration:** {exp.get('duration', '')}")
                                if exp.get('description'):
                                    st.write("**Description:**")
                                    for desc in exp['description']:
                                        st.write(f"- {desc}")

            except Exception as e:
                logger.error(f"Error processing document: {str(e)}")
                logger.error(traceback.format_exc())
                st.error(f"Error processing document: {str(e)}")

            finally:
                # Cleanup temporary file
                if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
                    try:
                        os.unlink(tmp_file_path)
                        logger.info("Temporary file cleaned up")
                    except Exception as e:
                        logger.error(f"Error cleaning up temporary file: {str(e)}")

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        logger.error(traceback.format_exc())
        st.error("An unexpected error occurred. Please try again.")

if __name__ == "__main__":
    main()