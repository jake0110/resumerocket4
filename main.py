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
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Starting ResumeRocket5 application")
        st.set_page_config(
            page_title="ResumeRocket5 - Resume Parser",
            layout="wide"
        )

        st.title("ResumeRocket5 - Resume Parser")
        st.write("Upload your resume and get structured information with AI-powered analysis")

        # File upload section with better error handling
        uploaded_file = st.file_uploader(
            "Upload your resume",
            type=['docx'],
            help="Upload a Word document (.docx)"
        )

        if uploaded_file:
            logger.info(f"Processing uploaded file: {uploaded_file.name}")

            # File size validation
            file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # Convert to MB
            if file_size > 10:
                st.error("File size exceeds 10MB limit. Please upload a smaller file.")
                logger.warning(f"File size {file_size}MB exceeds limit")
                return

            # Initialize tmp_file_path as None
            tmp_file_path = None
            try:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                    logger.debug(f"Saved temporary file at: {tmp_file_path}")

                # Initialize parser and parse document
                parser = ResumeParser()
                parsed_data = parser.parse_docx(tmp_file_path)

                if parsed_data:
                    st.success("Resume successfully parsed!")

                    # Display Contact Information
                    st.subheader("Contact Information")
                    contact_info = parsed_data.get('contact', {})
                    missing_fields = []

                    # Create columns for better layout
                    col1, col2 = st.columns(2)

                    with col1:
                        # Name field
                        if contact_info.get('name'):
                            st.write(f"**Name:** {contact_info['name']}")
                            logger.debug(f"Extracted name: {contact_info['name']}")
                        else:
                            missing_fields.append('name')

                        # Email field
                        if contact_info.get('email'):
                            st.write(f"**Email:** {contact_info['email']}")
                            logger.debug(f"Extracted email: {contact_info['email']}")
                        else:
                            missing_fields.append('email')

                    with col2:
                        # Phone field
                        if contact_info.get('phone'):
                            st.write(f"**Phone:** {contact_info['phone']}")
                            logger.debug(f"Extracted phone: {contact_info['phone']}")
                        else:
                            missing_fields.append('phone')

                        # Location field
                        if contact_info.get('location'):
                            st.write(f"**Location:** {contact_info['location']}")
                            logger.debug(f"Extracted location: {contact_info['location']}")
                        else:
                            missing_fields.append('location')

                    # Show missing fields warning with more details
                    if missing_fields:
                        warning_msg = "Some information could not be extracted: " + ", ".join(missing_fields)
                        st.warning(warning_msg)
                        logger.warning(f"Missing fields in contact info: {missing_fields}")

                        # Provide guidance for missing fields
                        st.info("💡 Tip: Make sure your resume includes these details in a clear format.")

                    # Display parsed content for debugging (collapsible)
                    with st.expander("Debug: View Parsed Content"):
                        st.json(parsed_data)

            except Exception as e:
                error_msg = f"Error processing document: {str(e)}"
                logger.error(error_msg)
                logger.error(traceback.format_exc())
                st.error(error_msg)
                st.error("Please ensure your document is properly formatted and try again.")

            finally:
                # Cleanup temporary file
                if tmp_file_path:
                    try:
                        os.unlink(tmp_file_path)
                        logger.debug("Temporary file cleaned up")
                    except Exception as e:
                        logger.error(f"Error cleaning up temporary file: {str(e)}")

    except Exception as e:
        error_msg = f"Application error: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        st.error("An unexpected error occurred. Please try again.")

if __name__ == "__main__":
    main()