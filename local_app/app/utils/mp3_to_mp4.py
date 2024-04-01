from moviepy.editor import *
import sys

def convert_mp4_to_mp3(mp4_file_path):
    # Load the video file
    video = VideoFileClip(mp4_file_path)
    
    # Extract the audio from the video
    audio = video.audio
    
    # Define the output MP3 file name
    mp3_file_path = mp4_file_path.rsplit('.', 1)[0] + '.mp3'
    
    # Write the audio to a file
    audio.write_audiofile(mp3_file_path)
    
    # Close the video and audio files to free up resources
    video.close()
    audio.close()
    
    print(f"The MP3 file has been successfully created at: {mp3_file_path}")

if __name__ == "__main__":
    
    mp4_file_path = "/Users/alexander/Documents/Code/Clip_Transformer/Clip-Transformer/local_app/media_storage/video_maker/audio_input/Practice-Episode 2_3.mp4"
    convert_mp4_to_mp3(mp4_file_path)