import os
import openai
import json
import logging
import json
from base64 import b64decode
from pathlib import Path


logging.basicConfig(level=logging.INFO)


class DALL_E():
    def __init__(self,
                 OUTPUT_FOLDER_PATH):
        self.OUTPUT_FOLDER_PATH = OUTPUT_FOLDER_PATH

    def generate_images(self, time_stamped_images):

        for image in time_stamped_images:

            if '_Nothing_Found_' in image['image']:
                # remove the '_Nothing_Found_' from the google_query string
                google_query = image['image'].replace('_Nothing_Found_', '')

                logging.info(f"Generating image for: {google_query}")
                PROMPT = self.generate_prompt(google_query)
                logging.info(f"Generated Prompt: {PROMPT}")

                response = openai.Image.create(
                    prompt=PROMPT,
                    n=1,
                    size="1024x1024",
                    response_format="b64_json",
                )

                file_name = self.OUTPUT_FOLDER_PATH + f"{PROMPT[:5]}-{response['created']}.json"

                with open(file_name, mode="w", encoding="utf-8") as file:
                    json.dump(response, file)

                self.save_image(file_name, google_query)
                
                # delete the json file
                os.remove(file_name)
                
                image['image'] = f"{google_query.replace(' ', '_')}.png"
                
                
        return time_stamped_images
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def save_image(self, json_file, google_query):
        DATA_DIR = Path.cwd()
        JSON_FILE = DATA_DIR / json_file

        image_path = Path(self.OUTPUT_FOLDER_PATH)
        image_path.mkdir(parents=True, exist_ok=True)

        with open(JSON_FILE, mode="r", encoding="utf-8") as file:
            response = json.load(file)

        for index, image_dict in enumerate(response["data"]):
            image_data = b64decode(image_dict["b64_json"])
            cleaned_query = google_query.replace(" ", "_")
            image_file = image_path / f"{cleaned_query}.png"
            with open(image_file, mode="wb") as png:
                png.write(image_data)
                
            logging.info(f"Saved image to: {image_file}")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def generate_prompt(self, text):
        openai.api_key = os.getenv("OPENAI_API_KEY")
         
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """You are a dalle image query generator.
                 Your job is to come up with an dall E prompt that would generate an image based on the given text, with the goal of making an interesting image for people to look at.
                 Do not make a prompt that would generate an image with text.
                 Do not have multiple options for the prompt.
                 Do not return anything except for the prompt you have made."""},
                {"role": "user", "content": f"""Here is your text: {text}"""},
            ]
        )
        prompt = response['choices'][0]['message']['content'].replace('"', '')
        # logging.info(f"Generated Prompt: + {prompt}")
        return prompt
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#testing
# dall_e = DALL_E('../media_storage/images/')

# time_stamp_images = [
#     {
#         'start_time': '00:00:00',
#         'end_time': '00:00:10',
#         'image': '_Nothing_Found_Challenging tasks for skill development with high succes probability'
#     }]

# dall_e.generate_images(time_stamp_images)
# dall_e.generate_prompt('Challenging tasks for skill development with high succes probability')

# convert.py



