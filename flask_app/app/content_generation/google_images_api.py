import logging
import os

import requests
from PIL import Image
from requests.exceptions import Timeout

logging.basicConfig(level=logging.INFO)

class GoogleImagesAPI:
    def __init__(self, 
                 image_evaluator = None,
                 image_file_path = None):
        self.api_key = "AIzaSyDq--kNy4Vot0SGaSRtbJ-CKDAa2qhOlrc"
        self.cx = "815224a42049e43d7"
        self.IMAGE_FILE_PATH = image_file_path
        self.used_links = []
        self.num_links_per_query = {}
        self.IMAGE_CLASSIFIER_THRESHOLD = 6.5
        self.image_evaluator = image_evaluator
        self.wants_royalty_free = False
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def get_image_link_from_query(self, query, link_start_loc=1):
        url = "https://www.googleapis.com/customsearch/v1"
        
        params = {
            "q": query,
            "key": self.api_key,
            "cx": self.cx,
            "searchType": "image",
            "start": link_start_loc,  # 'start' parameter specifies the first result to return
            "num": 1  # 'num' parameter specifies the number of search results to return
        }
        
        if self.wants_royalty_free:
            license_types = "cc_publicdomain,cc_attribute,cc_sharealike"
            params['rights'] = license_types

        response = requests.get(url, params=params)
        results = response.json()

        if "error" in results:
            logging.error(f"Error encountered: {results['error']['message']}")
            return None
        
        if "items" in results and len(results["items"]) > 0:
            return results["items"][0]['link']
        
        return None
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    
    def get_image_link(self, query, link_needed=1):
        while True:
            fetched_link = self.get_image_link_from_query(query, link_start_loc=link_needed)
            # Filter out youtube thumbnails, amazon images, alamy images, and quote images
            if "youtube.com" in fetched_link or "amazon.com" in fetched_link or "alamy.com" in fetched_link or "quote" in fetched_link:
                    logging.info(f"Found image link for query: {query}, but it was a youtube link. Trying again.")
                    link_needed += 1
            else:
                return fetched_link
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def download_image(self, 
                       url,
                       output_path):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537"
        }
        try:
            logging.info(f"Downloading image from {url}")
            response = requests.get(url, stream=True, headers=headers, timeout=5)
            logging.info(f"Response status code: {response.status_code}")
            response.raise_for_status()  # Raise an exception if the GET request was unsuccessful

            with open(output_path, "wb") as f:
                logging.info(f"Saving image to {output_path}")
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)

            # Check if the image is openable
            try:
                logging.info(f"Verifying image {output_path}")
                img = Image.open(output_path)
                img.verify()  # verify that it is, in fact an image
            except (IOError, SyntaxError) as e:
                logging.info('Bad file:', output_path)  # logging.info out the names of corrupt files
                os.remove(output_path)
                return False

        except Timeout:
            logging.error(f"Timeout occurred while attempting to download image from {url}")
            return False
        except requests.exceptions.HTTPError as err:
            logging.error(f"HTTP error occurred: {err}")
            return False
        except Exception as err:
            logging.error(f"An error occurred: {err}")
            return False
        
        return True
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def get_image_from_google(self, 
                              query,
                              output_file_name):
        
        # Store a dictionary representing the number of links found for each query
        if self.num_links_per_query.get(query) is not None:
            link_needed = self.num_links_per_query.get(query)
        else:
            link_needed = 1
            self.num_links_per_query[query] = 1

        while link_needed < 50:
            fetched_link = self.get_image_link(query, link_needed)
            if fetched_link is None:
                logging.info(f"Could not find image link for query: {query}")
                return False
            if fetched_link in self.used_links:
                logging.info(f"Found image link for query: {query}, but it was already used. Trying again.")
                link_needed += 1
                continue
            if "youtube.com" in fetched_link or "amazon.com" in fetched_link or "alamy.com" in fetched_link or "quote" in fetched_link:
                logging.info(f"Found image link for query: {query}, but it was a youtube link. Trying again.")
                link_needed += 1
                continue
            
            logging.info(f"Found image link for query: {query}. Trying download.")
            download_success = self.download_image(fetched_link, self.IMAGE_FILE_PATH + output_file_name)
            
            if download_success:
                logging.info(f"Downloaded image {fetched_link}")
                self.used_links.append(fetched_link)

                is_classified_and_colorful, link_needed = self.image_is_colorful(fetched_link,
                                                                                    output_file_name,
                                                                                    link_needed)
                
                if is_classified_and_colorful:
                    return True
                
            else:
                logging.info(f"Could not download image {fetched_link}. Trying again.")
                self.used_links.append(fetched_link)
                link_needed += 1
        
        self.num_links_per_query[query] = link_needed
                    
        return False
    
    def image_is_colorful(self, fetched_link, output_file_name, link_needed):
        if not self.image_evaluator.is_colorful_enough(output_file_name):
            logging.info(f"Image {fetched_link} is not colorful enough. Trying again.")
            # delete image
            os.remove(self.IMAGE_FILE_PATH + output_file_name)
            self.used_links.append(fetched_link)
            link_needed += 1
            return False, link_needed
        else:
            logging.info(f"Image {fetched_link} was colorful enough.")
        
        return True, link_needed
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def tear_down(self):
        self.used_links = []
        self.num_links_per_query = {}
# Tests ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# api = GoogleImagesAPI("../../media_storage/images")

# api.get_image_from_google("majestic dragon", 1)

