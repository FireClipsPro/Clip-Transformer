from flask import Blueprint

# Create a Blueprint for the api
media_adder_api_bp = Blueprint('media_adder_api', __name__)

from . import views