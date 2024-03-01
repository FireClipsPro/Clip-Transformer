import unittest
from moviepy.editor import VideoFileClip, AudioFileClip
from app.services.s3 import S3
import app.configuration.directories as directories
import app.configuration.buckets as buckets
import boto3

class TestS3(unittest.TestCase):
    def setUp(self):
        self.s3 = S3(s3=boto3.client('s3'))
        self.test_bg = "wormhole.mp4"
        
    def test_write_videofileclip(self):
        # Call the method under test
        clip = VideoFileClip(directories.VM_BACKGROUNDS + self.test_bg)  # No actual file needed due to mocking
        self.s3.write_videofileclip(clip, self.test_bg, buckets.bg_videos)

    def test_get_videofileclip(self):
        video_clip = self.s3.get_videofileclip(video_id=self.test_bg, 
                                               bucket_name=buckets.bg_videos,
                                               prefix=buckets.public_bg_videos_prefix)

        self.assertIsInstance(video_clip, VideoFileClip)
        self.assertIsNotNone(video_clip)
        
    def test_get_audiofileclip(self):        
        # Call the method under test
        audio_clip = self.s3.get_audiofileclip('archeaoaccoustics.mp3', buckets.audio_files)

        # Assertions
        self.assertIsInstance(audio_clip, AudioFileClip)
        self.assertIsNotNone(audio_clip)
        
        # optional save the audio clip to a file
        # audio_clip.write_audiofile(directories.VM_AUDIO_EXTRACTIONS + 'temp_audio.mp3')

    def test_get_item_url(self):
        actual = self.s3.get_item_url(bucket_name=buckets.bg_videos,
                                      object_key=self.test_bg,
                                      prefix=buckets.public_bg_videos_prefix,
                                      expiry_time=3600)
        
        print(actual)
        
        self.assertIsNotNone(actual)
        
    def test_create_folder(self):
        result = self.s3.create_folder(folder_name="5050",
                                       bucket_name=buckets.bg_videos,
                                       prefix=buckets.private_bg_prefix)
        
        self.assertTrue(result)
    
    def tearDown(self):
        self.s3.dispose_temp_files()

if __name__ == '__main__':
    unittest.main()