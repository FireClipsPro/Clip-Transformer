from flask import abort
from flask import request
from flask import jsonify
import requests
import app.configuration.buckets as buckets

from . import transcriber_api_bp
import logging

logging.basicConfig(level=logging.INFO)

url_expiry_time = 3600*5

@transcriber_api_bp.route('/transcribe', methods=['POST'])
def transcribe():
    '''
    {
        "project_id": "string",
        "user_id": "string"
    }
    '''
    logging.info("Adding subtitles")
    data = request.get_json()

    # Validate payload
    if not all(key in data for key in ['project_id', 'user_id']):
        abort(400, description="Missing data in request payload")

    project_id = data['project_id']
    user_id = data['user_id']
    
    url = f"http://ec2-54-82-24-182.compute-1.amazonaws.com:8000/transcribe?bucket_id=project-data-69&project_id={project_id}&user_id={user_id}"

    # Make the POST request
    response = requests.post(url)

    # Check if the request was successful   
    if response.status_code != 200:
        abort(400, description="Transcription Request failed")
    
    # Return the response
    return jsonify({"message": "Transcription Request sent successfully"}), 200