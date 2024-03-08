from flask import Blueprint

# Create a Blueprint for the api
image_generator_api_bp = Blueprint('image_generator_api', __name__)

from . import views