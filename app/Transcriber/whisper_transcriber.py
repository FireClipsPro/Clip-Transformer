import whisperx
import torch
import os
import json
from better_profanity import profanity
import logging


logging.basicConfig(level=logging.INFO)

SMALL_MODEL_SIZE = "small"
MEDIUM_MODEL_SIZE = "medium"
LARGE_MODEL_SIZE = "large"

class WhisperTranscriber:
    def __init__(self, 
                 audio_extractions_folder,
                 transcripts_folder):
        print("WhisperTranscriber created")
        self.audio_extractions_folder = audio_extractions_folder
        self.transcripts_folder = transcripts_folder
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    def transcribe(self, audio_file, censor_profanity=True):
        ''' Transcribes the audio file and returns a dictionary with the following keys:
            'word_segments': list of word segments, each with the following keys:
                'text': the text of the word segment
                'start': the start time of the word segment
                'end': the end time of the word segment
                'segment_num': the index of the segment that contains this word segment (used later for clustering)
        '''
        # check if file exists
        if not os.path.exists(self.audio_extractions_folder + audio_file):
            raise Exception('Audio file does not exist')
        else:
            logging.info("Audio file found, transcribing...")
            
        # check if json file exists
        if os.path.exists(self.transcripts_folder + audio_file[:-3] + ".json"):
            print("JSON file found, loading...")
            with open(self.transcripts_folder + audio_file[:-3] + ".json", "r") as f:
                transcription = json.load(f)
                transcription = self.assign_clusters(transcription)
            return transcription
        else:
            logging.info("JSON file not found, transcribing...")
        
        if torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"
        model = whisperx.load_model(LARGE_MODEL_SIZE, device=device)

        result = model.transcribe(self.audio_extractions_folder + audio_file)

        logging.info(result["segments"]) # before alignment

        # load alignment model and metadata
        model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)

        # align whisper output
        result_aligned = whisperx.align(result["segments"], model_a, metadata, self.audio_extractions_folder + audio_file, device)

        print("Segments: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(result_aligned["segments"]) # after alignment
        print("Word Segments: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(result_aligned["word_segments"]) # after alignment 

        transcription = self.parse_transcription(result_aligned)
        
        transcription = self.clean_transcription(transcription, censor_profanity)
        
        transcription = self.ensure_transcription_has_text(transcription)
                
        self.store_transcription(audio_file, transcription)
        
        transcription['word_segments'], transcription['num_segments'] = self.assign_clusters(transcription['segments'],
                                                                                             transcription['word_segments'])
        
        transcription['segments'] = None
        
        return transcription
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ensure_transcription_has_text(self, transcription):
        if (len(transcription['word_segments']) == 0
            or len(transcription['segments']) == 0
            or len(transcription['segments']) < 3):
            transcription = None
        return transcription
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def clean_transcription(self, transcription, censor_profanity=True):
        for word_segment in transcription['word_segments']:
            
            if censor_profanity:
                first_letter = word_segment['text'][0]
                word_segment['text'] = profanity.censor(word_segment['text'])
                # replace the first letter with first_letter to make shit = s***
                word_segment['text'] = first_letter + word_segment['text'][1:]
            
        return transcription
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def parse_transcription(self, result_aligned):
        transcription = {'word_segments': [],
                         'segments': []}
        
        for word_segment in result_aligned['word_segments']:
            new_word_segment = { 'text': word_segment['text'],  'start': word_segment['start'], 'end': word_segment['end']}
            transcription['word_segments'].append(new_word_segment)
            
        
        for segment in result_aligned['segments']:
            new_segment = { 'text': segment['text'],  'start': segment['start'], 'end': segment['end']}
            transcription['segments'].append(new_segment)
            
        return transcription
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def store_transcription(self, audio_file, result_aligned):
        with open(self.transcripts_folder + audio_file[:-3] + ".json", "w+") as file:
            json.dump(result_aligned, file)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def round_times(self, transcript):
        for segment in transcript['segments']:
            segment['start'] = round(segment['start'], 2)
            segment['end'] = round(segment['end'], 2)
        for word_segment in transcript['word_segments']:
            word_segment['start'] = round(word_segment['start'], 2)
            word_segment['end'] = round(word_segment['end'], 2)
        return transcript
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def assign_clusters(self, transcription):
        ''' Assign each word_segment a number that represents its position in segments.
            This is so we don't have to store segments and can rebuild it later.
        '''
        segments = transcription['segments']
        word_segments = transcription['word_segments']
        
        for i, segment in enumerate(segments):
            segment_text = segment['text']
            for word in word_segments:
                # Check if the word is completely within the segment
                if word['start'] >= segment['start'] and word['end'] <= segment['end']:
                    word['segment_num'] = i
                # Check for partial overlap and if the word text is in the segment text
                elif ((word['start'] < segment['end'] and word['end'] > segment['start']) and 
                    (word['text'] in segment_text)):
                    word['segment_num'] = i
                    
        # Set the number of segments and remove segments from the transcription
        transcription['num_segments'] = len(segments)
        transcription['word_segments'] = word_segments
        transcription['segments'] = None
        
        return transcription

# Tests ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# root = "../../media_storage/"
# AUDIO_EXTRACTIONS_PATH = f"{root}audio_extractions/"
# transcriber = WhisperTranscriber(AUDIO_EXTRACTIONS_PATH)

# transcriber = WhisperTranscriber(AUDIO_EXTRACTIONS_PATH)

# transcript = transcriber.clean_transcription(transcriber.transcribe("vikings_(0, 46)_(1, 44).mp3"))
# print(transcript)