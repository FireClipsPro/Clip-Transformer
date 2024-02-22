from flask import send_file, abort
from app.configuration import directories
from app.content_generation import  
# from . import blank_vid_maker_api_bp  # Import the Blueprint
import logging
import os

logging.basicConfig(level=logging.DEBUG)

@blank_vid_maker_api_bp.route('/video/<string:audio_id>')
def get_video(audio_id):
    '''
    This function builds a blank video based on the given audio_id.
    It retrieves the audio file from AWS S3, and then uses the audio file to create a blank video.
    '''
    # audio_file = "get audio file from AWS S3"
    
    
    
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
