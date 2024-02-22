from flask import Blueprint
# this init file is used to create Blueprints
# Blueprints are a way to organize your Flask app into smaller, reusable components
# Blueprints are a way to define a collection of routes and views in a way that can be registered with an application multiple times

# Create a Blueprint for the blank_vid_maker_api
blank_vid_maker_api_bp = Blueprint('blank_vid_maker_api', __name__)

from . import views