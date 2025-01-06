import logging
from typing import Dict, Optional, List
import json
import os
import requests
from docx import Document

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ResumeParser:
    """Resume parsing with optional AI-powered enhancement."""

    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the parser."""
        self.api_key = openai_api_key
        logger.info("Initializing ResumeParser")

    def set_api_key(self, api_key: str):
        """Set or update the OpenAI API key."""
        self.api_key = api_key
        logger.info("API key updated")

    def _extract_contact_info(self, paragraphs: List[str]) -> Dict:
        """Extract contact information using basic parsing."""
        contact_info = {
            'name': '',
            'email': '',
            'phone': ''
        }

        # Look for patterns in first few paragraphs
        for para in paragraphs[:5]:  # Usually contact info is at the top
            text = para.lower()

            # Email pattern
            if '@' in text and '.' in text and not contact_info['email']:
                words = text.split()
                for word in words:
                    if '@' in word and '.' in word:
                        contact_info['email'] = word.strip()
                        break

            # Phone pattern
            if any(char.isdigit() for char in text) and not contact_info['phone']:
                # Extract sequence of numbers and common separators
                phone_candidates = []
                current = ''
                for char in text:
                    if char.isdigit() or char in '+-().':
                        current += char
                    elif current:
                        if sum(c.isdigit() for c in current) >= 10:  # Most phone numbers have at least 10 digits
                            phone_candidates.append(current.strip())
                        current = ''
                if current and sum(c.isdigit() for c in current) >= 10:
                    phone_candidates.append(current.strip())

                if phone_candidates:
                    contact_info['phone'] = phone_candidates[0]

            # Name pattern (usually in the first or second paragraph)
            if not contact_info['name'] and len(paragraphs) > 0:
                # Assume the first non-empty paragraph that's not an email or phone is the name
                first_para = paragraphs[0].strip()
                if first_para and '@' not in first_para and not any(char.isdigit() for char in first_para):
                    contact_info['name'] = first_para

        return contact_info

    def _extract_experience(self, paragraphs: List[str]) -> List[Dict]:
        """Extract experience information using basic parsing."""
        experiences = []
        current_exp = None

        # Common section headers
        experience_headers = ['experience', 'work experience', 'professional experience', 'employment history']

        in_experience_section = False
        for para in paragraphs:
            text = para.strip().lower()

            # Check if we're entering experience section
            if any(header in text for header in experience_headers):
                in_experience_section = True
                continue

            if in_experience_section and text:
                # New experience entry often starts with company name or position
                if text.isupper() or any(word[0].isupper() for word in text.split()):
                    if current_exp:
                        experiences.append(current_exp)
                    current_exp = {
                        'company': para.strip(),
                        'position': '',
                        'duration': '',
                        'description': []
                    }
                elif current_exp:
                    if not current_exp['position']:
                        current_exp['position'] = para.strip()
                    elif not current_exp['duration'] and ('20' in para or '19' in para):
                        current_exp['duration'] = para.strip()
                    else:
                        current_exp['description'].append(para.strip())

        # Add the last experience
        if current_exp:
            experiences.append(current_exp)

        return experiences

    def parse_docx(self, file_path: str) -> Dict:
        """Parse DOCX resume file and extract information."""
        logger.info(f"Parsing DOCX file: {file_path}")

        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            doc = Document(file_path)
            paragraphs = []

            # Extract text from the document
            for paragraph in doc.paragraphs:
                text = paragraph.text.strip()
                if text:
                    paragraphs.append(text)

            if not paragraphs:
                raise ValueError("Document appears to be empty")

            # Parse basic information
            contact_info = self._extract_contact_info(paragraphs)
            experiences = self._extract_experience(paragraphs)

            parsed_data = {
                'contact': contact_info,
                'experience': experiences
            }

            logger.info("Successfully parsed resume content")
            return parsed_data

        except Exception as e:
            logger.error(f"Error parsing DOCX file: {str(e)}")
            raise

    def enhance_with_ai(self, parsed_data: Dict) -> Dict:
        """Enhance parsed data with AI analysis."""
        if not self.api_key:
            raise ValueError("OpenAI API key is required for AI analysis")

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # Convert parsed data to text for analysis
            resume_text = f"""
            Name: {parsed_data['contact'].get('name', '')}
            Email: {parsed_data['contact'].get('email', '')}
            Phone: {parsed_data['contact'].get('phone', '')}

            Experience:
            """
            for exp in parsed_data['experience']:
                resume_text += f"\n{exp.get('company', '')}\n"
                resume_text += f"{exp.get('position', '')} ({exp.get('duration', '')})\n"
                for desc in exp.get('description', []):
                    resume_text += f"- {desc}\n"

            analysis_prompt = f"""
            Analyze the following resume and provide insights. Return in JSON format:
            {{
                "experience_level": "entry/mid/senior/executive",
                "key_skills": ["top 5 most important skills"],
                "experience_summary": "brief summary of experience",
                "best_suited_roles": ["role1", "role2"]
            }}

            Resume text:
            {resume_text}
            """

            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a professional resume analyst."},
                    {"role": "user", "content": analysis_prompt}
                ],
                "response_format": {"type": "json_object"}
            }

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                ai_analysis = json.loads(result['choices'][0]['message']['content'])
                parsed_data['ai_analysis'] = ai_analysis
                logger.info("Successfully added AI analysis")
            else:
                logger.error(f"OpenAI API error: {response.text}")
                raise Exception(f"OpenAI API error: {response.status_code}")

            return parsed_data

        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            raise