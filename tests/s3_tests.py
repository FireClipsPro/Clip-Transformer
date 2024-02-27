import unittest
from moviepy.editor import VideoFileClip, AudioFileClip
from app.services.s3 import S3
import app.configuration.directories as directories
import app.configuration.buckets as buckets
import boto3

class TestS3(unittest.TestCase):
    def setUp(self):
        self.s3 = S3(s3=boto3.client('s3'))

    def test_write_videofileclip(self):
        # Call the method under test
        clip = VideoFileClip(directories.VM_BACKGROUNDS + "wormhole.mp4")  # No actual file needed due to mocking
        self.s3.write_videofileclip(clip, 'wormhole', buckets.bg_videos)

    def test_get_videofileclip(self):
        video_clip = self.s3.get_videofileclip('wormhole', 
                                               buckets.bg_videos)

        self.assertIsInstance(video_clip, VideoFileClip)
        self.assertIsNotNone(video_clip)
        
    def test_get_audiofileclip(self):
        video_clip = self.s3.get_videofileclip('wormhole', 
                                               buckets.bg_videos)

        self.assertIsInstance(video_clip, VideoFileClip)
        self.assertIsNotNone(video_clip)
        
        # Call the method under test
        audio_clip = self.s3.get_audiofileclip('archeaoaccoustics', buckets.audio_files)

        # Assertions
        self.assertIsInstance(audio_clip, AudioFileClip)
        self.assertIsNotNone(audio_clip)
        
        # optional save the audio clip to a file
        # audio_clip.write_audiofile(directories.VM_AUDIO_EXTRACTIONS + 'temp_audio.mp3')

    def tearDown(self):
        self.s3.dispose_temp_files()

if __name__ == '__main__':
    unittest.main()