from flask import abort
from flask import request
from app.VideoEditor import AWSBackgroundCreator
from app.services.s3 import S3
from flask import jsonify
import boto3
import app.configuration.buckets as buckets

# from app.content_generation import  
from . import background_maker_api_bp  # Import the Blueprint
import logging

logging.basicConfig(level=logging.INFO)

url_expiry_time = 3600*5 #(5 hours)

@background_maker_api_bp.route('/background_maker', methods=['POST'])
def make_background():
    '''
    This function builds a blank video based on the given audio_id.
    It retrieves the audio file from AWS S3, and then uses the audio file to create a blank video.
    The data sent should be:
    {
        "audio_id": "audio_id"
        "background_media_ids": ["media_id1", "media_id2", ...],
        "width": 1920,
        "height": 1080
    }
    
    Audio ID must first be put in the database
    '''
    logging.info("Creating video")
    data = request.get_json()

    # Validate payload
    if not all(key in data for key in ['audio_id', 'background_media_ids', 'width', 'height']):
        abort(400, description="Missing data in request payload")

    audio_id = data['audio_id']
    background_media_ids = data['background_media_ids']
    width = data['width']
    height = data['height']

    bg_creator = AWSBackgroundCreator(audio_bucket=buckets.audio_files,
                                      output_video_bucket=buckets.blank_videos,
                                      background_video_bucket=buckets.public_bg_videos,
                                      s3=S3(boto3.client('s3')))
    
    try:
        response = bg_creator.create_horizontal(audio_id,
                                                background_media_ids,
                                                width,
                                                height)
    except Exception as e:
        # Log the exception and return a 500 error
        logging.exception("Failed to create video")
        abort(500, description=str(e))
    
    if response:
        return jsonify({"message": "Video created successfully"}), 200
    else:
        logging.debug("Video not found")
        abort(404, description="Video not found")

@background_maker_api_bp.route('/get_blank_video', methods=['GET'])
def get_blank_video():
    '''
    Returns a url to the video with the given id.
    URL expires in url_expiry_time seconds
    '''
    video_id = request.args.get('id')
    if not video_id:
        # If no video ID is provided, return an error response
        abort(400, description="Missing video ID parameter")
        
    s3 = S3(boto3.client('s3'))
    url = s3.get_item_url(bucket_name=buckets.blank_videos,
                          object_key=video_id,
                          expiry_time=url_expiry_time)

    if url == None:
        abort(404, description="Video not found")
    
    return jsonify({'url': url})

@background_maker_api_bp.route('/get_user_bg_video', methods=['GET'])
def get_user_bg_video():
    '''
    input id, user_id
    Returns a url to the video with the given id 
    At location: buckets.bg_videos/private/user_id/id
    URL expires in url_expiry_time seconds
    '''
    user_id = request.args.get('user_id')
    video_id = request.args.get('id')
    if not video_id or not user_id:
        # If no video ID is provided, return an error response
        abort(400, description="Missing video ID parameter")
        
    s3 = S3(boto3.client('s3'))
    user_folder = user_id + "/"
    url = s3.get_item_url(bucket_name=buckets.bg_videos,
                         object_key=video_id,
                         expiry_time=url_expiry_time,
                         prefix=buckets.private_bg_prefix + user_folder)

    if url == None:
        abort(404, description="Video not found")
    
    return jsonify({'url': url})

@background_maker_api_bp.route('/get_all_public_bgs', methods=['GET'])
def get_all_public_bgs():
    '''
    No input required
    Returns a list links of all public background videos
    '''
    s3 = S3(boto3.client('s3'))
    bg_video_ids = s3.get_all_items(bucket_name=buckets.bg_videos, 
                                    prefix=buckets.public_bg_videos_prefix)
    
    bg_video_links = []
    for id in bg_video_ids:
        bg_video_links.append(s3.get_item_url(bucket_name=buckets.bg_videos,
                                              object_key=id,
                                              expiry_time=url_expiry_time,
                                              prefix=buckets.public_bg_videos_prefix))
    return jsonify(bg_video_links)