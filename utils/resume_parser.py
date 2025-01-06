import logging
from typing import Dict, List, Optional
import re
from datetime import datetime
import json
import csv
from io import StringIO
import os
import openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from docx import Document
except ImportError as e:
    logger.error(f"Failed to import python-docx: {str(e)}")
    raise ImportError("python-docx is required but not properly installed. Please install it using 'pip install python-docx'")

class ResumeParser:
    """Resume parsing with AI-powered extraction."""

    def __init__(self):
        """Initialize the parser."""
        logger.info("Initializing ResumeParser")
        # Initialize OpenAI client
        openai.api_key = os.getenv('OPENAI_API_KEY')
        if not openai.api_key:
            logger.warning("OpenAI API key not found in environment variables")

    def _extract_with_ai(self, text: str) -> Dict[str, Dict[str, str]]:
        """Use OpenAI to extract specific information from resume text."""
        try:
            prompt = f"""Extract the following specific information from this resume text, maintaining exactly this structure:
            {{
                "Contact Information": {{
                    "Name": "person's full name",
                    "Email": "email address",
                    "Phone": "phone number",
                    "Location": "city, state",
                    "LinkedIn": "linkedin profile url"
                }},
                "Most Recent Position": {{
                    "Company": "company name",
                    "Title": "job title",
                    "Dates": "employment dates"
                }}
            }}

            If any field is not found, use "No information available".
            Resume text:
            {text}
            """

            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a precise resume parser that extracts specific fields exactly as requested."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )

            parsed_data = json.loads(response.choices[0].message.content)
            logger.info("Successfully extracted information using AI")
            return parsed_data

        except Exception as e:
            logger.error(f"Error in AI extraction: {str(e)}")
            # Return default structure if AI extraction fails
            return {
                "Contact Information": {
                    "Name": "No information available",
                    "Email": "No information available",
                    "Phone": "No information available",
                    "Location": "No information available",
                    "LinkedIn": "No information available"
                },
                "Most Recent Position": {
                    "Company": "No information available",
                    "Title": "No information available",
                    "Dates": "No information available"
                }
            }

    def parse_docx(self, file_path: str, output_format: str = 'json') -> str:
        """Parse DOCX resume file and extract only specific requested fields."""
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

            # Return formatted output
            if output_format.lower() == 'json':
                return json.dumps(parsed_data, indent=2)
            else:
                logger.warning("Unsupported output format requested, defaulting to JSON")
                return json.dumps(parsed_data, indent=2)

        except Exception as e:
            logger.error(f"Error parsing DOCX file: {str(e)}")
            raise