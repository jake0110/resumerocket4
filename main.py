import os
import sys
import tempfile
import logging
from typing import Optional

# Configure logging first
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

logger.debug("Starting application...")

# Import required packages with error handling
try:
    logger.debug("Importing required packages...")
    import streamlit as st
    from openai import OpenAI
    logger.debug("Successfully imported all required packages")
except ImportError as e:
    logger.error(f"Failed to import required packages: {str(e)}")
    sys.exit(1)

def test_openai_connection(api_key: Optional[str] = None) -> bool:
    """Test OpenAI API connection."""
    if not api_key:
        return False

    try:
        if not api_key.startswith('sk-'):
            st.error("Invalid API key format. Please enter a valid OpenAI API key.")
            return False

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": "Test connection"
            }],
            max_tokens=10
        )
        return True
    except Exception as e:
        logger.error(f"OpenAI API Error: {str(e)}")
        st.error(f"OpenAI API Error: {str(e)}")
        return False

def main():
    """Main application entry point."""
    try:
        logger.debug("Setting up Streamlit page configuration...")
        # Configure page
        st.set_page_config(
            page_title="ResumeRocket5 - Resume Analyzer",
            layout="wide"
        )

        st.title("ResumeRocket5 - Resume Analyzer")
        st.write("Upload your resume for intelligent analysis using Airparser and OpenAI")

        # Personal Information Form
        st.subheader("Personal Information")
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name", placeholder="John Doe")
            email = st.text_input("Email", placeholder="john@example.com")
            phone = st.text_input("Phone", placeholder="(555) 123-4567")
            city = st.text_input("City", placeholder="New York")
        
        with col2:
            states = ["Select State", "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
            state = st.selectbox("State", states)
            
            role_types = ["Select Role Type", "Entry Level", "Individual Contributor", "Team Lead", "Manager", "Director", "Vice President", "Executive"]
            role_type = st.selectbox("Role Type", role_types)

        # OpenAI API Test Section
        st.subheader("OpenAI API Test")
        api_key = st.text_input("Enter your OpenAI API Key", type="password")

        if st.button("Test Connection"):
            if test_openai_connection(api_key):
                st.success("✅ OpenAI API connection verified")

        # File Upload Section
        st.subheader("Resume Upload")
        st.info("✨ We're transitioning to Airparser for enhanced resume parsing!")

        uploaded_file = st.file_uploader(
            "Upload your resume",
            type=['docx', 'pdf'],
            help="Upload a Word document (.docx) or PDF file"
        )

        if uploaded_file:
            file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # Size in MB

            if file_size > 10:
                st.error("File size exceeds 10MB limit. Please upload a smaller file.")
                return

            tmp_file_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                    logger.debug(f"Saved uploaded file to {tmp_file_path}")

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
                logger.error(f"Error processing file: {str(e)}")
                st.error("Error processing your file. Please try again.")

            finally:
                if tmp_file_path and os.path.exists(tmp_file_path):
                    try:
                        os.unlink(tmp_file_path)
                        logger.debug("Cleaned up temporary file")
                    except Exception as e:
                        logger.error(f"Error cleaning up temporary file: {str(e)}")

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error("An unexpected error occurred. Please try again.")

if __name__ == "__main__":
    logger.debug("Starting main application...")
    main()