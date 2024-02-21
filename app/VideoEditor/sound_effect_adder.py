import os
import random
import logging
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips

logging.basicConfig(level=logging.INFO)

class SoundEffectAdder:
    def __init__(self, image_sounds_folder,
                 video_input_folder,
                 output_folder):
        self.image_sounds = [os.path.join(image_sounds_folder, sound) 
                             for sound in os.listdir(image_sounds_folder) 
                             if sound.endswith('.mp3')]
        self.video_input_folder = video_input_folder
        self.output_folder = output_folder

    def add_sounds_to_images(self, images, video, wants_sounds):
        if not wants_sounds:
            return video

        video_path = os.path.join(self.video_input_folder, video['file_name'])
        video_clip = VideoFileClip(video_path)
        video_duration = video_clip.duration

        original_audio = video_clip.audio

        audio_clips = [original_audio]
        for image in images:
            sound_file = random.choice(self.image_sounds)
            sound_clip = AudioFileClip(sound_file)
            sound_clip = sound_clip.volumex(0.6)
            sound_duration = sound_clip.duration

            logging.info(f"Adding sound {sound_file} to image")
            logging.info(f"Sound duration: {sound_duration}")

            if (image['start'] + sound_duration <= image['end']) and (sound_duration + image['start'] <= video_duration):
                audio_clips.append(sound_clip.set_start(image['start']))
            else:
                logging.warning(f"Sound {sound_file} does not fit within the image duration and will not be added.")

        composite_audio_clip = CompositeAudioClip(audio_clips)
        video_clip.audio = composite_audio_clip

        output_video_path = os.path.join(self.output_folder, 'eff_' + video['file_name'])
        video_clip.write_videofile(output_video_path, threads=4)
        
        video['file_name'] = 'eff_' + video['file_name']
        
        logging.info(f"Done! Sound added to {output_video_path}")
        return video
