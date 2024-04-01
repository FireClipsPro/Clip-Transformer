# This file is the entry point for the application. 
# It creates the Flask app and registers the blueprints.
from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.routes.account_setup_api import account_setup_api_bp
from app.routes.background_maker_api import background_maker_api_bp
from app.routes.file_retriever_api import file_retriever_api_bp
from app.routes.image_animator_api import image_animator_api_bp
from app.routes.image_generator_api import image_generator_api_bp
from app.routes.media_adder_api import media_adder_api_bp
from app.routes.music_adder_api import music_adder_api_bp
from app.routes.project_creation_api import project_creation_api_bp
from app.routes.project_data_retriever_api import project_data_retriever_api_bp
from app.routes.query_maker_api import query_maker_api_bp
from app.routes.subtitle_adder_api import subtitle_adder_api_bp
from app.routes.test_api import test_api_bp
from app.routes.transcriber_api import transcriber_api_bp
from app.routes.upload_audio_api import upload_audio_api_bp


def create_app():
    application = Flask(__name__)
    application.config.from_object(Config)
    application.logger.setLevel(application.config['LOG_LEVEL'])
    
    CORS(application)
    
    application.register_blueprint(background_maker_api_bp, url_prefix='/background_maker_api')
    application.register_blueprint(media_adder_api_bp, url_prefix='/media_adder_api')
    application.register_blueprint(account_setup_api_bp, url_prefix='/account_setup_api')
    application.register_blueprint(query_maker_api_bp, url_prefix='/query_maker_api')
    application.register_blueprint(image_generator_api_bp, url_prefix='/image_generator_api')
    application.register_blueprint(project_creation_api_bp, url_prefix='/project_creation_api')
    application.register_blueprint(upload_audio_api_bp, url_prefix='/upload_audio_api')
    application.register_blueprint(image_animator_api_bp, url_prefix='/image_animator_api')
    application.register_blueprint(music_adder_api_bp, url_prefix='/music_adder_api')
    application.register_blueprint(transcriber_api_bp, url_prefix='/transcriber_api')
    application.register_blueprint(subtitle_adder_api_bp, url_prefix='/subtitle_adder_api')
    application.register_blueprint(file_retriever_api_bp, url_prefix='/file_retriever_api')
    application.register_blueprint(test_api_bp, url_prefix='/test_api')
    application.register_blueprint(project_data_retriever_api_bp, url_prefix='/project_data_retriever_api')
    
    return application