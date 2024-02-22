import unittest
import os
from VideoEditor import BackgroundRemover
import configuration.directories as directories

class BackgroundRemoverTest(unittest.TestCase):
    def setUp(self):
        self.input_video_folder = directories.RESIZED_FOLDER
        self.input_image_folder = directories.BACKGROUND_IMAGE_FOLDER
        self.output_folder = directories.BACKGROUNDLESS_VIDEOS_FOLDER
        self.remover = BackgroundRemover(self.input_video_folder, self.input_image_folder, self.output_folder)

    def test_remove_background(self):
        video = "JordanClip_15.mp4"
        image_to_overlay = "meal.jpg"

        output_video = self.remover.remove_background(video, image_to_overlay)

        # Assert that the output video exists
        self.assertTrue(os.path.exists(output_video))

        # Additional assertions or checks for the output video can be added

    def tearDown(self):
        # Clean up any generated output files
        output_files = os.listdir(self.output_folder)
        # for file in output_files:
        #     file_path = os.path.join(self.output_folder, file)
        #     os.remove(file_path)

if __name__ == "__main__":
    unittest.main()
