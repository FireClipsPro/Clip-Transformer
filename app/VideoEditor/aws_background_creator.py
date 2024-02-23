from moviepy.editor import *
import os
from moviepy.editor import concatenate_videoclips
import logging
from app.services.s3 import S3

logging.basicConfig(level=logging.DEBUG)

class AWSBackgroundCreator:
    def __init__(self,
                 audio_bucket,
                 output_video_bucket,
                 background_video_bucket,
                 s3: S3):
        self.audio_bucket = audio_bucket
        self.output_video_bucket = output_video_bucket
        self.bg_video_bucket = background_video_bucket
        self.s3 = s3
    
    # returns:
    # video = {'file_name': background_video_name,
    #             'start_time_sec': 0,
    #             'end_time_sec': audio_duration}
    def create_horizontal(self, 
                      audio_id,
                      background_media_ids,
                      width,
                      height):
        # Determine audio duration
        audio_clip = AudioFileClip(os.path.join(self.audio_bucket, audio_id))
        audio_duration = audio_clip.duration
        audio_clip = self.s3.get_audiofileclip(audio_id)
        
        clips = []
        
        for id in background_media_ids:
            bg_vid = self.s3.get_videofileclip(video_id= id, 
                                                              bucket_name=self.bg_video_bucket)
            bg_vid = bg_vid.resize(newsize=(width, height))
            clips.append(bg_vid)

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

        # Write the final video to s3
        self.s3.write_videofileclip(clip=clip, 
                                    id = audio_id,
                                    bucket_name=self.output_video_bucket)
        
        self.s3.dispose_temp_files()
        
        return True
    

    