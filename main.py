import streamlit as st
from utils.resume_parser import ResumeParser
import tempfile
import os
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

                # Initialize parser and parse the resume
                parser = ResumeParser()
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

if __name__ == "__main__":
    main()