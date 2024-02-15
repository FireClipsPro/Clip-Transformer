import whisperx
import torch
import os
import json
from better_profanity import profanity
import logging

SMALL_MODEL_SIZE = "small"
MEDIUM_MODEL_SIZE = "medium"
LARGE_MODEL_SIZE = "large"

class WhisperTranscriber:
    def __init__(self, audio_files_folder, transcripts_folder):
        logging.info("WhisperTranscriber created")
        self.audio_files_path = audio_files_folder
        self.transcripts_folder = transcripts_folder
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    def transcribe(self, audio_file, censor_profanity=True):
        # check if file exists
        if not os.path.exists(self.audio_files_path + audio_file):
            raise Exception(f'Audio file {self.audio_files_path + audio_file} does not exist')
        else:
            logging.info("Audio file found, transcribing...")
            
        # check if json file exists
        if os.path.exists(self.transcripts_folder + audio_file + ".json"):
            logging.info("JSON file found, loading...")
            with open(self.transcripts_folder + audio_file + ".json", "r") as f:
                transcription = json.load(f)
                transcription = self.fix_numerical_transcriptions(transcription)
            return transcription
        else:
            logging.info("JSON file not found, transcribing...")
        
        if torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"
        model = whisperx.load_model("large-v2", device, compute_type="float32")
        
        audio = whisperx.load_audio(self.audio_files_path + audio_file)

        result = model.transcribe(audio, batch_size = 16)

        logging.info(result["segments"]) # before alignment

        # load alignment model and metadata
        model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)

        # align whisper output
        result_aligned = whisperx.align(result["segments"], model_a, metadata, self.audio_files_path + audio_file, device)

        logging.info("Segments: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        logging.info(result_aligned["segments"]) # after alignment
        # logging.info("Word Segments: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        # logging.info(result_aligned["word_segments"]) # after alignment 

        transcription = self.parse_transcription(result_aligned)
        
        transcription = self.clean_transcription(transcription, censor_profanity)
        
        transcription = self.ensure_transcription_has_text(transcription)
        
        transcription = self.fix_numerical_transcriptions(transcription)
        
        self.store_transcription(audio_file, transcription)
        
        return transcription
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def fix_numerical_transcriptions(self, transcription):
        word_segments = transcription['word_segments']
        for i in range(0, len(word_segments)):
            # if the word_segment contains a digit, replace it with the word
            if any(char.isdigit() for char in word_segments[i]['text']):
                word_segments[i]['end'] = word_segments[i + 1]['start'] - (0.01 * (word_segments[i + 1]['start'] - word_segments[i]['end']))
        
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

        words = []
        for element in result_aligned['segments']:
            words.extend(element['words'])
            
        print(result_aligned)
        
        print(words)
        # words should be [{'word':'the', 'start': 0.78, 'end': 1.23},{},]
        for word_segment in words:
            new_word_segment = { 'text': word_segment['word'],  'start': word_segment['start'], 'end': word_segment['end']}
            transcription['word_segments'].append(new_word_segment)
    
        for segment in result_aligned['segments']:
            new_segment = { 'text': segment['text'],  'start': segment['start'], 'end': segment['end']}
            transcription['segments'].append(new_segment)
            
        return transcription
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def store_transcription(self, audio_file, result_aligned):
        with open(self.transcripts_folder + audio_file + ".json", "w+") as file:
            json.dump(result_aligned, file)

# Tests ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# root = "../../media_storage/"
# AUDIO_EXTRACTIONS_PATH = f"{root}audio_extractions/"
# transcriber = WhisperTranscriber(AUDIO_EXTRACTIONS_PATH)

# transcriber = WhisperTranscriber(AUDIO_EXTRACTIONS_PATH)

# transcript = transcriber.clean_transcription(transcriber.transcribe("vikings_(0, 46)_(1, 44).mp3"))
# logging.info (transcript)