from flask import request
from app.services.s3 import S3
from flask import jsonify
import boto3
import app.configuration.buckets as buckets
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os

# from app.content_generation import  
from . import upload_audio_api_bp  # Import the Blueprint
import logging

logging.basicConfig(level=logging.INFO)

url_expiry_time = 3600*5 #(5 hours)

@upload_audio_api_bp.route('/upload', methods=['POST'])
def upload():
    '''
    This function takes in the following json payload:
    {   
        "user_id": "panda@example.com",
        "project_id": "42069",
        "audio_file": <audio_file>
    }
    Stores the audio file for the project in S3.
    Returns the link to the audio file.
    '''
    # Check for the audio file in the request
    if 'audio_file' not in request.files:
        return jsonify({'error': 'No audio file part'}), 400
    file = request.files['audio_file']
    if file.filename == '':
        return jsonify({'error': 'No selected audio file'}), 400
    
    try:
        # Validate file extension
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext != '.mp3':
            return jsonify({'error': 'File format not supported. Only MP3 files are allowed.'}), 400

        # Check for the user_id and project_id in the request form
        user_id = request.form.get('user_id')
        project_id = request.form.get('project_id')
        if not user_id or not project_id:
            return jsonify({'error': 'Missing user_id or project_id'}), 400
        
        if file:
            s3 = S3(boto3.client('s3'))
            s3.upload_mp3(file_name=buckets.audio_file_name,
                            file=file,
                            bucket_name=buckets.project_data,
                            prefix=user_id + "/" + project_id + "/" + buckets.audio_folder)

            url = s3.get_item_url(bucket_name=buckets.project_data,
                                    object_key=buckets.audio_file_name,
                                    expiry_time=url_expiry_time,
                                    prefix=user_id + "/" + project_id + "/" + buckets.audio_folder)
    except Exception as e:
        logging.exception("Failed to upload audio file")
        return jsonify({'error': 'Failed to upload audio file'}), 500
    
    return jsonify({'message': 'File uploaded successfully', 'url': url}), 200

        
    
# example curl command
# curl -X POST http://localhost:5000/upload_audio_api/upload \
#      -F "user_id=SnoopDoggyDog@weed.com" \
#      -F "project_id=a6b121a3-e67c-41a8-8f52-aac375934a02" \
#      -F "audio_file=@/Users/alexander/Documents/Code/Clip_Transformer/Clip-Transformer/media_storage/video_maker/audio_input/short_test.mp3"