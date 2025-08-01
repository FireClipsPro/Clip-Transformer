import openai
import logging
from base64 import b64decode
from pathlib import Path

logging.basicConfig(level=logging.INFO)

class DALL_E():
    def __init__(self, api_key_path="../../../OPENAI_API_KEY.txt"):
        self.dall_e_image_width = 1024
        self.dall_e_image_height = 1024
        self.key_path = api_key_path
        openai.api_key = self.get_api_key()

    def generate_image_json(self, prompt):
        image_params = {
            "model": "dall-e-3",  
            "n": 1,
            "size": f"{self.dall_e_image_width}x{self.dall_e_image_height}",  
            "prompt": prompt,
            "user": "myName",
            }
        
        image_params.update({"response_format": "b64_json"}) 

        response = openai.images.generate(**image_params)
            
        return response

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
    def save_image_to_folder(self, 
                             json_data,
                             file_name,
                             output_folder):

        image_path = Path(output_folder)
        image_path.mkdir(parents=True, exist_ok=True)

        response = json_data

        for index, image_dict in enumerate(response.data):
            image_data = b64decode(image_dict.b64_json)
            with open(output_folder + file_name, mode="wb") as png:
                png.write(image_data)
                
            logging.info(f"Saved image to: {file_name}")
        return True
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~            
    def get_api_key(self):
        try:
            with open(self.key_path, 'r') as file:
                api_key = file.readline().strip()  # Read the first line and remove any leading/trailing white spaces
            return api_key
        except FileNotFoundError:
            print(f"API key file not found at {self.key_path}")
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

# dall_e = DALL_E()

# json_data = dall_e.generate_image_json("A cute cat playing with a ball of yarn.")

# dall_e.save_image_to_folder(json_data, "cat_playing_with_yarn.png", "./")
