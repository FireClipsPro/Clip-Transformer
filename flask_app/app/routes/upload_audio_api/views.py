import logging
import os

import boto3
from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename

import app.configuration.buckets as buckets
from app.services.s3 import S3

# from app.content_generation import  
from . import upload_audio_api_bp  # Import the Blueprint

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
            bucket_path = user_id + "/" + project_id + "/" + buckets.audio_folder
            logging.info(f"Uploading audio file to {bucket_path}")
            s3.upload_mp3(file_name=buckets.audio_fname,
                            file=file,
                            bucket_name=buckets.project_data,
                            prefix=bucket_path)

            url = s3.get_item_url(bucket_name=buckets.project_data,
                                    object_key=buckets.audio_fname,
                                    expiry_time=url_expiry_time,
                                    prefix=bucket_path)
    except Exception as e:
        logging.exception("Failed to upload audio file")
        return jsonify({'error': 'Failed to upload audio file'}), 500
    if url:
        return jsonify({'message': 'File uploaded successfully', 'url': url}), 200
    else:
        return jsonify({'error': 'Failed to upload audio file'}), 500

        
    
# example curl command
# curl -X POST http://localhost:5000/upload_audio_api/upload \
#      -F "user_id=SnoopDoggyDog@weed.com" \
#      -F "project_id=19b112e0-e393-4247-9d36-7d9e54cfa222" \
#      -F "audio_file=@/Users/alexander/Documents/Code/Clip_Transformer/Clip-Transformer/media_storage/video_maker/audio_input/joe_beast.mp3"