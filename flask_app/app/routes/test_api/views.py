import logging

from flask import abort, jsonify, request

# from app.content_generation import  
from . import test_api_bp  # Import the Blueprint

logging.basicConfig(level=logging.INFO)

url_expiry_time = 3600*5 #(5 hours)

@test_api_bp.route('/test', methods=['GET'])
def test():
    '''
    {
        "input": "anything"
    }
    '''
    logging.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Doing my thing~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    user_input = request.args.get('input')
    
    if not user_input:
        abort(400, description="Missing video ID parameter")
    
    return jsonify({'input': user_input}), 200