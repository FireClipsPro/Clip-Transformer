import logging
import uuid

import boto3
from flask import abort, jsonify, request

import app.configuration.buckets as buckets
from app.configuration import directories
from app.content_generation import DALL_E, GoogleImagesAPI
from app.models.image_model import ImageModel
from app.services.s3 import S3

# from app.content_generation import  
from . import image_generator_api_bp  # Import the Blueprint

logging.basicConfig(level=logging.INFO)

url_expiry_time = 3600*5 #(5 hours)

# the route for this is http://localhost:5000/media_adder_api/add_media
@image_generator_api_bp.route('/create_images', methods=['POST'])
def create_images():
    '''
    This function takes in the following json payload:
    {   
        "user_id": "panda@example.com",
        "project_id": "42069",
        "queries": [{   "query": "cherry blossom tree",
                        "is_dall_e": "true",
                        "start": 0,
                        "end": 10
                    }, ...]
    }
    stores the images in the image bucket and returns a list of the image ids
    '''
    payload = request.get_json()
    is_valid, message = validate_payload(payload)
    if not is_valid:
        return jsonify({"error": message}), 400
    
    user_id = payload['user_id']
    project_id = payload['project_id']
    query_list = payload['queries']
    images = build_image_models(query_list)

    try:
        images = scrape_and_generate_images(project_id,
                                                images,
                                                DALL_E(api_key_path=directories.OPENAI_API_KEY_PATH,),
                                                S3(boto3.client('s3')),
                                                GoogleImagesAPI(),
                                                user_id)
    except Exception as e:
        # Log the exception and return a 500 error
        logging.exception("Failed to create video")
        abort(500, description=str(e))
    
    response = create_response(images)
    
    return jsonify(response), 200

def generate_and_scrape_image(query, 
                              dall_e,
                              s3,
                              image_scraper,
                              project_id,
                              user_id):
    if query.is_dall_e:
        image_json_data = dall_e.generate_image_json(prompt=query.query)

        bucket_path = user_id + "/" + project_id + "/" + buckets.images_folder
        s3.save_image_to_s3(json_image_data=image_json_data,
                            file_name=query.uid + ".png",
                            bucket_name=buckets.project_data,
                            prefix=bucket_path)

        query.url = s3.get_item_url(bucket_name=buckets.project_data,
                                    object_key=query.uid + ".png",
                                    expiry_time=url_expiry_time,
                                    prefix=bucket_path)
    else:
        query.url = image_scraper.get_image_link(query=query.query)
    return query

def scrape_and_generate_images(project_id,
                    queries,
                    dall_e,
                    s3,
                    image_scraper,
                    user_id):
    results = []
    for query in queries:
        results.append(generate_and_scrape_image(query,
                                                    dall_e,
                                                    s3,
                                                    image_scraper,
                                                    project_id,
                                                    user_id))

    return results

def build_image_models(query_list):
    image_models = []
    for query in query_list:
        # generate a unique id for the image
        uid = str(uuid.uuid4())
        image_models.append(ImageModel(uid=uid,
                                        query=query['query'],
                                        is_dall_e = query['is_dall_e'],
                                        url="",
                                        start=query['start'],
                                        end=query['end'],
                                        width=None,
                                        height=None))
        
    return image_models
        
def create_response(queries: [ImageModel]):
    image_ids = []
    for query in queries:
        image_ids.append({"id": query.uid, 
                          "url": query.url,
                          "start": query.start,
                          "end": query.end,
                          "query": query.query,
                          "is_dall_e": query.is_dall_e})
    return image_ids
        
def validate_payload(payload):
    """
    Validates the input JSON payload to ensure it meets the API's requirements.
    """
    if not payload or "queries" not in payload:
        return False, "Missing 'queries' in payload."
    
    if not isinstance(payload['queries'], list):
        return False, "'queries' must be a list."
    
    for required_field in ["user_id", "project_id"]:
        if required_field not in payload:
            return False, f"Missing '{required_field}' in payload."
    
    for query in payload['queries']:
        required_fields = ["query", "is_dall_e", "start", "end"]
        for field in required_fields:
            if field not in query:
                return False, f"Missing '{field}' in query."
            if field == "is_dall_e" and not isinstance(query[field], bool):
                return False, f"'{field}' must be a boolean."
            if field in ["start", "end"] and not (isinstance(query[field], float) or isinstance(query[field], int)):
                return False, f"'{field}' must be an float."
    return True, "Valid payload."