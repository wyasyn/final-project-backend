from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
from itsdangerous import URLSafeTimedSerializer

import os
import logging

# Load environment variables
load_dotenv()

# Initialize extensions globally
db = SQLAlchemy()
jwt = JWTManager()


class Config:
    """Centralized configuration class for all app settings."""
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default-jwt-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  

def create_app():
    """Application factory to create and configure the Flask app."""
    app = Flask(__name__)
    
    app.config.from_object(Config)  
    
    # Enable CORS with app-specific configuration if needed
    CORS(app, origins=["http://localhost:3000", "https://yourfrontend.com"])

    # Initialize extensions with the app
    initialize_extensions(app)

    # Initialize serializer with the app secret key for secure token generation
    app.serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    # Register blueprints
    register_blueprints(app)

    # Setup database within app context
    with app.app_context():
        initialize_database(app)

    # Configure logging
    configure_logging(app)

    return app

def initialize_extensions(app):
    """Initialize Flask extensions with the app instance."""
    db.init_app(app)
    jwt.init_app(app)

def register_blueprints(app):
    """Register Flask blueprints for modular routing."""
    # Import blueprints inside the function to avoid circular imports
    from .users.routes import user_bp
    from .income.routes import income_bp
    from .expense.routes import expense_bp
    from .budget.routes import budget_bp
    from .savings_goal.routes import savings_goal_bp

    # Register each blueprint with a URL prefix
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(income_bp, url_prefix='/income')
    app.register_blueprint(expense_bp, url_prefix='/expense')
    app.register_blueprint(budget_bp, url_prefix='/budget')
    app.register_blueprint(savings_goal_bp, url_prefix='/savings-goal')

def initialize_database(app):
    """Initialize database and create tables if they don't exist."""
    try:
        # Import models for table creation
        from . import models  
        db.create_all()
        app.logger.info("Database tables created successfully.")
    except Exception as e:
        app.logger.error(f"Database setup failed: {e}")

def configure_logging(app):
    """Configure logging for the app."""
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)
    app.logger.info("Application startup complete.")
