import os
import logging
from openai import OpenAI
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ResumeAnalyzer:
    """AI-powered resume analysis using OpenAI GPT."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI client.

        Args:
            api_key: Optional API key. If not provided, will try to get from environment variable.
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
            )

        self.client = OpenAI(api_key=self.api_key)
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.model = "gpt-4o"

    def analyze_resume(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze resume content using GPT and provide structured feedback.

        Args:
            resume_data: Dictionary containing parsed resume sections

        Returns:
            Dictionary containing analysis results:
            - overall_score: 1-10 rating
            - ats_score: 0-100 percentage
            - keyword_match: 0-100 percentage
            - strengths: List of identified strengths
            - weaknesses: List of areas for improvement
            - suggestions: List of specific improvement suggestions
            - ats_suggestions: List of ATS optimization tips
            - analysis: Detailed analysis explanation
        """
        try:
            # Construct the analysis prompt
            prompt = self._construct_analysis_prompt(resume_data)

            # Get GPT analysis with structured output
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "system",
                    "content": """You are an expert resume analyst and ATS optimization specialist. 
                    Analyze the resume and provide feedback in JSON format with the following structure:
                    {
                        "overall_score": (1-10 score),
                        "ats_score": (0-100 percentage),
                        "keyword_match": (0-100 percentage),
                        "strengths": [list of key strengths],
                        "weaknesses": [list of areas needing improvement],
                        "suggestions": [specific actionable suggestions],
                        "ats_suggestions": [ATS optimization tips],
                        "analysis": "detailed analysis explanation focusing on both content quality and ATS compatibility"
                    }"""
                }, {
                    "role": "user",
                    "content": prompt
                }],
                response_format={"type": "json_object"}
            )

            # Parse and return the analysis
            analysis = response.choices[0].message.content
            logger.info("Successfully analyzed resume with GPT")
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing resume: {str(e)}")
            raise

    def _construct_analysis_prompt(self, resume_data: Dict[str, Any]) -> str:
        """Construct a detailed prompt for GPT analysis."""
        sections = []

        # Add contact information
        if resume_data.get('contact'):
            sections.append("Contact Information:")
            contact = resume_data['contact']
            sections.extend([
                f"- Name: {contact.get('name', 'Not provided')}",
                f"- Email: {contact.get('email', 'Not provided')}",
                f"- Phone: {contact.get('phone', 'Not provided')}",
                f"- Location: {contact.get('location', 'Not provided')}"
            ])

        # Add education
        if resume_data.get('education'):
            sections.append("\nEducation:")
            for edu in resume_data['education']:
                sections.append(
                    f"- {edu.get('degree', '')} from {edu.get('institution', '')} "
                    f"({edu.get('graduation_year', '')})"
                )

        # Add experience
        if resume_data.get('experience'):
            sections.append("\nExperience:")
            for exp in resume_data['experience']:
                sections.append(f"- {exp.get('position', '')} at {exp.get('company', '')}")
                sections.append(f"  Duration: {exp.get('duration', '')}")
                if exp.get('description'):
                    sections.extend([f"  • {item}" for item in exp['description']])

        # Add skills
        if resume_data.get('skills'):
            sections.append("\nSkills:")
            sections.append(", ".join(resume_data['skills']))

        # Construct final prompt
        prompt = "\n".join([
            "Please analyze this resume thoroughly and provide detailed feedback focusing on both content quality and ATS compatibility. Include:",
            "\n".join(sections),
            "\nProvide a comprehensive analysis including:",
            "1. Overall resume score (1-10)",
            "2. ATS compatibility score (0-100%)",
            "3. Relevant keyword match percentage (0-100%)",
            "4. Key strengths and accomplishments",
            "5. Areas needing improvement",
            "6. Specific suggestions for enhancement",
            "7. ATS optimization recommendations",
            "8. Detailed explanation of the analysis"
        ])

        return prompt