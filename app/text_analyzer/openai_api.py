import openai
import os
import logging
import time

logging.basicConfig(level=logging.ERROR)

class OpenaiApi:
    def __init__(self):
        logging.info("Created OpenaiApi object")
    
    def get_api_key(self):
        file_path = "../../OPENAI_API_KEY.txt"  # path to the file with the API key
        try:
            with open(file_path, 'r') as file:
                api_key = file.readline().strip()  # Read the first line and remove any leading/trailing white spaces
            return api_key
        except FileNotFoundError:
            print(f"API key file not found at {file_path}")
            return None
    
    def query(self, system_prompt, user_prompt, model):
        openai.api_key = self.get_api_key()
        
        num_retries = 50
        
        while num_retries > 0:
            try:
                num_retries -= 1
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                logging.info(f"OpenAI response: {response}")
                return response['choices'][0]['message']['content']
                
            except openai.error.APIError as e:
                logging.info(f"APIError occurred: {e}. Retrying in 5 seconds...")
                time.sleep(5)

            except openai.error.Timeout as e:
                logging.info(f"Timeout occurred: {e}. Retrying in 5 seconds...")
                time.sleep(5)
            
            except openai.error.RateLimitError as e:
                logging.info(f"RateLimitError occurred: {e}. Retrying in 10 seconds...")
                time.sleep(10)

            except openai.error.APIConnectionError as e:
                logging.error(f"APIConnectionError occurred: {e}. Please check your network settings.")
                break
                
            except openai.error.InvalidRequestError as e:
                logging.error(f"InvalidRequestError occurred: {e}. Please check your request parameters.")
                break
                
            # except openai.error.AuthenticationError as e:
            #     logging.error(f"AuthenticationError occurred: {e}. Please check your API key or token.")
            #     break

            except openai.error.ServiceUnavailableError as e:
                logging.info(f"ServiceUnavailableError occurred: {e}. Retrying in 5 seconds...")
                time.sleep(5)
