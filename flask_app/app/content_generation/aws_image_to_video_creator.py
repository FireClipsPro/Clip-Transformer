import logging
import math
import os
import subprocess

import moviepy.editor as mp
import moviepy.video.fx.all as vfx
import numpy
from moviepy.editor import ImageClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from PIL import Image

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


class AWSImageToVideoCreator:
    def __init__(self,
                 frame_width=YOUTUBE_SHORT_WIDTH,
                 frame_height=YOUTUBE_SHORT_HALF_HEIGHT):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.x_scroll_speed = 200
        self.y_scroll_speed = 200
        self.__last_used_color = None
        self.zoom_in_was_last_used = False
        logging.info("ImageToVideoCreator created")
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def convert_to_videos(self, 
                          images: [ImageClip],
                          border_colors,
                          frame_width,
                          frame_height,
                          zoom_speed):
        self.frame_width = int(math.floor(frame_width * .9))
        self.frame_height = int(math.floor(frame_height * .9))
        
        if images == None:
            return None
        
        animated_images = []
        #for each image in the list of images
        for image in images:
            animated_image = self.resize_and_animate_image(image=image,
                                                            frame_height=frame_height,
                                                            frame_width=frame_width,
                                                            zoom_speed=zoom_speed)
            bordered_image = self.add_border(animated_image, border_colors)
            
            animated_images.append(bordered_image)
            
        self.__last_used_color = None
        
        return animated_images
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def initialize_output_path(self, output_file):
        # delete the output file if it exists
        if os.path.exists(output_file):
            os.remove(output_file)
        
        return os.path.abspath(self.video_2_image_file_path + output_file)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def animate_image(self, 
                      image: ImageClip,
                      effect,
                      zoom_speed) -> ImageClip:
        logging.info("Animating image.")
        slide = image.set_fps(25)
        
        # if effect is zoom in
        if effect == ZOOM_EFFECT:
            if zoom_speed == FAST_SPEED:
                speed_factor = 0.05
            elif zoom_speed == SLOW_SPEED:
                speed_factor = 0.025
            
            if self.zoom_in_was_last_used:
                slide = self.zoom_out_effect(slide, speed_factor)
                self.zoom_in_was_last_used = False
            else:
                slide = self.zoom_in_effect(slide, speed_factor)
                self.zoom_in_was_last_used = True
            
        return slide
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def zoom_out_effect(self, clip: ImageClip, speed_factor=0.04):
        duration = clip.duration
        logging.info(f"Duration: {duration}")
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
    def add_border(self, animated_image: ImageClip, border_colors):
        """
        Adds a colored border to an ImageClip.

        :param animated_image: The ImageClip to which the border will be added.
        :param border_colors: A list of colors to use for the border. Cycles through if called multiple times.
        :return: An ImageClip with the border added.
        """
        border_size = 10
        
        if self.__last_used_color is None:
            border_color = border_colors[0]
        elif len(border_colors) > 1:
            # Scroll through the list of colors
            border_color = border_colors[(border_colors.index(self.__last_used_color) + 1) % len(border_colors)]
        else:
            border_color = border_colors[0]
            
        self.__last_used_color = border_color
        
        logging.info(f'Border color: {border_color}')
        
        # Apply the border to the ImageClip
        animated_image_with_border = animated_image.margin(
            left=border_size, 
            right=border_size, 
            top=border_size, 
            bottom=border_size, 
            color=border_color)

        return animated_image_with_border
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def resize_and_animate_image(self,
                                    image: ImageClip,
                                    frame_width,
                                    frame_height,
                                    zoom_speed):            
        # if the image is already the correct size, don't crop it
        image_width, image_height = image.size
        if image_width == frame_width and image_height == frame_height:
            logging.info('Image is already the correct size.')
            animated_image = self.animate_image(image, ZOOM_EFFECT, zoom_speed)
        # if the image is too small enlarge it
        elif image_width < frame_width and image_height < frame_height:
            logging.info('Image is too small to crop. enlarging instead.')
            image = self.enlarge_image(image, frame_width, frame_height)
            animated_image = self.animate_image(image, ZOOM_EFFECT, zoom_speed)
        # if the image is too tall use a vertical scroll
        # elif image_width * 2 <= image_height:
        #     logging.info(f'Image is too tall to crop. scrolling instead.')
        #     image = self.shrink_image_width(image, frame_width)
        #     image = self.scroll_image_vertically(image)
        # # if the image is too wide use a horizontal scroll
        # elif image_height * 2.5 <= image_width:
        #     logging.info(f'Image is too wide to crop. scrolling instead.')
        #     image = self.shrink_image_height(image, frame_height)
        #     image = self.scroll_image_horizontally(image)
        # if the image is too tall and too wide shrink it
        else:
            logging.info('Image is too large to crop. Shrinking instead.')
            image = self.shrink_image(image, frame_width, frame_height)
            animated_image = self.animate_image(image, ZOOM_EFFECT, zoom_speed)
        
        return animated_image
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
    def shrink_image(self,
                     image: ImageClip, 
                     frame_width: int,
                     frame_height: int) -> ImageClip:
        """
        Shrinks the image to not exceed the specified frame width and height,
        maintaining aspect ratio and considering a percentage of the display screen size.

        :param image: The ImageClip to be resized.
        :param frame_width: The maximum width of the frame to fit the image into.
        :param frame_height: The maximum height of the frame to fit the image into.
        :return: A new ImageClip that has been resized if necessary.
        """
        original_width, original_height = image.size
        new_width, new_height = original_width, original_height

        # Determine scale factors for width and height separately
        width_scale = frame_width * PERCENT_OF_DISPLAY_SCREEN / original_width
        height_scale = frame_height * PERCENT_OF_DISPLAY_SCREEN / original_height
        
        # Use the smaller scale factor to ensure the image fits within both dimensions
        scale_factor = min(width_scale, height_scale)

        # Calculate new dimensions
        new_width = int(math.floor(original_width * scale_factor))
        new_height = int(math.floor(original_height * scale_factor))
        
        # Resize the image using the calculated dimensions
        resized_image = image.resize(newsize=(new_width, new_height))

        return resized_image
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def shrink_image_width(image: ImageClip, frame_width: int) -> ImageClip:
        """
        Shrinks the image width to not exceed the specified frame width,
        maintaining aspect ratio and considering a percentage of the display screen size.

        :param image: The ImageClip to be resized.
        :param frame_width: The maximum width of the frame to fit the image into.
        :return: A new ImageClip that has been resized if necessary.
        """
        original_width, original_height = image.size
        
        # Determine if the width needs to be shrunk
        if original_width > frame_width:
            # Calculate the new width to not exceed the frame_width scaled by PERCENT_OF_DISPLAY_SCREEN
            new_width = int(math.floor(frame_width * PERCENT_OF_DISPLAY_SCREEN))
            # Calculate new height to maintain aspect ratio
            new_height = int(original_height * (new_width / original_width))
            
            # Resize the image using the calculated dimensions
            resized_image = image.resize(newsize=(new_width, new_height))
        else:
            # If resizing is not necessary, return the original image
            resized_image = image

        return resized_image
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def shrink_image_height(image: ImageClip, frame_height: int) -> ImageClip:
        """
        Shrinks the image height to not exceed the specified frame height,
        maintaining aspect ratio and considering a percentage of the display screen size.

        :param image: The ImageClip to be resized.
        :param frame_width: The width of the frame for context (not directly used here).
        :param frame_height: The maximum height of the frame to fit the image into.
        :return: A new ImageClip that has been resized if necessary.
        """
        original_width, original_height = image.size
        
        # Determine if the height needs to be shrunk
        if original_height > frame_height:
            # Calculate the new height and corresponding width to maintain aspect ratio
            new_height = int(math.floor(frame_height * PERCENT_OF_DISPLAY_SCREEN))
            new_width = int(math.floor(original_width * (new_height / original_height)))
            
            # Resize the image using the calculated dimensions
            resized_image = image.resize(newsize=(new_width, new_height))
        else:
            # If resizing is not necessary, return the original image
            resized_image = image

        return resized_image
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    def enlarge_image(self, image: ImageClip, frame_width: int, frame_height: int) -> ImageClip:
        """
        Resizes the image to fit within a specified frame width and height, maintaining aspect ratio.

        :param image: The ImageClip to be resized.
        :param frame_width: The width of the frame to fit the image into.
        :param frame_height: The height of the frame to fit the image into.
        :return: A new ImageClip that has been resized.
        """
        image_width, image_height = image.size

        # Calculate the scale factor to fit the image within the frame dimensions
        # while maintaining the aspect ratio.
        if image_width > image_height:
            scale_factor = frame_width * PERCENT_OF_DISPLAY_SCREEN / image_width
        else:
            scale_factor = frame_height * PERCENT_OF_DISPLAY_SCREEN / image_height

        # Resize the image using the calculated scale factor
        resized_image = image.resize(scale_factor)

        new_width, new_height = resized_image.size
        logging.info(f"Image enlarged to {new_width}x{new_height}.")

        return resized_image