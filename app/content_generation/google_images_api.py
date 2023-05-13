import requests
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(filename='app.log'),
        logging.StreamHandler()
    ]
)

class GoogleImagesAPI:
    def __init__(self, image_file_path):
        self.IMAGE_FILE_PATH = image_file_path
        self.used_links = []
        self.num_links_per_query = {}
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def get_image_link(self, query, api_key, cx, link_needed):
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "q": query,
            "key": api_key,
            "cx": cx,
            "searchType": "image",
            "start": link_needed,  # 'start' parameter specifies the first result to return
            "num": 1  # 'num' parameter specifies the number of search results to return
        }

        response = requests.get(url, params=params)
        results = response.json()

        if "error" in results:
            logging.error(f"Error encountered: {results['error']['message']}")
            return None
        
        if "items" in results and len(results["items"]) > 0:
            return results["items"][0]['link']

        return None
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def download_image(self, url, output_path):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537"
        }
        try:
            response = requests.get(url, stream=True, headers=headers)
            response.raise_for_status()  # Raise an exception if the GET request was unsuccessful

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)

        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred: {err}")
            return False
        except Exception as err:
            print(f"An error occurred: {err}")
            return False
        
        return True
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def get_image_from_google(self, query, output_file_name):
        api_key = "AIzaSyDq--kNy4Vot0SGaSRtbJ-CKDAa2qhOlrc"
        cx = "815224a42049e43d7"
        # Store a dictionary representing the number of links found for each query
        if self.num_links_per_query.get(query) is not None:
            link_needed = self.num_links_per_query.get(query)
        else:
            link_needed = 1
            self.num_links_per_query[query] = 1

        while link_needed < 50:
            fetched_link = self.get_image_link(query, api_key, cx, link_needed)
            if fetched_link is None:
                logging.info(f"Could not find image link for query: {query}")
                return False
            if fetched_link in self.used_links:
                logging.info(f"Found image link for query: {query}, but it was already used. Trying again.")
                link_needed += 1
                continue
            
            logging.info(f"Found image link for query: {query}. Trying download.")
            if self.download_image(fetched_link, self.IMAGE_FILE_PATH + output_file_name):
                logging.info(f"Downloaded image {fetched_link}")
                self.used_links.append(fetched_link)
                return True
            else:
                logging.info(f"Could not download image {fetched_link}. Trying again.")
                self.used_links.append(fetched_link)
                link_needed += 1
        
        self.num_links_per_query[query] = link_needed
                    
        return False
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def tear_down(self):
        self.used_links = []
        self.num_links_per_query = {}
# Tests ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# api = GoogleImagesAPI("../../media_storage/images")

# api.get_image_from_google("majestic dragon", 1)

