import unittest
from unittest.mock import patch, MagicMock
from moviepy.editor import VideoFileClip, AudioFileClip
from app.services.s3 import S3
import app.configuration.directories as directories
import app.configuration.buckets as buckets
import boto3

class TestS3(unittest.TestCase):
    def setUp(self):
        s3 = boto3.client('s3')
        self.s3 = S3(s3=s3)

    def test_write_videofileclip(self):
        # Call the method under test
        clip = VideoFileClip(directories.VM_BACKGROUNDS + "wormhole.mp4")  # No actual file needed due to mocking
        self.s3.write_videofileclip(clip, 'wormhole', buckets.bg_videos)

    # @patch('tempfile.NamedTemporaryFile')
    # @patch('boto3.client')
    # def test_get_videofileclip(self, mock_s3_client, mock_tempfile):
    #     # Setup mock for download_fileobj to simulate S3 download
    #     mock_s3_client.return_value.download_fileobj = MagicMock()

    #     # Mock the tempfile to simulate video file creation
    #     mock_tempfile.return_value.__enter__.return_value.name = 'temp_video_file.mp4'

    #     # Call the method under test
    #     video_clip = self.s3.get_videofileclip('test_video', 'test_bucket')

    #     # Assertions can be made here regarding the video_clip object
    #     # For simplicity, we'll check the type
    #     self.assertIsInstance(video_clip, VideoFileClip)

    # @patch('tempfile.NamedTemporaryFile')
    # @patch('boto3.client')
    # def test_get_audiofileclip(self, mock_s3_client, mock_tempfile):
    #     # Similar setup and assertions for testing get_audiofileclip
    #     mock_s3_client.return_value.download_fileobj = MagicMock()
    #     mock_tempfile.return_value.__enter__.return_value.name = 'temp_audio_file.mp3'
        
    #     # Call the method under test
    #     audio_clip = self.s3.get_audiofileclip('test_audio', 'test_bucket')

    #     # Assertions
    #     self.assertIsInstance(audio_clip, AudioFileClip)

    # def test_dispose_temp_files(self):
    #     # Test the disposal of temporary files
    #     with patch('os.remove') as mock_remove:
    #         self.s3.temp_files = ['temp_file_1.mp4', 'temp_file_2.mp3']
    #         self.s3.dispose_temp_files()
    #         mock_remove.assert_any_call('temp_file_1.mp4')
    #         mock_remove.assert_any_call('temp_file_2.mp3')
    #         self.assertEqual(self.s3.temp_files, [])

if __name__ == '__main__':
    unittest.main()