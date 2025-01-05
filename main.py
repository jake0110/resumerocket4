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
logger.debug(f"Added {project_root} to Python path")

try:
    # Import local modules
    from utils.resume_parser import ResumeParser
    from utils.ai_analyzer import ResumeAnalyzer
    logger.debug("Successfully imported all local modules")
except Exception as e:
    logger.error(f"Failed to import modules: {str(e)}", exc_info=True)
    raise

def main():
    try:
        logger.info("Starting Resume Analyzer application")
        st.set_page_config(
            page_title="Resume Analyzer",
            page_icon="📝",
            layout="wide"
        )

        st.title("AI-Powered Resume Analyzer")
        st.write("Upload your resume for instant AI analysis and feedback")

        # Initialize session state
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = None
        if 'api_key' not in st.session_state:
            st.session_state.api_key = ''

        # API Key input in sidebar for better organization
        with st.sidebar:
            st.header("Configuration")
            api_key = st.text_input(
                "Enter your OpenAI API Key",
                value=st.session_state.api_key,
                type="password",
                help="Get your API key from https://platform.openai.com/account/api-keys"
            )
            if api_key:
                st.session_state.api_key = api_key

        # Main content area
        uploaded_file = st.file_uploader(
            "Upload your resume (DOCX)",
            type=['docx'],
            help="Upload your resume in DOCX format for AI analysis"
        )

        if uploaded_file is not None:
            st.info(f"Selected file: {uploaded_file.name}")

            if not st.session_state.api_key:
                st.warning("Please enter your OpenAI API key in the sidebar to analyze the resume.")
            elif st.button("Analyze Resume"):
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

                            # Analyze the resume with API key from session state
                            analyzer = ResumeAnalyzer(api_key=st.session_state.api_key)
                            analysis_results = analyzer.analyze_resume(parsed_content)
                            st.session_state.analysis_results = analysis_results
                            logger.info("Completed resume analysis")

                except Exception as e:
                    logger.error(f"Error processing resume: {str(e)}", exc_info=True)
                    st.error(f"Error processing resume: {str(e)}")

        # Display analysis results if available
        if st.session_state.analysis_results:
            results = st.session_state.analysis_results

            # Overall Score with visual indicator
            score = float(results.get('overall_score', 0))
            st.header("Analysis Results")
            col1, col2 = st.columns([1, 4])
            with col1:
                st.metric("Overall Score", f"{score}/10")
            with col2:
                progress = score / 10
                st.progress(progress)

            # Detailed Analysis
            st.subheader("Detailed Analysis")
            st.write(results.get('analysis', ''))

            # Strengths and Weaknesses in columns
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("✅ Strengths")
                for strength in results.get('strengths', []):
                    st.write(f"• {strength}")

            with col2:
                st.subheader("🔍 Areas for Improvement")
                for weakness in results.get('weaknesses', []):
                    st.write(f"• {weakness}")

            # Improvement Suggestions
            st.subheader("📈 Suggested Improvements")
            for suggestion in results.get('suggestions', []):
                st.write(f"• {suggestion}")

    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()