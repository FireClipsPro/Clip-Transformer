import os
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips, VideoFileClip
import logging

logging.basicConfig(level=logging.INFO)

class OutroCreator:
    def __init__(self, 
                 text_to_audio,
                 outro_text_folder, 
                 outro_audio_folder,
                 affirmation_tracks_folder,
                 output_folder,
                 outro_image_folder):
        self.text_to_audio = text_to_audio
        self.outro_text_folder = outro_text_folder
        self.outro_audio_folder = outro_audio_folder
        self.affirmation_tracks_folder = affirmation_tracks_folder
        self.output_folder = output_folder
        self.outro_image_folder = outro_image_folder
        
    def add_outro_video(self, 
                        outro_image_filename,
                        outro_text_filename,
                        affirmation_track_filename):
        logging.info(f'Adding outro video to {affirmation_track_filename}')
        outro_text_filepath = os.path.join(self.outro_text_folder, outro_text_filename)
        
        # returns dict: {filename, text, length}
        outro_text = self.read_txt_file(outro_text_filepath)
        
        outro_audio = self.generate_outro_audio(outro_text, outro_text_filename)
        
        logging.info("Outro audio is: " + str(outro_audio))
        full_video_name, duration = self.create_and_save_video(affirmation_track_filename,
                                                               outro_image_filename,
                                                               outro_audio['file_name'])
        
        return full_video_name, duration
    
    def read_txt_file(self, txt_file_path):
        with open(txt_file_path, 'r') as f:
            text = f.read()
        return text
    
    def create_and_save_video(self,
                              affirmation_track_filename,
                              outro_image_filename,
                              outro_audio_filename):
        if os.path.exists(os.path.join(self.output_folder, affirmation_track_filename)):
            logging.info(f'Outro video already exists: {affirmation_track_filename}')
            return affirmation_track_filename, VideoFileClip(os.path.join(self.output_folder, affirmation_track_filename)).duration
        logging.info(f'Creating outro video for {affirmation_track_filename}')
        
        # Load the audio
        audio_path = os.path.join(self.outro_audio_folder, outro_audio_filename)
        audio = AudioFileClip(audio_path)
        
        # Create an outro video using the outro image
        outro_image_path = os.path.join(self.outro_image_folder, outro_image_filename)
        outro_video = ImageClip(outro_image_path, duration=audio.duration)
        
        # Attach the audio to the outro video
        outro_video = outro_video.set_audio(audio)
        
        # Concatenate with the affirmation track
        affirmation_video = VideoFileClip(os.path.join(self.affirmation_tracks_folder, affirmation_track_filename))
        outro_video = outro_video.resize(affirmation_video.size)
        clips = [affirmation_video, outro_video]
        final_track = concatenate_videoclips(clips)
        
        # Determine the name and path for the resulting video
        output_file_path = os.path.join(self.output_folder, affirmation_track_filename)
        
        logging.info(f'Writing outro video to {output_file_path}')
        # Write the video to file
        final_track.write_videofile(output_file_path, codec='libx264', threads=4)
        
        return affirmation_track_filename, final_track.duration
        
    def generate_outro_audio(self, outro_text, outro_text_filename):
        #if audio file already exists, return it
        audio_file_path = os.path.join(self.outro_audio_folder, outro_text_filename[:-4] + '.mp3')
        if os.path.exists(audio_file_path):
            logging.info(f'Outro aulsdio file already exists: {outro_text_filename[:-4] + ".mp3"}')
            
            outro_audio = {'file_name': outro_text_filename[:-4] + ".mp3",
                           'length': AudioFileClip(audio_file_path).duration,
                           'text': outro_text}
            return outro_audio
        
        logging.info(f'Generating outro audio for {outro_text_filename}')
        self.text_to_audio.audio_folder = self.outro_audio_folder
        
        # returns dict: {filename, text, length}
        generated_audio = self.text_to_audio.generate_audio(outro_text_filename[:-4] + '.mp3', outro_text)
        
        return generated_audio
    