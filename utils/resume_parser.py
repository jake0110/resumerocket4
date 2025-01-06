import logging
from typing import Dict, Optional
import json
import os
from openai import OpenAI
from docx import Document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeParser:
    """Resume parsing with AI-powered extraction."""

    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the parser with OpenAI API key."""
        logger.info("Initializing ResumeParser")
        try:
            # Initialize OpenAI client with provided API key or environment variable
            self.client = OpenAI(api_key=openai_api_key or os.getenv('OPENAI_API_KEY'))
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise

    def _extract_with_ai(self, text: str) -> Dict:
        """Use OpenAI to extract specific information from resume text."""
        try:
            prompt = f"""
            Extract the following information from the resume text in a structured format.
            Return the data in the following JSON format:

            {{
                "contact": {{
                    "name": "full name",
                    "email": "email address",
                    "phone": "phone number",
                    "location": "city, state"
                }},
                "experience": [
                    {{
                        "company": "company name",
                        "position": "job title",
                        "duration": "employment period",
                        "description": ["bullet point 1", "bullet point 2"]
                    }}
                ],
                "education": [
                    {{
                        "institution": "school name",
                        "degree": "degree name",
                        "graduation_year": "year"
                    }}
                ],
                "skills": ["skill1", "skill2"]
            }}

            Resume text:
            {text}
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a precise resume parser that extracts specific fields exactly as they appear in the document."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )

            parsed_data = json.loads(response.choices[0].message.content)
            logger.info("Successfully extracted information using AI")
            return parsed_data

        except Exception as e:
            logger.error(f"Error in AI extraction: {str(e)}")
            raise

    def parse_docx(self, file_path: str) -> Dict:
        """Parse DOCX resume file and extract information."""
        logger.info(f"Parsing DOCX file: {file_path}")

        try:
            doc = Document(file_path)
            text_content = []

            # Extract text from the document
            for paragraph in doc.paragraphs:
                text = paragraph.text.strip()
                if text:
                    text_content.append(text)

            # Join all text for AI processing
            complete_text = '\n'.join(text_content)

            # Extract information using AI
            parsed_data = self._extract_with_ai(complete_text)

            # Add AI analysis of the resume
            try:
                analysis_prompt = f"""
                Analyze the following resume and provide insights. Return in JSON format:
                {{
                    "experience_level": "entry/mid/senior/executive",
                    "key_skills": ["top 5 most important skills"],
                    "experience_summary": "brief summary of experience",
                    "best_suited_roles": ["role1", "role2"],
                    "improvement_suggestions": ["suggestion1", "suggestion2"]
                }}

                Resume text:
                {complete_text}
                """

                analysis_response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a professional resume analyst."},
                        {"role": "user", "content": analysis_prompt}
                    ],
                    response_format={"type": "json_object"}
                )

                ai_analysis = json.loads(analysis_response.choices[0].message.content)
                parsed_data['ai_analysis'] = ai_analysis
                logger.info("Successfully added AI analysis")

            except Exception as e:
                logger.warning(f"AI analysis failed but continuing with basic parsing: {str(e)}")

            return parsed_data

        except Exception as e:
            logger.error(f"Error parsing DOCX file: {str(e)}")
            raise