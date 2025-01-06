import streamlit as st
import os
import tempfile
import logging

logger = logging.getLogger(__name__)

def render_personal_info():
    """Render the personal information form with file upload."""
    with st.form("personal_info_form"):
        st.subheader("Personal Information")

        # File upload section with better visual feedback
        st.markdown("### Resume Upload")
        uploaded_file = st.file_uploader(
            "Upload your resume (DOCX or PDF)",
            type=['docx', 'pdf'],
            key="resume_uploader",
            help="Upload your resume for Airparser analysis"
        )

        if uploaded_file is not None:
            st.info(f"File selected: {uploaded_file.name}")
            file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # Convert to MB
            if file_size > 10:  # 10MB limit
                st.warning(f"File size ({file_size:.1f}MB) exceeds 10MB limit")
            else:
                st.success(f"File size: {file_size:.1f}MB (Ready for processing)")

                if st.form_submit_button("Process Resume"):
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_file_path = tmp_file.name
                            logger.debug(f"Saved uploaded file to {tmp_file_path}")

                            # Placeholder for Airparser integration
                            st.info("Your resume will be processed through Airparser soon!")
                            st.info("Integration with Airparser via Zapier is under development.")

                            # Clean up temporary file
                            os.unlink(tmp_file_path)
                            logger.debug("Cleaned up temporary file")

                    except Exception as e:
                        logger.error(f"Error processing file: {str(e)}")
                        st.error("Error processing your file. Please try again.")

        # Manual input fields as fallback
        name = st.text_input(
            "Full Name",
            value="",
            key="name_input"
        )

        email = st.text_input(
            "Email",
            value="",
            key="email_input"
        )

        phone = st.text_input(
            "Phone",
            value="",
            key="phone_input"
        )

        # Professional level dropdown
        level_options = ['Entry Level', 'Mid Level', 'Senior Level', 'Executive']
        prof_level = st.selectbox(
            "Professional Level",
            options=level_options,
            index=0,
            key="prof_level"
        )

        # Save button for manual edits
        if st.form_submit_button("Save Personal Info"):
            st.session_state.personal_info = {
                'name': name,
                'email': email,
                'phone': phone,
                'professional_level': prof_level
            }
            st.success("✅ Personal information saved!")

def render_education():
    """Placeholder for education section."""
    st.info("Education section will be populated from Airparser analysis.")

def render_experience():
    """Placeholder for experience section."""
    st.info("Experience section will be populated from Airparser analysis.")

def render_skills():
    """Placeholder for skills section."""
    st.info("Skills section will be populated from Airparser analysis.")