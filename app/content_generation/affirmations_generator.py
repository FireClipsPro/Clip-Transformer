import logging
import os
import json

logging.basicConfig(level=logging.INFO)

class AffirmationsGenerator:
    def __init__(self, openai_api, affirmations_folder):
        self.openai_api = openai_api
        self.affirmations_folder = affirmations_folder
    
    def save_affirmations(self, filename, affirmation_list):
        """
        Save a list of affirmations to a JSON file
        """
        # Check if file exists
        if os.path.exists(os.path.join(self.affirmations_folder, filename)):
            return filename

        with open(os.path.join(self.affirmations_folder, filename), 'w') as f:
            json.dump(affirmation_list, f)

    def load_affirmations(self, filename):
        """
        Load a list of affirmations from a JSON file
        """
        with open(os.path.join(self.affirmations_folder, filename), 'r') as f:
            affirmation_list = json.load(f)
        
        return affirmation_list
    
    def generate(self, prompt, count, filename):
        filename = filename[:-4] + ".json"
        
        if os.path.exists(os.path.join(self.affirmations_folder, filename)):
            return self.load_affirmations(filename)
        
        correct_format_returned = False
        attempts = 0
        
        while not correct_format_returned and attempts <= 10:
            system_prompt = """(You are an affirmations genius. Please generate a list of 30 affirmations to address the following issues and aspirations.)
                            Example input: Aspiring to become richer. Struggling with excessive partying and alcohol consumption. Desire to study more frequently. Low self-esteem, especially when communicating with women.)
                            Please return the affirmations and only the affirmations.
                            Ensure that the affirmations are separated by a forward slash. If the affirmations are not separated by a forward slash the program will not run.
                            Example Output: I attract wealth and prosperity. / I have the power to control my financial future. / I find joy in sobriety. / Studying empowers me. / I am confident and capable in all interactions."""
            
            user_prompt = f"""Return a list of {count} forward slash seperated affirmations to address the following issues and aspirations:
                            {prompt}
                            """
            
            response = self.openai_api.query(str(system_prompt), str(user_prompt), 'gpt-3.5-turbo')
            
            affirmation_list = response.split("/")
            
            # if response contains numbers try again
            if any(char.isdigit() for char in response):
                correct_format_returned = False
                logging.info("Numbers detected in response. Trying again.")
            
            logging.info("length of affirmation list: " + str(len(affirmation_list)))
                         
            if len(affirmation_list) <= count:
                correct_format_returned = True
                logging.info("Correct format returned.")
            else:
                logging.info("Incorrect format returned. Trying again.")
            
            attempts += 1
        
        if not correct_format_returned:
            raise Exception("Affirmations not returned in correct format for prompt:\n" + prompt)
        
        
        affirmation_list = self.add_hiphens_to_list(affirmation_list)
        
        self.save_affirmations(filename, affirmation_list)
        return affirmation_list
    
    def add_hiphens_to_list(self, affirmations):
        for affirmation in affirmations :
            # always ad a -- after "I am"
            if len(affirmation.split(" ")) == 3:
                affirmation = affirmation.replace("I am ", "I am -- ")
                affirmation = affirmation.replace("I have ", "I have -- ")
                affirmation = affirmation.replace("I will ", "I will -- ")
            
            # if affirmation.contains(" and "):
            #     affirmation = affirmation.replace(" and ", " -- and ")
        
        return affirmations
    
