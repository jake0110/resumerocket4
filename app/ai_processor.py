from docx import Document
import openai
from .models import db, UploadedFile
from datetime import datetime

def extract_text_from_docx(filepath):
    doc = Document(filepath)
    return '\n'.join([paragraph.text for paragraph in doc.paragraphs])

def process_resume(file_id):
    uploaded_file = UploadedFile.query.get(file_id)
    if not uploaded_file:
        return False
        
    try:
        # Extract text from .docx
        filepath = f"uploads/{uploaded_file.filename}"
        resume_text = extract_text_from_docx(filepath)
        
        # Process with OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional resume reviewer. Analyze the resume and provide specific improvements."},
                {"role": "user", "content": f"Please analyze this resume and provide specific improvements:\n\n{resume_text}"}
            ],
            max_tokens=1000
        )
        
        # Update database
        uploaded_file.processed = True
        uploaded_file.processing_date = datetime.utcnow()
        uploaded_file.ai_summary = response.choices[0].message.content
        db.session.commit()
        
        return True
        
    except Exception as e:
        uploaded_file.error_message = str(e)
        db.session.commit()
        return False 