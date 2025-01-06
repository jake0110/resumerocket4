import streamlit as st
from utils.resume_parser import ResumeParser
import tempfile
import os
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
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
    st.title("ResumeRocket5 - Resume Parser")
    st.write("Upload your resume and get structured information with AI-powered analysis.")

    # Initialize session state
    init_session_state()

    # File upload section
    uploaded_file = st.file_uploader("Upload your resume", type=['docx'])

    if uploaded_file is not None:
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

                try:
                    # Initialize parser and parse the resume
                    parser = ResumeParser()
                    parsed_data = parser.parse_docx(tmp_file_path)

                    # Display results in organized sections
                    st.subheader("Parsed Resume Data")

                    # Display Contact Information
                    if 'contact' in parsed_data:
                        st.write("### Contact Information")
                        contact = parsed_data["contact"]
                        for field, value in contact.items():
                            st.write(f"**{field.title()}:** {value}")

                    # Display Experience
                    if 'experience' in parsed_data:
                        st.write("### Professional Experience")
                        for exp in parsed_data["experience"]:
                            st.write(f"**{exp.get('company', '')}**")
                            st.write(f"*{exp.get('position', '')} ({exp.get('duration', '')})*")
                            if exp.get('description'):
                                for bullet in exp['description']:
                                    st.write(f"- {bullet}")
                            st.write("")

                    # Display Education
                    if 'education' in parsed_data:
                        st.write("### Education")
                        for edu in parsed_data["education"]:
                            st.write(f"**{edu.get('institution', '')}**")
                            st.write(f"{edu.get('degree', '')} - {edu.get('graduation_year', '')}")
                            st.write("")

                    # Display Skills
                    if 'skills' in parsed_data:
                        st.write("### Skills")
                        st.write(", ".join(parsed_data["skills"]))

                    # Display AI Analysis if available
                    if 'ai_analysis' in parsed_data:
                        st.write("### AI Analysis")
                        analysis = parsed_data["ai_analysis"]
                        st.write(f"**Experience Level:** {analysis.get('experience_level', 'N/A')}")
                        st.write(f"**Key Skills:** {', '.join(analysis.get('key_skills', []))}")
                        st.write(f"**Experience Summary:** {analysis.get('experience_summary', 'N/A')}")
                        st.write("**Best Suited Roles:**")
                        for role in analysis.get('best_suited_roles', []):
                            st.write(f"- {role}")
                        st.write("**Improvement Suggestions:**")
                        for suggestion in analysis.get('improvement_suggestions', []):
                            st.write(f"- {suggestion}")

                    # Update session state with parsed data
                    st.session_state.personal_info = parsed_data.get('contact', {})
                    st.session_state.education = parsed_data.get('education', [])
                    st.session_state.experience = parsed_data.get('experience', [])
                    st.session_state.skills = parsed_data.get('skills', [])

                except Exception as e:
                    st.error(f"Error parsing resume: {str(e)}")
                    logger.error(f"Resume parsing error: {str(e)}", exc_info=True)

                finally:
                    # Clean up temporary file
                    try:
                        os.unlink(tmp_file_path)
                    except Exception as e:
                        logger.error(f"Error cleaning up temporary file: {str(e)}")

        except Exception as e:
            st.error(f"Error handling uploaded file: {str(e)}")
            logger.error(f"File handling error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()