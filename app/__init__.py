from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Add secret key for sessions
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    
    # Configure upload settings
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['ALLOWED_EXTENSIONS'] = {'docx'}
    
    # Import routes after app is created to avoid circular imports
    from app import routes
    app.register_blueprint(routes.bp)
    
    return app 