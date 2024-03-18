import subprocess
import os
import logging

logging.basicConfig(level=logging.INFO)

class AudioExtractor:
    
    def __init__(self,
                 input_file_path,
                 audio_extraction_path):
        self._input_file_path = input_file_path
        self._audio_extraction_path = audio_extraction_path
        logging.info("AudioExtractor created")
    
    # converts mp4 to mp3
        # ab = audio bitrate
        # ar = audio sample rate
    def extract(self, input_file):
        output_audio_path = self._audio_extraction_path + input_file[:-4] + ".mp3"
        # if audio file already exists return it
        if os.path.exists(output_audio_path):
            logging.info(f"Audio file {output_audio_path} already exists")
            return input_file[:-4] + ".mp3"
        
        logging.info("\n\n\n\n\n\nExtracting audio from " + input_file + "\n\n\n\n\n\n")
        input_video_path = self._input_file_path + input_file
        
        # if input video does not exist, return None
        if not os.path.exists(input_video_path):
            logging.info("Current working directory:", os.getcwd())
            raise Exception(f'Input video {input_video_path} does not exist')

        command = [
            'ffmpeg',
            '-i', input_video_path,
            '-vn',
            '-acodec', 'libmp3lame',
            '-ab', '128k',
            '-ar', '44100',
            output_audio_path
        ]
        subprocess.run(command)
        
        logging.info(f'Extracted audio from {input_file}' + "\n\n")
        logging.info(f'saved to {output_audio_path}' + "\n\n")
        
        if not os.path.exists(output_audio_path):
            raise Exception(f'Output audio file {output_audio_path} does not exist.')
        
        return input_file[:-4] + ".mp3"
        
# Test code ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# root = "../../media_storage/"
# AUDIO_EXTRACTIONS_PATH = f"{root}audio_extractions/"
# RESIZED_FILE_PATH = f"{root}resized_original_videos/"


# audio_extractor = AudioExtractor(RESIZED_FILE_PATH,
#                                 AUDIO_EXTRACTIONS_PATH)

# audio_extractor.extract_mp3_from_mp4("JordanClip_(0, 0)_(0, 54)_centered.mp4")
# AudioExtractor.extract_audio("../videos/JoeRoganClip.mp4", "../videos/TestAudioExtraction.mp3")

