import os
import sys
import tempfile
import logging
import streamlit as st
from utils.resume_parser import ResumeParser

# Configure logging for both file and console output
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log', mode='w')
    ]
)
logger = logging.getLogger(__name__)

def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    logger.debug("Initializing session state")
    session_vars = {
        'personal_info': {},
        'education': [],
        'experience': [],
        'skills': [],
        'parsed_resume': None,
        'parsing_error': None,
        'api_key_provided': False
    }

    for var, default in session_vars.items():
        if var not in st.session_state:
            st.session_state[var] = default
            logger.debug(f"Initialized {var} in session state")

def main():
    try:
        logger.info("Starting main application")
        initialize_session_state()

        # Basic page config
        st.set_page_config(
            page_title="ResumeRocket5 - Resume Parser",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        logger.debug("Page configuration set")

        # Main content
        st.title("ResumeRocket5 - Resume Parser")
        st.write("Upload your resume and get structured information with AI-powered analysis")

        # File upload section
        uploaded_file = st.file_uploader(
            "Upload your resume",
            type=['docx'],
            help="Upload a Word document (.docx)"
        )

        if uploaded_file is not None:
            logger.info(f"File uploaded: {uploaded_file.name}")
            file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # Size in MB
            logger.debug(f"File size: {file_size:.2f}MB")

            if file_size > 10:
                st.error("File size exceeds 10MB limit")
                return

            try:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                    logger.debug(f"Saved uploaded file to {tmp_file_path}")

                # Initialize parser without OpenAI integration first
                parser = ResumeParser()
                logger.debug("Initialized ResumeParser")

                with st.spinner("Parsing resume..."):
                    # Basic parsing without OpenAI
                    logger.info("Starting resume parsing")
                    parsed_data = parser.parse_docx(tmp_file_path)
                    logger.info("Basic parsing completed")

                    # Display parsed content
                    if parsed_data:
                        st.success("✅ Resume successfully parsed!")
                        logger.debug(f"Parsed data: {parsed_data}")

                        if 'contact' in parsed_data:
                            st.subheader("Contact Information")
                            contact_info = parsed_data['contact']
                            logger.debug(f"Contact info: {contact_info}")

                            # Check for missing fields
                            missing_fields = []
                            for field in ['name', 'email', 'phone']:
                                if not contact_info.get(field):
                                    missing_fields.append(field)

                            if missing_fields:
                                logger.warning(f"Missing contact fields: {missing_fields}")
                                st.warning(f"Missing information: {', '.join(missing_fields)}")

                            # Display contact info in a clean format
                            if contact_info.get('name'):
                                st.markdown(f"**Name:** {contact_info['name']}")
                            if contact_info.get('email'):
                                st.markdown(f"**Email:** {contact_info['email']}")
                            if contact_info.get('phone'):
                                st.markdown(f"**Phone:** {contact_info['phone']}")

                        # Optional AI Analysis Section
                        st.markdown("---")
                        with st.expander("AI-Powered Analysis (Optional)"):
                            api_key = st.text_input(
                                "Enter OpenAI API Key for enhanced analysis",
                                type="password",
                                help="Optional: Provide API key for AI-powered analysis"
                            )

                            if api_key:
                                if st.button("Run AI Analysis"):
                                    try:
                                        parser.api_key = api_key  # Set API key
                                        logger.info("Starting AI analysis")
                                        enhanced_data = parser.enhance_with_ai(parsed_data)
                                        if enhanced_data.get('ai_analysis'):
                                            st.success("✅ AI Analysis completed!")
                                            st.json(enhanced_data['ai_analysis'])
                                            logger.info("AI analysis completed successfully")
                                    except Exception as e:
                                        logger.error(f"AI analysis failed: {str(e)}", exc_info=True)
                                        st.error(f"AI analysis failed: {str(e)}")

            except Exception as e:
                logger.error(f"Error processing resume: {str(e)}", exc_info=True)
                st.error(f"Error processing resume: {str(e)}")

            finally:
                # Clean up temporary file
                if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
                    try:
                        os.unlink(tmp_file_path)
                        logger.debug("Cleaned up temporary file")
                    except Exception as e:
                        logger.error(f"Error cleaning up temporary file: {str(e)}")

    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        st.error("An unexpected error occurred. Please try again.")

if __name__ == "__main__":
    logger.info("Starting main application")
    main()