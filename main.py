import os
import sys
import tempfile
import logging
import traceback
import streamlit as st
from utils.resume_parser import ResumeParser

# Configure logging with more detailed format
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
    if 'parsed_data' not in st.session_state:
        st.session_state.parsed_data = None
    if 'parsing_error' not in st.session_state:
        st.session_state.parsing_error = None

def main():
    try:
        logger.info("Starting Streamlit application")
        initialize_session_state()

        # Basic page config
        st.set_page_config(
            page_title="ResumeRocket5 - Resume Parser",
            layout="wide"
        )
        logger.info("Page configuration set")

        st.title("ResumeRocket5 - Resume Parser")
        st.write("Upload your resume and get structured information with AI-powered analysis")

        # File upload
        uploaded_file = st.file_uploader(
            "Upload your resume",
            type=['docx'],
            help="Upload a Word document (.docx)"
        )

        if uploaded_file is not None:
            logger.info(f"Processing uploaded file: {uploaded_file.name}")
            tmp_file_path = None

            try:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                    logger.info(f"Saved temporary file at: {tmp_file_path}")

                try:
                    # Initialize parser without OpenAI first
                    parser = ResumeParser()
                    logger.info("Initialized ResumeParser")

                    # Parse the document (basic parsing)
                    parsed_data = parser.parse_docx(tmp_file_path)

                    if parsed_data:
                        st.success("✅ Resume successfully parsed!")

                        # Display parsed content
                        st.subheader("Contact Information")
                        if 'contact' in parsed_data:
                            contact_info = parsed_data['contact']

                            # Check for missing fields
                            missing_fields = []
                            for field in ['name', 'email', 'phone']:
                                if not contact_info.get(field):
                                    missing_fields.append(field)

                            if missing_fields:
                                st.warning(f"Missing information: {', '.join(missing_fields)}")
                                logger.warning(f"Missing contact fields: {missing_fields}")

                            # Display available contact info
                            for field in ['name', 'email', 'phone']:
                                if contact_info.get(field):
                                    st.markdown(f"**{field.title()}:** {contact_info[field]}")

                        # Experience Section
                        if 'experience' in parsed_data and parsed_data['experience']:
                            st.subheader("Experience")
                            for exp in parsed_data['experience']:
                                with st.expander(f"{exp.get('company', 'Experience Entry')}"):
                                    st.write(f"**Position:** {exp.get('position', 'N/A')}")
                                    st.write(f"**Duration:** {exp.get('duration', 'N/A')}")
                                    if exp.get('description'):
                                        st.write("**Description:**")
                                        for desc in exp['description']:
                                            st.write(f"- {desc}")

                        # Optional AI Analysis Section
                        st.markdown("---")
                        with st.expander("AI-Powered Analysis (Optional)"):
                            st.info("💡 AI analysis is optional and separate from basic parsing.")
                            api_key = st.text_input(
                                "OpenAI API Key",
                                type="password",
                                help="Optional: Provide API key for AI-powered insights"
                            )

                            if api_key and st.button("Run AI Analysis"):
                                try:
                                    parser.api_key = api_key
                                    logger.info("Starting AI analysis")
                                    enhanced_data = parser.enhance_with_ai(parsed_data)

                                    if enhanced_data.get('ai_analysis'):
                                        st.success("✅ AI Analysis completed!")
                                        st.json(enhanced_data['ai_analysis'])
                                except Exception as e:
                                    logger.error(f"AI analysis failed: {str(e)}")
                                    st.error(f"AI analysis failed: {str(e)}")

                    else:
                        st.warning("No content found in the document")
                        logger.warning("Document parsing returned no content")

                except Exception as e:
                    st.error(f"Error processing document: {str(e)}")
                    logger.error(f"Document processing failed: {str(e)}")
                    logger.error(traceback.format_exc())

            finally:
                # Cleanup
                if tmp_file_path and os.path.exists(tmp_file_path):
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