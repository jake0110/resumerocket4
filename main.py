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
        ['JSON'],
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

                # Parse the JSON string into a Python dictionary
                data = json.loads(parsed_data)

                # Display Contact Information
                st.write("### Contact Information")
                contact_info = data["Contact Information"]
                st.write(f"**Name:** {contact_info['Name']}")
                st.write(f"**Email:** {contact_info['Email']}")
                st.write(f"**Phone:** {contact_info['Phone']}")
                st.write(f"**Location:** {contact_info['Location']}")
                st.write(f"**LinkedIn:** {contact_info['LinkedIn']}")

                # Display Most Recent Position
                st.write("### Most Recent Position")
                position = data["Most Recent Position"]
                st.write(f"**Company:** {position['Company']}")
                st.write(f"**Title:** {position['Title']}")
                st.write(f"**Dates:** {position['Dates']}")

                # Clean up temporary file
                os.unlink(tmp_file_path)

        except Exception as e:
            st.error(f"Error parsing resume: {str(e)}")
            logger.error(f"Resume parsing error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()