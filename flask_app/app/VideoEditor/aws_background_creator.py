import logging

from moviepy.editor import *
from moviepy.editor import concatenate_videoclips

logging.basicConfig(level=logging.DEBUG)

class AWSBackgroundCreator:
    def __init__(self):
        logging.info("AWSBackgroundCreator initialized")
        
    # returns: VideoFileClip
    def create_horizontal(self, 
                          audio_clip: AudioFileClip,
                          background_videos: [VideoFileClip],
                          width,
                          height):
        # Determine audio duration
        audio_duration = audio_clip.duration
        
        clips = []
        for video in background_videos:
            video = video.resize(newsize=(width, height))
            clips.append(video)

        # Concatenate all clips
        concatenated_clip = concatenate_videoclips(clips)
        
        # If the concatenated clip's duration is less than the audio_duration
        if concatenated_clip.duration < audio_duration:
            loops_required = int(audio_duration / concatenated_clip.duration) + 1
            clip = concatenate_videoclips([concatenated_clip] * loops_required)
        else:
            clip = concatenated_clip.subclip(0, audio_duration)
        
        # Add audio to the video clip
        clip = clip.set_audio(audio_clip).set_duration(audio_duration)

        # Add fps attribute to the clip
        clip.fps = 24

        return clip
    