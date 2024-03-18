from flask import Blueprint

# Create a Blueprint for the api
upload_audio_api_bp = Blueprint('upload_audio_api', __name__)

from . import views