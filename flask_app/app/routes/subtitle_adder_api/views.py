from flask import abort
from flask import request
from app.subtitle_adder import AWSSubtitleAdder
from app.services.s3 import S3
from flask import jsonify
import os
import boto3
import app.configuration.buckets as buckets
import app.configuration.video_maker_presets as presets

from . import subtitle_adder_api_bp
import logging

logging.basicConfig(level=logging.INFO)

url_expiry_time = 3600*5

@subtitle_adder_api_bp.route('/add_subtitles', methods=['POST'])
def add_subtitles():
    '''
    This function adds subtitles to a video given a video id and transcription id
    It fetches the video and transcription from an s3 bucket using this id.
    The data sent should be:
    {
        "project_id": "string",
        "video_id": "string"
    }
    '''
    logging.info("Adding subtitles")
    data = request.get_json()

    # Validate payload
    if not all(key in data for key in ['project_id', 'video_id', 'font_size', 'font_name', 'outline_color', 'outline_width', 'font_color', 'all_caps', 'punctuation', 'y_percent']):
        abort(400, description="Missing data in request payload")

    project_id = data['project_id']
    video_id = data['video_id']
    font_size = presets.preset['default']['FONT_SIZE']
    font_name = presets.preset['default']['FONT']
    outline_color = "black"
    outline_width = presets.preset['default']['FONT_OUTLINE_WIDTH']
    font_color = "white"
    all_caps = presets.preset['default']['ALL_CAPS']
    punctuation = presets.preset['default']['PUNCTUATION']
    y_percent = presets.preset['default']['Y_PERCENT_HEIGHT_OF_SUBTITLE']
    
    fonts_directory = os.path.join(os.getcwd(), 'fonts/')
    ensure_fonts_directory_exists(fonts_directory=fonts_directory)
    local_font_path = os.path.join(fonts_directory, font_name)

    s3 = S3(boto3.client('s3'))

    if not os.path.exists(local_font_path):
        s3.download_file(bucket_name=buckets.font_bucket,
                         font_key=font_name,
                         local_font_path=local_font_path)

    clip = s3.get_videofileclip(video_id=video_id, bucket_name=buckets.videos_with_media)
    transcription = s3.get_dict_from_video_data(project_id=project_id ,
                                                file_name='transcription.json',
                                                bucket_name=buckets.project_data)
    
    subtitle_adder = AWSSubtitleAdder()

    try:
        final = subtitle_adder.add_subtitles(
            clip,
            transcription,
            font_size,
            local_font_path,
            outline_color,
            outline_width,
            font_color,
            all_caps,
            punctuation,
            y_percent)
        
        # Write the final video to s3
        s3.write_videofileclip(clip=final,
                               video_id=video_id,
                               bucket_name=buckets.videos_with_subtitles)
        s3.dispose_temp_files()

    except Exception as e:
        # Log the exception and return a 500 error
        logging.exception("Failed to add subtitles to video")
        abort(500, description=str(e))

    return jsonify({"message": f"Subtitles added successfully. Video saved to bucket {buckets.videos_with_subtitles} with video id {video_id}"}), 200

def ensure_fonts_directory_exists(fonts_directory):
    """Ensure that the fonts directory exists."""
    if not os.path.exists(fonts_directory):
        os.makedirs(fonts_directory)