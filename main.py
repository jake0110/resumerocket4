import streamlit as st
from utils.pdf_generator import generate_pdf
from utils.resume_parser import ResumeParser
from components.forms import render_personal_info, render_education, render_experience, render_skills
from components.preview import render_preview
import base64
import tempfile
import os

def main():
    st.set_page_config(
        page_title="Resume Builder",
        page_icon="📄",
        layout="wide"
    )

    # Try to load custom CSS if available
    try:
        with open('styles/custom.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Custom styles not found. Using default styling.")

    st.title("Professional Resume Builder")

    # Initialize session state
    if 'personal_info' not in st.session_state:
        st.session_state.personal_info = {}
    if 'education' not in st.session_state:
        st.session_state.education = [{}]
    if 'experience' not in st.session_state:
        st.session_state.experience = [{}]
    if 'skills' not in st.session_state:
        st.session_state.skills = []
    if 'parsed_resume' not in st.session_state:
        st.session_state.parsed_resume = None

    # File Upload Section
    st.header("Upload Existing Resume")
    uploaded_file = st.file_uploader("Upload your resume", type=['docx'])

    if uploaded_file is not None:
        try:
            # Create a temporary file to save the uploaded content
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            # Parse the resume
            parser = ResumeParser()
            parsed_content = parser.parse_docx(tmp_file_path)

            # Store parsed content in session state
            st.session_state.parsed_resume = parsed_content

            # Show success message
            st.success("Resume successfully parsed!")

            # Display parsed content in an expander
            with st.expander("View Parsed Content"):
                st.write(parsed_content)

            # Clean up temporary file
            os.unlink(tmp_file_path)

        except Exception as e:
            st.error(f"Error parsing resume: {str(e)}")

    # Create two columns: Form and Preview
    col1, col2 = st.columns([3, 2])

    with col1:
        st.header("Enter Your Information")

        # Template Selection
        template = st.selectbox(
            "Select Resume Template",
            ["Professional", "Modern", "Classic"],
            key="template"
        )

        # Tabs for different sections
        tabs = st.tabs(["Personal Info", "Education", "Experience", "Skills"])

        with tabs[0]:
            render_personal_info()

        with tabs[1]:
            render_education()

        with tabs[2]:
            render_experience()

        with tabs[3]:
            render_skills()

    with col2:
        st.header("Resume Preview")
        render_preview(template)

        if st.button("Generate PDF"):
            try:
                pdf_bytes = generate_pdf(
                    st.session_state.personal_info,
                    st.session_state.education,
                    st.session_state.experience,
                    st.session_state.skills,
                    template
                )

                b64_pdf = base64.b64encode(pdf_bytes).decode()
                href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="resume.pdf">Download PDF</a>'
                st.markdown(href, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")

if __name__ == "__main__":
    main()