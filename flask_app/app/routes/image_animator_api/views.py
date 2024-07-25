import logging

import boto3
from flask import abort, jsonify, request

import app.configuration.buckets as buckets
import app.configuration.video_maker_presets as configuration
from app.content_generation import AWSImageToVideoCreator
from app.models.overlay_video import OverlayVideo
from app.services.s3 import S3

# from app.content_generation import  
from . import image_animator_api_bp  # Import the Blueprint

logging.basicConfig(level=logging.INFO)

url_expiry_time = 3600*5 #(5 hours)

@image_animator_api_bp.route('/animate_images', methods=['POST'])
def animate_images():
    '''
    This function takes in the following json payload:
    {
        "user_id": "panda@example.com",
        "project_id": "42069",
        "images": [{    "id": "id",
                        "start": 0,
                        "end": 10
                    }, ...],
        "video_type": "horizontal" or "vertical"
    }
    Videos are the videos (or animated images) that will be overlayed on top of the original video.
    '''
    logging.info("Creating video")
    data = request.get_json()
    # TODO remove the overlay variables from the payload
    # Validate payload
    if not all(key in data for key in ['user_id',
                                       'project_id',
                                       'images',
                                       'video_type']):
        abort(400, description="Missing data in request payload")
    
    if data['video_type'] == 'horizontal':
        frame_width = configuration.HORIZONTAL_VIDEO_WIDTH
        frame_height = configuration.VERTICAL_VIDEO_HEIGHT
    elif data['video_type'] == 'vertical':
        frame_width = configuration.VERTICAL_VIDEO_WIDTH
        frame_height = configuration.VERTICAL_VIDEO_HEIGHT
    
    images = data['images']
    if not isinstance(images, list):
        abort(400, description="Videos must be a list")
    user_id = data['user_id']
    project_id = data['project_id']
    s3 = S3(boto3.client('s3'))
    image_to_video_creator = AWSImageToVideoCreator(frame_height=frame_height,
                                                    frame_width=frame_width) 

    try:    
        image_clips = get_images_from_s3(user_id=user_id, 
                                            project_id=project_id,
                                            images=images,
                                            s3=s3)
                
        animated_images = image_to_video_creator.convert_to_videos(images=image_clips,
                                                                    border_colors=[(0,0,0)],
                                                                    frame_width=frame_width,
                                                                    frame_height=frame_height,
                                                                    zoom_speed='fast')
        
        urls = []
        for i in range(len(animated_images)):
            bucket_path = user_id + "/" + project_id + "/" + buckets.image_videos_folder
            response = s3.write_imageclip_as_videofile(image_clip=animated_images[i],
                                                        video_id=images[i]['id'][:-4],
                                                        bucket_name=buckets.project_data,
                                                        prefix=bucket_path)
            if response:
                urls.append(s3.get_item_url(bucket_name=buckets.project_data,
                                            object_key=images[i]['id'][:-4] + ".mp4",
                                            expiry_time=url_expiry_time,
                                            prefix=bucket_path))
        
    except Exception as e:
        # Log the exception and return a 500 error
        logging.exception("Failed to create video")
        abort(500, description=str(e))
    
    if len(urls) > 0:
        return jsonify({"message": "images created successfully", 
                        "urls" : urls}), 200
    else:
        logging.debug("Video not found")
        abort(404, description="Video not found")

def get_images_from_s3(user_id, 
                       project_id,
                       images,
                       s3: S3):
    
    image_clips = []
    for image in images:
        bucket_path = user_id + "/" + project_id + "/" + buckets.images_folder
        
        image_clip = s3.get_imageclip(image_id=image['id'],
                                        bucket_name=buckets.project_data,
                                        duration=image['end'] - image['start'],
                                        prefix=bucket_path)
        
        image_clips.append(image_clip)
        
    return image_clips