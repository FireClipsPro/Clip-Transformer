# This file is the entry point for the application. 
# It creates the Flask app and registers the blueprints.
from flask import Flask
from app.config import Config  # Assuming you have a config.py for configurations
from app.routes.background_maker_api import background_maker_api_bp  # Adjust the import path based on your project structure

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.logger.setLevel(app.config['LOG_LEVEL'])
    
    
    # Register blueprints
    # This blueprint is stored in app/routes/background_maker_api/__init__.py
    app.register_blueprint(background_maker_api_bp, url_prefix='/background_maker_api')

    return app