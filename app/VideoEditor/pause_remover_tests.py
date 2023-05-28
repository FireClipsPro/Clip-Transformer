import unittest
import json
from moviepy.video.io.VideoFileClip import VideoFileClip
from pause_remover import PauseRemover

root = "../../media_storage/"
RESIZED_FOLDER = f"{root}resized_original_videos/"
AUDIO_EXTRACTIONS_FOLDER = f"{root}audio_extractions/"

class TestPauseRemover(unittest.TestCase):
    
    def setUp(self):
        self.pause_remover = PauseRemover(RESIZED_FOLDER, RESIZED_FOLDER)

    @classmethod
    def setUpClass(cls):
        cls.pause_remover = PauseRemover(RESIZED_FOLDER, RESIZED_FOLDER)

        with open(AUDIO_EXTRACTIONS_FOLDER + "Eliezer_(0, 0)_(0, 25)_centered.mp3.json", "r") as f:
            cls.transcript = json.load(f)['word_segments']

        cls.file_name = "Eliezer_(0, 0)_(0, 25)_centered.mp4"
        cls.max_pause_length = 0.4
        
    def test_remove_pauses_from_transcript(self):
        transcript = [
            {'text': 'word1', 'start': 0.0, 'end': 1.0},
            {'text': 'word2', 'start': 2.0, 'end': 3.0},
            {'text': 'word3', 'start': 4.5, 'end': 5.5}
        ]

        max_pause_length = 1.0

        expected_transcript = [
            {'text': 'word1', 'start': 0.0, 'end': 1.0},
            {'text': 'word2', 'start': 2.0, 'end': 3.0},
            {'text': 'word3', 'start': 4.0, 'end': 5.0}
        ]

        new_transcript = self.pause_remover.remove_transcript_pauses(transcript, max_pause_length)

        self.assertEqual(new_transcript, expected_transcript)
        
        
    def test_remove_pauses_from_transcript_and_video(self):
        max_pause_length = 0.4
        video = {}
        video['file_name'] = "Eliezer_(0, 0)_(0, 25)_centered.mp4"
        new_video, new_transcript = self.pause_remover.remove_pauses(video,
                                                                        self.transcript,
                                                                        max_pause_length)
        original_video = VideoFileClip(self.pause_remover.input_video_folder + video['file_name'])

        original_duration = original_video.duration
        new_video = VideoFileClip(self.pause_remover.output_video_folder + video['file_name'])
        new_video_duration = new_video.duration

        original_transcript_duration = sum([seg['end'] - seg['start'] for seg in self.transcript])
        new_transcript_duration = sum([seg['end'] - seg['start'] for seg in new_transcript])

        self.assertAlmostEqual(original_duration - new_video_duration,
                               original_transcript_duration - new_transcript_duration,
                               places=2)


if __name__ == '__main__':
    unittest.main()
