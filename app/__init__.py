# This file is the entry point for the application. 
# It creates the Flask app and registers the blueprints.
from flask import Flask
from app.config import Config
from app.routes.background_maker_api import background_maker_api_bp
from app.routes.media_adder_api import media_adder_api_bp 
from app.routes.query_maker_api import query_maker_api_bp
from app.routes.image_generator_api import image_generator_api_bp
from app.routes.project_creation_api import project_creation_api_bp
from app.routes.upload_audio_api import upload_audio_api_bp
from app.routes.image_animator_api import image_animator_api_bp
from app.routes.music_adder_api import music_adder_api_bp
from app.routes.transcriber_api import transcriber_api_bp
from app.routes.subtitle_adder_api import subtitle_adder_api_bp
from app.routes.file_retriever_api import file_retriever_api_bp
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    # Enable CORS for all routes
    CORS(app)

    app.config.from_object(Config)
    app.logger.setLevel(app.config['LOG_LEVEL'])
    
    app.register_blueprint(background_maker_api_bp, url_prefix='/background_maker_api')
    app.register_blueprint(media_adder_api_bp, url_prefix='/media_adder_api')
    app.register_blueprint(query_maker_api_bp, url_prefix='/query_maker_api')
    app.register_blueprint(image_generator_api_bp, url_prefix='/image_generator_api')
    app.register_blueprint(project_creation_api_bp, url_prefix='/project_creation_api')
    app.register_blueprint(upload_audio_api_bp, url_prefix='/upload_audio_api')
    app.register_blueprint(image_animator_api_bp, url_prefix='/image_animator_api')
    app.register_blueprint(music_adder_api_bp, url_prefix='/music_adder_api')
    app.register_blueprint(transcriber_api_bp, url_prefix='/transcriber_api')
    app.register_blueprint(subtitle_adder_api_bp, url_prefix='/subtitle_adder_api')
    app.register_blueprint(file_retriever_api_bp, url_prefix='/file_retriever_api')
    
    return app