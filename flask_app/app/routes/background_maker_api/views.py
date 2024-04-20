import logging

import boto3
from flask import Blueprint, Flask, abort, jsonify, request
from werkzeug.utils import secure_filename

import app.configuration.buckets as buckets
from app.services.s3 import S3
from app.VideoEditor import AWSBackgroundCreator

# from app.content_generation import  
from . import background_maker_api_bp  # Import the Blueprint

logging.basicConfig(level=logging.INFO)

url_expiry_time = 3600*5 #(5 hours)

@background_maker_api_bp.route('/make_background', methods=['POST'])
def make_background():
    '''
    This function builds a blank video based on the given audio_id.
    It retrieves the audio file from AWS S3, and then uses the audio file to create a blank video.
    The data sent should be:
    {
        "user_id": "panda@example.com",
        "project_id": "42069",
        "background_videos": [{"file_name": "media_id1",
                               "bucket": "project-data-69",
                               "is_private": true}, ...],
        "width": 1920,
        "height": 1080
    }
    Audio ID must first be put in the database
    '''
    logging.info("Creating video")
    payload = request.get_json()
    is_valid, message = validate_payload(payload)
    if not is_valid:
        return jsonify({"error": message}), 400
    
    user_id = payload['user_id']
    project_id = payload['project_id']
    background_videos = payload['background_videos']  # This is a list of dictionaries
    width = payload['width']
    height = payload['height']
    
    s3 = S3(boto3.client('s3'))
    bg_creator = AWSBackgroundCreator()
    
    try:
        audio_bucket_path = user_id + "/" + project_id + "/" + buckets.audio_folder
        audio_clip = s3.get_audiofileclip(audio_id=buckets.audio_fname,
                                          bucket_name=buckets.project_data,
                                          prefix=audio_bucket_path)
        
        background_videofileclips = []
        for video in background_videos:
            logging.info(f"Getting video {video['file_name']}")
            
            if video['is_private']:
                bucket_path = user_id + "/" + project_id + "/" + buckets.background_videos_folder
                bucket = buckets.project_data
            else:
                bucket_path = buckets.public_bg_videos_prefix
                bucket = buckets.bg_videos
            
            background_videofileclips.append(s3.get_videofileclip(video_id=video['file_name'],
                                                                    bucket_name=bucket,
                                                                    prefix=bucket_path))
        
        video_clip = bg_creator.create_horizontal(audio_clip=audio_clip,
                                                    background_videos=background_videofileclips,
                                                    width=width,
                                                    height=height)
        
        video_clip_path = user_id + "/" + project_id + "/" + buckets.blank_videos_folder
        result = s3.write_videofileclip(clip=video_clip,
                                        video_id=buckets.blank_video_fname,
                                        bucket_name=buckets.project_data,
                                        prefix=video_clip_path)
        
        url = s3.get_item_url(bucket_name=buckets.project_data,
                              object_key=buckets.blank_video_fname,
                              expiry_time=url_expiry_time,
                              prefix=video_clip_path)
        
        s3.dispose_temp_files()

    except Exception as e:
        # Log the exception and return a 500 error
        logging.exception("Failed to create video")
        abort(500, description=str(e))
    
    if result and url:
        return jsonify({"url": url}), 200
    else:
        logging.debug("Video not found")
        abort(404, description="Video not found")

@background_maker_api_bp.route('/get_blank_video', methods=['GET'])
def get_blank_video():
    '''
    Parameters:
    {
        "user_id": "panda@example.com",
        "project_id": "42069",
    }
    Returns a url to the video with the given id.
    URL expires in url_expiry_time seconds
    '''
    user_id = request.args.get('user_id')
    project_id = request.args.get('project_id')
    
    if not user_id or not project_id:
        abort(400, description="Missing parameter")
    
    try:
        video_clip_path = user_id + "/" + project_id + "/" + buckets.blank_videos_folder
        s3 = S3(boto3.client('s3'))
        url = s3.get_videofileclip(video_id=buckets.blank_video_fname,
                                    bucket_name=buckets.project_data,
                                    prefix=video_clip_path,
                                    expiry_time=url_expiry_time)
    except Exception as e:
        # Log the exception and return a 500 error
        logging.exception("Failed to get video")
        abort(500, description=str(e))

    if url == None:
        abort(404, description="Video not found")
    
    return jsonify({'url': url})

@background_maker_api_bp.route('/upload_background', methods=['POST'])
def upload_background():
    '''
    Parameters:
    {
        "user_id": ",
        "background_video": <background_video>
    }
    Stores the background video in the project's bucket.
    Returns the link to the background video.
    '''
    user_id = request.form.get('user_id')
    video_file = request.files['background_video']

    # Ensure all required parameters and file are present
    if not user_id or not video_file:
        return jsonify({"error": "Missing parameter or file"}), 400

    # Validate file extension
    filename = secure_filename(video_file.filename)
    if not filename.endswith('.mp4'):
        return jsonify({"error": "File format not supported. Only MP4 files are allowed."}), 400
    
    s3 = S3(boto3.client('s3'))
    try:
        bucket_path = user_id + "/" + buckets.background_videos_folder
        result = s3.upload_mp4(file_name=filename,
                                file=video_file,
                                bucket_name=buckets.project_data,
                                prefix=bucket_path)
        
        if result:
            url = s3.get_item_url(bucket_name=buckets.project_data,
                                    object_key=filename,
                                    expiry_time=url_expiry_time,
                                    prefix=bucket_path)
        
        return jsonify({"message": "Video uploaded successfully", "url": str(url)}), 200
    except Exception as e:
        # Handle exceptions and errors
        return jsonify({"error": str(e)}), 500

@background_maker_api_bp.route('/get_user_bg_video', methods=['GET'])
def get_user_bg_video():
    '''
    input:
    {
        "user_id": "panda@example.com"
    }
    Returns a url to the video with the given id
    '''
    user_id = request.args.get('user_id')
    
    s3 = S3(boto3.client('s3'))
    bg_videos_path = user_id + "/"
    bg_video_ids = s3.get_all_items(bucket_name=buckets.project_data, 
                                    prefix=bg_videos_path)
    
    bg_video_links = []
    for id in bg_video_ids:
        bg_video_links.append(s3.get_item_url(bucket_name=buckets.project_data,
                                              object_key=id,
                                              expiry_time=url_expiry_time,
                                              prefix=bg_videos_path))
    return jsonify(bg_video_links)

@background_maker_api_bp.route('/get_all_public_bgs', methods=['GET'])
def get_all_public_bgs():
    '''
    No input required
    Returns a list links of all public background videos and their ids
    '''
    s3 = S3(boto3.client('s3'))
    bg_video_ids = s3.get_all_items(bucket_name=buckets.bg_videos, 
                                    prefix=buckets.public_bg_videos_prefix)

    bg_video_links = []
    for id in bg_video_ids:
        bg_video_links.append({"url": s3.get_item_url(bucket_name=buckets.bg_videos,
                                              object_key=id,
                                              expiry_time=url_expiry_time),
                                # id is public/cloud.mp4 and we want cloud.mp4
                               "id": id.split('/')[1]})
        
    return jsonify(bg_video_links)

def validate_payload(payload):
    """
    Validates the input JSON payload based on the new specifications for the background maker.

    :param payload: The payload to validate.
    :return: A tuple (bool, str) indicating whether the payload is valid and a message.
    """
    # Check if payload exists and has required keys
    if not payload:
        return False, "Payload is empty."
    
    required_top_level_keys = ["user_id", "project_id", "background_videos", "width", "height"]
    for key in required_top_level_keys:
        if key not in payload:
            return False, f"Missing '{key}' in payload."
    
    # Specific validations for each field
    if not isinstance(payload["user_id"], str) or not payload["user_id"]:
        return False, "'user_id' must be a non-empty string."
    
    if not isinstance(payload["project_id"], str) or not payload["project_id"]:
        return False, "'project_id' must be a string."
    
    if not isinstance(payload["background_videos"], list) or not payload["background_videos"]:
        return False, "'background_videos' must be a non-empty list."
    
    for item in payload["background_videos"]:
        required_media_keys = ["file_name", "is_private"]
        for media_key in required_media_keys:
            if media_key not in item:
                return False, f"Missing '{media_key}' in background_videos item."
    
    if not isinstance(payload["width"], int) or payload["width"] <= 0:
        return False, "'width' must be a positive integer."
    
    if not isinstance(payload["height"], int) or payload["height"] <= 0:
        return False, "'height' must be a positive integer."
    
    return True, "Valid payload."


'''
curl -X POST http://localhost:5000/background_maker_api/upload_background \
     -F "user_id=SnoopDoggyDog@weed.com" \
     -F "project_id=a6b121a3-e67c-41a8-8f52-aac375934a02" \
     -F "background_video=@/Users/alexander/Documents/Code/Clip_Transformer/Clip-Transformer/media_storage/video_maker/backgrounds/wormhole_from_aws.mp4"
'''