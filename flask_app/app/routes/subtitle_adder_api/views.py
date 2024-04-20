import logging
import os

import boto3
from flask import abort, jsonify, request

import app.configuration.buckets as buckets
import app.configuration.video_maker_presets as presets
from app.services.s3 import S3
from app.subtitle_adder import AWSSubtitleAdder

from . import subtitle_adder_api_bp

logging.basicConfig(level=logging.INFO)

url_expiry_time = 3600*5

@subtitle_adder_api_bp.route('/add_subtitles', methods=['POST'])
def add_subtitles():
    '''
    This function adds subtitles to a video given a video id and transcription id
    It fetches the video and transcription from an s3 bucket using this id.
    The data sent should be:
    {   
        "user_id": "int",
        "project_id": "string"
    }
    '''
    logging.info("Adding subtitles")
    data = request.get_json()

    # Validate payload
    if not all(key in data for key in ['user_id', 'project_id']):
        abort(400, description="Missing data in request payload")

    user_id = data['user_id']
    project_id = data['project_id']
    font_size = presets.preset['default']['FONT_SIZE']
    font_name = presets.preset['default']['FONT']
    outline_color = presets.preset['default']['FONT_OUTLINE_COLOR']
    outline_width = presets.preset['default']['FONT_OUTLINE_WIDTH']
    font_color = presets.preset['default']['FONT_COLOR']
    all_caps = presets.preset['default']['ALL_CAPS']
    punctuation = presets.preset['default']['PUNCTUATION']
    y_percent = presets.preset['default']['Y_PERCENT_HEIGHT_OF_SUBTITLE']
    charcters_per_line = presets.preset['default']['NUMBER_OF_CHARACTERS_PER_LINE']
    
    fonts_directory = os.path.join(os.getcwd(), 'fonts/')
    ensure_fonts_directory_exists(fonts_directory=fonts_directory)
    local_font_path = os.path.join(fonts_directory, font_name)

    s3 = S3(boto3.client('s3'))

    # get the font
    if not os.path.exists(local_font_path):
        s3.download_file(bucket_name=buckets.font_bucket,
                         font_key=font_name,
                         local_font_path=local_font_path)

    clip = s3.get_videofileclip(video_id=buckets.video_with_media_fname, 
                                bucket_name=buckets.project_data,
                                prefix=f"{user_id}/{project_id}/{buckets.video_with_media_folder}")
    
    transcription = s3.get_dict_from_video_data(prefix=f"{user_id}/{project_id}/{buckets.transcripts_folder}",
                                                file_name='transcription.json',
                                                bucket_name=buckets.project_data)
    
    for word in transcription['word_segments']:  # Loop through each dictionary in the list
        if 'word' in word:  # Check if the dictionary has the key 'word'
            word['text'] = word['word'] 
            
    transcription = clean_transcription(transcription)
    
    subtitle_adder = AWSSubtitleAdder()

    try:
        final = subtitle_adder.add_subtitles_to_video(clip,
                                                        transcription['word_segments'],
                                                        font_size,
                                                        font_name,
                                                        outline_color,
                                                        outline_width,
                                                        font_color,
                                                        all_caps,
                                                        punctuation,
                                                        y_percent,
                                                        charcters_per_line)
        
        # Write the final video to s3
        s3.write_videofileclip(clip=final,
                               video_id=buckets.video_with_subtitles_fname,
                               bucket_name=buckets.project_data,
                               prefix=f"{user_id}/{project_id}/{buckets.subtitled_vid_folder}")
        
        # get the url
        url = s3.get_item_url(bucket_name=buckets.project_data,
                                object_key=f"{user_id}/{project_id}/{buckets.subtitled_vid_folder}{buckets.video_with_subtitles_fname}",
                                expiry_time=url_expiry_time)
        
        s3.dispose_temp_files()

    except Exception as e:
        # Log the exception and return a 500 error
        logging.exception("Failed to add subtitles to video")
        abort(500, description=str(e))

    return jsonify({"url": url}), 200

def clean_transcription(transcription):
    for i in range(len(transcription["word_segments"])):
        transcription["word_segments"][i]['text'] = transcription["word_segments"][i]['word']
        del transcription["word_segments"][i]['word']
        if i == 0:
            if 'start' not in transcription["word_segments"][i]:
                transcription["word_segments"][i]['start'] = 0
            if 'end' not in transcription["word_segments"][i]:
                if len(transcription["word_segments"]) > 1:
                    for j in range(1, len(transcription["word_segments"])):
                        if 'start' in transcription["word_segments"][j]:
                            transcription["word_segments"][i]['end'] = transcription["word_segments"][j]['start']
                            break
                else:
                    transcription["word_segments"][i]['end'] = 0
        else:
            if 'start' not in transcription["word_segments"][i]:
                transcription["word_segments"][i]['start'] = transcription["word_segments"][i-1]['end']
            if 'end' not in transcription["word_segments"][i]:
                if len(transcription["word_segments"]) > i+1:
                    for j in range(i+1, len(transcription["word_segments"])):
                        if 'start' in transcription["word_segments"][j]:
                            transcription["word_segments"][i]['end'] = transcription["word_segments"][j]['start']
                            break
                else:
                    transcription["word_segments"][i]['end'] = transcription["word_segments"][i]['start']
    return transcription

def ensure_fonts_directory_exists(fonts_directory):
    """Ensure that the fonts directory exists."""
    if not os.path.exists(fonts_directory):
        os.makedirs(fonts_directory)