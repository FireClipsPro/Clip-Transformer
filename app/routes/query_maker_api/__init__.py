from flask import Blueprint

# Create a Blueprint for the api
query_maker_api_bp = Blueprint('query_maker_api', __name__)

from . import views