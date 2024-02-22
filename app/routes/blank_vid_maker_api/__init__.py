from flask import Blueprint

# Create a Blueprint for the blank_vid_maker_api
blank_vid_maker_api_bp = Blueprint('blank_vid_maker_api', __name__)

from . import views