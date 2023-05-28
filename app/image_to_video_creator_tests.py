from VideoEditor import MediaAdder
from content_generation import ImageToVideoCreator, ImageEvaluator, FullScreenImageSelector
import unittest
import os
import subprocess

root = "../test_material/"

RAW_VIDEO_FOLDER = f"{root}raw_videos/"
INPUT_FOLDER = f"{root}InputVideos/"
AUDIO_EXTRACTIONS_PATH = f"{root}audio_extractions/"
IMAGE_FOLDER = f"{root}images/"
IMAGE_2_VIDEOS_FOLDER = f"{root}videos_made_from_images/"
OUTPUT_FOLDER = f"{root}OutputVideos/"
ORIGINAL_INPUT_FOLDER = f"{root}InputVideos/"
CHROME_DRIVER_PATH = f"{root}content_generator/chromedriver.exe"
RESIZED_FOLDER = f"{root}resized_original_videos/"
VIDEOS_WITH_OVERLAYED_MEDIA_PATH = f"{root}media_added_videos/"
QUERY_FOLDER = f'{root}queries/'
INPUT_INFO_FOLDER = f'{root}input_info.csv'
VIDEO_INFO_FOLDER = f"{root}video_info/"
GENERATED_PROMPTS_FOLDER = f"{root}generated_prompts/"

VERTICAL_VIDEO_HEIGHT = 1920
VERTICAL_VIDEO_WIDTH = 1080
PERECENT_OF_IMAGES_TO_BE_FULLSCREEN = 1
       
def test_full_usage():
    image_evaluator = ImageEvaluator(IMAGE_FOLDER)
    
    VERTICAL_VIDEO_WIDTH, VERTICAL_VIDEO_HEIGHT = image_evaluator.get_video_dimensions(INPUT_FOLDER + 'JordanClip_15.mp4')
    
    print(f"VERTICAL_VIDEO_WIDTH: {VERTICAL_VIDEO_WIDTH}")
    print(f"VERTICAL_VIDEO_HEIGHT: {VERTICAL_VIDEO_HEIGHT}")
    
    fullscreen_selector = FullScreenImageSelector(IMAGE_FOLDER,
                                                  image_evaluator)
    
    
    image_to_video_creator = ImageToVideoCreator(IMAGE_FOLDER,
                                                IMAGE_2_VIDEOS_FOLDER,
                                                image_evaluator)
    media_adder = MediaAdder(INPUT_FOLDER,
                             OUTPUT_FOLDER,
                             IMAGE_2_VIDEOS_FOLDER,
                             OUTPUT_FOLDER)
    
    images = [{'start_time': 2,
                'end_time': 5,
                'image': 'soccer_teammates_celebrating_after_scoring_a_goal_0.jpg'},
                {'start_time': 7,
                'end_time': 10,
                'image': 'team_celebrating_after_scoring_a_goal_0.jpg'},
                {'start_time': 12,
                'end_time': 15,
                'image': 'team_celebration_after_scoring_a_goal_2.jpg'}]
    
    images = fullscreen_selector.choose_fullscreen_images(images,
                                                        VERTICAL_VIDEO_WIDTH,
                                                        VERTICAL_VIDEO_HEIGHT,
                                                        VERTICAL_VIDEO_WIDTH,
                                                        int(VERTICAL_VIDEO_HEIGHT/2),
                                                        percent_of_images_to_be_fullscreen=PERECENT_OF_IMAGES_TO_BE_FULLSCREEN)
    
    #print current working directory
    print(os.getcwd())
    
    for image in images:
        if not os.path.exists(IMAGE_FOLDER + image['image']):
            print(f"Error: {IMAGE_FOLDER + image['image']} does not exist. Stopping program.")
            return
    
    video_data = image_to_video_creator.convert_to_videos(images)
    if video_data == None:
        print("Error: Images were not found. Stopping program.")
        return 
        
    
    original_clip = {'file_name': 'JordanClip_15.mp4',
                     'end_time_sec': 15,
                     'start_time_sec': 0}
    
    print("video_data:" + str(video_data))
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\nStarting media_adder.add_videos_to_original_clip\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    output = media_adder.add_videos_to_original_clip(original_clip=original_clip,
                                       videos=video_data,
                                       original_clip_width=media_adder.YOUTUBE_SHORT_WIDTH,
                                       original_clip_height=media_adder.YOUTUBE_SHORT_HALF_HEIGHT * 2)
    
    print(str(output))


# def test_cropped_images_are_correct_sizes():
#     after_crop_data = [
#         {'image': 'pizza_cropped.jpg', 'start_time': 0.0, 'end_time': 8},
#         {'image': 'biebs_cropped.jpg', 'start_time': 10, 'end_time': 18}
#     ]
#     imageToVideoCreator = ImageToVideoCreator(IMAGE_FOLDER, IMAGE_2_VIDEOS_FOLDER)
    
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
