from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class UploadedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    file_size = db.Column(db.Integer)  # Size in bytes 
    
    # New fields for AI processing
    processed = db.Column(db.Boolean, default=False)
    processing_date = db.Column(db.DateTime)
    ai_summary = db.Column(db.Text)
    ai_suggestions = db.Column(db.Text)
    error_message = db.Column(db.Text) 