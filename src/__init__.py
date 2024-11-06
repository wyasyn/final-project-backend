from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.secret_key = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')  
    jwt = JWTManager(app)
    # Configure email
    MAIL_USERNAME = os.getenv("MAIL_USERNAME") 
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")  
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_USERNAME")
    MAIL_SERVER = 'smtp.gmail.com' 
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    

    db.init_app(app)

    with app.app_context():
        from . import models  
        db.create_all()

    return app
