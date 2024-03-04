import os
import logging
import json
from nltk.tokenize import word_tokenize
from .openai_api import OpenaiApi

class AWSTranscriptAnalyzer:
    def __init__(self,
                 music_category_list,
                 openai_api: OpenaiApi):
        self.CATEGORY_LIST_STRING = ""
        self.openai_api = openai_api
        # get the keys from the dictionary category list
        music_category_list.keys()
        for key in music_category_list.keys():
            self.CATEGORY_LIST_STRING += key + ", "
            
    def get_clip_info(self, 
                      clipped_video,
                      transcription,
                      music_category_options):
        transcription_text = ""
        for text_segment in transcription['word_segments']:
            transcription_text += text_segment['text']
            
        transcription_info = self.__query_gpt_for_json(transcription_text,
                                                        clipped_video,
                                                        music_category_options=music_category_options)
        
        # set the start and end times for the description
        transcription_info['descriptions'] = [{
            'description': transcription_info['description'],
            'start': transcription['word_segments'][0]['start'],
            'end': transcription['word_segments'][-1]['end']}]
        
        # add transcription_info dictionary to clipped_video dictionary
        clipped_video['transcription_info'] = transcription_info
        
        # Save the transcription info to a file
        with open(self.TRANSCRIPTION_INFO_FILE_PATH + clipped_video['file_name'][:-4] + ".json", "w") as f:
            json.dump(transcription_info, f)
        
        return clipped_video
    
    # returns a list of dictionaries
    # each dictionary contains the description and the start and end time of the segment
    def get_info_for_entire_pod(self, transcription):
        # split the transcription into 4096 token chunks
        chunks = self.split_transcript_into_chunks(transcription)
        
        video_info_list = []
        for chunk in chunks:
            logging.info(str(chunk))
            description = self.__query_gpt_for_segment_description(chunk['text'])
            video_info_list.append({'description': description,
                                    'start': chunk['start'],
                                    'end': chunk['end']})
        
        return video_info_list
    
    def split_transcript_into_chunks(self, transcript):
        chunks = []
        current_chunk = []
        current_token_count = 0
        start_time_of_current_chunk = None

        for text_segment in transcript['word_segments']:
            tokens = word_tokenize(text_segment['text'])
            for token in tokens:
                if start_time_of_current_chunk is None:
                    start_time_of_current_chunk = text_segment['start']

                # We cut it down to smaller token chunks because that is a good sized context window
                if current_token_count + len(token) > 800:
                    end_time_of_last_chunk = text_segment['start']  # The start time of the current segment is the end time of the last chunk
                    chunks.append({
                        'text': ' '.join(current_chunk),
                        'start': start_time_of_current_chunk,
                        'end': end_time_of_last_chunk
                    })

                    current_chunk = [token]
                    current_token_count = len(token)
                    start_time_of_current_chunk = text_segment['start']
                else:
                    current_chunk.append(token)
                    current_token_count += len(token)

        # Don't forget to add the last chunk if it's non-empty
        if current_chunk:
            chunks.append({
                'text': ' '.join(current_chunk),
                'start': start_time_of_current_chunk,
                'end': text_segment['end']
            })

        return chunks

    
    def __query_gpt_for_segment_description(self, transcription_text):
        logging.info("Querying openai for transcript info.")
        model="gpt-3.5-turbo"
        
        system_prompt = f"""You will be given a transcript of a section of a podcast.
                            Your task is to create a 1 sentence description of the transcript that is passed to you.
                            Return the one sentence description and nothing else."""
        user_prompt = "Here is the transcript section: " + transcription_text + "."
        
        response = self.openai_api.query(system_prompt=system_prompt, 
                                         user_prompt=user_prompt,
                                         model=model)
        logging.info(f"Response: {response}")

        return response

    def __query_gpt_for_json(self, 
                             transcription_text,
                             clipped_video,
                             music_category_options):
        logging.info("Querying openai for transcript info.")
        model="gpt-3.5-turbo"
        
        system_prompt = self.__create_system_prompt(music_category_options)        
        user_prompt = "Here is the text: " + transcription_text + ". Reply with only the json and nothing else."
        
        response = self.openai_api.query(system_prompt, user_prompt, model)
        logging.info(f"Response: {response}")
        json_string = response
        
        video_info_dictionary = self.__parse_json_string(json_string, clipped_video)
        
        if music_category_options == 1:
            video_info_dictionary['category'] = music_category_options[0]
        
        logging.info(f"Generated dictionary: {str(video_info_dictionary)}")

        return video_info_dictionary

    def __create_system_prompt(self, music_category_options):
        if len(music_category_options) > 1:
            self.__initialize_category_list_string(music_category_options)
            system_prompt = ("You will be given a transcript of a video. "
                    "Please return in json format, the following 3 things: "
                    "1. 'description': a 1 sentence description of the transcript "
                    "2. 'title': a clickbait title for the video that is as intriguing and attention grabbing as possible."
                    "The best title must be, concise and short, refuting something, epic or extreme," 
                    "have a timeframe, contain an authority, invoke curiosity fear or negativity." 
                    "3. 'category': for this transcript. Choose the BEST option from: " + self.CATEGORY_LIST_STRING + ".")
        else: 
            system_prompt = ("You will be given a transcript of a video. "
                    "Please return in json format, the following 2 things: "
                    "1. 'description': a 1 sentence description of the transcript "
                    "2. 'title': a clickbait title for the video that is as intriguing and attention grabbing as possible."
                    "The best title must be, refuting something, epic or extreme, include a time, contain an authority, invoke curiosity fear or negativity, have a timeframe.")
                    
        return system_prompt

    def __initialize_category_list_string(self, music_category_options):
        self.CATEGORY_LIST_STRING = ""
        for category in music_category_options:
            self.CATEGORY_LIST_STRING += category + ", "
    
    # TODO Handle the case where the json string is not valid
    def __parse_json_string(self, json_string, clipped_video):
        try:
            json_dict = json.loads(json_string)
            json_dict = self.__validate_dict(json_dict)
            return json_dict
        except ValueError as e:
            print(f"Error parsing JSON string: {e}")
            return {"description": json_string, "hashtags": ["", ""], "title": clipped_video['file_name'], "category": "motivational"}
        except TypeError as t:
            print(f"Error parsing JSON string: {t}")
            return {"description": {json_string}, "hashtags": ["", ""], "title": clipped_video['file_name'], "category": "motivational"}
        
    def __validate_dict(self, json_dict):
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