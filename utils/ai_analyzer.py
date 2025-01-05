import os
import logging
from openai import OpenAI
from typing import Dict, Any
import json

logger = logging.getLogger(__name__)

class ResumeAnalyzer:
    """AI-powered resume analysis using OpenAI GPT."""

    def __init__(self):
        """Initialize the OpenAI client with API key from environment."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

        try:
            self.client = OpenAI(
                api_key=self.api_key
            )
            self.model = "gpt-4-turbo-preview"
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise ValueError(f"Unable to initialize AI service: {str(e)}")

    def test_connection(self) -> bool:
        """Test the OpenAI connection with a simple query."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": "Return a simple JSON response with the key 'status' and value 'connected'"
                    }
                ],
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
            return result.get('status') == 'connected'
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False

    def analyze_resume(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze resume content using GPT and provide structured feedback."""
        try:
            # First test the connection
            if not self.test_connection():
                raise ValueError("Unable to connect to OpenAI service")

            prompt = self._construct_analysis_prompt(resume_data)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a resume analyst. Analyze the provided resume and return a JSON object with:
                        - overall_score: number between 1-10
                        - strengths: array of 2-3 key strengths
                        - weaknesses: array of 2-3 areas for improvement
                        - suggestions: array of 2-3 specific suggestions
                        - analysis: string containing brief overall analysis"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"}
            )

            analysis = json.loads(response.choices[0].message.content)
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing resume: {str(e)}")
            raise ValueError(f"Unable to complete resume analysis: {str(e)}")

    def _construct_analysis_prompt(self, resume_data: Dict[str, Any]) -> str:
        """Construct analysis prompt with resume content."""
        try:
            sections = []

            # Add basic context
            sections.append("Please analyze this resume for the following role:")
            sections.append(f"Target Role: {resume_data.get('user_context', {}).get('role', 'Not specified')}")
            sections.append("\nResume Content:")

            # Add parsed content sections
            if resume_data.get('contact'):
                sections.append("\nContact Information:")
                contact = resume_data['contact']
                sections.extend([
                    f"Name: {contact.get('name', 'Not provided')}",
                    f"Email: {contact.get('email', 'Not provided')}"
                ])

            if resume_data.get('education'):
                sections.append("\nEducation:")
                for edu in resume_data['education']:
                    sections.append(
                        f"- {edu.get('degree', '')} from {edu.get('institution', '')} "
                        f"({edu.get('graduation_year', '')})"
                    )

            if resume_data.get('experience'):
                sections.append("\nExperience:")
                for exp in resume_data['experience']:
                    sections.append(f"- {exp.get('position', '')} at {exp.get('company', '')}")
                    sections.append(f"  Duration: {exp.get('duration', '')}")
                    if exp.get('description'):
                        sections.extend([f"  • {item}" for item in exp['description']])

            if resume_data.get('skills'):
                sections.append("\nSkills:")
                sections.append(", ".join(resume_data['skills']))

            return "\n".join(sections)

        except Exception as e:
            logger.error(f"Error constructing analysis prompt: {str(e)}")
            raise ValueError(f"Failed to construct analysis prompt: {str(e)}")