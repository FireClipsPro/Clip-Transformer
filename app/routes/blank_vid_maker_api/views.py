from flask import send_file, abort
from flask import request, jsonify
from app.configuration import directories
from app.VideoEditor import AWSBackgroundCreator
# from app.content_generation import  
from . import blank_vid_maker_api_bp  # Import the Blueprint
import logging
import os

logging.basicConfig(level=logging.DEBUG)

@blank_vid_maker_api_bp.route('/video', methods=['POST'])
def get_video(audio_id):
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
    '''
    data = request.get_json()
    
    audio_id = data['audio_id']
    background_media_ids = data['background_media_ids']
    width = data['width']
    height = data['height']
    
    # audio_file = "get audio file from AWS S3"
    
    audio_bucket_name = 'audio-files-69'
    background_vid_bucket_name = 'background-videos-69'
    blank_vid_bucket_name = 'blank-videos-69'
    
     # create a blank video
    bg_creator = AWSBackgroundCreator()
    
    video_path = f'{os.getcwd()}/{directories.VM_BACKGROUNDS}{audio_id}.mp4'
    # log if video exists:
    logging.debug(f'os.cwd: {os.getcwd()}')
    logging.debug(f' video_path: {video_path}'
                  f' video_id: {audio_id}'
                  f' directories.VM_BACKGROUNDS: {directories.VM_BACKGROUNDS}')
    if os.path.exists(video_path):
        logging.debug(f'video exists: {video_path}')
    else:
        logging.debug(f'video does not exist: {video_path}')
    
    try:
        return send_file(video_path, as_attachment=True)
    except FileNotFoundError:
        abort(404, description="Video not found")
