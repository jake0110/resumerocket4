import streamlit as st
import os
import tempfile
from utils.resume_parser import ResumeParser
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_session_state():
    """Initialize session state variables if they don't exist"""
    if 'personal_info' not in st.session_state:
        st.session_state.personal_info = {}
    if 'education' not in st.session_state:
        st.session_state.education = []
    if 'experience' not in st.session_state:
        st.session_state.experience = []
    if 'skills' not in st.session_state:
        st.session_state.skills = []

def main():
    try:
        # Basic page config
        st.set_page_config(
            page_title="ResumeRocket5 - Resume Parser",
            layout="wide"
        )

        # Initialize session state
        init_session_state()

        # Main content
        st.title("ResumeRocket5 - Resume Parser")
        st.write("Upload your resume and get structured information with AI-powered analysis.")

        # OpenAI API Key input
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Required for AI-powered resume analysis"
        )

        # File upload section
        uploaded_file = st.file_uploader(
            "Upload your resume",
            type=['docx'],
            help="Upload a Word document (.docx) to analyze"
        )

        if uploaded_file is not None:
            # Verify API key presence
            if not api_key:
                st.warning("Please enter your OpenAI API Key to enable resume analysis.")
                return

            try:
                with st.spinner("Processing your resume..."):
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name

                        # Initialize parser with API key and parse resume
                        parser = ResumeParser(openai_api_key=api_key)
                        parsed_data = parser.parse_docx(tmp_file_path)

                        if parsed_data:
                            st.success("✅ Resume successfully parsed!")

                            # Display parsed information
                            if 'contact' in parsed_data:
                                st.subheader("Contact Information")
                                for field, value in parsed_data['contact'].items():
                                    st.write(f"**{field.title()}:** {value}")

                            if 'experience' in parsed_data:
                                st.subheader("Professional Experience")
                                for exp in parsed_data['experience']:
                                    st.write(f"**{exp.get('company', '')}**")
                                    st.write(f"*{exp.get('position', '')} ({exp.get('duration', '')})*")
                                    for bullet in exp.get('description', []):
                                        st.write(f"• {bullet}")
                                    st.write("---")

                            if 'education' in parsed_data:
                                st.subheader("Education")
                                for edu in parsed_data['education']:
                                    st.write(f"**{edu.get('institution', '')}**")
                                    st.write(f"{edu.get('degree', '')} ({edu.get('graduation_year', '')})")
                                    st.write("---")

                            if 'skills' in parsed_data:
                                st.subheader("Skills")
                                st.write(", ".join(parsed_data['skills']))

                            if 'ai_analysis' in parsed_data:
                                st.subheader("AI Analysis")
                                analysis = parsed_data['ai_analysis']

                                st.info(f"**Experience Level:** {analysis.get('experience_level', 'N/A')}")
                                st.write(f"**Key Skills:** {', '.join(analysis.get('key_skills', []))}")
                                st.write(f"**Experience Summary:** {analysis.get('experience_summary', 'N/A')}")

                                st.write("**Best Suited Roles:**")
                                for role in analysis.get('best_suited_roles', []):
                                    st.write(f"• {role}")

                                st.write("**Improvement Suggestions:**")
                                for suggestion in analysis.get('improvement_suggestions', []):
                                    st.write(f"• {suggestion}")

            except Exception as e:
                logger.error(f"Error processing resume: {str(e)}", exc_info=True)
                st.error(f"Error processing resume: {str(e)}")

            finally:
                # Clean up temporary file
                if 'tmp_file_path' in locals():
                    try:
                        os.unlink(tmp_file_path)
                    except Exception as e:
                        logger.error(f"Error cleaning up temporary file: {str(e)}")

    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        st.error("An unexpected error occurred. Please try again.")

if __name__ == "__main__":
    main()