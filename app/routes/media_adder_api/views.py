from flask import abort
from flask import request
from app.VideoEditor import AWSMediaAdder
from app.services.s3 import S3
from app.models.overlay_video import OverlayVideo
from flask import jsonify
import boto3
import app.configuration.buckets as buckets

# from app.content_generation import  
from . import media_adder_api_bp  # Import the Blueprint
import logging

logging.basicConfig(level=logging.INFO)

url_expiry_time = 3600*5 #(5 hours)

# the route for this is http://localhost:5000/media_adder_api/add_media
@media_adder_api_bp.route('/add_media', methods=['POST'])
def add_media():
    '''
    This function takes in the following json payload:
    {
        "original_vid_id": "original_vid_id",
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
    if not all(key in data for key in ['original_vid_id',
                                       'videos',
                                       'overlay_zone_top_left',
                                       'overlay_zone_width',
                                       'overlay_zone_height']):
        abort(400, description="Missing data in request payload")
    
    try:
        media_adder = AWSMediaAdder(input_video_bucket=buckets.blank_videos,
                                    media_addied_videos_bucket=buckets.videos_with_media,
                                    image_videos_bucket=buckets.image_videos,
                                    output_video_bucket=buckets.videos_with_media,
                                    s3=S3(boto3.client('s3')))
        
        videos = create_video_objects(data['videos'])
        
        response = media_adder.add_media_to_video(original_vid_id=data['original_vid_id'],
                                                  videos=videos,
                                                  overlay_zone_top_left=data['overlay_zone_top_left'],
                                                  overlay_zone_width=data['overlay_zone_width'],
                                                  overlay_zone_height=data['overlay_zone_height'])
    except Exception as e:
        # Log the exception and return a 500 error
        logging.exception("Failed to create video")
        abort(500, description=str(e))
    
    if response:
        return jsonify({"message": "Video created successfully"}), 200
    else:
        logging.debug("Video not found")
        abort(404, description="Video not found")

def create_video_objects(videos):
    video_objects = []
    for video in videos:
        video_objects.append(OverlayVideo(id=video['id'],
                                         start=video['start'],
                                         end=video['end']))
        logging.info(f"Video object created: {video_objects[-1]}")
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