from flask import abort
from flask import request
from app.subtitle_adder import AWSSubtitleAdder
from app.services.s3 import S3
from flask import jsonify
import boto3
import app.configuration.buckets as buckets

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
        "font_size": "int",
        "font_name": "string",
        "outline_color": "string",
        "outline_width": "int",
        "font_color": "string",
        "all_caps": "boolean",
        "punctuation": "boolean,
        "y_percent": "int",
    }
    '''
    logging.info("Adding subtitles")
    data = request.get_json()

    # Validate payload
    if not all(key in data for key in ['project_id', 'video_id', 'font_size', 'font_name', 'outline_color', 'outline_width', 'font_color', 'all_caps', 'punctuation', 'y_percent']):
        abort(400, description="Missing data in request payload")

    project_id = data['project_id']
    video_id = data['video_id']
    font_size = data['font_size']
    font_name = data['font_name']
    outline_color = data['outline_color']
    outline_width = data['outline_width']
    font_color = data['font_color']
    all_caps = data['all_caps']
    punctuation = data['punctuation']
    y_percent = data['y_percent']
    
    s3 = S3(boto3.client('s3'))

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
                      font_name,
                      outline_color,
                      outline_width,
                      font_color,
                      all_caps,
                      punctuation,
                      y_percent)
        
        # Write the final video to s3
        s3.write_videofileclip(clip=final, video_id=video_id, bucket_name=buckets.videos_with_subtitles)
        s3.dispose_temp_files()

    except Exception as e:
        # Log the exception and return a 500 error
        logging.exception("Failed to add subtitles to video")
        abort(500, description=str(e))

    return jsonify({"message": f"Subtitles added successfully. Video saved to bucket {buckets.videos_with_subtitles} with video id {video_id}"}), 200