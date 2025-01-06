import os
import sys
import tempfile
import logging
import traceback
from openai import OpenAI, OpenAIError
import streamlit as st

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

def test_openai_connection():
    """Test OpenAI API connection."""
    try:
        api_key = st.text_input("Enter your OpenAI API Key", type="password", key="openai_api_key")
        if api_key and st.button("Test OpenAI Connection"):
            try:
                if not api_key.startswith('sk-') or len(api_key) < 20:
                    st.error("Invalid API key format. Please enter a valid OpenAI API key.")
                    return False

                client = OpenAI(api_key=api_key)
                logger.info("Attempting to connect to OpenAI API")
                st.info("Testing OpenAI API connection...")

                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{
                        "role": "user",
                        "content": "Hello, this is a test message. Please respond with 'OpenAI connection successful!'"
                    }],
                    max_tokens=50
                )
                st.success(f"OpenAI API Response: {response.choices[0].message.content}")
                logger.info("OpenAI API test successful")
                return True
            except OpenAIError as e:
                error_msg = f"OpenAI API Error: {str(e)}"
                logger.error(error_msg)
                st.error(error_msg)
                return False
            except Exception as e:
                error_msg = f"Unexpected error during OpenAI API test: {str(e)}"
                logger.error(error_msg)
                st.error(error_msg)
                return False
    except Exception as e:
        error_msg = f"Error in test_openai_connection: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)
        return False

def main():
    try:
        logger.info("Starting ResumeRocket5 application")
        st.set_page_config(
            page_title="ResumeRocket5 - Resume Analyzer",
            layout="wide"
        )

        st.title("ResumeRocket5 - Resume Analyzer")
        st.write("Upload your resume for intelligent analysis using Airparser and OpenAI")

        # Add OpenAI test section
        st.subheader("OpenAI API Test")
        api_test_result = test_openai_connection()
        if api_test_result:
            st.success("✅ OpenAI API connection verified")

        # File upload section with error handling
        uploaded_file = st.file_uploader(
            "Upload your resume",
            type=['docx', 'pdf'],  # Added PDF support for Airparser
            help="Upload a Word document (.docx) or PDF file"
        )

        if uploaded_file:
            logger.info(f"Processing uploaded file: {uploaded_file.name}")

            # File size validation
            file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # Convert to MB
            if file_size > 10:
                st.error("File size exceeds 10MB limit. Please upload a smaller file.")
                logger.warning(f"File size {file_size}MB exceeds limit")
                return

            # Save uploaded file temporarily
            tmp_file_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                    logger.debug(f"Saved temporary file at: {tmp_file_path}")

                st.success("Resume uploaded successfully!")
                st.info("Your resume will be processed through Airparser for detailed analysis.")

                # Display file information
                st.write({
                    "Filename": uploaded_file.name,
                    "File size": f"{file_size:.2f} MB",
                    "File type": uploaded_file.type
                })

                st.info("Processing through Airparser... This feature will be available soon.")

            except Exception as e:
                error_msg = f"Error processing document: {str(e)}"
                logger.error(error_msg)
                logger.error(traceback.format_exc())
                st.error(error_msg)
                st.error("Please ensure your document is properly formatted and try again.")

            finally:
                # Cleanup temporary file
                if tmp_file_path and os.path.exists(tmp_file_path):
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