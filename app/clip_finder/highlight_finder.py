import nltk
from nltk.tokenize import word_tokenize
import json
import logging
import os
import math

logging.basicConfig(level=logging.INFO)

class HighlightFinder:
    def __init__(self, 
                 openai_api,
                 hooks_folder_path,
                 clip_end_folder_path,
                 re_use_hooks=True,
                 re_use_clip_ends=True,
                 min_clip_length=20,):
        self.openai_api = openai_api
        self.valid_start_stamps = []
        self.valid_end_stamps = []
        self.valid_start_stamps = []
        self.valid_end_stamps = []
        self.re_use_hooks = re_use_hooks
        self.hooks_folder_path = hooks_folder_path
        self.clip_end_folder_path = clip_end_folder_path
        self.re_use_clip_ends = re_use_clip_ends
        self.min_clip_length = min_clip_length

    # input should be a transcript in the following format:
    # [{'text': 'text goes here', 'start': 0.22332, 'end': 2.3342}, ...]
    # returns list of clips [{'start': 0.22332, 'end': 65.3342}, ...]
    def get_highlights(self, video_id, transcript):
        self.valid_start_stamps = [segment["start"] for segment in transcript]
        self.valid_end_stamps = [segment["end"] for segment in transcript]
        
        hooks = self.init_hooks(video_id, transcript)
        
        highlights = self.find_clips(transcript, hooks, video_id)
        
        return highlights
    
    def throw_away_small_clips(self, clips):
        for clip in clips:
            if clip['end'] - clip['start'] < self.min_clip_length:
                logging.info(f"Throwing away clip at: {clip['start']}, because it is too short.")
                clips.remove(clip)
        return clips

    def init_hooks(self, video_name, transcript):
        if self.re_use_hooks:
            hooks_path = self.hooks_folder_path + video_name[:-4] + ".json"
            #check if there is a json file with the same name as the video
            if os.path.exists(hooks_path):
                logging.info("Json file found. Using hooks from json file.")
                with open(hooks_path , "r") as file:
                    hooks = json.load(file)
            else:
                logging.info("No json file found. Finding hooks...")
                hooks = self.find_hooks(transcript)
                with open(hooks_path , "w+") as file:
                    json.dump(hooks, file)
        return hooks

    def chunk_transcript(self, transcript):
        # print(transcript)
        cleaned_transcript = ""
        
        for segment in transcript:
            cleaned_transcript += f"(start:{segment['start']}, {segment['text']}), "
        # Tokenize the transcript
        tokens = word_tokenize(cleaned_transcript)
        
        # Split the tokens into chunks of at most 4096 tokens
        chunks = []
        current_chunk = []
        current_token_count = 0
        for token in tokens:
            if current_token_count + len(token) > 4096:
                # If adding the next token would exceed the limit, we start a new chunk
                chunks.append(' '.join(current_chunk))
                current_chunk = [token]
                current_token_count = len(token)
            else:
                # Otherwise, we add the token to the current chunk
                current_chunk.append(token)
                current_token_count += len(token)
        
        # Don't forget to add the last chunk if it's non-empty
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    

    def find_hooks(self, transcript):
        logging.info("Finding hooks")
        
        transcript_chunks = self.chunk_transcript(transcript)
        responses = []
        
        for chunk in transcript_chunks:
            model = "gpt-3.5-turbo"
            system_prompt = """Given a list of podcast transcript segments like the following:
            [
                (start: 0.22332, text goes here),
                (start: 2.3342, another segment text),
                (start: 5.1234, more dialogue here),
                ...
            ]
            Please analyze the 'text' within each segment to identify intriguing starting points for a short video. An 'intriguing' starting point could be a moment where a question is asked, a surprising statement is made, an interesting topic is introduced, or a humorous incident is shared - essentially, anything that would immediately catch a viewer's attention and encourage them to continue watching the video. 
            Only return the start times of the best 1-2 starting points and make sure they are not close to each other in the transcript.
            Return only the 'start' timestamps of these intriguing starting points as a list, in this form:
            [2.3342, 72.1442]
            Return absolutely nothing other than the list of timestamps.
            """
            user_prompt = str(chunk)
            response = self.openai_api.query(system_prompt, user_prompt, model)
            
            # response is a list in string format. Convert this string to an array.
            array = json.loads(response)
            for timestamp in array:
                if timestamp not in responses:
                    responses.append(timestamp)
            
            logging.info("Response: " + str(array))
        
        hooks = responses
        logging.info("Responses: " + str(responses))
        
        # ensure that every hook is a valid start time
        hooks = [hook for hook in hooks if self._is_valid_timestamp(hook)]
        
        logging.info("Hooks after removing invalid ones:" + str(hooks))
        
        return hooks

    def find_clips(self, transcript, hooks, video_id):
        logging.info("Finding clips")
        clips = []

        clip_end_path = self.clip_end_folder_path + video_id[:-4] + ".json"
        # check if clip ends have already been foun
        if self.re_use_clip_ends and os.path.exists(clip_end_path):
            logging.info("Json file found. Using clip ends from json file.")
            with open(clip_end_path , "r") as file:
                clips = json.load(file)
        else:
            for hook in hooks:
                clips.append(self.query_gpt_for_end_times(hook, transcript, clips))
            logging.info(f"Saving clip ends to json file {clip_end_path}")
            with open(clip_end_path , "w+") as file:
                json.dump(clips, file)
        
        logging.info("Clips: " + str(clips))
        
        clips = self.throw_away_small_clips(clips)
        
        clips = self.get_transcripts(transcript, clips)
        
        return clips

    # returns list of clips with transcripts
    # clips = [{'start': 0.22332,
    #           'end': 65.3342,
    #           'transcript': [
    #               {'text': 'text goes here',
    #                'start': 0.22332, 
    #                'end': 2.3342}, ...]}, ...]
    def get_transcripts(self, transcript, clips):
        for clip in clips:
            logging.info("previous start and end times: " + str(clip))
            clip['transcript'] = []
            # add all segments inside of transcript to the clip
            for segment in transcript:
                # we have to round numbers down because the timestamps in the transcript are rounded down
                
                # check if all start and end times are floats
                if not (isinstance(segment['start'], float) and isinstance(segment['end'], float)):
                    # throw an error if they are not
                    raise ValueError(f"segment {str(segment)} has a start or end time that is not a float")
                
                if ((segment['start'] <= clip['end'] and segment['start'] >= clip['start'])
                    and (segment['end'] <= clip['end'] and segment['end'] >= clip['start'])):
                    clip['transcript'].append(segment)
                    # break

            # ensure that start and end time set correctly
            # previously they were rounded but now they are not
            clip['start'] = clip['transcript'][0]['start']
            clip['end'] = clip['transcript'][-1]['end']
            logging.info(f"new start and end times: {clip['start']} to {clip['end']}")

        return clips
    
    def query_gpt_for_end_times(self, hook, transcript, clips):
        is_valid_timestamp = False
        transcript_section = str(self.get_first_4k_tokens_after_timestamp(hook, transcript))

        while not is_valid_timestamp:
            logging.info("Querying GPT for end time for hook: " + str(hook))
            model = "gpt-3.5-turbo"
            system_prompt = """Given a podcast transcript in the following format:
                (end: 5.1234, dialogue goes here),
                (end: 7.6543, more dialogue here),
                ...
                The start of the transcript is the start of a short clip. You need to find the end of the clip.
                Identify an end timestamp around 60 seconds after the start that would make a good ending for the clip. A good ending would be where the speakers stop discussing the topic introduced at the start, or the conversation loses its interesting quality, or just a point that would be a good wrap up.
                Only return the 'end' timestamp of this section. 
                Respond with only the number and absolutely nothing else.
                For example:
                Your response: 5.1234"""
            
            user_prompt = transcript_section

            response = self.openai_api.query(system_prompt, user_prompt, model)
            logging.info("Response for end timestamp query: " + str(response))
            #remove all of the letters or spaces or symbols from the response
            response = ''.join([i for i in response if i.isdigit() or i == '.'])
            # if the first character of the response is a period, remove it
            if response[0] == '.':
                response = response[1:]
            if response[-1] == '.':
                response = response[:-1]
            
            end_time = response

            if self._is_valid_timestamp(end_time):
                is_valid_timestamp = True
                end_time = float(end_time)
            else:
                logging.info("Invalid timestamp returned. Trying again...")
        
        logging.info(f"found valid clip: {hook} to {end_time}")
        clip = {"start": hook, "end": end_time}
        return clip

    def get_first_4k_tokens_after_timestamp(self, hook, transcript):
        logging.info("Getting first 4k tokens after timestamp")
        logging.info("Hook: " + str(hook))
        #get remove the part of the transcript before the hook timestamp
        transcript = [segment for segment in transcript if segment['start'] >= hook and segment['end'] <= hook + 120]
        
        cleaned_transcript = ""
        
        for segment in transcript:
            cleaned_transcript += f"({segment['text']}, end:{segment['end']}), "
        # Tokenize the transcript
        tokens = word_tokenize(cleaned_transcript)
        
        # Split the tokens into chunks of at most 4096 tokens
        current_chunk = []
        current_token_count = 0
        for token in tokens:
            if current_token_count + len(token) > 4096:
                # If adding the next token would exceed the limit, we end the loop
                # logging.info("Chunk: " + str(current_chunk))
                break
            else:
                # Otherwise, we add the token to the current chunk
                current_chunk.append(token)
                current_token_count += len(token)
        
        #de-tokenize the chunk
        current_chunk = ' '.join(current_chunk)
        
        logging.info("Chunk created.")
        return current_chunk

    def _is_valid_timestamp(self, timestamp):
        """Helper function to check if a given timestamp is valid."""
        # Check if timestamp can be converted to a float
        try:
            float(timestamp)
        except ValueError:
            logging.info(f"Timestamp {timestamp} is not a valid float.")
            return False  # If it can't be converted to a float, it's not a valid timestamp
        
        if float(timestamp) in self.valid_end_stamps or timestamp in self.valid_start_stamps:
            return True
        else :
            logging.info(f"Timestamp {timestamp} is not found in list:{self.valid_end_stamps}")
            return False 
        



# transcribe video

# look through transcript and find hooks 
# return list of start times

# take transcript from start times -> end of transcript and find where the subject ends