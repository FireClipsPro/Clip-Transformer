from flask import Blueprint

project_data_retriever_api_bp = Blueprint('project_data_retriever_api', __name__)

from . import views