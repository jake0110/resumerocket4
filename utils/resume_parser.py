import logging
from typing import Dict, List, Optional
import re
from datetime import datetime
import json
import csv
from io import StringIO
import os
from openai import OpenAI

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
        # Initialize OpenAI client with minimal configuration
        self.client = OpenAI()
        logger.info("OpenAI client initialized successfully")

    def _extract_with_ai(self, text: str) -> Dict[str, Dict[str, str]]:
        """Use OpenAI to extract specific information from resume text."""
        try:
            prompt = f"""Given the following resume text, extract ONLY the specified information, ensuring exact matching of email addresses, phone numbers, and LinkedIn URLs. Use pattern recognition for these fields.

            Required format:
            {{
                "Contact Information": {{
                    "Name": "full name",
                    "Email": "exact email address from document",
                    "Phone": "exact phone number from document",
                    "Location": "city, state",
                    "LinkedIn": "exact linkedin url from document"
                }},
                "Most Recent Position": {{
                    "Company": "company name",
                    "Title": "exact job title",
                    "Dates": "employment period"
                }}
            }}

            Rules:
            1. Maintain exact formatting of emails, phones, and URLs
            2. Do not make up or infer missing information
            3. Use "No information available" only when the field is truly missing
            4. For dates, include both start and end dates if available
            5. Extract the most recent position only

            Resume text:
            {text}
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise resume parser that extracts specific fields exactly as they appear in the document."
                    },
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