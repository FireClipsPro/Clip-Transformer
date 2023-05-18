import os
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(filename='app.log'),
        logging.StreamHandler()
    ]
)

class ImageGetter:
    def __init__(self, image_file_path, image_scraper):
        self.IMAGE_FILE_PATH = image_file_path
        self.image_scraper = image_scraper

    def get_images(self, query_list):
        logging.info('Starting get_images method')

        time_stamped_images = []
        query_file_list = self.clean_query_list(query_list)
        logging.info(f'Cleaned query list: {query_file_list}')
        
        for query in query_file_list:
            if os.path.exists(self.IMAGE_FILE_PATH + query['image_file_name']):
                logging.info(f"Download unecessary: Image file already exists: {self.IMAGE_FILE_PATH + query['image_file_name']}.")
                time_stamped_images.append({'start_time': query['start'],
                                            'end_time': query['end'],
                                            'image': query['image_file_name']})
                continue
            
            logging.info(f"Download required for query: {query['query']}, using image_scraper")
            image_found = self.image_scraper.get_image_from_google(query['query'],
                                                                   query['image_file_name'])
            
            if not image_found:
                logging.info(f"No image found for query: {query['query']}")
                time_stamped_images.append({'start_time': query['start'],
                                            'end_time': query['end'],
                                            'image': '_Nothing_Found_' + query['query']})
            else:
                logging.info(f"Image found for query: {query['query']}")
                time_stamped_images.append({'start_time': query['start'],
                                            'end_time': query['end'],
                                            'image': query['image_file_name']})
        
        self.image_scraper.tear_down()
        
        logging.info('Ending get_images method')
        return time_stamped_images


# this is super hacky and dependent on the implementation of the google images api
# but it works for now
    def clean_query_list(self, query_list):
        query_count_dict = {}
        result_list = []

        # make all queries lower case
        for query_dict in query_list:
            query_dict['query'] = query_dict['query'].lower()
        
        for query_dict in query_list:
            query = query_dict['query']
            if query in query_count_dict:
                query_count_dict[query] += 1
            else:
                query_count_dict[query] = 1

        for query_dict in query_list:
            query = query_dict['query']
            start = query_dict['start']
            end = query_dict['end']
            image_file_name = f"{query.replace(' ', '_')}_{query_count_dict[query] - 1}.jpg"
            query_count = query_count_dict[query]
            query_count_dict[query] -= 1

            result_list.append({
                'query': query,
                'start': start,
                'end': end,
                'image_file_name': image_file_name,
                'query_count': query_count,
                'is_found': False
            })

        return result_list


#tests ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# from image_classifier import ImageClassifier
# from google_images_api import GoogleImagesAPI
# from image_evaluator import ImageEvaluator
# root = "../../"
# IMAGE_FILE_PATH = f"{root}media_storage/images/"

# # get the queries from the json file
# with open(f"{root}media_storage/queries/JordanClip_(0, 0)_(0, 54)_centered.json", 'r') as f:
#     query_list = json.load(f)
    
# image_classifier = ImageClassifier(IMAGE_FILE_PATH)
# image_evaluator = ImageEvaluator(IMAGE_FILE_PATH)

# image_scraper = GoogleImagesAPI(IMAGE_FILE_PATH,
#                                 image_classifier,
#                                 image_evaluator)
# image_getter = ImageGetter(IMAGE_FILE_PATH, image_scraper)
# time_stamped_images = image_getter.get_images(query_list)
