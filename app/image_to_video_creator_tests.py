from VideoEditor import MediaAdder
from content_generation import ImageToVideoCreator

import unittest
import os
import subprocess

root = "../media_storage/"

RAW_VIDEO_FILE_PATH = f"{root}raw_videos/"
INPUT_FILE_PATH = f"{root}InputVideos/"
AUDIO_EXTRACTIONS_PATH = f"{root}audio_extractions/"
IMAGE_FILE_PATH = f"{root}images/"
IMAGE_2_VIDEOS_FILE_PATH = f"{root}videos_made_from_images/"
OUTPUT_FILE_PATH = f"{root}OutputVideos/"
ORIGINAL_INPUT_FILE_PATH = f"{root}InputVideos/"
CHROME_DRIVER_PATH = f"{root}content_generator/chromedriver.exe"
RESIZED_FILE_PATH = f"{root}resized_original_videos/"
VIDEOS_WITH_OVERLAYED_MEDIA_PATH = f"{root}media_added_videos/"
QUERY_FILE_PATH = f'{root}queries/'
INPUT_INFO_FILE_PATH = f'{root}input_info.csv'
VIDEO_INFO_FILE_PATH = f"{root}video_info/"
GENERATED_PROMPTS_FILE_PATH = f"{root}generated_prompts/"
       
def test_full_usage():

    image_to_video_creator = ImageToVideoCreator(IMAGE_FILE_PATH,
                                                IMAGE_2_VIDEOS_FILE_PATH)
    time_stamped_images = [
                           {'start_time': 15, 'end_time': 20, 'image': 'tall.jpg'}]
    
    
    video_data = image_to_video_creator.convert_to_videos(time_stamped_images)
    if video_data == None:
        print("Error: Images were not found. Stopping program.")
        return
        
    # media_adder = MediaAdder(ORIGINAL_INPUT_FILE_PATH,
    #                          OUTPUT_FILE_PATH,
    #                          IMAGE_2_VIDEOS_FILE_PATH,
    #                          OUTPUT_FILE_PATH)
    
    # output = media_adder.add_videos_to_original_clip(original_clip='JordanClip_(0, 0)_(0, 10)_centered.mp4',
    #                                    videos=video_data,
    #                                    original_clip_width=media_adder.YOUTUBE_SHORT_WIDTH,
    #                                    original_clip_height=media_adder.YOUTUBE_SHORT_HALF_HEIGHT * 2,
    #                                    overlay_zone_width=media_adder.YOUTUBE_SHORT_OVERLAY_ZONE_WIDTH,
    #                                    overlay_zone_height=media_adder.YOUTUBE_SHORT_OVERLAY_ZONE_HEIGHT,
    #                                    overlay_zone_x=media_adder.YOUTUBE_SHORT_OVERLAY_ZONE_X,
    #                                    overlay_zone_y=media_adder.YOUTUBE_SHORT_OVERLAY_ZONE_Y)
    
    # print(str(output))


# def test_cropped_images_are_correct_sizes():
#     after_crop_data = [
#         {'image': 'pizza_cropped.jpg', 'start_time': 0.0, 'end_time': 8},
#         {'image': 'biebs_cropped.jpg', 'start_time': 10, 'end_time': 18}
#     ]
#     imageToVideoCreator = ImageToVideoCreator(IMAGE_FILE_PATH, IMAGE_2_VIDEOS_FILE_PATH)
    
#     before_crop_data = [
#         {'image': 'pizza.jpg', 'start_time': 0.0, 'end_time': 8},
#         {'image': 'biebs.jpg', 'start_time': 10, 'end_time': 18}
#     ]
    
#     after = imageToVideoCreator.find_image_sizes(after_crop_data)
#     before = imageToVideoCreator.find_image_sizes(before_crop_data)
    
#     # print the before and after names and sizes
#     print('Images must fit in a 1080x960 frame. If not, they will be cropped.')
#     for i in range(len(after)):
#         print(f'{before[i]["image"]}: {before[i]["width"]}x{before[i]["height"]}')
#         print(f'{after[i]["image"]}: {after[i]["width"]}x{after[i]["height"]}')
    
    

# test_cropped_images_are_correct_sizes()

test_full_usage()
