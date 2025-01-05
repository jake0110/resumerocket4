import streamlit as st
import tempfile
import os
import logging
from utils.resume_parser import ResumeParser
from utils.ai_analyzer import ResumeAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Streamlit app
st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="📝",
    layout="wide"
)

# Initialize session state
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}

# Updated roles list
ROLES = [
    "Individual Contributor",
    "Manager",
    "Client Manager",
    "Selling Partner/Principal",
    "Practice Leader"
]

# Main UI elements
st.title("Resume Analyzer")
st.markdown("""
Upload your resume for instant AI analysis that includes:
- Overall resume score and evaluation
- Key strengths and improvement areas
- Actionable suggestions for enhancement
""")

# Initialize AI analyzer early to catch any connection issues
try:
    analyzer = ResumeAnalyzer()
    # Test connection
    if not analyzer.test_connection():
        st.error("Unable to connect to AI service. Please try again later.")
        st.stop()
    logger.info("Successfully connected to OpenAI service")
except Exception as e:
    st.error(f"Error initializing AI service: {str(e)}")
    st.stop()

# Contact Information Form
with st.form("contact_info"):
    st.subheader("Contact Information")
    name = st.text_input("Full Name*", key="name")
    email = st.text_input("Email Address*", key="email")
    phone = st.text_input("Phone Number (Optional)", key="phone")

    # Role Selection with updated options
    role = st.selectbox(
        "Select Role*",
        options=ROLES,
        key="role"
    )

    # File upload
    uploaded_file = st.file_uploader(
        "Upload your resume (DOCX)*",
        type=['docx'],
        help="Upload your resume in DOCX format for AI analysis"
    )

    submit_button = st.form_submit_button("Analyze Resume")

# Analysis logic
if submit_button and uploaded_file and name and email and role:
    try:
        with st.spinner("Analyzing your resume..."):
            # Save uploaded file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

                try:
                    # Parse resume
                    parser = ResumeParser()
                    parsed_content = parser.parse_docx(tmp_file_path)

                    # Add user context to parsed content
                    parsed_content['user_context'] = {
                        'name': name,
                        'email': email,
                        'phone': phone,
                        'role': role
                    }

                    # Get analysis
                    analysis_results = analyzer.analyze_resume(parsed_content)
                    st.session_state.analysis_results = analysis_results

                    # Cleanup temporary file
                    os.unlink(tmp_file_path)

                except Exception as e:
                    logger.error(f"Error processing resume: {str(e)}")
                    st.error("Error processing resume. Please ensure you've uploaded a valid DOCX file.")
                    if os.path.exists(tmp_file_path):
                        os.unlink(tmp_file_path)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        st.error("An unexpected error occurred. Please try again.")

elif submit_button:
    if not name:
        st.error("Please enter your name")
    if not email:
        st.error("Please enter your email")
    if not role:
        st.error("Please select a role")
    if not uploaded_file:
        st.error("Please upload your resume")

# Display results
if st.session_state.analysis_results:
    try:
        results = st.session_state.analysis_results

        st.header("Analysis Results")
        col1, col2 = st.columns([1, 4])
        with col1:
            st.metric("Overall Score", f"{results.get('overall_score', 0)}/10")
        with col2:
            progress = float(results.get('overall_score', 0)) / 10
            st.progress(progress)

        st.subheader("📊 Detailed Analysis")
        st.write(results.get('analysis', ''))

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("✅ Key Strengths")
            for strength in results.get('strengths', []):
                st.markdown(f"- {strength}")

        with col2:
            st.subheader("🎯 Areas for Improvement")
            for weakness in results.get('weaknesses', []):
                st.markdown(f"- {weakness}")

        st.subheader("📈 Recommended Actions")
        for suggestion in results.get('suggestions', []):
            st.markdown(f"- {suggestion}")

    except Exception as e:
        logger.error(f"Error displaying results: {str(e)}")
        st.error("Error displaying analysis results")