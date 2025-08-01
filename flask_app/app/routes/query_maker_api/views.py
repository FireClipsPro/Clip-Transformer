import logging
from typing import Any, Dict

import boto3
from flask import abort, jsonify, request

from app.configuration import buckets, directories
from app.services import S3
from app.text_analyzer import (AWSImageQueryCreator, AWSTranscriptAnalyzer,
                               OpenaiApi)

from . import query_maker_api_bp

logging.basicConfig(level=logging.INFO)

@query_maker_api_bp.route('/make_queries', methods=['POST'])
def make_queries() -> Any:
    """
    Extracts queries from video data using transcription analysis and OpenAI's API.

    Returns:
        JSON response with a list of queries generated from video transcription.
        
    Params:
    {
        'user_id': 'panda@example.com',
        'project_id': '42069',
        'seconds_per_photo': 5,
    }
    Returns:
    {
        'queries': [{'query': "Shubh eating lots of vegtables", 
                     'start': 0,
                     'end': 4,
                     'sentence': sentence,
                     'description': description['description'],
                     'description_start': description['start'],
                     'description_end': description['end'],
                     'image_id': None}, ...]
    }
    """
    request_data = validate_request_data(request.json)
    user_id = request_data['user_id']
    project_id = request_data['project_id']
    seconds_per_photo = request_data['seconds_per_photo']
    
    openai_api = OpenaiApi(api_key_path=directories.OPENAI_API_KEY_PATH)
    
    s3 = S3(boto3.client('s3'))
    
    transcription_bucket_path = user_id + "/" + project_id + "/" + buckets.transcripts_folder
    transcription = s3.get_dict_from_video_data(prefix=transcription_bucket_path,
                                                file_name=buckets.transcription_fname,
                                                bucket_name=buckets.project_data)
    
    transcript_analyzer = AWSTranscriptAnalyzer(music_category_list=directories.MUSIC_CATEGORY_PATH_DICT,
                                                openai_api=openai_api)
    
    image_query_creator = AWSImageQueryCreator(openai_api=openai_api)

    description_list = transcript_analyzer.get_info_for_entire_pod(transcription)
    query_dict = image_query_creator.process_transcription(transcription['word_segments'],
                                                            transcription['word_segments'][-1]['end'],
                                                            seconds_per_photo,
                                                            description_list,
                                                            wants_free_images=True)

    logging.info(f"Query list: {query_dict}")
    query_bucket_path = user_id + "/" + project_id + "/" + buckets.queries_folder
    if not s3.write_dict_to_video_data(prefix=query_bucket_path, 
                                        dictionary=query_dict,
                                        file_name=buckets.query_fname,
                                        bucket_name=buckets.project_data):
        abort(500)

    return jsonify(query_dict)

def validate_request_data(request_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates the request data for required fields and types.

    Args:
        request_json: The JSON payload from the request.

    Returns:
        The validated request data as a dictionary.

    Raises:
        HTTP 400: If the request JSON is missing or invalid.
    """
    if not request_json:
        abort(400, description="Request data is missing.")

    required_fields = {'user_id': str, 'seconds_per_photo': int, 'project_id': str}
    for field, expected_type in required_fields.items():
        if field not in request_json or not isinstance(request_json[field], expected_type):
            abort(400, description=f"Invalid or missing '{field}'.")

    return request_json
