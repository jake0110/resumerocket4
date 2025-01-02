from flask import Flask
from .models import db
from .config import Config

def create_app():
    app = Flask(__name__)

    # Load config from Config class
    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)

    # Create tables
    with app.app_context():
        db.create_all()

    # Import routes after app is created to avoid circular imports
    from app import routes
    app.register_blueprint(routes.bp)

    return app