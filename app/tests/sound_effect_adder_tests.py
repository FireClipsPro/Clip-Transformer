import unittest
from app.VideoEditor.sound_effect_adder import SoundEffectAdder
import app.configuration.directories as directories
from moviepy.editor import VideoFileClip
import os
import logging

logging.basicConfig(level=logging.INFO)

class TestSoundEffectAdder(unittest.TestCase):
    def setUp(self):
        self.image_sounds_folder = "../media_storage/image_display_sounds/"
        self.video_input_folder = "./test_material/InputVideos/"
        self.output_folder = "./test_material/OutputVideos/"
        
        self.adder = SoundEffectAdder(self.image_sounds_folder, 
                                      self.video_input_folder, 
                                      self.output_folder)

    def test_add_sounds_to_images(self):
        # Suppose we have a list of images with their start and end times in the video
        images = [{'start': 1, 'end': 3},
                  {'start': 4, 'end': 7},
                  {'start': 8, 'end': 10}]
        video = "JordanClip_15.mp4"
        output_video = self.adder.add_sounds_to_images(images, video, True)
        self.assertTrue(os.path.exists(output_video), "Output video does not exist")
        
        # Now we will play the video for the user to manually check
        clip = VideoFileClip(output_video)

if __name__ == "__main__":
    unittest.main()
