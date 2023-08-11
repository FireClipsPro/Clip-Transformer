import nltk
from nltk.tokenize import word_tokenize
import json
import logging
import math

logging.basicConfig(level=logging.INFO)

class HighlightFinder:
    def __init__(self, 
                 openai_api):
        self.openai_api = openai_api
        self.valid_start_stamps = []
        self.valid_end_stamps = []
        self.valid_start_stamps = []
        self.valid_end_stamps = []

    # input should be a transcript in the following format:
    # [{'text': 'text goes here', 'start': 0.22332, 'end': 2.3342}, ...]
    # returns list of clips [{'start': 0.22332, 'end': 65.3342}, ...]
    def get_highlights(self, transcript):
        self.valid_start_stamps = [segment["start"] for segment in transcript]
        self.valid_end_stamps = [segment["end"] for segment in transcript]
        
        hooks = self.find_hooks(transcript)
        
        highlights = self.find_clips(transcript, transcript, hooks)
        
        return highlights

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
            Only return the start times of the best 1-3 starting points and make sure they are not close to each other in the transcript.
            Return only the 'start' timestamps of these intriguing starting points as a list, in this form:
            [2.3342, 5.1234, ...]
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

    def find_clips(self, transcript, hooks):
        logging.info("Finding clips")
        clips = []

        for hook in hooks:
            clips = self.query_gpt_for_end_times(hook, transcript, clips)
            
        logging.info("Clips: " + str(clips))
        
        clips = self.get_transcripts(transcript, clips)
        
        return clips

    def get_transcripts(self, transcript, clips):
        for clip in clips:
            logging.info("previous start and end times: " + str(clip))
            clip['transcript'] = []
            # add all segments inside of transcript to the clip
            for segment in transcript:
                # we have to round numbers down because the timestamps in the transcript are rounded down
                if ((segment['start'] <= clip['end'] and segment['start'] >= clip['start'])
                    and (segment['end'] <= clip['end'] and segment['end'] >= clip['start'])):
                    clip['transcript'].append(segment['text'])
                    break

            # ensure that start and end time set correctly
            # previously they were rounded but now they are not
            clip['start'] = clip['transcript'][0]
            clip['end'] = clip['transcript'][-1]
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
                For example:
                5.1234
                Return only the number and absolutely nothing else."""
            
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
            else:
                logging.info("Invalid timestamp returned. Trying again...")
        
        logging.info(f"found valid clip: {hook} to {end_time}")
        clips.append({"start": hook, "end": end_time})   
        return clips

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