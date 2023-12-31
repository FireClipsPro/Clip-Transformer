
from clip_finder import ClipLenghtReducer
from text_analyzer import OpenaiApi
from configuration import directories
from subtitle_adder import SubtitleAdder
import moviepy.editor as moviepy
import unittest
import copy
import json
import math

transcript_folder = "../test_medias/audio_extractions/"
input_folder = "../test_medias/InputVideos/"
shortened_folder = "../test_medias/OutputVideos/"

class TestClipLengthReducer(unittest.TestCase):
    def setUp(self):
        openai_api = OpenaiApi()
        self.clip_length_reducer = ClipLenghtReducer(openai_api,
                                                     input_folder,
                                                     shortened_folder)
        subtitle_adder = SubtitleAdder(shortened_folder,
                                       shortened_folder)

    # def test_reduce(self):
    #     with open(transcript_folder + 'repub.json') as f:
    #         transcript = json.load(f)
            
    #     self.assertIsNotNone(transcript)
    #     # transcript = self.round_times(transcript)
        
    #     self.clip_length_reducer.MAX_VIDEO_DURATION = 35
    #     new_transcript = self.clip_length_reducer.reduce(transcript=transcript['segments'], 
    #                                     clip_file_name='repub.mp4')
        
    #     print(str(new_transcript))
        
    #     transcript_length = new_transcript[-1]['end'] - new_transcript[0]['start']
        
    #     video = moviepy.VideoFileClip(input_folder + 'repub.mp4')
    #     video_duration = video.duration
        
        
        
    #     self.assertLess(transcript_length, video_duration)
    #     self.assertLessEqual(transcript_length, self.clip_length_reducer.MAX_VIDEO_DURATION)
    
    def test_removing_parts_from_transcript_and_video(self):
        with open(transcript_folder + 'repub.json') as f:
            transcript = json.load(f)
            
        transcript = transcript['segments']
        
        parts_to_remove = [{'start': 0.1408187134502924,
                            'end': 3.1784795321637427},
                           {'start': 37.46, 
                            'end': 40.66},
                           {'start': 41.680352941176466, 
                            'end': 41.822823529411764}]
        parts_to_remove_from_video = copy.deepcopy(parts_to_remove)
        
        initial_transcript_length = transcript[-1]['end'] - transcript[0]['start']
        initial_video_duration = moviepy.VideoFileClip(input_folder + 'repub.mp4').duration

        transcript = self.clip_length_reducer.remove_parts_from_transcript(transcript, parts_to_remove)
        clip_file_name, video_duration = self.clip_length_reducer.remove_parts_from_video(clip_file_name='repub.mp4',
                                                                                          parts_to_remove=parts_to_remove_from_video)
        
        resulting_transcript_length = transcript[-1]['end'] - transcript[0]['start']
        resulting_video_duration = moviepy.VideoFileClip(shortened_folder + clip_file_name).duration
        
        transcript_len_diff = initial_transcript_length - resulting_transcript_length
        video_len_diff = initial_video_duration - resulting_video_duration
        
        print(f"initial transcript length: {initial_transcript_length}, initial video duration: {initial_video_duration}")
        print(f"transcript_len_diff: {transcript_len_diff}, video_len_diff: {video_len_diff}")
        print(f"Resulting Video duration: {video_duration}")
        print(f"Resulting Transcript length: {resulting_transcript_length}")
        # assert that the video is longer or equal to the duration of the transcript
        self.assertTrue(video_duration >= resulting_transcript_length)
        # asssert that the length of the transcript has been reduced as much as the video
        # self.assertEqual(video_len_diff, transcript_len_diff)
        
    
    def round_times(self, transcript):
        for segment in transcript['segments']:
            segment['start'] = self.floor(segment['start'])
            segment['end'] = self.ceil(segment['end'])
            
        return transcript
    
    def floor(self, num):
        return math.floor(num * 1000) / 1000
    
    def ceil(self, num):
        return math.ceil(num * 1000) / 1000
    
    # def test_RemovePartsFromVideo_RemoveOnePart_CorrectTimeIsRemoved(self):
    #     self.clip_length_reducer.output_clip_folder_path = input_folder
    #     # get starting duration of video
    #     video = moviepy.VideoFileClip(input_folder + 'test_file_1.mp4')
    #     starting_duration = video.duration
        
    #     final_clip, duration = self.clip_length_reducer.remove_parts_from_video('test_file_1.mp4',
    #                                                                             [{'start': 2, 'end': 4}])
        
    #     # get the duration of the video
    #     video = moviepy.VideoFileClip(input_folder + final_clip)
        
    #     self.assertNotEqual(duration, starting_duration)
    #     print(f"starting_duration: {starting_duration}, returned duration: {duration}")
    #     print(f"calculated duration: {video.duration}")
    #     self.assertEqual(starting_duration - video.duration, 2.0)
    #     self.assertEqual(starting_duration - 2.0, video.duration)
        
    #     # tear down
    #     self.clip_length_reducer.output_clip_folder_path = shortened_folder
        
    # def test_get_parts_to_remove(self):
    #     def is_overlapping(part1, part2):
    #         return part1['start'] < part2['end'] and part1['end'] > part2['start']
    #     # load the transcript from the transcript folder
    #     with open(transcript_folder + 'repub.json') as f:
    #         transcript = json.load(f)
        
    #     # print(str(transcript['segments']))
        
    #     parts_to_remove = self.clip_length_reducer.get_parts_to_remove(transcript['segments'])
        
    #     print(str(parts_to_remove))
    #     # ensure that the parts to remove are not empty
    #     self.assertTrue(len(parts_to_remove) > 0)
    #     # ensure that the parts to remove are valid parts of the transcript
    #     for part in parts_to_remove:
    #         start_times = [segment['start'] for segment in transcript['segments']]
    #         end_times = [segment['end'] for segment in transcript['segments']]

    #         self.assertTrue(part['start'] in start_times, f"Start time {part['start']} not found in transcript segments")
    #         self.assertTrue(part['end'] in end_times, f"End time {part['end']} not found in transcript segments")
            
    #     # ensure that the parts to remove are not overlapping
    #     for i in range(len(parts_to_remove)):
    #         for j in range(i + 1, len(parts_to_remove)):
    #             self.assertFalse(is_overlapping(parts_to_remove[i], parts_to_remove[j]))

    # def test_remove_parts_from_transcript(self):
    #     transcript = [{'text': 'segment1', 'start': 1, 'end': 4}, 
    #                   {'text': 'segment2', 'start': 5, 'end': 9}, 
    #                   {'text': 'segment3', 'start': 10, 'end': 15}]
    #     parts_to_remove = [{'start': 1, 'end': 4}, {'start': 10, 'end': 15}]
        
    #     expected_transcript = [{'text': 'segment2', 'start': 1, 'end': 5}]
    #     result_transcript = self.clip_length_reducer.remove_parts_from_transcript(transcript, parts_to_remove)

        self.assertEqual(result_transcript, expected_transcript)
    
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
