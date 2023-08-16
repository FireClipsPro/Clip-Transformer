import os
import logging
from moviepy.editor import AudioFileClip, concatenate_audioclips
from moviepy.audio.AudioClip import AudioArrayClip
import numpy as np
import copy

logging.basicConfig(level=logging.INFO)

# silence padding at the beginning and end of the track
SILENCE_TIME = 4

class AffirmationsTrackBuilder:
    def __init__(self,
                 text_to_speech,
                 affirmations_folder,
                 output_folder):
        self.affirmations_folder = affirmations_folder
        self.output_folder = output_folder
        self.text_to_speech = text_to_speech

    # input is a list of string affirmations
    def build_track(self, affirmations, affirmations_filename_base, output_file_name, num_repeats=4):
        logging.info(f'Building track for {affirmations_filename_base}')
        output_file_path = os.path.join(self.output_folder, output_file_name)
        
        transcript = []
        # current time set to silence time to account for silence at the beginning of the track
        current_time = SILENCE_TIME
        audio_clips = []
        
        audio_affirmations = []
        for i, audio_affirmation in enumerate(affirmations):
            audio_file_name = f"{affirmations_filename_base.split('.')[0]}_{i}.mp3"
            audio_affirmations.append(self.text_to_speech.generate_audio(audio_file_name, audio_affirmation))

        logging.info(f"Audio affirmations: {audio_affirmations}")
        
        for audio_affirmation in audio_affirmations:
            # affirmation in the form {'file_name': audio_file_name, 'length': audio_length, 'text': text}

            # Get the audio file
            audio_file_path = os.path.join(self.affirmations_folder, audio_affirmation['file_name'])
            audio_clip = AudioFileClip(audio_file_path)

            # Append it to our list of audio clips
            audio_clips.append(audio_clip)

            # Add double the length of the audio as silence to the track
            silence_duration = audio_affirmation['length'] * 2
            
            # Update the transcript
            transcript.append({'text': audio_affirmation['text'],
                            'start': current_time,
                            'end': current_time + audio_affirmation['length'] + silence_duration})

            # Generate silence
            end_silence = self.generate_silence(silence_duration, audio_clip.fps)
            audio_clips.append(end_silence)

            current_time += audio_affirmation['length'] + silence_duration

        affirmation_tracks = concatenate_audioclips(audio_clips)
        
        # Repeate the track num_repeats times and update the transcript
        repeated_tracks = concatenate_audioclips([affirmation_tracks] * num_repeats)
        transcript_length = transcript[-1]['end'] - transcript[0]['start']
        transcript = self.concatenate_transcript(transcript, num_repeats, transcript_length)

        audio_clips = [repeated_tracks]
        
        # add SILENCE time seconds of silence to the beginning and end of the track
        start_silence = self.generate_silence(SILENCE_TIME, audio_clip.fps)
        # append start silence to the front of audio_clips
        audio_clips.insert(0, start_silence)
        
        end_of_affirmations_silence = self.generate_silence(SILENCE_TIME, audio_clip.fps)
        audio_clips.append(end_of_affirmations_silence)
        
        # Concatenate audio clips to form the final track
        final_track = concatenate_audioclips(audio_clips)
        final_track.write_audiofile(output_file_path)
        
        # Return a track object
        track = {'file_name': output_file_name, 
                 'length': current_time,
                 'transcript': transcript}
        
        return track

    
    def generate_silence(self, duration, fps):
        """Generate an AudioArrayClip representing silence."""
        samples = int(fps * duration)
        silence_array = np.zeros((samples, 2), dtype=np.int16)
        return AudioArrayClip(silence_array, fps=fps)
    

    def concatenate_transcript(self, 
                               transcript,
                               num_repeats,
                               transcript_length):
        old_transcript = copy.deepcopy(transcript)

        for i in range(1, num_repeats):
            new_transcript = copy.deepcopy(old_transcript)
            for text in new_transcript:
                text['start'] += transcript_length * i
                text['end'] += transcript_length * i
            
            transcript.extend(new_transcript)
        
        return transcript
    
track_builder = AffirmationsTrackBuilder(text_to_speech=None,
                                            affirmations_folder=None,
                                            output_folder=None)

tranny = track_builder.concatenate_transcript(transcript=[{'text': 'test',
                                                            'start': 5,
                                                            'end': 10},
                                                            {'text': 'next',
                                                            'start': 16,
                                                            'end': 20}],
                                                            num_repeats=3,
                                                            transcript_length=15)

print(tranny)