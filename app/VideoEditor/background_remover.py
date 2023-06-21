import subprocess
import os
import logging
from moviepy.editor import VideoFileClip, CompositeVideoClip

logging.basicConfig(level=logging.INFO)

class BackgroundRemover:
    def __init__(self, input_video_folder, input_image_folder, output_folder):
        self.input_video_folder = input_video_folder
        self.input_image_folder = input_image_folder
        self.output_folder = output_folder


    def remove_background(self, video, image_to_overlay):
        input_video_path = os.path.join(self.input_video_folder, video)
        input_image_path = os.path.join(self.input_image_folder, image_to_overlay)

        # Get the duration of the input video
        video_clip = VideoFileClip(input_video_path)
        video_duration = video_clip.duration  # in seconds
        logging.info(f"Video duration: {video_duration} seconds")

        # Convert image to a video with the same duration as input video
        # check first if the video already exists
        image_video_path = os.path.join(self.output_folder, "image_video.mp4")
        if not os.path.exists(image_video_path):
            ffmpeg_command = f'ffmpeg -loop 1 -i "{input_image_path}" -c:v libx264 -t {video_duration} -pix_fmt yuv420p "{image_video_path}"'
            subprocess.run(ffmpeg_command, shell=True, check=True)
            logging.info(f"Image converted to video with duration {video_duration} seconds")
            
        output_video_path = os.path.join(self.output_folder, "output.mov")

        # Construct command for background removal
        # command = f'backgroundremover -i \"{input_video_path}\" -tv -o \"{output_video_path}\"'
        # # command = f'backgroundremover -i \"{input_video_path}\" -o \"{output_video_path[:-4] + ".mov"}\"'
        # subprocess.run(command, shell=True, check=True)
        # logging.info(f"Background removed and saved as {output_video_path}")
        
        # # Now convert the ".mov" file to ".mp4"
        mp4_output_video_path = os.path.join(self.output_folder, "output.mp4")
        ffmpeg_command = f'ffmpeg -i "{output_video_path}" -vcodec h264 -acodec mp2 "{mp4_output_video_path}"'
        subprocess.run(ffmpeg_command, shell=True, check=True)
        logging.info(f"converted {output_video_path} to {mp4_output_video_path}")
        
        # overlay the backgroundless video with the image video
        # use moviepy for this
        video_clip = VideoFileClip(mp4_output_video_path)
        image_video_clip = VideoFileClip(image_video_path)
        # Set the duration of both clips to the shorter of the two clip durations
        duration = min(video_clip.duration, image_video_clip.duration)
        video_clip = video_clip.set_duration(duration)
        image_video_clip = image_video_clip.set_duration(duration)

        # Overlay video_clip on top of image_video_clip
        final_video_clip = CompositeVideoClip([image_video_clip, video_clip])

        final_video_clip.write_videofile(mp4_output_video_path, fps=30)
        logging.info(f"Overlayed {mp4_output_video_path} with {image_video_path}")

        logging.info(f"Done!")
        return mp4_output_video_path
