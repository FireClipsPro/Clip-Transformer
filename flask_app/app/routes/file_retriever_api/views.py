import logging

import boto3
from flask import abort, jsonify, request

import app.configuration.buckets as buckets
from app.services.s3 import S3

# from app.content_generation import  
from . import file_retriever_api_bp  # Import the Blueprint

logging.basicConfig(level=logging.INFO)

url_expiry_time = 3600*5 #(5 hours)

@file_retriever_api_bp.route('/get_file', methods=['GET'])
def get_file():
    '''
    {
        "file_key": "user_id/project_id/videos/KanyeWestSecretMixtape.mp3"
    }
    '''
    file_key = request.args.get('file_key')
    if not file_key:
        # If no video ID is provided, return an error response
        abort(400, description="Missing video ID parameter")
        
    s3 = S3(boto3.client('s3'))
    url = s3.get_item_url(bucket_name=buckets.project_data,
                          object_key=file_key,
                          expiry_time=url_expiry_time)

    if url == None:
        abort(404, description="Video not found")
    
    return jsonify({'url': url}), 200