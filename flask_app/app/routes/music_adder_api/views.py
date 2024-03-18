from flask import request
from app.services.s3 import S3
from flask import jsonify
import boto3
import app.configuration.buckets as buckets
from app.music_adder.aws_music_adder import AWSMusicAdder
from flask import Flask, request, jsonify, abort
from werkzeug.utils import secure_filename
import os

# from app.content_generation import  
from . import music_adder_api_bp  # Import the Blueprint
import logging

logging.basicConfig(level=logging.INFO)

url_expiry_time = 3600*5 #(5 hours)

@music_adder_api_bp.route('/add_music', methods=['POST'])
def add_music():
    '''
    This function takes in the following json payload:
    {
        "user_id": "panda@example.com",
        "project_id": "42069",
        "music_id": "id",
        "music_is_private": "true",
        "video_name": "video.mp4",
        "video_folder": "video_folder"
    }
    '''
    logging.info("Creating video")
    data = request.get_json()
    
    # Validate payload
    if not all(key in data for key in ['user_id',
                                       'project_id',
                                       'music_id',
                                       'music_is_private']):
        abort(400, description="Missing data in request payload")
    
    user_id = data['user_id']
    project_id = data['project_id']
    music_id = data['music_id']
    music_is_private = data['music_is_private']
    s3 = S3(boto3.client('s3'))
    music_adder = AWSMusicAdder()
    
    
    try:
        if music_is_private:
            bucket_path = user_id + "/" + buckets.music_folder
        else:
            bucket_path = buckets.music_folder

        audio_clip = s3.get_audiofileclip(audio_id=music_id,
                                            bucket_name=buckets.project_data,
                                            prefix=bucket_path)
    
        video_clip_path = user_id + "/" + project_id + "/" + data['video_folder']
        video_clip = s3.get_videofileclip(video_id=data['video_name'],
                                            bucket_name=buckets.project_data,
                                            prefix=video_clip_path)
    
        # do music adder magic:
        clip_with_music = music_adder.add_music_to(music=audio_clip, video=video_clip)
        
        video_clip_path = user_id + "/" + project_id + "/" + buckets.video_with_music_folder
        result = s3.write_videofileclip(clip=clip_with_music,
                                        video_id=buckets.video_with_music_fname,
                                        bucket_name=buckets.project_data,
                                        prefix=video_clip_path)
        if result:
            url = s3.get_item_url(bucket_name=buckets.project_data,
                                    object_key=buckets.video_with_music_fname,
                                    expiry_time=url_expiry_time,
                                    prefix=video_clip_path)
        
        s3.dispose_temp_files()
            
    except Exception as e:
        # Log the exception and return a 500 error
        logging.exception("Failed to add music to video")
        abort(500, description=str(e))
    
    if url:
        return jsonify({"message": "Video created successfully", 
                        "url" : url}), 200
    else:
        logging.debug("Video not found")
        abort(404, description="Video not found")

@music_adder_api_bp.route('/upload', methods=['POST'])
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
            bucket_path = user_id + "/" + project_id + "/" + buckets.music_folder
            logging.info(f"Uploading audio file to {bucket_path}")
            s3.upload_mp3(file_name=filename,
                            file=file,
                            bucket_name=buckets.project_data,
                            prefix=bucket_path)

            url = s3.get_item_url(bucket_name=buckets.project_data,
                                    object_key=filename,
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
# curl -X POST http://localhost:5000/music_adder_api/upload \
#      -F "user_id=SnoopDoggyDog@weed.com" \
#      -F "project_id=19b112e0-e393-4247-9d36-7d9e54cfa222" \
#      -F "audio_file=@/Users/alexander/Documents/Code/Clip_Transformer/Clip-Transformer/media_storage/video_maker/audio_input/joe_beast.mp3"