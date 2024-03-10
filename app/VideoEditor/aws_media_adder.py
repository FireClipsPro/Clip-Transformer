import os
from moviepy.editor import *
import logging
import app.services.s3 as S3
from app.models.overlay_video import OverlayVideo

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class AWSMediaAdder:
    def __init__(self):
        logging.info("MediaAdder created")
    
    def add_media_to_video(self,
                            original_vid: VideoFileClip,
                            videos: [OverlayVideo],
                            overlay_zone_top_left,
                            overlay_zone_width,
                            overlay_zone_height) -> VideoFileClip:
        composite_clips = [original_vid]
        
        for video in videos:
            composite_clips = self.add_clip_to_video(original_vid,
                                                     composite_clips,
                                                     video,
                                                     overlay_zone_top_left,
                                                     overlay_zone_width,
                                                     overlay_zone_height)
        
        final_video = CompositeVideoClip(composite_clips)
        
        return final_video
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def add_clip_to_video(self, 
                          base_vid: VideoFileClip,
                          composite_clips,
                          overlay_video: OverlayVideo,
                          overlay_zone_top_left,
                          overlay_zone_width,
                          overlay_zone_height):

        overlay_top_left_x, overlay_top_left_y = self.calculate_top_left_xy(overlay_video.video.w,
                                                                            overlay_video.video.h,
                                                                            overlay_zone_width,
                                                                            overlay_zone_height,
                                                                            overlay_zone_top_left[0],
                                                                            overlay_zone_top_left[1])
            
        end_time = self.get_end_time(base_vid=base_vid, overlay_vid_end_time=overlay_video.end)
        overlay_vid = overlay_vid.set_start(overlay_video.start)
        overlay_vid = overlay_vid.set_end(end_time)
        overlay_vid = overlay_vid.set_position((overlay_top_left_x, overlay_top_left_y))
        composite_clips.append(overlay_vid)
        
        return composite_clips
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def get_end_time(self, base_vid: VideoFileClip, overlay_vid_end_time):
        if overlay_vid_end_time > base_vid.duration:
            end_time = base_vid.duration
        else:
            end_time = overlay_vid_end_time
        return end_time
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

