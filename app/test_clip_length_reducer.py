
from clip_finder import ClipLenghtReducer
from text_analyzer import OpenaiApi
from configuration import directories
import moviepy.editor as moviepy
import unittest
import json
import math

transcript_folder = "../test_material/audio_extractions/"
input_folder = "../test_material/InputVideos/"
shortened_folder = "../test_material/OutputVideos/"

class TestTranscriptModification(unittest.TestCase):
    def setUp(self):
        openai_api = OpenaiApi()
        self.clip_length_reducer = ClipLenghtReducer(openai_api,
                                                     input_folder,
                                                     shortened_folder)

    # def test_reduce(self):
    #     with open(transcript_folder + 'repub.json') as f:
    #         transcript = json.load(f)
            
    #     self.assertIsNotNone(transcript)
    #     transcript = self.round_times(transcript)
        
    #     self.clip_length_reducer.MAX_VIDEO_DURATION = 35
    #     new_transcript = self.clip_length_reducer.reduce(transcript=transcript['segments'], 
    #                                     clip_file_name='repub.mp4')
        
    #     transcript_length = new_transcript[-1]['end'] - new_transcript[0]['start']
        
    #     video = moviepy.VideoFileClip(input_folder + 'repub.mp4')
    #     video_duration = video.duration
        
    #     self.assertEqual(transcript_length, video_duration)
    #     self.assertTrue(transcript_length <= self.clip_length_reducer.MAX_VIDEO_DURATION)
    
    def round_times(self, transcript):
        for segment in transcript['segments']:
            segment['start'] = self.floor(segment['start'])
            segment['end'] = self.ceil(segment['end'])
            
        return transcript
    
    def floor(self, num):
        return math.floor(num * 1000) / 1000
    
    def ceil(self, num):
        return math.ceil(num * 1000) / 1000
    
    def test_remove_parts_from_video(self):
        self.clip_length_reducer.output_clip_folder_path = input_folder
        # get starting duration of video
        video = moviepy.VideoFileClip(input_folder + 'repub.mp4')
        starting_duration = video.duration
        
        final_clip, duration = self.clip_length_reducer.remove_parts_from_video('repub.mp4', [{'start': 0, 'end': 4}, {'start': 10, 'end': 15}])

        # get the duration of the video
        video = moviepy.VideoFileClip(input_folder + final_clip)
        
        self.assertEqual(duration, video.duration)
        self.assertNotEqual(duration, starting_duration)
        self.assertEqual(starting_duration - duration, 11)
        
        # tear down
        self.clip_length_reducer.output_clip_folder_path = shortened_folder
        
    # def test_get_parts_to_remove(self):
    #     # load the transcript from the transcript folder
    #     with open(transcript_folder + 'repub.json') as f:
    #         transcript = json.load(f)
        
    #     # print(str(transcript['segments']))
        
    #     parts_to_remove = self.clip_length_reducer.get_parts_to_remove(transcript['segments'])
        
    #     print(str(parts_to_remove))

    # def test_remove_parts_from_transcript(self):
    #     transcript = [{'text': 'segment1', 'start': 0, 'end': 4}, 
    #                   {'text': 'segment2', 'start': 5, 'end': 9}, 
    #                   {'text': 'segment3', 'start': 10, 'end': 15}]
    #     parts_to_remove = [{'start': 0, 'end': 4}, {'start': 10, 'end': 15}]
        
    #     expected_transcript = [{'text': 'segment2', 'start': 1, 'end': 5}]
    #     result_transcript = self.clip_length_reducer.remove_parts_from_transcript(transcript, parts_to_remove)

    #     self.assertEqual(result_transcript, expected_transcript)
    
    # def test_remove_parts_from_empty_transcript(self):
    #     transcript = []
    #     parts_to_remove = [{'start': 0, 'end': 4}, {'start': 10, 'end': 15}]
    #     expected_transcript = []
    #     result_transcript = self.clip_length_reducer.remove_parts_from_transcript(transcript, parts_to_remove)
    #     self.assertEqual(result_transcript, expected_transcript)

    # def test_remove_no_parts_from_transcript(self):
    #     transcript = [{'text': 'segment1', 'start': 0, 'end': 4}, 
    #                 {'text': 'segment2', 'start': 5, 'end': 9}, 
    #                 {'text': 'segment3', 'start': 10, 'end': 15}]
    #     parts_to_remove = []
    #     expected_transcript = transcript
    #     result_transcript = self.clip_length_reducer.remove_parts_from_transcript(transcript, parts_to_remove)
    #     self.assertEqual(result_transcript, expected_transcript)

    # def test_single_segment_transcript(self):
    #     transcript = [{'text': 'segment1', 'start': 0, 'end': 4}]
    #     parts_to_remove = [{'start': 0, 'end': 4}]
    #     expected_transcript = []
    #     result_transcript = self.clip_length_reducer.remove_parts_from_transcript(transcript, parts_to_remove)
    #     self.assertEqual(result_transcript, expected_transcript)

    
    # def test_remove_parts_partially_overlapped_with_transcript(self):
    #     transcript = [{'text': 'segment1', 'start': 0, 'end': 4}, 
    #                 {'text': 'segment2', 'start': 5, 'end': 9}, 
    #                 {'text': 'segment3', 'start': 10, 'end': 15}]
    #     parts_to_remove = [{'start': 3, 'end': 6}]
    #     with self.assertRaises(Exception):
    #         self.clip_length_reducer.remove_parts_from_transcript(transcript, parts_to_remove)

    
    # def test_remove_extra_parts_from_list(self):
    #     parts = [{'start': 0, 'end': 4}, {'start': 10, 'end': 15},
    #              {'start': 20, 'end': 25}, {'start': 30, 'end': 35}]
    #     transcript_length = 70
        
    #     expected_parts = [{'start': 20, 'end': 25}, {'start': 30, 'end': 35}]
    #     result_parts = self.clip_length_reducer.remove_extra_parts(parts, transcript_length)
        
    #     self.assertEqual(result_parts, expected_parts)

if __name__ == "__main__":
    unittest.main()
