import subprocess
import os
import moviepy.editor as mp
import math
from PIL import Image
import numpy
import logging
import moviepy.video.fx.all as vfx
from moviepy.video.io.VideoFileClip import VideoFileClip
import shutil
import time

logging.basicConfig(level=logging.INFO)

YOUTUBE_SHORT_ASPECT_RATIO = 9/16
YOUTUBE_SHORT_HALF_HEIGHT = 960
YOUTUBE_SHORT_WIDTH = 1080
PERCENT_OF_DISPLAY_SCREEN = 0.90
ZOOM_EFFECT = 'zoom'
HORIZONTAL_SCROLL_EFFECT = 'horizontal_scroll'
VERTICAL_SCROLL_EFFECT = 'vertical_scroll'
HORIZONTAL_SPEED_COEFFICIENT = .714
VERTICAL_SPEED_COEFFICIENT = .6
FAST_SPEED = 'fast'
SLOW_SPEED = 'slow'


class ImageToVideoCreator:
    def __init__(self,
                 image_folder,
                 image_2_videos_folder,
                 image_evaluator,
                 frame_width=YOUTUBE_SHORT_WIDTH,
                 frame_height=YOUTUBE_SHORT_HALF_HEIGHT):

        self.image_file_path = image_folder
        self.video_2_image_file_path = image_2_videos_folder
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.x_scroll_speed = 200
        self.y_scroll_speed = 200
        self.image_evaluator = image_evaluator
        self.__last_used_color = None
        self.zoom_in_was_last_used = False
        logging.info("ImageToVideoCreator created")
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def convert_to_videos(self, 
                          images,
                          border_colors,
                          frame_width,
                          frame_height,
                          zoom_speed):
        self.frame_width = int(math.floor(frame_width * .9))
        self.frame_height = int(math.floor(frame_height * .9))
        
        if images == None:
            return None
        
        #for each image in the list of images
        for image in images:
            video_file_name = f'{image["image"][:-4]}.mp4'
            if os.path.exists(self.video_2_image_file_path + video_file_name):
                logging.info(f'Video for {image["image"]} already exists.')
                image['width'], image['height'] = self.image_evaluator.get_video_dimensions(self.video_2_image_file_path + video_file_name)
                image['video_file_name'] = video_file_name
                continue
            
            image = self.record_image_size(image)
            image = self.resize_and_animate_image(image,
                                                  image['overlay_zone_width'],
                                                  image['overlay_zone_height'],
                                                  zoom_speed)
            image = self.add_border(image, border_colors)
            image = self.record_image_size(image)
            
        self.__last_used_color = None
        
        return images
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def initialize_output_path(self, output_file):
        # delete the output file if it exists
        if os.path.exists(output_file):
            os.remove(output_file)
        
        return os.path.abspath(self.video_2_image_file_path + output_file)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def animate_image(self, image, input_file_path, output_file, effect, zoom_speed):
        logging.info(f'Animating {image["image"]}')
        
        output_file_path = self.initialize_output_path(output_file)

        if self.files_do_not_exist(input_file_path, output_file, image):
            return
            
        duration = image["end_time"] - image["start_time"]
        
        slide = mp.ImageClip(input_file_path).set_fps(25).set_duration(duration)
        
        # if effect is zoom in
        if effect == ZOOM_EFFECT:
            if zoom_speed == FAST_SPEED:
                speed_factor = 0.05
            elif zoom_speed == SLOW_SPEED:
                speed_factor = 0.025
            
            if self.zoom_in_was_last_used:
                logging.info(f' Zooming out on {image["image"]}')
                slide = self.zoom_out_effect(slide, speed_factor)
                self.zoom_in_was_last_used = False
            else:
                logging.info(f'Zooming in on {image["image"]}')
                slide = self.zoom_in_effect(slide, speed_factor)
                self.zoom_in_was_last_used = True
            

        slide.write_videofile(output_file_path, threads=4)
        
        #check if the output file exists
        if not os.path.exists(os.path.abspath(output_file_path)):
            raise Exception("Output file was not created")
        
        # find the dimensions of the output file
        image['width'], image['height'] = self.image_evaluator.get_video_dimensions(output_file_path)
        
        logging.info(f'Created video for {image["image"]}')
        logging.info(f'Dimensions: {image["width"]}x{image["height"]}')
        image['video_file_name'] = output_file
        return image
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def zoom_out_effect(self, clip, speed_factor=0.04):
        duration = clip.duration

        def effect(get_frame, t):
            img = Image.fromarray(get_frame(t))
            base_size = img.size

            # Calculate the amount of zoom we should have at the start of the clip.
            max_zoom = 1 + speed_factor * duration

            # Calculate how much we should zoom out over time.
            # This value will decrease from max_zoom to 1 as t goes from 0 to duration.
            current_zoom = max_zoom - (speed_factor * t)

            # Calculate the size of the region of the original image we will show based on the current zoom level.
            crop_size = [
                math.floor(base_size[0] / current_zoom),
                math.floor(base_size[1] / current_zoom)
            ]
            
            # The crop dimensions must be even.
            crop_size[0] = crop_size[0] + (crop_size[0] % 2)
            crop_size[1] = crop_size[1] + (crop_size[1] % 2)

            # Calculate the top-left coordinates for cropping the center of the image.
            x = math.ceil((base_size[0] - crop_size[0]) / 2)
            y = math.ceil((base_size[1] - crop_size[1]) / 2)

            # Crop the image.
            img = img.crop([x, y, x + crop_size[0], y + crop_size[1]])

            # Resize the cropped image back to the original dimensions, creating the zoom-out effect.
            img = img.resize(base_size, Image.LANCZOS)

            result = numpy.array(img)
            img.close()

            return result

        return clip.fl(effect)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def files_do_not_exist(self, input_file_path, output_file, image):
        # throw error if the input file does not exist
        if not os.path.exists(input_file_path):
            logging.info("Input file does not exist")
            return True
        
        if image is None:
            # throw error
            logging.info("Image is None")
            return True
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def zoom_in_effect(self, clip, zoom_speed=0.04):
        def effect(get_frame, t):
            img = Image.fromarray(get_frame(t))
            base_size = img.size

            new_size = [
                math.ceil(img.size[0] * (1 + (zoom_speed * t))),
                math.ceil(img.size[1] * (1 + (zoom_speed * t)))
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
    def add_border(self, animated_image, border_colors):
        animated_image_file = f'{self.video_2_image_file_path}{animated_image["video_file_name"]}'
        animated_image_output_file = f'{self.video_2_image_file_path}{animated_image["video_file_name"][:-4]}_border.mp4'
        
        clip = VideoFileClip(animated_image_file)

        border_size = 10
        
        if self.__last_used_color == None:
            border_color = border_colors[0]
        elif len(border_colors) > 1:
            #scroll through the list of colors
            border_color = border_colors[(border_colors.index(self.__last_used_color) + 1) % len(border_colors)]
        else:
            border_color = border_colors[0]
            
        self.__last_used_color = border_color
        
        logging.info(f'Border color: {border_color}')
        bordered_clip = vfx.margin(clip,
                               left=border_size, 
                               right=border_size, 
                               top=border_size, 
                               bottom=border_size, 
                               color=border_color)
        
        bordered_clip.write_videofile(animated_image_output_file, threads=4)
        
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
                      frame_height,
                      zoom_speed):
        logging.info(f'image_file_path: {self.image_file_path}')
        logging.info(f'image file name: {image["image"]}')
        image_path = self.image_file_path + image["image"]
        resized_image_path = f'{self.image_file_path}{image["image"][:-4]}_cropped.jpg'
        animated_image_filename = f'{image["image"][:-4]}.mp4'
        image['video_file_name'] = animated_image_filename
        
        if os.path.exists(resized_image_path):
            os.remove(resized_image_path)
            # return image
        if os.path.exists(self.video_2_image_file_path + animated_image_filename):
            os.remove(self.video_2_image_file_path + animated_image_filename)
            # return image
            
        logging.info(f'image dimensions: {image["width"]}x{image["height"]}')
        # if the image is already the correct size, don't crop it
        if image['width'] == frame_width and image['height'] == frame_height:
            logging.info(f'Image {image["image"]} is already the correct size.')
            image = self.animate_image(image, image_path, animated_image_filename, ZOOM_EFFECT, zoom_speed)
        # if the image is too small enlarge it
        elif image['width'] < frame_width and image['height'] < frame_height:
            logging.info(f'Image {image["image"]} is too small to crop. enlarging instead.')
            image = self.enlarge_image(image, image_path, resized_image_path, frame_width, frame_height)
            image = self.animate_image(image, resized_image_path, animated_image_filename, ZOOM_EFFECT, zoom_speed)
        # if the image is too tall use a vertical scroll
        elif image['width'] * 2 <= image['height']:
            logging.info(f'Image {image["image"]} is too tall to crop. scrolling instead.')
            image = self.shrink_image_width(image, image_path, resized_image_path, frame_width, frame_height)
            image = self.scroll_image_vertically(image, resized_image_path, animated_image_filename)
        # if the image is too wide use a horizontal scroll
        elif image['height'] * 2.5 <= image['width']:
            logging.info(f'Image {image["image"]} is too wide to crop. scrolling instead.')
            image = self.shrink_image_height(image, image_path, resized_image_path, frame_width, frame_height)
            image = self.scroll_image_horizontally(image, resized_image_path, animated_image_filename)
        # if the image is too tall and too wide shrink it
        else:
            logging.info(f'Image {image["image"]} is too large to crop. Shrinking instead.')
            image = self.shrink_image(image, image_path, resized_image_path, frame_width, frame_height)
            image = self.animate_image(image, resized_image_path, animated_image_filename, ZOOM_EFFECT, zoom_speed)
        
        return image
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    
    def scroll_image_horizontally(self, image, resized_image_path, animated_image_filename):
        image_duration = image["end_time"] - image["start_time"]
        # speed is pixels / 0.1 * second (centisecond)
        scroll_speed = math.ceil((image["width"] - self.frame_width * PERCENT_OF_DISPLAY_SCREEN) / image_duration) 
        
        image_clip = mp.ImageClip(resized_image_path, duration=image_duration)
        image_clip = image_clip.set_position(lambda t: (t * (-scroll_speed), 'center'))
        image_clip.fps = 30
        composite = mp.CompositeVideoClip([image_clip], size=image_clip.size)
        # Crop the composite clip
        composite = composite.fx(vfx.crop, x1=0, y1=0, width=(self.frame_width * PERCENT_OF_DISPLAY_SCREEN), height=image["height"])

        output_path = self.initialize_output_path(animated_image_filename)
        composite.write_videofile(output_path, threads=4)
        
        # find the dimensions of the output file
        image['width'], image['height'] = self.image_evaluator.get_video_dimensions(output_path)
        
        logging.info(f'Created video for {image["image"]}')
        logging.info(f'Dimensions: {image["width"]}x{image["height"]}')
        image['video_file_name'] = animated_image_filename
        return image
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def scroll_image_vertically(self, image, resized_image_path, animated_image_filename):
        image_duration = image["end_time"] - image["start_time"]

        scroll_speed = math.ceil((image["height"] - self.frame_height * PERCENT_OF_DISPLAY_SCREEN) / image_duration)
        
        image_clip = mp.ImageClip(resized_image_path, duration=image_duration)
        image_clip = image_clip.set_position(lambda t: ('center', t * (-scroll_speed)))
        image_clip.fps = 30
        composite = mp.CompositeVideoClip([image_clip], size=image_clip.size)
        # Crop the composite clip
        composite = composite.fx(vfx.crop, x1=0, y1=0, width=image["width"], height=(self.frame_height * PERCENT_OF_DISPLAY_SCREEN))

        output_path = self.initialize_output_path(animated_image_filename)
        composite.write_videofile(output_path, threads=4)
        
        # find the dimensions of the output file
        image['width'], image['height'] = self.image_evaluator.get_video_dimensions(output_path)
        
        logging.info(f'Created video for {image["image"]}')
        logging.info(f'Dimensions: {image["width"]}x{image["height"]}')
        image['video_file_name'] = animated_image_filename
        return image
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def shrink_image(self, image, input_file, output_file, frame_width, frame_height):
        logging.info(f'Shrinking image to fit in {frame_width}x{frame_height} frame.')
        # delete output file if it exists
        if os.path.exists(output_file):
            os.remove(output_file)
        
        new_width = image['width']
        new_height = image['height']

        if new_width > frame_width:
            new_width = frame_width * PERCENT_OF_DISPLAY_SCREEN
            new_height = int(image['height'] * (new_width / image['width']))
            
        if new_height > frame_height:
            new_height = frame_height * PERCENT_OF_DISPLAY_SCREEN
            new_width = int(image['width'] * (new_height / image['height']))
        
        # Create and Run the command to shrink the image
        command = [
            'ffmpeg',
            '-i', input_file,
            '-vf', f'scale={new_width}:{new_height}',
            '-c:a', 'copy',
            output_file
        ]
        subprocess.run(command)
        
        logging.info(f'new image dimensions: {new_width}x{new_height}')
        logging.info(f'saved image to: {output_file}')
        
        # replace the old image widths and heights
        image['width'] = new_width
        image['height'] = new_height
        
        return image
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def shrink_image_width(self, image, input_file, output_file, frame_width, frame_height):
        logging.info(f'Shrinking image width.')
        # delete output file if it exists
        if os.path.exists(output_file):
            os.remove(output_file)
        
        new_width = image['width']
        new_height = image['height']

        if new_width > frame_width:
            new_width = frame_width * PERCENT_OF_DISPLAY_SCREEN
            new_height = int(image['height'] * (new_width / image['width']))
        
        # Create and Run the command to shrink the image
        command = [
            'ffmpeg',
            '-i', input_file,
            '-vf', f'scale={new_width}:{new_height}',
            '-c:a', 'copy',
            output_file
        ]
        subprocess.run(command)
        
        logging.info(f'new image dimensions: {new_width}x{new_height}')
        logging.info(f'saved image to: {output_file}')
        
        # replace the old image widths and heights
        image['width'] = new_width
        image['height'] = new_height
        
        return image
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def shrink_image_height(self, 
                            image,
                            input_file,
                            output_file,
                            frame_width,
                            frame_height):
        logging.info(f'Shrinking image height to fit in frame.')
        # delete output file if it exists
        if os.path.exists(output_file):
            os.remove(output_file)
        
        new_width = int(image['width'])
        new_height = int(image['height'])
            
        if new_height > frame_height:
            new_height = int(math.floor(frame_height * PERCENT_OF_DISPLAY_SCREEN))
            new_width = int(math.floor(image['width'] * (new_height / image['height'])))
        
        # Create and Run the command to shrink the image
        command = [
            'ffmpeg',
            '-i', input_file,
            '-vf', f'scale={new_width}:{new_height}',
            '-c:a', 'copy',
            output_file
        ]
        subprocess.run(command)
        
        logging.info(f'new image dimensions: {new_width}x{new_height}')
        logging.info(f'saved image to: {output_file}')
        
        # replace the old image widths and heights
        image['width'] = new_width
        image['height'] = new_height
        
        return image
        
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    def enlarge_image(self, image, image_path, enlarged_image_path, frame_width, frame_height):
        logging.info(f'Image {str(image)} is too small to crop. enlarging instead.')
        
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
        
        logging.info(f"Image enlarged to {new_width}x{new_height}.")
        return image
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def record_image_size(self, image):
        #log working directory
        directory = os.getcwd()
        logging.info(directory)
        # ensure that the file exists
        if not os.path.exists(self.image_file_path + image['image']):
            logging.info(f'ERROR: File {self.image_file_path + image["image"]} does not exist')
            
            
        image['width'], image['height'] = self.get_image_dimensions(self.image_file_path + image['image'])
        logging.info(f'Image {image["image"]} is {image["width"]}x{image["height"]}')
        return image
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def get_image_dimensions(self, file_path):
        if not os.path.exists(file_path):
            raise Exception("File does not exist: " + file_path)
        
        command = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            '-of', 'csv=s=x:p=0',
            f'{file_path}'
        ]
        
        output = subprocess.run(command, stdout=subprocess.PIPE)
        output = output.stdout.decode('utf-8').split('x')
        
        if output[0] == 0 or output[1] == 0:
            raise Exception("Image dimensions are 0 for file path: " + file_path)
        
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