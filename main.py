import streamlit as st
from utils.resume_parser import ResumeParser
import tempfile
import os
import logging
import json # Added import for json handling
from components.forms import render_personal_info, render_education, render_experience, render_skills
from components.preview import render_preview

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize session state if needed
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

    # File upload section
    uploaded_file = st.file_uploader("Upload your resume", type=['docx'])
    output_format = st.selectbox(
        "Select output format",
        ['JSON', 'CSV'],
        index=0
    )

    if uploaded_file is not None:
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

                # Initialize parser
                parser = ResumeParser()

                # Parse the resume
                parsed_data = parser.parse_docx(tmp_file_path, output_format.lower())

                # Display results in organized sections
                st.subheader("Parsed Resume Data")

                if output_format == 'JSON':
                    # First display a clean summary
                    st.write("### Contact Information")
                    data = json.loads(parsed_data)
                    cols = st.columns(2)
                    with cols[0]:
                        st.write("Name:", data['name'])
                        st.write("Email:", data['email'])
                        st.write("Phone:", data['phone'])
                    with cols[1]:
                        st.write("Location:", data['location'])
                        st.write("LinkedIn:", data['linkedin'])

                    st.write("### Most Recent Position")
                    st.write("Company:", data['most_recent_company'])
                    st.write("Title:", data['most_recent_title'])
                    st.write("Dates:", data['most_recent_dates'])

                    # Then show the raw JSON for reference
                    st.write("### Raw JSON Output")
                    st.json(parsed_data)
                else:  # CSV
                    st.text("CSV Output:")
                    st.code(parsed_data)

                # Clean up temporary file
                os.unlink(tmp_file_path)

        except Exception as e:
            st.error(f"Error parsing resume: {str(e)}")
            logger.error(f"Resume parsing error: {str(e)}", exc_info=True)

    # Render form components
    st.markdown("---")
    st.subheader("Manual Entry")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Personal Info",
        "Education",
        "Experience",
        "Skills",
        "Preview"
    ])

    with tab1:
        render_personal_info()

    with tab2:
        render_education()

    with tab3:
        render_experience()

    with tab4:
        render_skills()

    with tab5:
        render_preview("modern")  # Default template

if __name__ == "__main__":
    main()