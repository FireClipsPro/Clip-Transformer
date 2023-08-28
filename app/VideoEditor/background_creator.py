from moviepy.editor import *
import os
from moviepy.editor import concatenate_videoclips

class BackgroundCreator:
    def __init__(self,
                 input_audio_folder,
                 output_video_folder,
                 background_media_folder):
        self.audio_folder = input_audio_folder
        self.video_folder = output_video_folder
        self.background_image_folder = background_media_folder

    def create_horizontal(self, 
                      audio_file_name,
                      background_media,
                      background_color,
                      width,
                      height):
        # Determine audio duration
        audio_clip = AudioFileClip(os.path.join(self.audio_folder, audio_file_name))
        audio_duration = audio_clip.duration
        
        # Determine the name and path for the resulting video
        background_video_name = os.path.splitext(audio_file_name)[0] + ".mp4"
        background_video_path = os.path.join(self.video_folder, background_video_name)
        
        # if the video name already exists return it
        if os.path.exists(background_video_path):
            video = {'file_name': background_video_name,
                    'start_time_sec': 0,
                    'end_time_sec': audio_duration}
            return video

        clips = []
        
        for media_name in background_media:
            bg_media_path = os.path.join(self.background_image_folder, media_name)

            # Check the file extension to determine if it's an image or video
            extension = os.path.splitext(media_name)[1].lower()

            if extension == ".jpg":
                # For images, use the image and resize it to the desired dimensions
                clips.append(ImageClip(bg_media_path).resize(newsize=(width, height)))

            else:  # Assuming it's a video format
                bg_video_clip = VideoFileClip(bg_media_path).resize(newsize=(width, height))
                clips.append(bg_video_clip)

        # Concatenate all clips
        concatenated_clip = concatenate_videoclips(clips)
        
        # If the concatenated clip's duration is less than the audio_duration
        if concatenated_clip.duration < audio_duration:
            loops_required = int(audio_duration / concatenated_clip.duration) + 1
            clip = concatenate_videoclips([concatenated_clip] * loops_required)
        else:
            clip = concatenated_clip.subclip(0, audio_duration)
        
        # If no background media is given, create a black video
        if not background_media:
            clip = ColorClip((width, height), color=background_color).set_duration(audio_duration)

        # Add audio to the video clip
        clip = clip.set_audio(audio_clip).set_duration(audio_duration)

        # Add fps attribute to the clip
        clip.fps = 24

        # Write the final video
        clip.write_videofile(background_video_path, codec='libx264', fps=24, threads=4)

        video = {'file_name': background_video_name,
                'start_time_sec': 0,
                'end_time_sec': audio_duration}
        return video

    def create_horizontal1(self, 
                        audio_file_name,
                        background_media_name,
                        background_color,
                        width,
                        height):
        
        # Determine audio duration
        audio_clip = AudioFileClip(os.path.join(self.audio_folder, audio_file_name))
        audio_duration = audio_clip.duration
        # Determine the name and path for the resulting video
        background_video_name = "blank_" + os.path.splitext(audio_file_name)[0] + ".mp4"
        background_video_path = os.path.join(self.video_folder, background_video_name)
        
        # if the video name already exists return it
        if os.path.exists(background_video_path):
            video = {'file_name': background_video_name,
                'start_time_sec': 0,
                'end_time_sec': audio_duration}
            return video

        # If no background media is given, create a black video
        if background_media_name is None:
            clip = ColorClip((width, height), color=background_color).set_duration(audio_duration)

        else:
            bg_media_path = os.path.join(self.background_image_folder, background_media_name)
            
            # Check the file extension to determine if it's an image or video
            extension = os.path.splitext(background_media_name)[1].lower()

            if extension == ".jpg":
                # Use the background image and resize it to the desired dimensions
                clip = ImageClip(bg_media_path, duration=audio_duration).resize(newsize=(width, height))

            else: # Assuming it's a video format
                bg_video_clip = VideoFileClip(bg_media_path).resize(newsize=(width, height))
                if bg_video_clip.duration < audio_duration:
                    loops_required = int(audio_duration / bg_video_clip.duration) + 1
                    clip = concatenate_videoclips([bg_video_clip] * loops_required)
                else:
                    clip = bg_video_clip.subclip(0, audio_duration)

        # Add audio to the video clip
        clip = clip.set_audio(audio_clip).set_duration(audio_duration)


        # Add fps attribute to the clip
        clip.fps = 24

        # Write the final video
        clip.write_videofile(background_video_path, codec='libx264', fps=24, threads=4)

        video = {'file_name': background_video_name,
                'start_time_sec': 0,
                'end_time_sec': audio_duration}
        return video

