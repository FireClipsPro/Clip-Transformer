import logging

import boto3
from flask import abort, jsonify, request

import app.configuration.buckets as buckets
from app.models.overlay_video import OverlayVideo
from app.services.s3 import S3
from app.VideoEditor import AWSMediaAdder

# from app.content_generation import  
from . import media_adder_api_bp  # Import the Blueprint

logging.basicConfig(level=logging.INFO)

url_expiry_time = 3600*5 #(5 hours)

@media_adder_api_bp.route('/add_media', methods=['POST'])
def add_media():
    '''
    This function takes in the following json payload:
    {
        "user_id": "panda@example.com",
        "project_id": "42069",
        "videos": [{    "id": "id",
                        "start": 0,
                        "end": 10
                    }, ...],
        "overlay_zone_top_left": [x, y],
        "overlay_zone_width": 100,
        "overlay_zone_height": 100
    }
    Videos are the videos (or animated images) that will be overlayed on top of the original video.
    '''
    logging.info("Creating video")
    data = request.get_json()
    
    # Validate payload
    if not all(key in data for key in ['user_id',
                                       'project_id',
                                       'videos',
                                       'overlay_zone_top_left',
                                       'overlay_zone_width',
                                       'overlay_zone_height']):
        abort(400, description="Missing data in request payload")
    
    videos = data['videos']
    if not isinstance(videos, list):
        abort(400, description="Videos must be a list")
    user_id = data['user_id']
    project_id = data['project_id']
    s3 = S3(boto3.client('s3'))
    media_adder = AWSMediaAdder()
    
    try:    
        videos = create_video_objects(user_id=user_id, 
                                      project_id=project_id,
                                      videos=videos,
                                      s3=s3)
        
        bucket_path = user_id + "/" + project_id + "/" + buckets.blank_videos_folder
        blank_video = s3.get_videofileclip(video_id=buckets.blank_video_fname,
                                             bucket_name=buckets.project_data,
                                             prefix=bucket_path)
        
        video_with_media = media_adder.add_media_to_video(original_vid=blank_video,
                                                            videos=videos,
                                                            overlay_zone_top_left=data['overlay_zone_top_left'],
                                                            overlay_zone_width=data['overlay_zone_width'],
                                                            overlay_zone_height=data['overlay_zone_height'])
        
        bucket_path = user_id + "/" + project_id + "/" + buckets.video_with_media_folder
        response = s3.write_videofileclip(clip=video_with_media,
                                            video_id=buckets.video_with_media_fname,
                                            bucket_name=buckets.project_data,
                                            prefix=bucket_path)
        if  response:
            url = s3.get_item_url(bucket_name=buckets.project_data,
                                    object_key=buckets.video_with_media_fname,
                                    expiry_time=url_expiry_time,
                                    prefix=bucket_path)
        
    except Exception as e:
        # Log the exception and return a 500 error
        logging.exception("Failed to create video")
        abort(500, description=str(e))
    
    if url:
        return jsonify({"message": "Video created successfully", 
                        "url" : url}), 200
    else:
        logging.debug("Video not found")
        abort(404, description="Video not found")

def create_video_objects(user_id, project_id, videos, s3: S3):
    video_objects = []
    for video in videos:
        
        bucket_path = user_id + "/" + project_id + "/" + buckets.image_videos_folder
        video_file_clip = s3.get_videofileclip(video_id=video['id'],
                                               bucket_name=buckets.project_data,
                                               prefix=bucket_path)
        
        video_objects.append(OverlayVideo(video=video_file_clip,
                                         start=video['start'],
                                         end=video['end']))
        
        logging.info(f"Video object created with id: {video['id']} and start: {video['start']} and end: {video['end']}")
        
    return video_objects

@media_adder_api_bp.route('/get_video', methods=['GET'])
def get_video():
    '''
    Returns a url to the video with the given id.
    URL expires in url_expiry_time seconds
    '''
    video_id = request.args.get('id')
    if not video_id:
        # If no video ID is provided, return an error response
        abort(400, description="Missing video ID parameter")
        
    s3 = S3(boto3.client('s3'))
    url = s3.get_item_url(bucket_name=buckets.videos_with_media,
                          object_key=video_id,
                          expiry_time=url_expiry_time)

    if url == None:
        abort(404, description="Video not found")
    
    return jsonify({'url': url})