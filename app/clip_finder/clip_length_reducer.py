from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import moviepy.editor as moviepy
import logging
import math
import json
import copy
import shutil
import os

logging.basicConfig(level=logging.INFO)

class ClipLenghtReducer():
    def __init__(self,
                 openai_api,
                 input_clip_folder_path,
                 output_clip_folder_path):
        self.openai_api = openai_api
        self.input_clip_folder_path = input_clip_folder_path
        self.output_clip_folder_path = output_clip_folder_path
        self.valid_start_stamps = []
        self.valid_end_stamps = []
        self.MAX_VIDEO_DURATION = 60
    
    def get_video_duration(self, clip_file_name):
        video = moviepy.VideoFileClip(f"{self.input_clip_folder_path}/{clip_file_name}")
        return video.duration

    
    def reduce(self, 
               transcript,
               clip_file_name):
        """Reduces the length of the clip to 60 seconds or less
        Args:
            transcript (_type_): The transcript must have ['segments'] and ['word_segments'] keys
            clip_file_name (_type_): name.mp4
        Returns:
            _type_: modified transcript and name of shortened clip
        """
        video_duration = self.get_video_duration(clip_file_name)
        # edge_time = self.calculate_edge_time(transcript, video_duration)
        
        # renaming the clip_file_name
        clip_file_name = self.rename_and_move(clip_file_name)
        num_reductions = 0
        while video_duration > self.MAX_VIDEO_DURATION:
            logging.info(f"Video duration is {video_duration} seconds, reducing...")
            parts_to_remove = self.get_parts_to_remove(transcript['segments'])
            parts_to_remove_from_video = copy.deepcopy(parts_to_remove)
            
            logging.info("Removing parts from segments")
            transcript['segments'] = self.remove_parts_from_transcript(transcript['segments'], parts_to_remove)
            logging.info("Removing parts from word_segments")
            transcript['word_segments'] = self.remove_parts_from_transcript(transcript['word_segments'], parts_to_remove)

            clip_file_name, video_duration = self.remove_parts_from_video(clip_file_name, parts_to_remove_from_video, num_reductions)
            
            transcript_length = self.get_length_of_transcript(transcript['segments'])
            if ((video_duration * 1000) / 1000 < transcript_length):
                raise Exception(f"Video duration: {video_duration} does not match transcript length: {transcript_length}")
            
            num_reductions += 1
            
        logging.info(f"Video duration is {video_duration} seconds, finished reducing.")
        return transcript, clip_file_name

    def rename_and_move(self, clip_file_name):
        renamed_clip_file_name = f"reduced_{clip_file_name}"
        source = os.path.join(self.input_clip_folder_path, clip_file_name)
        destination = os.path.join(self.output_clip_folder_path, renamed_clip_file_name)
        
        shutil.copy2(source, destination)
        
        return renamed_clip_file_name
    
    def get_length_of_transcript(self, transcript):
        return transcript[-1]['end'] - transcript[0]['start']
    
    def remove_parts_from_video(self, clip_file_name, parts_to_remove, num_reductions):
        video = moviepy.VideoFileClip(f"{self.output_clip_folder_path}{clip_file_name}")
        logging.info(f"Removing parts: {parts_to_remove} from video: {clip_file_name}")
        #log the number of seconds being removed:
        time_removed = 0
        for part in parts_to_remove:
            time_removed += part['end'] - part['start']
        logging.info(f"Removing: {time_removed}, from the video")
        
        remaining_parts = []
        end_of_last_part = 0.0
        for part in sorted(parts_to_remove, key=lambda x: x['start']):
            remaining_parts.append(video.subclip(end_of_last_part, part['start']))
            end_of_last_part = part['end']
        
        remaining_parts.append(video.subclip(end_of_last_part, video.duration))
        
        final_clip = moviepy.concatenate_videoclips(remaining_parts)
        final_clip_name = f"reduced_{num_reductions}_{clip_file_name}"
        final_clip.write_videofile(f"{self.output_clip_folder_path}{final_clip_name}")
        
        return final_clip_name, final_clip.duration
    
    # used to calculate the time before the first word of the transcript
    # and the time after the last word of the transcript
    # this function assumes that the the video_duration and transcript are accurate
    # also assumes that transcript is normalized
    def calculate_edge_time(self, transcript, video_duration):
        return self.to_seconds(self.to_milliseconds(transcript[0]['start']) 
                                + self.to_milliseconds(video_duration) 
                                - self.to_milliseconds(transcript[-1]['end']))
    
    def to_milliseconds(self, timestamp):
        return int(timestamp * 1000)
    
    def to_seconds(self, timestamp):
        return timestamp / 1000
    
    def remove_parts_from_transcript(self, transcript, parts_to_remove):
        logging.info(f"Removing parts: {parts_to_remove} from transcript")
        # logging.info(f"before removing parts: {transcript}")
        logging.info(f"transcript len = {len(transcript)}")
        #put all times in integer form (decimal subtraction keeps giving errors)
        for part in parts_to_remove:
            part['start'] = self.to_milliseconds(part['start'])
            part['end'] = self.to_milliseconds(part['end'])
        for segment in transcript:
            segment['start'] = self.to_milliseconds(segment['start'])
            segment['end'] = self.to_milliseconds(segment['end'])
        
        time_removed = 0
        for part in parts_to_remove:
            part['start'] -= time_removed
            part['end'] -= time_removed
            transcript = self.remove_part_from_transcript(transcript, part)
            time_removed += part['end'] - part['start']
            logging.info(f"transcript len = {len(transcript)}")
            # logging.info(f"Time removed from part to remove: {time_removed} milliseconds")
        
        logging.info(f"Time removed from transcript: {time_removed} milliseconds")
        # put times back to seconds form
        for segment in transcript:
            segment['start'] = self.to_seconds(segment['start'])
            segment['end'] = self.to_seconds(segment['end'])
        for part in parts_to_remove:
            part['start'] = self.to_seconds(part['start'])
            part['end'] = self.to_seconds(part['end'])
        logging.info(f"after removing parts: {transcript}")
        
        return transcript
    
    def remove_part_from_transcript(self, transcript, rem_part):
        time_subtracted = rem_part['end'] - rem_part['start']
        print(f"current transcript end time: {transcript[-1]['end']}")
        # logging.info(f"Removing part: {rem_part} from transcript. Time to be subtracted: {time_subtracted} milliseconds")

        new_transcript = []
        if rem_part['start'] == transcript[-1]['start'] and rem_part['end'] == transcript[-1]['end']:
            logging.info(f"Removing last element of transcript: {transcript[-1]}")
            new_transcript = transcript[:-1]
            logging.info(f"New transcript end time: {new_transcript[-1]['end']}")
            return new_transcript
            
        
        # remove all parts that are inside of the part to remove
        # for all segments after part to remove, subtract the time removed from the start and end times
        for segment in transcript:
            # logging.info("transcript:" + str(transcript))
            # logging.info("segment:" + str(segment))
            if segment['start'] >= rem_part['end']:
                # logging.info(f"Subtracting {time_subtracted} milliseconds from segment: {segment}")
                new_transcript.append({'start': segment['start'] - time_subtracted,
                                        'end': segment['end'] - time_subtracted,
                                        'text': segment['text']})
            # case: segment is fully inside of part
            elif (segment['start'] >= rem_part['start'] and segment['end'] <= rem_part['end']):
                #remove segment from the transcript
                logging.info(f"Removing segment: {segment} of length: {segment['end'] - segment['start']} milliseconds")
            # case: segment is partially inside of part (straddling rem_part end or start) (this should not happen)
            elif ((segment['start'] > rem_part['start'] and segment['start'] < rem_part['end'] and segment['end'] > rem_part['end'])
                  or(segment['start'] < rem_part['start'] and segment['end'] < rem_part['end'] and segment['end'] > rem_part['start'])):
                # logging.info(f"Removing segment: {segment} of length: {segment['end'] - segment['start']} milliseconds")
                raise Exception(f"Segment: ({segment['start']}, {segment['end']}) is partially inside of part to remove: ({rem_part['start']}, {rem_part['end']}). This should not happen.")
            # case: segment is before part to remove
            else:
                new_transcript.append(segment)
        logging.info(f"New transcript end time: {new_transcript[-1]['end']}")
        # logging.info(f"New transcript: {str(new_transcript)}")
        return new_transcript

    # returns list of parts to remove in the form [{start: 0, end: 10}, {start: 20, end: 30}]
    def get_parts_to_remove(self, transcript):
        # pass the transcript into the openai api and as it to return a list of start and end times
        # that can be removed from the clip, in the form [{start: 0, end: 10}, {start: 20, end: 30}]
        # return list of parts that can be removed
        cleaned_transcript = self.clean_transcript(transcript)
        response_is_valid = False
        
        while not response_is_valid:
            model = "gpt-3.5-turbo"
            system_prompt = """Given a list of podcast transcript segments like the following:
                (start: 0.22, end: 2.33, text goes here),
                (start: 3.30, end: 4.33, another segment text),
                (start: 5.12, end: 6.34, more dialogue here),
                ...
                This transcript that is too long and needs to be shortened.
                Your task is to identify the very best 1-3 segments to remove from the clip so that the length of the clip is reduced to 60 seconds.
                The best segments to remove are those least interesting to the viewer or least critical to the story.
                Return the list of the parts to remove in this form and only this form:
                {"list": [{"start: 2.3342, "end": 5.1234}, {"start": 6.1234, "end": 7.1234}, ...}]}
                Return absolutely nothing other than the json. Make sure that it is perfectly formatted.
                """
            response = self.openai_api.query(system_prompt, cleaned_transcript, model)

            processed_response = self.ensure_valid_response(response)

            if processed_response is not None:
                response_is_valid = True

        transcript_length = transcript[-1]['end'] - transcript[0]['start']
        parts_to_remove = self.remove_extra_parts(processed_response['list'], transcript_length)

        return parts_to_remove

    # ensures that we remove the minimum amount of time from the clip
    # gets rid of the parts that will remove too much time from the clip
    def remove_extra_parts(self, parts, transcript_length):
        # order parts by descending start time (we start by removing from the back because the start of the video is more important)
        parts = sorted(parts, key=lambda x: x['start'], reverse=True)
        
        parts_to_be_removed = []
        time_to_be_removed = 0
        for part in parts:
            parts_to_be_removed.append(part)
            time_to_be_removed += part['end'] - part['start']
            if time_to_be_removed >= transcript_length - self.MAX_VIDEO_DURATION:
                break
        
        # order parts by ascending start time to be removed later
        parts_to_be_removed = sorted(parts_to_be_removed, key=lambda x: x['start'])
        return parts_to_be_removed
    
    def ensure_valid_response(self, response):
        try:
            # Attempt to parse the string into a dictionary
            response = json.loads(response)
        except json.JSONDecodeError:
            logging.info(f"Response {response} could not be parsed into a dictionary.")
            return None
        # Ensure response can be converted to a dictionary
        if not isinstance(response, dict):
            logging.info(f"Response {response} is not a valid dictionary.")
            return None

        # Ensure response has a 'list' key, and it's a list
        if 'list' not in response or not isinstance(response['list'], list):
            logging.info(f"Response {response} does not have a 'list' key or it's not a list.")
            return None

        # Ensure each section in the list is a dictionary with 'start' and 'end' keys,
        # and both keys correspond to numbers (int or float)
        for section in response['list']:
            logging.info(f"Section is {section}")
            if not isinstance(section, dict):
                logging.info(f"Section {section} is not a valid dictionary.")
                return None

            if 'start' not in section or 'end' not in section:
                logging.info(f"Section {section} does not have a 'start' or 'end' key.")
                return None

            if not isinstance(section['start'], (int, float)) or not isinstance(section['end'], (int, float)):
                logging.info(f"Section {section} does not have a 'start' or 'end' key that is a number.")
                return None

            if not self._is_valid_timestamp(section['start']) or not self._is_valid_timestamp(section['end']):
                logging.info(f"Section {section} does not have a 'start' or 'end' key that is a valid timestamp.")
                return None

        logging.info(f"Response {response} is valid.")
        # If all checks passed, the response is valid
        return response

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
    
    def clean_transcript(self, transcript):
        self.valid_start_stamps = [segment["start"] for segment in transcript]
        self.valid_end_stamps = [segment["end"] for segment in transcript]
        
        cleaned_transcript = ""
        for segment in transcript:
            cleaned_transcript += f"(start:{segment['start']}, end:{segment['end']}, {segment['text']}), "

        return cleaned_transcript[:-2] # remove the last comma and space