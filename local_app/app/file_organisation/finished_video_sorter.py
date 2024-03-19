import os
from moviepy.video.io.VideoFileClip import VideoFileClip
import shutil
import logging

logging.basicConfig(level=logging.INFO)

class FinishedVideoSorter:
    def __init__(self, finished_videos_folder):
        self.finished_videos_folder = finished_videos_folder
        
    def sort_video(self, raw_video_name, finished_video_name):
        raw_video_name = raw_video_name.replace(".mp4", "/")
        video_path = os.path.join(self.finished_videos_folder, finished_video_name)
        video = VideoFileClip(video_path)
        
        #remove .mp4 from raw_video_name and replace with /
        
        if video.duration > 59:
            logging.info("Video is greater than 60 seconds")
            short_video = video.subclip(0, 59)
            
            #if folder path: finished_videos_folder/shorts/raw_video_name/ does not exist
            shorts_folder_path = os.path.join(self.finished_videos_folder, "shorts/", raw_video_name)
            os.makedirs(shorts_folder_path, exist_ok=True)
            short_video.write_videofile(os.path.join(shorts_folder_path, finished_video_name), audio_codec='aac',threads=4)
            
            # if folder path: finished_videos_folder/tiktok/raw_video_name/ does exist create it
            tiktok_folder_path = os.path.join(self.finished_videos_folder, "tiktok/", raw_video_name)
            os.makedirs(tiktok_folder_path, exist_ok=True)
            shutil.move(video_path, os.path.join(tiktok_folder_path, finished_video_name))
        else:
            logging.info("Video is less than 60 seconds")
            #if folder path: finished_videos_folder/shorts/raw_video_name/ does not exist create it
            shorts_folder_path = os.path.join(self.finished_videos_folder, "shorts/", raw_video_name)
            os.makedirs(shorts_folder_path, exist_ok=True)
            
            # if folder path: finished_videos_folder/tiktok/raw_video_name/ does exist create it
            tiktok_folder_path = os.path.join(self.finished_videos_folder, "tiktok/", raw_video_name)
            os.makedirs(tiktok_folder_path, exist_ok=True)
            shutil.copyfile(video_path, os.path.join(tiktok_folder_path, finished_video_name))

            shutil.move(video_path, os.path.join(shorts_folder_path, finished_video_name))

            
        video.close()

# sorter = FinishedVideoSorter("../../media_storage/finished_videos/")

# sorter.sort_video("Joe_David_1.mp4", "The Power of Pushing Past Defeat | David Goggins.mp4")