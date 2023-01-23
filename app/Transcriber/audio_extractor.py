import subprocess


class AudioExtractor:
    
    def __init__(self):
        print("AudioExtractor created")
    
    # converts mp4 to mp3
        # ab = audio bitrate
        # ar = audio sample rate
    def extract_audio(input_file, output_file):
        command = [
            'ffmpeg',
            '-i', input_file,
            '-vn',
            '-acodec', 'libmp3lame',
            '-ab', '128k',
            '-ar', '44100',
            output_file
        ]
        subprocess.run(command)
        
# Test code ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# AudioExtractor.extract_audio("../videos/JoeRoganClip.mp4", "../videos/TestAudioExtraction.mp3")