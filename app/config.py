import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Existing configs
    SECRET_KEY = 'your-secret-key-here'
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'docx'}
    
    # Database config
    SQLALCHEMY_DATABASE_URI = 'sqlite:///uploads.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenAI config
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = 'gpt-3.5-turbo'
    MAX_TOKENS = 1000  # Adjust based on testing 