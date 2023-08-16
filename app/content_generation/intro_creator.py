import os
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips, VideoFileClip, vfx
import logging

logging.basicConfig(level=logging.INFO)
class IntroCreator:
    def __init__(self, 
                 text_to_audio,
                 intro_text_folder, 
                 intro_audio_folder,
                 affirmation_tracks_folder,
                 output_folder,
                 intro_image_folder,
                 animations_folder,
                 intro_video_folder):
        self.text_to_audio = text_to_audio
        self.intro_text_folder = intro_text_folder
        self.intro_audio_folder = intro_audio_folder
        self.affirmation_tracks_folder = affirmation_tracks_folder
        self.output_folder = output_folder
        self.intro_image_folder = intro_image_folder
        self.animations_folder = animations_folder
        self.intro_video_folder = intro_video_folder
        
    def add_intro_video(self,
                        transcript,
                        intro_media_files,
                        intro_text_filename,
                        affirmation_track_filename,
                        use_existing_intro=False,
                        intro_video_filename=None):
        intro_audio = {}
        intro_video_name = None
        if use_existing_intro:
            logging.info(f'Using existing intro video: {intro_video_filename}')
            intro_audio['length'] = VideoFileClip(os.path.join(self.intro_video_folder, intro_video_filename)).duration
            intro_video_name = intro_video_filename
        else:
            logging.info(f"Creating new video intro for text file: " + intro_text_filename)
            if os.path.exists(os.path.join(self.intro_audio_folder, intro_text_filename[:-4]+'.mp3')):
                logging.info(f'Intro audio file already exists: {intro_text_filename[:-4]+".mp3"}')
                audio = AudioFileClip(os.path.join(self.intro_audio_folder, intro_text_filename[:-4]+'.mp3'))
                intro_audio = {'file_name': intro_text_filename[:-4]+".mp3", 'length': audio.duration}
            else:
                logging.info(f'Intro audio file does not exist: {intro_text_filename[:-4]+".mp3"}')
                intro_text_filepath = os.path.join(self.intro_text_folder, intro_text_filename)
                intro_text = self.read_txt_file(intro_text_filepath)
                intro_audio = self.generate_intro_audio(intro_text, intro_text_filename)
            
            intro_video_name = self.create_intro_video(affirmation_track_filename,
                                                        intro_media_files,
                                                        intro_audio['file_name'])
            
        video_with_intro_name = self.add_intro_to_video(intro_video_name,
                                                        affirmation_track_filename)
        
        transcript = self.update_transcript(transcript, intro_audio['length'])
        
        return video_with_intro_name, transcript
    
    def update_transcript(self, transcript, duration):
        for text in transcript:
            text['start'] += duration
            text['end'] += duration
        return transcript
    
    def read_txt_file(self, txt_file_path):
        with open(txt_file_path, 'r') as f:
            text = f.read()
        return text
    
    def generate_intro_audio(self, intro_text, intro_text_filename):
        logging.info(f'Generating intro audio for {intro_text_filename}')
        #if audio file already exists, return it
        audio_file_path = os.path.join(self.intro_audio_folder, intro_text_filename[:-4]+'.mp3')
        if os.path.exists(audio_file_path):
            return intro_text_filename
        
        self.text_to_audio.audio_folder = self.intro_audio_folder
        # returns dict: {filename, text, length}
        return self.text_to_audio.generate_audio(intro_text_filename[:-4]+'.mp3', intro_text)
        
    def create_intro_video(self, 
                              affirmation_track_filename,
                              media_file,
                              audio_filename):
        if os.path.exists(os.path.join(self.intro_video_folder, affirmation_track_filename)):
            logging.info(affirmation_track_filename + ' intro already exists. Skipping...')
            return affirmation_track_filename
        else:
            logging.info(affirmation_track_filename + ' intro does not exist. Creating...')
        
        # Load the audio
        intro_audio = os.path.join(self.intro_audio_folder, audio_filename)
        audio = AudioFileClip(intro_audio)
        
        intro_videos = []
        for media_file in media_file:
            # Create an intro video using the intro image
            intro_media_path = os.path.join(self.animations_folder, media_file)
            intro_video = VideoFileClip(intro_media_path)
            intro_videos.append(intro_video)
            
            reversed_video = intro_video.fx(vfx.time_mirror)
            intro_videos.append(reversed_video)
        
        intro_video = concatenate_videoclips(intro_videos)
        
        # if intro_video is longer than the audio, add audio and cut it at the end of the audio
        if intro_video.duration > audio.duration:
            intro_video = intro_video.subclip(0, audio.duration)
            intro_video = intro_video.set_audio(audio)
        # if intro_video is shorter, repeat the intro_video until it is longer than the audio then cut it at the end of the audio
        else:
            repeated_clips = [intro_video] * int(audio.duration // intro_video.duration + 1)
            intro_video = concatenate_videoclips(repeated_clips)
            intro_video = intro_video.subclip(0, audio.duration)
            intro_video = intro_video.set_audio(audio)
        
        # Determine the name and path for the resulting video
        output_file_path = os.path.join(self.intro_video_folder, affirmation_track_filename)
        
        # Write the intro video to the intro file
        intro_video.write_videofile(output_file_path, codec='libx264', threads=4)
        
        return affirmation_track_filename

    def add_intro_to_video(self,
                           intro_video_filename,
                           affirmation_track_filename):
        # Concatenate with the affirmation track
        affirmation_video = VideoFileClip(os.path.join(self.affirmation_tracks_folder, affirmation_track_filename))
        intro_video = VideoFileClip(os.path.join(self.intro_video_folder, intro_video_filename))
        output_file_path = os.path.join(self.output_folder, affirmation_track_filename)
        if os.path.exists(output_file_path):
            logging.info(affirmation_track_filename + ' already exists. Skipping...')
            return affirmation_track_filename
        
        logging.info("Concatenating " + intro_video_filename + " with " + affirmation_track_filename)
        intro_video = intro_video.resize(newsize=(affirmation_video.size[0],
                                                  affirmation_video.size[1]))
        clips = [intro_video, affirmation_video]
        final_track = concatenate_videoclips(clips)
        logging.info(f"affirmation_video.duration: {affirmation_video.duration}")
        logging.info(f"intro_video.duration: {intro_video.duration}")
        logging.info(f"Final track duration: {final_track.duration}")
        logging.info(" firt fps: " + str(intro_video.fps) + " second fps:" + str(affirmation_video.fps))
        logging.info("first size: " + str(intro_video.size) + " second size: " + str(affirmation_video.size))

        
        final_track.write_videofile(output_file_path,
                                    fps=24,
                                    codec='libx264',
                                    threads=4,
                                    preset='ultrafast')
        
        logging.info('Intro video added to ' + affirmation_track_filename)
        logging.info("Saved to " + output_file_path)
        return affirmation_track_filename