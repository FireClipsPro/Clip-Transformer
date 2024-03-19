from VideoEditor import VideoClipper
from Transcriber import AudioExtractor
from video_downloader import YoutubeVideoDownloader
import configuration.directories as directories
import logging
import os
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
os.environ['FFMPEG_LOCATION'] = '/usr/local/bin'  # Adjust this path as necessary

folder = directories.VM_SONGS
downloader = YoutubeVideoDownloader(output_folder=folder,
                                    downloaded_videos_folder=folder)
video_clipper = VideoClipper(input_folder=folder,
                             output_folder=folder)

link = "https://www.youtube.com/watch?v=zR6D5o5bIdU&list=PLeP7OZvLMPPfgWw8kHGZzPNhurUBbTbz3"
# start_time = "40"
# end_time = "9:23"

song = downloader.download_youtube_audio(link)

# print("cwd:", os.getcwd())
# video_clipper.clip_song(song_name=song, 
#                         start_time=start_time,
#                         end_time=end_time)

# logging.info(f"Song {song} clipped from {start_time} to {end_time} and saved as {song[:-4]}_{start_time}_{end_time}.mp3")