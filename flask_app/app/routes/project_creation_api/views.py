import logging
import uuid

import boto3
from flask import abort, jsonify, request

import app.configuration.buckets as buckets
from app.services.s3 import S3
from app.VideoEditor import AWSBackgroundCreator

from . import project_creation_api_bp  # Import the Blueprint

logging.basicConfig(level=logging.INFO)

@project_creation_api_bp.route('/create', methods=['POST'])
def create():
    '''
    Creates a new project folder in the S3 bucket.
    Generates a unique project_id and creates a folder with that name in the user's private bucket.
    {
        "user_id": "panda@example.com"
    }
    '''
    payload = request.get_json()
    if not all(key in payload for key in ['user_id']):
        abort(400, description="Missing param in request payload")
    
    user_id = payload['user_id']
    unique_id = uuid.uuid4()
    project_id = str(unique_id)
    
    s3 = S3(boto3.client('s3'))
    
    try:
        user_folder = user_id + "/"
        user_project_folder = user_folder + project_id + "/"
        
        s3.create_folder(folder_name=project_id,
                         bucket_name=buckets.project_data,
                         prefix=user_folder)
        s3.create_folder(folder_name=buckets.music_folder[:-1],
                            bucket_name=buckets.project_data,
                            prefix=user_folder)
        s3.create_folder(folder_name=buckets.background_videos_folder[:-1],
                            bucket_name=buckets.project_data,
                            prefix=user_folder)
        s3.create_folder(folder_name=buckets.images_folder[:-1],
                            bucket_name=buckets.project_data,
                            prefix=user_project_folder)
        s3.create_folder(folder_name=buckets.audio_folder[:-1],
                            bucket_name=buckets.project_data,
                            prefix=user_project_folder)
        s3.create_folder(folder_name=buckets.blank_videos_folder[:-1],
                            bucket_name=buckets.project_data,
                            prefix=user_project_folder)
        s3.create_folder(folder_name=buckets.video_with_media_folder[:-1],
                            bucket_name=buckets.project_data,
                            prefix=user_project_folder)
        s3.create_folder(folder_name=buckets.image_videos_folder[:-1],
                            bucket_name=buckets.project_data,
                            prefix=user_project_folder)
        s3.create_folder(folder_name=buckets.transcripts_folder[:-1],
                            bucket_name=buckets.project_data,
                            prefix=user_project_folder)
        s3.create_folder(folder_name=buckets.queries_folder[:-1],
                            bucket_name=buckets.project_data,
                            prefix=user_project_folder)
        s3.create_folder(folder_name=buckets.video_with_music_folder[:-1],
                            bucket_name=buckets.project_data,
                            prefix=user_project_folder)
    
    except Exception as e:
        logging.exception("Failed to create project folder")
        abort(500, description=str(e))
    
    return jsonify({"project_id": project_id}), 200
