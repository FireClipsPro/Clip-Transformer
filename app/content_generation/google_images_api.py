import requests

class GoogleImagesAPI:
    def __init__(self, image_file_path):
        self.IMAGE_FILE_PATH = image_file_path

    def search_images(self, query, api_key, cx, num_results=10):
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "q": query,
            "key": api_key,
            "cx": cx,
            "searchType": "image",
            "num": num_results
        }

        response = requests.get(url, params=params)
        results = response.json()

        return results


    def download_image(self, url, output_path):
        response = requests.get(url)

        with open(output_path, "wb") as f:
            f.write(response.content)


    def get_image_from_google(self, query, num_results):
        api_key = "AIzaSyDq--kNy4Vot0SGaSRtbJ-CKDAa2qhOlrc"  # Replace with your API key
        cx = "815224a42049e43d7"  # Replace with your CSE ID

        results = self.search_images(query, api_key, cx, num_results)

        if "items" in results:
            for i, item in enumerate(results["items"]):
                url = item["link"]
                output_path = f"{self.IMAGE_FILE_PATH}{query.replace(' ', '_')}_{i}.jpg"
                self.download_image(url, output_path)
                print(f"Downloaded image {i + 1}: {url}")
            return True
        else:
            print("No results found.")
            return False

# Tests ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# api = GoogleImagesAPI("../media_storage/images")

# api.get_image_from_google("majestic dragon")