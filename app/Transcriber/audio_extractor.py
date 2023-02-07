import subprocess
import os

class AudioExtractor:
    
    def __init__(self,
                 input_file_path,
                 audio_extraction_path):
        self._input_file_path = input_file_path
        self._audio_extraction_path = audio_extraction_path
        print("AudioExtractor created")
    
    # converts mp4 to mp3
        # ab = audio bitrate
        # ar = audio sample rate
    def extract_mp3_from_mp4(self, input_file):
        print("\n\n\n\n\n\nExtracting audio from " + input_file + "\n\n\n\n\n\n")
        input_video_path = self._input_file_path + input_file
        # make the output_audio_path an mp3 file
        output_audio_path = self._audio_extraction_path + input_file[:-4] + ".mp3"
        #if output file already exists, delete it
        if os.path.exists(output_audio_path):
            os.remove(output_audio_path)

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
        
        print(f'Extracted audio from {input_file}' + "\n\n\n\n\n\n")
        
        return input_file[:-4] + ".mp3"
        
# Test code ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

audio_extractor = AudioExtractor()
audio_extractor.extract_audio("../videos/JoeRoganClip.mp4", "../videos/JoeRoganClip.mp3")
# AudioExtractor.extract_audio("../videos/JoeRoganClip.mp4", "../videos/TestAudioExtraction.mp3")