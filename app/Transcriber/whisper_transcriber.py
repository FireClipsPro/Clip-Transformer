import whisperx
import torch
import os
import json
from better_profanity import profanity

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
        # check if file exists
        if not os.path.exists(self.audio_extractions_folder + audio_file):
            raise Exception('Audio file does not exist')
        else:
            print("Audio file found, transcribing...")
            
        # check if json file exists
        if os.path.exists(self.transcripts_folder + audio_file[:-3] + ".json"):
            print("JSON file found, loading...")
            with open(self.transcripts_folder + audio_file[:-3] + ".json", "r") as f:
                transcription = json.load(f)
                transcription['segments'] = self.normalize_segments(transcription['segments'], transcription['word_segments'])
            return transcription
        
        if torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"
        model = whisperx.load_model(LARGE_MODEL_SIZE, device=device)

        result = model.transcribe(self.audio_extractions_folder + audio_file)

        print(result["segments"]) # before alignment

        # load alignment model and metadata
        model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)

        # align whisper output
        result_aligned = whisperx.align(result["segments"], model_a, metadata, self.audio_extractions_folder + audio_file, device)

        print("Segments: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(result_aligned["segments"]) # after alignment
        print("Word Segments: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(result_aligned["word_segments"]) # after alignment 

        transcription = self.parse_transcription(result_aligned)
        
        transcription = self.clean_transcription(transcription, censor_profanity)
        
        transcription = self.ensure_transcription_has_text(transcription)
        
        transcription['segments'] = self.normalize_segments(transcription['segments'], transcription['word_segments'])
        
        self.store_transcription(audio_file, transcription)
        
        return transcription
    
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
    def normalize_segments(self, segments, word_segments):
        def find_closest_time(target, key):
            closest_time = None
            start, end = 0, len(word_segments) - 1
            while start <= end:
                mid = (start + end) // 2
                mid_time = word_segments[mid][key]
                if closest_time is None or abs(mid_time - target) < abs(closest_time - target):
                    closest_time = mid_time
                if mid_time < target:
                    start = mid + 1
                else:
                    end = mid - 1
            return closest_time

        normalized_segments = []
        for segment in segments:
            closest_start = find_closest_time(segment['start'], 'start')
            closest_end = find_closest_time(segment['end'], 'end')
            normalized_segment = {'start': closest_start,
                                  'end': closest_end,
                                  'text': segment['text']}
            normalized_segments.append(normalized_segment)

        return normalized_segments
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def create_mapping(self, segments, word_segments):
        '''Creates map from word_segment to segment
        '''
        mapping = {}
        for segment in segments:
            for word_segment in word_segments:
                # if word segment is within segment
                if word_segment['start'] >= segment['start'] and word_segment['end'] <= segment['end']:
                    # Convert word_segment to a tuple (start, end)
                    word_segment_key = (word_segment['start'], word_segment['end'])
                    mapping[word_segment_key] = segment
        
        return mapping
# Tests ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# root = "../../media_storage/"
# AUDIO_EXTRACTIONS_PATH = f"{root}audio_extractions/"
# transcriber = WhisperTranscriber(AUDIO_EXTRACTIONS_PATH)

# transcriber = WhisperTranscriber(AUDIO_EXTRACTIONS_PATH)

# transcript = transcriber.clean_transcription(transcriber.transcribe("vikings_(0, 46)_(1, 44).mp3"))
# print (transcript)