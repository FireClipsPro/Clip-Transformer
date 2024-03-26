from flask import abort
from flask import request
import uuid
from app.services.s3 import S3
from flask import jsonify
import boto3
import app.configuration.buckets as buckets

from . import project_data_retriever_api_bp  # Import the Blueprint
import logging

logging.basicConfig(level=logging.INFO)

@project_data_retriever_api_bp.route('/get_users_projects', methods=['GET'])
def get_users_projects():
    '''
    Gets list of projects for a user
    {
        "user_id": "panda@example.com"
    }
    returns:
    {
        "projects": ["project1", "project2"]
    }
    '''
    user_id = request.args.get('user_id')
    if not user_id:
        abort(400, description="Missing param in request payload")
    
    s3 = S3(boto3.client('s3'))
    
    try:
        path = user_id + "/"
        projects = s3.get_list_of_projects(path, buckets.project_data)
    
    except Exception as e:
        logging.exception("Failed to create project folder")
        abort(500, description=str(e))
    
    return jsonify({"projects": projects}), 200

@project_data_retriever_api_bp.route('/get_images', methods=['GET'])
def get_images():
    '''
    Gets list of projects for a user
    {
        "user_id": "panda@example.com",
        "project_id": "42069"
    }
    returns:
    {
        "image_ids": ["420420", "696969"]
    }
    '''
    project_id = request.args.get('project_id')
    user_id = request.args.get('user_id')
    if not project_id or not user_id:
        abort(400, description="Missing param in request payload")
    
    s3 = S3(boto3.client('s3'))
    
    try:
        path = user_id + "/" + project_id + "/" + buckets.images_folder
        projects = s3.get_list_of_objects(path, buckets.project_data)
    
    except Exception as e:
        logging.exception("Failed to create project folder")
        abort(500, description=str(e))
    
    return jsonify({"projects": projects}), 200