import os
import sys
import tempfile
import logging
import traceback

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

try:
    import streamlit as st
except ImportError as e:
    logger.error(f"Failed to import streamlit: {str(e)}")
    raise

def main():
    try:
        logger.info("Starting ResumeRocket5 application")
        st.set_page_config(
            page_title="ResumeRocket5 - Resume Parser",
            layout="wide"
        )

        st.title("ResumeRocket5 - Resume Parser")
        st.write("Upload your resume and get structured information with AI-powered analysis")

        # File upload section with error handling
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

                st.success("Resume uploaded successfully!")
                st.info("Parse functionality is currently being upgraded. Please check back soon for enhanced features.")

                # Display raw file information for debugging
                with st.expander("Debug: File Information"):
                    st.write({
                        "Filename": uploaded_file.name,
                        "File size": f"{file_size:.2f} MB",
                        "File type": uploaded_file.type
                    })

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