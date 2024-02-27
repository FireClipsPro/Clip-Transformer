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

@background_maker_api_bp.route('/background_maker', methods=['POST'])
def get_video():
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
                                      background_video_bucket=buckets.bg_videos,
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
