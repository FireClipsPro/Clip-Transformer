import logging

import boto3
import requests
from flask import abort, jsonify, request

import app.configuration.buckets as buckets
from app.services.s3 import S3
from app.Transcriber import CloudTranscriber

from . import transcriber_api_bp

logging.basicConfig(level=logging.INFO)

url_expiry_time = 3600*5

@transcriber_api_bp.route('/transcribe', methods=['POST'])
def transcribe():
    '''
    {
        "project_id": "string",
        "user_id": "string"
    }
    '''
    logging.info("Adding subtitles")
    data = request.get_json()

    # Validate payload
    if not all(key in data for key in ['project_id', 'user_id']):
        abort(400, description="Missing data in request payload")

    project_id = data['project_id']
    user_id = data['user_id']

    url = f"http://service_5001:5001/transcribe?bucket_id=project-data-69&project_id={project_id}&user_id={user_id}"
    
    # Make the POST request
    response = requests.post(url)

    # Check if the request was successful   
    if response.status_code != 200:
        abort(400, description="Transcription Request failed")
    
    # Return the response
    return jsonify({"message": "Transcription Request sent successfully"}), 200

@transcriber_api_bp.route('/get_transcription', methods=['POST'])
def get_transcription():
    '''
    {
        "file_key": "user_id/project_id/transcription.json"
    }
    '''
    file_key = request.get_json().get('file_key')
    if not file_key:
        # If no video ID is provided, return an error response
        abort(400, description="Missing parameter")
        
    s3 = S3(boto3.client('s3'))
    transcription = s3.get_dict_from_video_data(prefix='',
                                                file_name=file_key,
                                                bucket_name="project-data-69")

    if transcription == None:
        abort(404, description="Transcription not found")
    else:
        s3.delete_item(bucket_name="project-data-69",
                        object_key=file_key)
    
    transcriber_helper = CloudTranscriber()
    
    transcription = transcriber_helper.clean_transcription(transcription)
    
    s3.write_dict_to_video_data(prefix='',
                                dictionary=transcription,
                                file_name=file_key,
                                bucket_name="project-data-69")
    
    url = s3.get_item_url(bucket_name=buckets.project_data,
                            object_key=file_key,
                            expiry_time=url_expiry_time)
    
    if url == None:
        abort(404, description="Video not found")
    
    return jsonify({'url': url}), 200