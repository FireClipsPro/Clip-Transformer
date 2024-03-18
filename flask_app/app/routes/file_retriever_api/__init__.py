from flask import Blueprint

# Create a Blueprint for the api
file_retriever_api_bp = Blueprint('file_retriever_api', __name__)

from . import views