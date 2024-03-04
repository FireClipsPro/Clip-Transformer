import openai
import os
import logging
import time
from openai import OpenAI

logging.basicConfig(level=logging.ERROR)

class OpenaiApi:
    def __init__(self):
        logging.info("Created OpenaiApi object")
    
    def get_api_key(self):
        file_path = "../OPENAI_API_KEY.txt"  # path to the file with the API key
        try:
            with open(file_path, 'r') as file:
                api_key = file.readline().strip()  # Read the first line and remove any leading/trailing white spaces
            return api_key
        except FileNotFoundError:
            print(f"API key file not found at {file_path}")
            return None
    
    def query(self, system_prompt, user_prompt, model):
        # openai.api_key = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=self.get_api_key())

        
        
        num_retries = 50
        
        while num_retries > 0:
            try:
                num_retries -= 1

                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                logging.info(f"OpenAI response: {response}")
                return response.choices[0].message.content
                
            except openai.APIError as e:
                logging.info(f"APIError occurred: {e}. Retrying in 5 seconds...")
                time.sleep(5)
            except openai.APITimeoutError as e:
                logging.info(f"Timeout occurred: {e}. Retrying in 5 seconds...")
                time.sleep(5)
            except openai.RateLimitError as e:
                logging.info(f"RateLimitError occurred: {e}. Retrying in 10 seconds...")
                time.sleep(10)
            except openai.APIConnectionError as e:
                logging.error(f"APIConnectionError occurred: {e}. Please check your network settings.")
            except openai.BadRequestError as e:
                logging.error(f"BadRequestError occurred: {e}. Please check your request parameters.")
            except openai.AuthenticationError as e:
                logging.error(f"AuthenticationError occurred: {e}. Please check your API key or token.")
            except openai.NotFoundError as e:
                logging.error(f"NotFoundError occurred: {e}. The requested resource could not be found.")
            except openai.PermissionDeniedError as e:
                logging.error(f"PermissionDeniedError occurred: {e}. Access denied to the requested resource.")
            except openai.InternalServerError as e:
                logging.error(f"InternalServerError occurred: {e}. A server error occurred. Please try again later.")
