import os
import subprocess
import time
import imageio_ffmpeg as ffmpeg
from moviepy.editor import *

class MediaAdder:
    def __init__(self,
                 input_videos_file_path,
                 output_file_path,
                 image_videos_file_path):
        self.input_videos_file_path = input_videos_file_path
        self.output_file_path = output_file_path
        self.image_videos_file_path = image_videos_file_path
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
    def add_videos_to_original_clip(self,
                                    original_clip,
                                    videos,
                                    original_clip_width,
                                    original_clip_height,
                                    overlay_zone_width,
                                    overlay_zone_height,
                                    overlay_zone_x,
                                    overlay_zone_y):
        
        # Initialize the input video path
        input_video = self.input_videos_file_path + original_clip
        if not os.path.exists(input_video):
            print(f'Input video {input_video} does not exist')
            return None
        
        for index, video in enumerate(videos):
            # initialize the overlay video path
            overlay_video_file_name = self.image_videos_file_path + video['video_file_name']
            if not os.path.exists(overlay_video_file_name):
                print(f'Overlay video {overlay_video_file_name} does not exist')
                return None
            # initialize the output video path
            output_video = self.output_file_path + original_clip + f'_{index}.mp4'
            if os.path.exists(output_video):
                os.remove(output_video)
            
            overlay_top_left, overlay_top_right = self.calculate_top_left_right(video['width'],
                                                                                video['height'],
                                                                                overlay_zone_width,
                                                                                overlay_zone_height,
                                                                                overlay_zone_x,
                                                                                overlay_zone_y)
            #remove the audio from the overlay video and the input video
            # self.remove_audio(overlay_video_file_name, index)
            # self.remove_audio(input_video, index)            
            
            
            
            # command = [
            #     "ffmpeg",
            #     "-i", input_video,
            #     "-i", overlay_video_file_name,
            #     "-filter_complex",
            #     f"[1:v]scale={video['width']}x{video['height']},format=yuva420p[ovrl];"
            #     f"[0:v][ovrl]overlay={overlay_top_left}:{overlay_top_right}:enable='between("
            #     f"t,{video['start_time']},{video['end_time']})'",
            #     "-c:a", "copy",
            #     output_video
            # ]
            # subprocess.run(command)
            
            # input1 = ffmpeg.input(input_video)
            # input2 = ffmpeg.input(overlay_video_file_name)
            # (input1.filter("scale", size=f"{video['width']}x{video['height']}")
            #     .filter("format", "yuva420p", is_complex=True)
            #     .filter("setpts", "PTS-STARTPTS", is_complex=True)
            #     .overlay(input2, x=overlay_top_left, y=overlay_top_right, enable=f"between(t,{video['start_time']},{video['end_time']})")
            #     .output(output_video)
            #     .run()
            # )
            
            background_video = VideoFileClip(input_video)
            overlay_video = VideoFileClip(overlay_video_file_name)
            # overlay_video = overlay_video.resize(width=video['width'],height=video['height'])
            overlay_video = overlay_video.set_start(video['start_time']).set_end(video['end_time'])
            overlay_video = overlay_video.set_position((overlay_top_left, overlay_top_right))
            final_video = CompositeVideoClip([background_video, overlay_video])
            final_video.write_videofile(output_video)
            
           
            
            # set the input video to the output video
            input_video = output_video

    def remove_audio(self, original_clip, index):
        overlay_video_no_audio = original_clip + f'_{index}_no_audio.mp4'
        if os.path.exists(overlay_video_no_audio):
            os.remove(overlay_video_no_audio)
        
        command = [
            "ffmpeg",
            "-i", original_clip,
            "-an",
            overlay_video_no_audio
        ]
        subprocess.run(command)
        
        # delete the original video
        os.remove(original_clip)
        
        # change the name of the video to the one without audio
        os.rename(overlay_video_no_audio, original_clip)
        

        
            
    def calculate_top_left_right(self,
                                 overlay_video_width,
                                 overlay_video_height,
                                 overlay_zone_width,
                                 overlay_zone_height,
                                 overlay_zone_x,
                                 overlay_zone_y):
        # calculate the overlay top left and right
        overlay_top_left = overlay_zone_x + abs((overlay_video_width - overlay_zone_width) / 2)
        overlay_top_right = overlay_zone_y + abs((overlay_video_height - overlay_zone_height) / 2)

        return overlay_top_left, overlay_top_right
        



            
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



    