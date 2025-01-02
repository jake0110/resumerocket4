from docx import Document
import anthropic
from .models import db, UploadedFile
from datetime import datetime
import os
from flask import current_app

def extract_text_from_docx(filepath):
    doc = Document(filepath)
    return '\n'.join([paragraph.text for paragraph in doc.paragraphs])

def process_resume(file_id):
    try:
        # Get file
        uploaded_file = UploadedFile.query.get(file_id)
        if not uploaded_file:
            return False

        # Extract text from .docx
        filepath = f"uploads/{uploaded_file.filename}"
        resume_text = extract_text_from_docx(filepath)

        # Process with Claude - get key from current_app
        api_key = current_app.config['ANTHROPIC_API_KEY']
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in config")
        client = anthropic.Client(api_key=api_key)
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": f"Please analyze this resume and provide specific improvements:\n\n{resume_text}"
            }]
        )

        # Update database
        uploaded_file.processed = True
        uploaded_file.processing_date = datetime.utcnow()
        uploaded_file.ai_summary = message.content
        db.session.commit()

        return True

    except Exception as e:
        uploaded_file.error_message = str(e)
        db.session.commit()
        return False

