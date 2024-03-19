from flask import abort
from flask import request
from app.services.s3 import S3
from flask import jsonify
import boto3
import app.configuration.buckets as buckets

# from app.content_generation import  
from . import account_setup_api_bp  # Import the Blueprint
import logging

logging.basicConfig(level=logging.INFO)

url_expiry_time = 3600*5 #(5 hours)

@account_setup_api_bp.route('/setup_account_db', methods=['POST'])
def setup_account_db():
    '''
    This function sets up the database for a new account.
    It creates S3 buckets for the account, and sets up the database.
    The data sent should be:
    {
        "account_id": "account_id"
    }
    '''
    # ensure the id field is in the request
    data = request.get_json()
    if not all(key in data for key in ['account_id']):
        abort(400, description="Missing data in request payload")
    s3 = S3(boto3.client('s3'))
    
    result = s3.create_folder(folder_name=data['account_id'],
                              bucket_name=buckets.bg_videos,
                              prefix=buckets.private_bg_prefix)
    
    if result:
        return jsonify({"message": "Account DB setup successfully"}), 200
    else:
        abort(500, description="Failed to setup account")