import openai
import os
from math import ceil
import logging
import re
import json

class TranscriptAnalyzer:
    def __init__(self,
             AI_PARSED_INFORMATION_FILE_PATH,
             CATEGORY_LIST):
        self.TRANSCRIPTION_INFO_FILE_PATH = AI_PARSED_INFORMATION_FILE_PATH
        self.CATEGORY_LIST_STRING = ""
        # get the keys from the dictionary category list
        CATEGORY_LIST.keys()
        for key in CATEGORY_LIST.keys():
            self.CATEGORY_LIST_STRING += key + ", "
            
    def get_info(self, clipped_video, transcription):
        # if the file already exists, then we don't need to query the AI
        if os.path.exists(self.TRANSCRIPTION_INFO_FILE_PATH + clipped_video['file_name'][:-4] + ".json"):
            with open(self.TRANSCRIPTION_INFO_FILE_PATH + clipped_video['file_name'][:-4] + ".json", "r") as f:
                transcription_info = json.load(f)
            clipped_video['transcription_info'] = transcription_info
            return clipped_video
        
        transcription_text = ""
        for text_segment in transcription['segments']:
            transcription_text += text_segment['text']
            
        transcription_info = self.query_gpt_for_json(transcription_text)
        
        # add transcription_info dictionary to clipped_video dictionary
        clipped_video['transcription_info'] = transcription_info
        
        # Save the transcription info to a file
        with open(self.TRANSCRIPTION_INFO_FILE_PATH + clipped_video['file_name'][:-4] + ".json", "w") as f:
            json.dump(transcription_info, f)
        
        return clipped_video
        
    def query_gpt_for_json(self, transcription_text):
        logging.info(f"Parsing sentence subject: {transcription_text}")

        openai.api_key = os.getenv("OPENAI_API_KEY")

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"""You will be given a transcript of a video.
                    Please return in json format, the following four things:
                    1. 'description': a 1 sentence description of the transcript 
                    2. 'hashtags': a list of tiktok hashtags to make the video go viral 
                    3. 'title': a title for the video that will grab peoples interest and make them want to watch it
                    4. 'category': for this transcript. Your options are: {self.CATEGORY_LIST_STRING}."""
                },
                {
                    "role": "user",
                    "content": f"""Here is the text: {transcription_text}. Reply with only the json and nothing else."""
                },
            ]
        )
        logging.info(f"Response: {response['choices'][0]['message']['content']}")
 
        json_sring = response['choices'][0]['message']['content']
        
        video_info_dictionary = self.parse_json_string(json_sring)
        
        logging.info(f"Generated dictionary: {str(video_info_dictionary)}")

        return video_info_dictionary
    
    def parse_json_string(self, json_string):
        try:
            json_dict = json.loads(json_string)
            json_dict = self.validate_dict(json_dict)
            return json_dict
        except ValueError as e:
            print(f"Error parsing JSON string: {e}")
            return None
        
    def validate_dict(self, json_dict):
        required_fields = ["description", "hashtags", "title", "category"]
        
        for field in required_fields:
            if field not in json_dict:
                json_dict[field] = ""
        
        if not isinstance(json_dict["hashtags"], list):
            json_dict["hashtags"] = ["", ""]
        
        return json_dict
    
# Tests ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# root = "../"

# ANGRY_MUSIC_FILE_PATH = f'{root}media_storage/songs/angry/'
# CUTE_MUSIC_FILE_PATH = f'{root}media_storage/songs/cute/'
# FUNNY_MUSIC_FILE_PATH = f'{root}media_storage/songs/funny/'
# MOTIVATIONAL_MUSIC_FILE_PATH = f'{root}media_storage/songs/motivational/'
# INTRIGUING_MUSIC_FILE_PATH = f'{root}media_storage/songs/fascinating/'
# CONSPIRACY_MUSIC_FILE_PATH = f'{root}media_storage/songs/conspiracy/'

# MUSIC_CATEGORY_PATH_DICT = {
#     'funny': FUNNY_MUSIC_FILE_PATH,
#     'cute': CUTE_MUSIC_FILE_PATH,
#     'motivational': MOTIVATIONAL_MUSIC_FILE_PATH,
#     'fascinating': INTRIGUING_MUSIC_FILE_PATH,
#     'angry': ANGRY_MUSIC_FILE_PATH,
#     'conspiracy': CONSPIRACY_MUSIC_FILE_PATH
# }

# analyzer = TranscriptAnalyzer("../media_storage/video_info/", MUSIC_CATEGORY_PATH_DICT)

# transcription= [{"text": " go out alone into the wild style.", "start": 0.3622360248447205, "end": 2.2337888198757763}, 
#     {"text": " You know, I'd have a hammock, a headlamp,", "start": 3.24, "end": 5.134461538461538}, 
#     {"text": " three days worth of food, some fish hooks, a machete.", "start": 5.900263157894737, "end": 8.155},
#     {"text": " That's it.", "start": 8.92, "end": 9.205714285714286}, 
#     {"text": " And so like one of the stories that happened early on", "start": 9.92, "end": 13.239526627218936}, 
#     {"text": " was I was out there and it was raining and I was lost.", "start": 13.32, "end": 15.558655462184875}, 
#     {"text": " And this is how we test your jungle knowledge.", "start": 15.780324324324326, "end": 19.339459459459462}, 
#     {"text": " Can you survive out there?", "start": 19.460377358490568, "end": 20.458867924528302}, 
#     {"text": " Do you know how to find food?", "start": 20.540384615384614, "end": 21.49846153846154}, 
#     {"text": " Have you listened to the things that we taught you?", "start": 21.580000000000002, "end": 23.353968253968254},
#     {"text": " And there was one night that I was in a hammock", "start": 24.36127659574468, "end": 26.894680851063832}, 
#     {"text": " and a jaguar came up", "start": 27.960674157303373, "end": 29.53820224719101}, 
#     {"text": " And I was asleep when it happened", "start": 29.7, "end": 31.019402985074624},
#     {"text": " and she came up right next to my head", "start": 31.06, "end": 32.498441558441556},
#     {"text": " and I could hear her smell.", "start": 32.92218149038461, "end": 35.19861538461538}]

# print(str(analyzer.get_info({'file_name': "test.mp4"}, transcription)))