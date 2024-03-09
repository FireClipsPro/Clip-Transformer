# This file is the entry point for the application. 
# It creates the Flask app and registers the blueprints.
from flask import Flask
from app.config import Config
from app.routes.background_maker_api import background_maker_api_bp
from app.routes.media_adder_api import media_adder_api_bp 
from app.routes.account_setup_api import account_setup_api_bp
from app.routes.query_maker_api import query_maker_api_bp
from app.routes.image_generator_api import image_generator_api_bp
from app.routes.subtitle_adder_api import subtitle_adder_api_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.logger.setLevel(app.config['LOG_LEVEL'])
    
    app.register_blueprint(background_maker_api_bp, url_prefix='/background_maker_api')
    app.register_blueprint(media_adder_api_bp, url_prefix='/media_adder_api')
    app.register_blueprint(account_setup_api_bp, url_prefix='/account_setup_api')
    app.register_blueprint(query_maker_api_bp, url_prefix='/query_maker_api')
    app.register_blueprint(image_generator_api_bp, url_prefix='/image_generator_api')
    app.register_blueprint(subtitle_adder_api_bp, url_prefix='/subtitle_adder_api')
    
    return app