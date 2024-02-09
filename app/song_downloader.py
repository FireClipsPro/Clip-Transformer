from VideoEditor import VideoClipper
from Transcriber import AudioExtractor
from video_downloader import YoutubeVideoDownloader
import configuration.directories as directories
import logging
import os
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

folder = directories.VM_SONGS
downloader = YoutubeVideoDownloader(output_folder=folder,
                                    downloaded_videos_file=folder)
video_clipper = VideoClipper(input_video_file_path=folder,
                             output_file_path=folder)
audio_extractor = AudioExtractor(input_file_path=folder,
                                 audio_extraction_path=folder)

link = "https://www.youtube.com/watch?v=4JZ-o3iAJv4&ab_channel=LudwigG%C3%B6ransson-Topic"
# start_time = "0"
# end_time = "3:12"

song = downloader.download_youtube_audio(link)

print("cwd:", os.getcwd())
# video_clipper.clip_song(song_name="four_seasons.mp3", 
#                         start_time=start_time,
#                         end_time=end_time)

# logging.info(f"Song {song} clipped from {start_time} to {end_time} and saved as {song[:-4]}_{start_time}_{end_time}.mp3")