from flask import Flask
from .models import db

def create_app():
    app = Flask(__name__)
    
    # Add secret key for sessions
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    
    # Configure upload settings
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['ALLOWED_EXTENSIONS'] = {'docx'}
    
    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///uploads.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Import routes after app is created to avoid circular imports
    from app import routes
    app.register_blueprint(routes.bp)
    
    return app 