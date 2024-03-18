from flask import Blueprint

# Create a Blueprint for the api
image_animator_api_bp = Blueprint('image_animator_api', __name__)

from . import views