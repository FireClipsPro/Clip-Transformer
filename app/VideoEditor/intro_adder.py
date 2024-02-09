from moviepy.editor import concatenate_videoclips, VideoFileClip, AudioFileClip,concatenate_audioclips,vfx
import os
from moviepy.audio.AudioClip import AudioArrayClip
import numpy as np


SILENCE_DURATION = 5
class IntroAdder:
    def __init__(self, intro_video_folder, video_folder, output_folder):
        self.intro_video_folder = intro_video_folder
        self.video_folder = video_folder
        self.output_folder = output_folder
    
    def add_audio_intro(self, affirmations_track_filename, intro_file_name, transcript):
        
        # Construct the paths for the audio and intro files
        intro_path = os.path.join(self.intro_video_folder, intro_file_name)
        audio_path = os.path.join(self.audio_folder, affirmations_track_filename)
        
        # Check if the files exist
        if not os.path.exists(intro_path):
            raise ValueError(f"Intro audio file not found: {intro_path}")
        if not os.path.exists(audio_path):
            raise ValueError(f"Main audio file not found: {audio_path}")
        
        # Load the audio clips
        intro_clip = AudioFileClip(intro_path)
        
        intro_clip = intro_clip.fx(vfx.speedx, 0.93)
        silence = self.generate_silence(SILENCE_DURATION, affirmations_audio.fps)
        affirmations_audio = AudioFileClip(audio_path)

        # Concatenate the intro with the main audio
        final_audio = concatenate_audioclips([intro_clip, silence, affirmations_audio])
        
        # Determine the name and path for the resulting audio
        output_file_name = affirmations_track_filename
        output_file_path = os.path.join(self.output_folder, output_file_name)
        
        # Write the concatenated audio to file
        final_audio.write_audiofile(output_file_path, codec='mp3')
        
        transcript = self.update_transcript_times(transcript, intro_clip.duration + silence.duration)
        
        return output_file_name, transcript
    
    def generate_silence(self, duration, fps):
        """Generate an AudioArrayClip representing silence."""
        samples = int(fps * duration)
        silence_array = np.zeros((samples, 2), dtype=np.int16)
        return AudioArrayClip(silence_array, fps=fps)
    
    def update_transcript_times(self, 
                                transcript,
                                intro_duration):
        for text in transcript:
            text['start'] += intro_duration
            text['end'] += intro_duration
        return transcript

    def add_video_intro(self,
                  video_file_name,
                  intro_file_name):
        """
        This function takes a video file name and an intro file name,
        concatenates the intro to the beginning of the video, 
        and then saves the output in the output folder.
        
        Parameters:
        - video_file_name: Name of the main video file.
        - intro_file_name: Name of the intro video file.
        
        Returns:
        - output_file_path: Path of the concatenated video.
        """
        
        # Load the intro and main video
        intro_clip = VideoFileClip(f"{self.intro_video_folder}/{intro_file_name}")
        main_clip = VideoFileClip(f"{self.video_folder}/{video_file_name}")
        
        # Concatenate the two clips
        final_clip = concatenate_videoclips([intro_clip, main_clip])
        
        # Save the result
        output_file_path = f"{self.output_folder}/{video_file_name}"
        final_clip.write_videofile(output_file_path, threads=4)
        
        # Close the clips to free up memory
        intro_clip.close()
        main_clip.close()
        
        return video_file_name