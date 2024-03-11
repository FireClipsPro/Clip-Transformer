from flask import Blueprint

# Create a Blueprint for the api
music_adder_api_bp = Blueprint('music_adder_api', __name__)

from . import views