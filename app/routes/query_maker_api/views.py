from flask import request, jsonify, abort
from typing import Dict, Any
from app.services import S3
from app.text_analyzer import OpenaiApi
from app.configuration import directories, buckets
from app.text_analyzer import AWSTranscriptAnalyzer, AWSImageQueryCreator
import logging
import boto3
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
        'seconds_per_photo': 5,
        'project_id': '1234',
    }
    Returns: 
    {   
        'queries': [{'query': query, 
                     'start': time_chunk_start,
                     'end': time_chunk_end,
                     'sentence': sentence,
                     'description': description['description'],
                     'description_start': description['start'],
                     'description_end': description['end'],
                     'image_id': None}, ...]
    }
    """
    request_data = validate_request_data(request.json)
    project_id = request_data['project_id']
    seconds_per_photo = request_data['seconds_per_photo']
    
    openai_api = OpenaiApi()
    
    s3 = S3(boto3.client('s3'))
    
    transcription = s3.get_dict_from_video_data(project_id=project_id,
                                                file_name='transcription.json',
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
    if not s3.write_dict_to_video_data(project_id, query_dict, "queries.json", buckets.project_data):
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

    required_fields = {'seconds_per_photo': int, 'project_id': str}
    for field, expected_type in required_fields.items():
        if field not in request_json or not isinstance(request_json[field], expected_type):
            abort(400, description=f"Invalid or missing '{field}'.")

    return request_json
