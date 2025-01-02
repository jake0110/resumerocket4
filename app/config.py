    import os
    from dotenv import load_dotenv

    load_dotenv()

    print("Debug: Loading environment variables...")
    api_key = os.getenv('ANTHROPIC_API_KEY')
    print(f"Debug: API Key found: {'Yes' if api_key else 'No'}")
    print(f"Debug: API Key starts with: {api_key[:7] if api_key else 'None'}")

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

        # Anthropic config
        ANTHROPIC_API_KEY = api_key  # Use the variable we checked above