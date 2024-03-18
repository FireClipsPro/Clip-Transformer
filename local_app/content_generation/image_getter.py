import os
import logging
import json
import subprocess
from .image_evaluator import ImageEvaluator
from .google_images_api import GoogleImagesAPI
from .dall_e import DALL_E

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(filename='app.log'),
        logging.StreamHandler()
    ]
)

class ImageGetter:
    def __init__(self,
                 image_file_path,
                 image_scraper: GoogleImagesAPI,
                 image_evaluator: ImageEvaluator,
                 image_generator: DALL_E):
        self.image_file_path = image_file_path
        self.image_scraper = image_scraper
        self.image_evaluator = image_evaluator
        self.image_generator = image_generator
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def get_images(self, query_list, wants_to_use_dall_e=False):
        logging.info('Starting get_images method')

        time_stamped_images = []
        query_file_list = self.clean_query_list(query_list)
        logging.info(f'Cleaned query list: {query_file_list}')
        
        for query in query_file_list:
            if os.path.exists(self.image_file_path + query['image_file_name']):
                logging.info(f"Download unecessary: Image file already exists: {self.image_file_path + query['image_file_name']}.")
                
                image_width, image_height = self.image_evaluator.get_dimensions(self.image_file_path + query['image_file_name'])
                time_stamped_images.append({'start_time': query['start'],
                                            'end_time': query['end'],
                                            'image': query['image_file_name'],
                                            'width': image_width,
                                            'height': image_height})
                continue
            if wants_to_use_dall_e:
                logging.info(f"Query: {query['query']}, using DALL-E")
                json_image_data = self.image_generator.generate_image_json(prompt=query['query'])
                width = 1024
                height = 1024
                image_was_found = self.image_generator.save_image_to_folder(json_data=json_image_data,
                                                                            file_name=query['image_file_name'],
                                                                            output_folder=self.image_file_path)
            else:
                logging.info(f"Download required for query: {query['query']}, using image_scraper")
                width, height = self.image_evaluator.get_dimensions(self.image_file_path + query['image_file_name'])
                image_was_found = self.image_scraper.get_image_from_google(query=query['query'],
                                                                       output_file_name=query['image_file_name'])
            
            if image_was_found:
                time_stamped_images.append({'image': query['image_file_name'],
                                            'start_time': query['start'],
                                            'end_time': query['end'],
                                            'width': width,
                                            'height': height})
            else:
                logging.info(f"No image found for query: {query['query']}")
                time_stamped_images.append({'start_time': query['start'],
                                            'end_time': query['end'],
                                            'image': '_Nothing_Found_' + query['query']})
        self.image_scraper.tear_down()
        
        logging.info('Ending get_images method')
        return time_stamped_images

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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