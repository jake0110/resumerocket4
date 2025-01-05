import streamlit as st
import tempfile
import os
import logging
import sys
from pathlib import Path

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Add the project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

try:
    from utils.resume_parser import ResumeParser
    from utils.ai_analyzer import ResumeAnalyzer
    logger.info("Successfully imported local modules")
except Exception as e:
    logger.error(f"Failed to import modules: {str(e)}")
    raise

def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None

def main():
    try:
        logger.info("Starting Resume Analyzer application")
        st.set_page_config(
            page_title="Resume Analyzer",
            page_icon="📝",
            layout="wide"
        )

        # Initialize session state
        initialize_session_state()

        st.title("AI-Powered Resume Analyzer")
        st.markdown("""
        Upload your resume for instant AI analysis that includes:
        - Overall resume score and evaluation
        - Key strengths and improvement areas
        - ATS compatibility analysis
        - Actionable suggestions for enhancement
        """)

        # Main content area
        uploaded_file = st.file_uploader(
            "Upload your resume (DOCX)",
            type=['docx'],
            help="Upload your resume in DOCX format for AI analysis"
        )

        if uploaded_file is not None:
            st.info(f"Selected file: {uploaded_file.name}")

            if st.button("Analyze Resume"):
                try:
                    with st.spinner("Analyzing your resume..."):
                        # Save uploaded file temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_file_path = tmp_file.name
                            logger.debug(f"Saved uploaded file to {tmp_file_path}")

                            # Parse the resume
                            parser = ResumeParser()
                            parsed_content = parser.parse_docx(tmp_file_path)
                            logger.info("Successfully parsed resume content")

                            # Clean up temporary file
                            os.unlink(tmp_file_path)
                            logger.debug("Cleaned up temporary file")

                            # Initialize analyzer
                            analyzer = ResumeAnalyzer()
                            analysis_results = analyzer.analyze_resume(parsed_content)
                            st.session_state.analysis_results = analysis_results
                            logger.info("Completed resume analysis")

                except Exception as e:
                    logger.error(f"Error processing resume: {str(e)}")
                    st.error(f"Error processing resume: {str(e)}")

        # Display analysis results if available
        if st.session_state.analysis_results:
            results = st.session_state.analysis_results

            # Create three columns for the main metrics
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Overall Score", f"{results.get('overall_score', 0)}/10")

            with col2:
                st.metric("ATS Compatibility", f"{results.get('ats_score', 0)}%")

            with col3:
                st.metric("Keyword Match", f"{results.get('keyword_match', 0)}%")

            # Detailed Analysis Section
            st.subheader("📊 Detailed Analysis")
            st.write(results.get('analysis', ''))

            # Strengths and Areas for Improvement
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("✅ Key Strengths")
                for strength in results.get('strengths', []):
                    st.markdown(f"- {strength}")

            with col2:
                st.subheader("🎯 Areas for Improvement")
                for weakness in results.get('weaknesses', []):
                    st.markdown(f"- {weakness}")

            # ATS Optimization Suggestions
            st.subheader("🤖 ATS Optimization Tips")
            for ats_tip in results.get('ats_suggestions', []):
                st.markdown(f"- {ats_tip}")

            # Action Items
            st.subheader("📈 Recommended Actions")
            for suggestion in results.get('suggestions', []):
                st.markdown(f"- {suggestion}")

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()