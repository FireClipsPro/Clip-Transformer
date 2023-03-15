import whisperx
import torch
import os
import json

class WhisperTranscriber:
    def __init__(self, audio_files_path):
        print("WhisperTranscriber created")
        self.audio_files_path = audio_files_path
    
    def transcribe(self, audio_file):
        # check if file exists
        if not os.path.exists(self.audio_files_path + audio_file):
            raise Exception('Audio file does not exist')
        else:
            print("Audio file found, transcribing...")
            
        # check if json file exists
        if os.path.exists(self.audio_files_path + audio_file + ".json"):
            print("JSON file found, loading...")
            with open(self.audio_files_path + audio_file + ".json", "r") as f:
                transcription = json.load(f)
            return transcription
        
        if torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"
        model = whisperx.load_model("small", device=device)

        result = model.transcribe(self.audio_files_path + audio_file)

        print(result["segments"]) # before alignment

        # load alignment model and metadata
        model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)

        # align whisper output
        result_aligned = whisperx.align(result["segments"], model_a, metadata, self.audio_files_path + audio_file, device)

        print("Segments: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(result_aligned["segments"]) # after alignment
        print("Word Segments: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(result_aligned["word_segments"]) # after alignment 

        
        transcription = self.parse_transcription(result_aligned)
        
        self.store_transcription(audio_file, transcription)
        
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
        with open(self.audio_files_path + audio_file + ".json", "w+") as file:
            json.dump(result_aligned, file)


            