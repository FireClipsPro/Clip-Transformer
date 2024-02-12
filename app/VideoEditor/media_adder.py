import os
import subprocess
from moviepy.editor import *
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class MediaAdder:
    def __init__(self,
                 input_video_folder,
                 media_added_vidoes_file_path,
                 image_videos_file_path,
                 final_output_file_path):
        
        self.input_videos_file_path = input_video_folder
        self.output_file_path = media_added_vidoes_file_path
        self.image_videos_file_path = image_videos_file_path
        self.final_output_file_path = final_output_file_path
        
        self.YOUTUBE_SHORT_HEIGHT = 1920
        self.YOUTUBE_SHORT_HALF_HEIGHT = 960
        self.YOUTUBE_SHORT_WIDTH = 1080
        self.YOUTUBE_SHORT_OVERLAY_ZONE_X = 0
        self.YOUTUBE_SHORT_OVERLAY_ZONE_Y = 960
        self.YOUTUBE_SHORT_OVERLAY_ZONE_WIDTH = 1080
        self.YOUTUBE_SHORT_OVERLAY_ZONE_HEIGHT = 960
        
        print("MediaAdder created")
    
    
    #   Videos is a list of dictionaries with the following keys:
    #   video_file_name: the name of the video file to be added
    #   width: the width of the video
    #   height: the height of the video
    #   start_time: the time at which to start adding the video
    #   end_time: the time at which to stop adding the video
    #   Overlay zone is the area of the original clip where the video will be added
    #   x: the x coordinate of the top left corner of the overlay zone
    #   y: the y coordinate of the top left corner of the video
    def add_media_to_video(self,
                                    original_clip,
                                    videos,
                                    original_clip_width,
                                    original_clip_height,
                                    overlay_zone_top_left,
                                    overlay_zone_width,
                                    overlay_zone_height):
        self.log_parameters(original_clip,
                            videos,
                            original_clip_width,
                            original_clip_height)

        # Initialize the input video path
        input_video = self.input_videos_file_path + original_clip['file_name']
        if not os.path.exists(input_video):
            print(f'Input video {input_video} does not exist')
            return None
        
        # if os.path.exists(self.output_file_path + original_clip['file_name']):
        #     print(f'Output video {self.output_file_path + original_clip["file_name"]} already exists')
        #     return original_clip
        
        output_video = None
        background_video = VideoFileClip(input_video)
        composite_clips = [background_video]
        
        # initialize the output video path
        output_video = self.final_output_file_path + original_clip['file_name']
        if os.path.exists(output_video):
            os.remove(output_video)
        
        for video in videos:
            # initialize the overlay video path
            overlay_video_file_name = self.image_videos_file_path + video['video_file_name']
            if not os.path.exists(overlay_video_file_name):
                print(f'Overlay video {overlay_video_file_name} does not exist')
            
            self.add_clip_to_video(original_clip,
                                   composite_clips,
                                   video,
                                   overlay_video_file_name,
                                   overlay_zone_top_left,
                                   overlay_zone_width,
                                   overlay_zone_height)
        
        final_video = CompositeVideoClip(composite_clips)
        final_video.write_videofile(output_video, threads=4)
        
        return original_clip
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def add_clip_to_video(self, 
                          original_clip,
                          composite_clips,
                          video,
                          overlay_video_file_name,
                          overlay_zone_top_left,
                          overlay_zone_width,
                          overlay_zone_height):
        overlay_video = VideoFileClip(overlay_video_file_name)

        overlay_top_left_x, overlay_top_left_y = self.calculate_top_left_xy(overlay_video.w,
                                                                            overlay_video.h,
                                                                            overlay_zone_width,
                                                                            overlay_zone_height,
                                                                            overlay_zone_top_left[0],
                                                                            overlay_zone_top_left[1])
            
            
        end_time = self.get_end_time(original_clip, video)
        overlay_video = overlay_video.set_start(video['start_time']).set_end(end_time)
        overlay_video = overlay_video.set_position((overlay_top_left_x, overlay_top_left_y))
        composite_clips.append(overlay_video)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def get_end_time(self, original_clip, video):
        if video['end_time'] > original_clip['end_time_sec']:
            end_time = original_clip['end_time_sec']
        else:
            end_time = video['end_time']
        return end_time
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def log_parameters(self, original_clip, videos, original_clip_width, original_clip_height):
        logging.info("Logging parameters...")
        logging.info(f"original_clip: {original_clip}")
        logging.info(f"Original clip: {original_clip['file_name']}")
        logging.info(f"Videos: {videos}")
        logging.info(f"Original clip width: {original_clip_width}")
        logging.info(f"Original clip height: {original_clip_height}")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    
    def calculate_top_left_xy(self,
                                 overlay_video_width,
                                 overlay_video_height,
                                 overlay_zone_width,
                                 overlay_zone_height,
                                 overlay_zone_x,
                                 overlay_zone_y):
        # calculate the overlay top left and right

        overlay_video_top_left_x = int(overlay_zone_x + ((overlay_zone_width - overlay_video_width) / 2))
        overlay_video_top_left_y = int(overlay_zone_y + ((overlay_zone_height - overlay_video_height) / 2))
        
        logging.info(f"For video with width: {overlay_video_width} and height: {overlay_video_height}")
        logging.info(f"overlay zone with width: {overlay_zone_width} and height: {overlay_zone_height}")
        logging.info(f"overlay zone with x: {overlay_zone_x} and y: {overlay_zone_y}")
        logging.info(f"overlay_video_top_left_x: {overlay_video_top_left_x}")
        logging.info(f"overlay_video_top_left_y: {overlay_video_top_left_y}")
        
        return overlay_video_top_left_x, overlay_video_top_left_y 
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

