from flask import Blueprint

project_creation_api_bp = Blueprint('project_creation_api', __name__)

from . import views