import logging
import unittest

from  content_generation import FullScreenImageSelector

class FullScreenImageSelectorTest(unittest.TestCase):

    def setUp(self):
        self.image_folder_path = "path/to/images"
        self.selector = FullScreenImageSelector(self.image_folder_path)

    def test_choose_fullscreen_images(self):
        images = [
            {"name": "image1.jpg", "height": 900, "width": 600},
        ]
        screen_width = 1920
        screen_height = 1080
        overlay_zone_width = 400
        overlay_zone_height = 300
        percent_of_images_to_be_fullscreen = .51

        expected_fullscreen_images = [
            {"name": "image1.jpg","fullscreen": True, "overlay_zone_width": screen_width, "overlay_zone_height": screen_height},

        ]

        selected_images = self.selector.choose_fullscreen_images(images, screen_width, screen_height, overlay_zone_width, overlay_zone_height, percent_of_images_to_be_fullscreen)

        
        
        self.assertEqual(len(selected_images), len(expected_fullscreen_images))
        for selected, expected in zip(selected_images, expected_fullscreen_images):
            self.assertEqual(selected["name"], expected["name"])
            self.assertEqual(selected["fullscreen"], expected["fullscreen"])
            self.assertEqual(selected["overlay_zone_width"], expected["overlay_zone_width"])
            self.assertEqual(selected["overlay_zone_height"], expected["overlay_zone_height"])

if __name__ == "__main__":
    unittest.main()
