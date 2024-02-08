import os
import openai
import json
import logging
import json
import os
from io import BytesIO
import openai
from datetime import datetime
import base64 
import requests 
from PIL import Image
from base64 import b64decode
from pathlib import Path


logging.basicConfig(level=logging.INFO)



class DALL_E():
    def __init__(self,
                 output_folder,
                 dalle_prompt_folder):
        self.output_folder = output_folder
        self.GENERATED_PROMPT_FOLDER_PATH = dalle_prompt_folder
        self.dall_e_image_width = 1024
        self.dall_e_image_height = 1024

    # This method generates images where an image was not found through google
    def create_missing_images(self,
                        time_stamped_images,
                        prompts_log_file_name="prompts_log.json"):
        dall_e_prompts = []
        
        for image in time_stamped_images:

            if '_Nothing_Found_' in image['image']:
                # remove the '_Nothing_Found_' from the google_query string
                google_query = image['image'].replace('_Nothing_Found_', '')

                prompt = self.generate_prompt(google_query)
                
                prompt = self.remove_naughty_words(prompt)
                
                dall_e_prompts.append(prompt)

                response = openai.Image.create(
                    prompt=prompt,
                    n=1,
                    size="1024x1024",
                    response_format="b64_json",
                )

                json_file = self.output_folder + f"{prompt[:5]}-{response['created']}.json"

                with open(json_file, mode="w", encoding="utf-8") as file:
                    json.dump(response, file)

                image_file = f"{google_query.replace(' ', '_')}.png"
                self.save_image(json_file, image_file)
                
                # delete the json file
                os.remove(json_file)
                
                image['image'] = image_file
                
                image['width'] = 1024
                image['height'] = 1024
                
        # store the prompts in a json file
        with open(self.GENERATED_PROMPT_FOLDER_PATH + prompts_log_file_name,
                  mode="w",
                  encoding="utf-8") as file:
            json.dump(dall_e_prompts, file)
        
        
        return time_stamped_images
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def generate_and_save_image(self,
                                prompt,
                                file_name):
        openai.api_key_path = '../../OPENAI_API_KEY.txt'
        
        image_params = {
            "model": "dall-e-3",  
            "n": 1,               
            "size": f"{self.dall_e_image_width}x{self.dall_e_image_height}",  
            "prompt": prompt,
            "user": "myName",
            }
        
        image_params.update({"response_format": "b64_json"}) 

        response = openai.Image.create(**image_params)
        
        json_filename = self.output_folder + f"{prompt[:5]}-{response['created']}.json"

        with open(json_filename, mode="w", encoding="utf-8") as file:
            json.dump(response, file)

        self.save_image(json_filename, file_name)
        
        os.remove(json_filename)
            
        return True, self.dall_e_image_width, self.dall_e_image_height

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def remove_naughty_words(self, 
                             prompt: str):
        for word in prompt.split(" "):
            if word == "stalking":
                prompt = prompt.replace(word, "chasing")
                        
            response = openai.Moderation.create(
                        input = word
                    )
            output = response["results"][0]
                    
            for category in output["categories"].values():
                if category == True:
                            # true value indicates word dall e does not like
                    logging.info(f"Removing word: {word}")
                    prompt.replace(word, "")
                    break
        return prompt
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def save_image(self, json_file, file_name):
        DATA_DIR = Path.cwd()
        JSON_FILE = DATA_DIR / json_file

        image_path = Path(self.output_folder)
        image_path.mkdir(parents=True, exist_ok=True)

        with open(JSON_FILE, mode="r", encoding="utf-8") as file:
            response = json.load(file)

        for index, image_dict in enumerate(response["data"]):
            image_data = b64decode(image_dict["b64_json"])
            with open(self.output_folder + file_name, mode="wb") as png:
                png.write(image_data)
                
            logging.info(f"Saved image to: {file_name}")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~            
    def get_api_key(self):
        file_path = "../../OPENAI_API_KEY.txt"  # path to the file with the API key
        try:
            with open(file_path, 'r') as file:
                api_key = file.readline().strip()  # Read the first line and remove any leading/trailing white spaces
            return api_key
        except FileNotFoundError:
            print(f"API key file not found at {file_path}")
            return None
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def generate_prompt(self, text):
        # openai.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.get_api_key()
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """You are a dall E image prompt generator.
                 Your job is to come up with an dall E prompt that would generate an image based on the given text, with the goal of making an interesting image for people to look at.
                 Do not make a prompt that would generate an image with text.
                 Do include any inappropriate words.
                 Do not have multiple options for the prompt.
                 Do not return anything except for the prompt you have made."""},
                {"role": "user", "content": f"""Here is your text: {text}"""},
            ]
        )
        prompt = response['choices'][0]['message']['content'].replace('"', '')

        logging.info(f"Generated Prompt: {prompt}")
        return prompt
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#testing
# dall_e = DALL_E('./', './')

# time_stamp_images = [
#     {
#         'start_time': '00:00:00',
#         'end_time': '00:00:10',
#         'image': '_Nothing_Found_Challenging tasks for skill development with high succes probability'
#     }]

# dall_e.generate_and_save_image("All of my gangstas hanging out knitting", "knitting_ganstas.png")

# dall_e.generate_images(time_stamp_images)
# dall_e.generate_prompt('Challenging tasks for skill development with high succes probability')

# convert.py

# dall_e = DALL_E('../media_storage/images/', '../media_storage/generated_prompts/')

# PROMPT = "Jaguar following its prey in the jungle."

