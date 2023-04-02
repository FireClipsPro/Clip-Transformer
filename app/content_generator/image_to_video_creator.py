import subprocess
import os
import moviepy.editor as mp
import math
from PIL import Image
import numpy
import logging
from moviepy.video.fx.all import *
from moviepy.video.io.VideoFileClip import VideoFileClip
import shutil

logging.basicConfig(level=logging.INFO)

YOUTUBE_SHORT_ASPECT_RATIO = 9/16
YOUTUBE_SHORT_HALF_HEIGHT = 960
YOUTUBE_SHORT_WIDTH = 1080
PERCENT_OF_DISPLAY_SCREEN = 0.95
ZOOM_EFFECT = 'zoom'
HORIZONTAL_SCROLL_EFFECT = 'horizontal_scroll'
VERTICAL_SCROLL_EFFECT = 'vertical_scroll'
SPEED_COEFFICIENT = 0.1


class ImageToVideoCreator:
    def __init__(self,
                 image_file_path,
                 video_2_image_file_path,
                 frame_width=YOUTUBE_SHORT_WIDTH,
                 frame_height=YOUTUBE_SHORT_HALF_HEIGHT):

        self.image_file_path = image_file_path
        self.video_2_image_file_path = video_2_image_file_path
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.x_scroll_speed = 200
        self.y_scroll_speed = 200
        print("ImageToVideoCreator created")
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# takes in the file name (with extension) of the image and the start and end time of the image in the video
# make the video slowly zooming in on the center of the picture
    def animate_image(self, image, input_file, output_file, effect):
        input_file_path = input_file
        
        output_file_path = self.video_2_image_file_path + output_file
        # throw error if the input file does not exist
        if not os.path.exists(input_file_path):
            print("Input file does not exist")
            return
        
        # delete the output file if it exists
        if os.path.exists(output_file):
            os.remove(output_file)
        
        if image is None:
            # throw error
            print("Image is None")
            return
        else:
            size = (image["width"], image["height"])
            
        duration = image["end_time"] - image["start_time"]
        
        #todo expirement with removing resize
        slide = mp.ImageClip(input_file_path).set_fps(25).set_duration(duration)
        
        # if effect is zoom in
        if effect == ZOOM_EFFECT:
            slide = self.zoom_in_effect(slide, 0.05)
        if effect == VERTICAL_SCROLL_EFFECT:
            slide = self.vertical_scroll(slide, image, self.frame_height)
            slide = crop(slide, x_center=0.5 * image['width'],
                     y_center=0.5 * image['height'],
                     width=image['width'],
                     height=self.frame_height)
        if effect == HORIZONTAL_SCROLL_EFFECT:
            slide = self.horizontal_scroll(slide, image, self.frame_width)
            slide = crop(slide, x_center=0.5 * image['width'],
                     y_center=0.5 * image['height'],
                     width=self.frame_width,
                     height=image['height'])
        
        slide.write_videofile(output_file_path)
        
        # find the dimensions of the output file
        image['width'], image['height'] = self.get_image_dimensions(output_file_path)
        
        print(f'Created video for {image["image"]}')
        print(f'Dimensions: {image["width"]}x{image["height"]}')
        image['video_file_name'] = output_file
        return image
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def zoom_in_effect(self, clip, zoom_ratio=0.04):
        def effect(get_frame, t):
            img = Image.fromarray(get_frame(t))
            base_size = img.size

            new_size = [
                math.ceil(img.size[0] * (1 + (zoom_ratio * t))),
                math.ceil(img.size[1] * (1 + (zoom_ratio * t)))
            ]

            # The new dimensions must be even.
            new_size[0] = new_size[0] + (new_size[0] % 2)
            new_size[1] = new_size[1] + (new_size[1] % 2)

            img = img.resize(new_size, Image.LANCZOS)

            x = math.ceil((new_size[0] - base_size[0]) / 2)
            y = math.ceil((new_size[1] - base_size[1]) / 2)

            img = img.crop([
                x, y, new_size[0] - x, new_size[1] - y
            ]).resize(base_size, Image.LANCZOS)

            result = numpy.array(img)
            img.close()

            return result

        return clip.fl(effect)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    def process_images(self, images):
        if images == None:
            return None
        
        #for each image in the list of images
        for image in images:
            #todo make each one a png
            image = self.record_image_size(image)
            image = self.resize_and_animate_image(image, YOUTUBE_SHORT_WIDTH, YOUTUBE_SHORT_HALF_HEIGHT)
            image = self.add_border(image)
        return images
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def add_border(self, animated_image):
        animated_image_file = f'{self.video_2_image_file_path}{animated_image["video_file_name"]}'
        animated_image_output_file = f'{self.video_2_image_file_path}{animated_image["video_file_name"][:-4]}_border.mp4'
        
        clip = VideoFileClip(animated_image_file)

        border_size = 10
        border_color = (255, 255, 0)  # Yellow color in RGB format
        bordered_clip = margin(clip,
                               left=border_size, 
                               right=border_size, 
                               top=border_size, 
                               bottom=border_size, 
                               color=border_color)
        
        bordered_clip.write_videofile(animated_image_output_file)
        
        # delete the old input file
        if os.path.exists(animated_image_file):
            os.remove(animated_image_file)
        
        # rename the output file to the input file
        os.rename(animated_image_output_file, animated_image_file)

        return animated_image
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def resize_and_animate_image(self,
                      image,
                      frame_width,
                      frame_height):
        logging.info(f'image_file_path: {self.image_file_path}')
        logging.info(f'image file name: {image["image"]}')
        image_path = self.image_file_path + image["image"]
        resized_image_path = f'{self.image_file_path}{image["image"][:-4]}_cropped.jpg'
        animated_image_filename = f'{image["image"][:-4]}.mp4'
        image['video_file_name'] = animated_image_filename
        
        if os.path.exists(resized_image_path):
            os.remove(resized_image_path)
        
        # if the image is already the correct size, don't crop it
        if image['width'] == frame_width and image['height'] == frame_height:
            logging.info(f'Image {image["image"]} is already the correct size.')
            image = self.animate_image(image, image_path, animated_image_filename, ZOOM_EFFECT)
        # if the image is too small enlarge it
        elif image['width'] < frame_width and image['height'] < frame_height:
            logging.info(f'Image {image["image"]} is too small to crop. enlarging instead.')
            image = self.enlarge_image(image, image_path, resized_image_path, frame_width, frame_height)
            image = self.animate_image(image, resized_image_path, animated_image_filename, ZOOM_EFFECT)
        # if the image is too tall use a vertical scroll
        elif image['width'] * 3 <= image['height']:
            logging.info(f'Image {image["image"]} is too tall to crop. scrolling instead.')
            image = self.shrink_image(image, image_path, resized_image_path, frame_width, frame_height)
            image = self.animate_image(image, resized_image_path, animated_image_filename, VERTICAL_SCROLL_EFFECT)
        # if the image is too wide use a horizontal scroll
        elif image['height'] * 3 <= image['width']:
            logging.info(f'Image {image["image"]} is too wide to crop. scrolling instead.')
            image = self.shrink_image(image, image_path, resized_image_path, frame_width, frame_height)
            image = self.animate_image(image, resized_image_path, animated_image_filename, HORIZONTAL_SCROLL_EFFECT)
        # if the image is too tall and too wide shrink it
        else:
            logging.info(f'Image {image["image"]} is too large to crop. Shrinking instead.')
            image = self.shrink_image(image, image_path, resized_image_path, frame_width, frame_height)
            image = self.animate_image(image, resized_image_path, animated_image_filename, ZOOM_EFFECT)
        
        return image
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def shrink_image(self, image, input_file, output_file, frame_width, frame_height):
        print(f'Image {image["image"]} is too large to crop. Shrinking instead.')
        # delete output file if it exists
        if os.path.exists(output_file):
            os.remove(output_file)
        
        new_width = image['width']
        new_height = image['height']

        if new_width > frame_width:
            new_width = frame_width * PERCENT_OF_DISPLAY_SCREEN
            new_height = int(image['height'] * (frame_width / image['width']))
            
        if new_height > frame_height:
            new_height = frame_height * PERCENT_OF_DISPLAY_SCREEN
            new_width = int(image['width'] * (frame_height / image['height']))
        
        # Create and Run the command to shrink the image
        command = [
            'ffmpeg',
            '-i', input_file,
            '-vf', f'scale={new_width}:{new_height}',
            '-c:a', 'copy',
            output_file
        ]
        subprocess.run(command)
        
        # replace the old image widths and heights
        image['width'] = new_width
        image['height'] = new_height
        
        return image
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    def enlarge_image(self, image, image_path, enlarged_image_path, frame_width, frame_height):
        print(f'Image {image["image"]} is too small to crop. enlarging instead.')
        
        scale_factor = 1
        if image['width'] > image['height']:
            scale_factor = frame_width * PERCENT_OF_DISPLAY_SCREEN / image['width']
        else:
            scale_factor = frame_height * PERCENT_OF_DISPLAY_SCREEN / image['height']
        
        new_height = int(image['height'] * scale_factor)
        new_width = int(image['width'] * scale_factor)
        
        command = [
            'ffmpeg',
            '-i', image_path,
            '-vf', f'scale={new_width}:{new_height}',
            '-c:a', 'copy',
            enlarged_image_path
        ]
        
        subprocess.run(command)
        
        # replace the old image widths and heights
        image['width'] = new_width
        image['height'] = new_height
        return image
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def horizontal_scroll(self, slide, image, frame_width):
    # Retrieve image dimensions
        img_height = image["height"]
        image_duration = image["end_time"] - image["start_time"]
        # speed is pixels / 0.1 * second (centisecond)
        scroll_speed = SPEED_COEFFICIENT * image["width"] / image_duration
        
        # Apply the scroll effect with the desired width and height
        modified_slide = scroll(
            slide,
            h=img_height,
            w=frame_width,
            x_speed=scroll_speed,
            y_speed=0,
            x_start=0,
            y_start=0,
            apply_to='mask'
        )

        return modified_slide
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def vertical_scroll(self, slide, image, frame_height):
    # Retrieve image dimensions
        img_width = image["width"]
        image_duration = image["end_time"] - image["start_time"]
        # speed is pixels / 0.1 * second (centisecond)
        scroll_speed = SPEED_COEFFICIENT * image["width"] / image_duration
        
        # Apply the scroll effect with the desired width and height
        modified_slide = scroll(
            slide,
            h=frame_height,
            w=img_width,
            x_speed=0,
            y_speed=scroll_speed,  # Set y_speed to a non-zero value for vertical scrolling
            x_start=0,
            y_start=0,
            apply_to='mask'
        )

        return modified_slide
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def record_image_size(self, image):
        image['width'], image['height'] = self.get_image_dimensions(self.image_file_path + image['image'])
        logging.info(f'Image {image["image"]} is {image["width"]}x{image["height"]}')
        return image
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def get_image_dimensions(self, file_path):
        command = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            '-of', 'csv=s=x:p=0',
            f'{file_path}'
        ]
        # if file does not exist, skip it
        if not os.path.exists(f'{file_path}'):
            print(f'ERROR: File {file_path} does not exist')
            return None
            
        output = subprocess.run(command, stdout=subprocess.PIPE)
        output = output.stdout.decode('utf-8').split('x')
        return int(output[0]), int(output[1])
       
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# root = "./app/"
# IMAGE_FILE_PATH = f"{root}media_storage/images/"
# IMAGE_2_VIDEOS_FILE_PATH = f"{root}media_storage/videos_made_from_images/"

# creator = ImageToVideoCreator(IMAGE_2_VIDEOS_FILE_PATH,
#                               IMAGE_2_VIDEOS_FILE_PATH)

# image_to_video_creator = ImageToVideoCreator(IMAGE_FILE_PATH,
#                                             IMAGE_2_VIDEOS_FILE_PATH)
# time_stamped_images = [{'start_time': 0, 'end_time': 5, 'image': 'wide.jpg'},
#                        {'start_time': 0, 'end_time': 5, 'image': 'tall_speed200.jpg'}]
# time_stamped_images = [{'start_time': 0, 'end_time': 5, 'image': 'skill_challenge_for_reasonable_success.jpg'}]
# video_data = image_to_video_creator.process_images(time_stamped_images)