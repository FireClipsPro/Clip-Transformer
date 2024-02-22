from flask import Flask
from app.config import Config  # Assuming you have a config.py for configurations
from app.routes.blank_vid_maker_api import blank_vid_maker_api_bp  # Adjust the import path based on your project structure

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.logger.setLevel(app.config['LOG_LEVEL'])
    
    # Initialize extensions
    # For example: db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(blank_vid_maker_api_bp, url_prefix='/blank_vid_maker_api')

    return app