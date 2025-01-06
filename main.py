import os
import sys
import tempfile
import logging
import streamlit as st
from utils.resume_parser import ResumeParser

# Configure logging to both file and console
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Initialize variables
        tmp_file_path = None

        # Basic page config
        st.set_page_config(
            page_title="ResumeRocket5 - Resume Parser",
            layout="wide"
        )

        # Main content
        st.title("ResumeRocket5 - Resume Parser")
        st.write("Upload your resume and get structured information with AI-powered analysis.")

        # OpenAI API Key input
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Required for AI-powered resume analysis"
        )

        # File upload
        uploaded_file = st.file_uploader(
            "Upload your resume",
            type=['docx'],
            help="Upload a Word document (.docx)"
        )

        if uploaded_file is not None:
            logger.info(f"File uploaded: {uploaded_file.name}")

            if not api_key:
                st.warning("Please enter your OpenAI API Key to enable resume analysis.")
                return

            try:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                    logger.debug(f"Saved uploaded file to {tmp_file_path}")

                    with st.spinner("Processing your resume..."):
                        # Parse resume
                        parser = ResumeParser(openai_api_key=api_key)
                        parsed_data = parser.parse_docx(tmp_file_path)
                        logger.info("Successfully parsed resume content")

                        if parsed_data:
                            st.success("✅ Resume successfully parsed!")

                            # Display basic information first
                            if 'contact' in parsed_data:
                                st.subheader("Contact Information")
                                st.write(parsed_data['contact'])

                            if 'experience' in parsed_data:
                                st.subheader("Professional Experience")
                                for exp in parsed_data['experience']:
                                    st.markdown(f"**{exp.get('company', '')}**")
                                    st.markdown(f"*{exp.get('position', '')}* ({exp.get('duration', '')})")
                                    for bullet in exp.get('description', []):
                                        st.markdown(f"- {bullet}")

                            if 'education' in parsed_data:
                                st.subheader("Education")
                                for edu in parsed_data['education']:
                                    st.markdown(f"**{edu.get('institution', '')}**")
                                    st.markdown(f"{edu.get('degree', '')} - {edu.get('graduation_year', '')}")

                            if 'skills' in parsed_data:
                                st.subheader("Skills")
                                st.write(", ".join(parsed_data['skills']))

                            # Display AI analysis if available
                            if 'ai_analysis' in parsed_data:
                                st.success("✅ AI Analysis completed!")
                                st.subheader("AI Analysis")

                                analysis = parsed_data['ai_analysis']
                                if 'error' not in analysis:
                                    st.markdown("#### Experience Level")
                                    st.write(analysis.get('experience_level', 'Not specified'))

                                    st.markdown("#### Key Skills")
                                    st.write(", ".join(analysis.get('key_skills', [])))

                                    st.markdown("#### Experience Summary")
                                    st.write(analysis.get('experience_summary', ''))

                                    st.markdown("#### Best Suited Roles")
                                    st.write(", ".join(analysis.get('best_suited_roles', [])))

                                    if 'improvement_suggestions' in analysis:
                                        st.markdown("#### Improvement Suggestions")
                                        for suggestion in analysis['improvement_suggestions']:
                                            st.markdown(f"- {suggestion}")
                                else:
                                    st.warning("AI analysis encountered an error. Basic parsing was still successful.")

            except Exception as e:
                logger.error(f"Error processing resume: {str(e)}", exc_info=True)
                st.error(f"Error processing resume: {str(e)}")

            finally:
                # Clean up temporary file
                if tmp_file_path:
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