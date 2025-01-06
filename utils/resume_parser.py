"""Resume parsing module with improved error handling and logging."""
import logging
import re
from typing import Dict, Optional, List
import json
import os
import requests

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import required packages with proper error handling
DOCX_IMPORT_ERROR = None
try:
    import docx
    logger.info("Successfully imported python-docx package")
except ImportError as e:
    DOCX_IMPORT_ERROR = str(e)
    logger.error(f"Failed to import python-docx: {str(e)}")

class ResumeParser:
    """Resume parser with improved pattern matching and error handling."""

    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the parser with optional OpenAI API key."""
        if DOCX_IMPORT_ERROR:
            raise ImportError(f"python-docx package is required but not installed: {DOCX_IMPORT_ERROR}")
        self.api_key = openai_api_key
        logger.debug("ResumeParser initialized")

    def parse_docx(self, file_path: str) -> Dict:
        """Parse DOCX resume file with enhanced error handling."""
        logger.info(f"Starting to parse DOCX file: {file_path}")

        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                raise FileNotFoundError(f"File not found: {file_path}")

            try:
                doc = docx.Document(file_path)
                logger.info("Successfully opened document")
            except Exception as e:
                logger.error(f"Error opening document: {str(e)}")
                raise ValueError(f"Error opening document. Please ensure it's a valid .docx file: {str(e)}")

            # Extract paragraphs with enhanced metadata
            paragraphs = []
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    # Enhanced metadata extraction
                    metadata = {
                        'text': text,
                        'style_name': para.style.name if para.style else None,
                        'alignment': para.alignment,
                        'runs': []
                    }

                    max_font_size = 0
                    is_bold = False
                    for run in para.runs:
                        run_data = {
                            'text': run.text,
                            'bold': run.bold,
                            'font_name': run.font.name,
                            'font_size': None,
                            'all_caps': run.font.all_caps,
                            'position': 'top' if len(paragraphs) < 3 else 'body'
                        }

                        # Extract font size with better error handling
                        if hasattr(run.font, 'size') and run.font.size:
                            try:
                                size_pt = float(run.font.size) / 12700
                                run_data['font_size'] = size_pt
                                max_font_size = max(max_font_size, size_pt)
                            except (ValueError, TypeError):
                                pass

                        if run.bold:
                            is_bold = True

                        metadata['runs'].append(run_data)

                    metadata['max_font_size'] = max_font_size
                    metadata['is_bold'] = is_bold
                    metadata['is_header'] = max_font_size > 12 or is_bold
                    paragraphs.append(metadata)

            if not paragraphs:
                logger.warning("No content found in document")
                return {'contact': {}, 'sections': []}

            # Extract contact information with improved detection
            contact_info = self._extract_contact_info(paragraphs)
            logger.info(f"Extracted contact info: {contact_info}")

            # Extract experience entries
            experience = self._extract_experience(paragraphs)
            logger.info(f"Extracted {len(experience)} experience entries")

            return {
                'contact': contact_info,
                'sections': self._extract_sections(paragraphs),
                'experience': experience
            }

        except Exception as e:
            logger.error(f"Error parsing DOCX: {str(e)}", exc_info=True)
            raise

    def _extract_contact_info(self, paragraphs: List[Dict]) -> Dict:
        """Extract contact information with improved pattern matching."""
        contact_info = {
            'name': None,
            'email': None,
            'phone': None,
            'location': None
        }

        # Name detection with improved heuristics
        name_candidates = []
        for idx, para in enumerate(paragraphs[:3]):  # Look at first 3 paragraphs
            text = para['text'].strip()

            # Skip obvious non-name content
            if any(keyword in text.lower() for keyword in ['resume', 'cv', 'curriculum vitae']):
                continue

            # Name heuristics
            score = 0
            if idx == 0:  # First paragraph
                score += 3
            if para['is_header']:
                score += 2
            if para['max_font_size'] > 14:
                score += 2
            if any(run['bold'] for run in para['runs']):
                score += 1
            if all(word[0].isupper() for word in text.split() if word):
                score += 1

            words = text.split()
            if 1 <= len(words) <= 4:  # Most names are 1-4 words
                score += 1

            if score >= 3:  # Threshold for name detection
                name_candidates.append((text, score))

        # Sort candidates by score and select the best one
        if name_candidates:
            contact_info['name'] = sorted(name_candidates, key=lambda x: x[1], reverse=True)[0][0]
            logger.info(f"Detected name: {contact_info['name']}")

        # Extract other contact information
        for para in paragraphs:
            text = para['text']

            # Email extraction
            if not contact_info['email']:
                email_matches = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text.lower())
                if email_matches:
                    contact_info['email'] = email_matches[0]
                    logger.info(f"Found email: {contact_info['email']}")

            # Phone extraction with multiple patterns
            if not contact_info['phone']:
                phone_patterns = [
                    r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                    r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',
                    r'\+\d{1,2}\s*\d{3}[-.]?\d{3}[-.]?\d{4}',
                    r'\b\d{3}[.]?\d{3}[.]?\d{4}\b'
                ]
                for pattern in phone_patterns:
                    matches = re.findall(pattern, text)
                    if matches:
                        phone = re.sub(r'[^\d+]', '', matches[0])
                        if len(phone) >= 10:
                            contact_info['phone'] = phone
                            logger.info(f"Found phone: {contact_info['phone']}")
                            break

            # Location extraction with enhanced patterns
            if not contact_info['location']:
                location_patterns = [
                    r'(?i)(\d+\s+[A-Za-z\s]+(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard)[.,]?\s+[A-Z]{2}\s*\d{5}(?:-\d{4})?)',
                    r'(?i)(.*?,\s*[A-Z]{2}\s*\d{5}(?:-\d{4})?)',
                    r'(?i)([A-Za-z\s]+,\s*[A-Z]{2}\s*\d{5})',
                    r'(?i)([A-Za-z\s]+,\s*[A-Z]{2})'
                ]
                for pattern in location_patterns:
                    matches = re.findall(pattern, text)
                    if matches:
                        location = matches[0]
                        if isinstance(location, tuple):
                            location = location[0]
                        location = re.sub(r'\s+', ' ', location).strip(' ,')
                        contact_info['location'] = location
                        logger.info(f"Found location: {contact_info['location']}")
                        break

        # Return the contact info with default values for missing fields
        return {k: v if v is not None else 'No information available'
                for k, v in contact_info.items()}

    def _extract_sections(self, paragraphs: List[Dict]) -> List[Dict]:
        """Extract document sections."""
        sections = []
        current_section = None

        for para in paragraphs:
            text = para['text'].strip()
            if para['is_header'] and len(text.split()) <= 3:
                if current_section:
                    sections.append(current_section)
                current_section = {'title': text, 'content': []}
            elif current_section:
                current_section['content'].append(text)

        if current_section:
            sections.append(current_section)
        return sections

    def _extract_experience(self, paragraphs: List[Dict]) -> List[Dict]:
        """Extract experience entries."""
        experiences = []
        current_exp = None
        in_experience_section = False

        try:
            for para in paragraphs:
                text = para['text'].strip()
                is_header = para['is_header']

                if not text:
                    continue

                # Detect experience section
                if any(keyword in text.lower() for keyword in
                       ['experience', 'work history', 'employment', 'professional experience']):
                    in_experience_section = True
                    continue

                if not in_experience_section:
                    continue

                # New experience entry detection
                if (is_header or
                    (text[0].isupper() and len(text.split()) <= 4) or
                    any(text.lower().startswith(prefix) for prefix in ['senior ', 'lead ', 'chief '])):

                    if current_exp and current_exp.get('company'):
                        experiences.append(current_exp)

                    current_exp = {
                        'company': text,
                        'position': '',
                        'duration': '',
                        'description': []
                    }
                elif current_exp:
                    if not current_exp['position']:
                        current_exp['position'] = text
                    elif not current_exp['duration'] and re.search(r'\b(19|20)\d{2}\b|present|current', text.lower()):
                        current_exp['duration'] = text
                    else:
                        cleaned_text = re.sub(r'^[-•●\s]+', '', text).strip()
                        if cleaned_text:
                            current_exp['description'].append(cleaned_text)

            if current_exp and current_exp.get('company'):
                experiences.append(current_exp)

            return experiences

        except Exception as e:
            logger.error(f"Error extracting experience: {str(e)}", exc_info=True)
            return []

    def enhance_with_ai(self, parsed_data: Dict) -> Dict:
        """Enhance parsed data with AI analysis."""
        if not self.api_key:
            raise ValueError("OpenAI API key is required for AI analysis")

        try:
            # Prepare resume text for analysis
            resume_text = self._prepare_resume_text(parsed_data)
            logger.debug("Prepared resume text for AI analysis")

            # Make API request
            response = self._make_openai_request(resume_text)

            # Process response
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
            logger.error(f"Error in AI analysis: {str(e)}", exc_info=True)
            raise

    def _prepare_resume_text(self, parsed_data: Dict) -> str:
        """Prepare resume text for AI analysis."""
        resume_text = []

        # Add contact information
        if 'contact' in parsed_data:
            contact = parsed_data['contact']
            resume_text.extend([
                f"Name: {contact.get('name', '')}",
                f"Email: {contact.get('email', '')}",
                f"Phone: {contact.get('phone', '')}",
                f"Location: {contact.get('location','')}",
                ""
            ])

        # Add experience information
        if 'experience' in parsed_data:
            resume_text.append("Experience:")
            for exp in parsed_data['experience']:
                resume_text.extend([
                    f"\nCompany: {exp.get('company', '')}",
                    f"Position: {exp.get('position', '')}",
                    f"Duration: {exp.get('duration', '')}",
                    "Description:"
                ])
                for desc in exp.get('description', []):
                    resume_text.append(f"- {desc}")
                resume_text.append("")

        return "\n".join(resume_text)

    def _make_openai_request(self, resume_text: str):
        """Make request to OpenAI API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional resume analyzer. Provide analysis in JSON format."
                },
                {
                    "role": "user",
                    "content": f"Analyze this resume and provide insights:\n\n{resume_text}"
                }
            ],
            "response_format": {"type": "json_object"}
        }

        return requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )