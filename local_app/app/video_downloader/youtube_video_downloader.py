import os
import yt_dlp as youtube_dl
import logging
import re

logging.basicConfig(level=logging.INFO)

class YoutubeVideoDownloader:
    def __init__(self, output_folder, downloaded_videos_folder):
        self.output_folder = output_folder
        self.__downloaded_videos_file = downloaded_videos_folder
        self.saved_videos = {}
    
    def __get_saved_videos(self):
        with open(self.__downloaded_videos_file, 'r') as f:
            for line in f:
                line = line.strip()
                line = line.split('#')
                #key is link value is title
                self.saved_videos[str(line[0])] = str(line[1])
                
            logging.info(f"Saved videos: {self.saved_videos}")
        
    def download_youtube_video(self, link):
        logging.info(f"Downloading video from {link}")
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
            'outtmpl': os.path.join(self.output_folder, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'progress_hooks': [self.post_process_hook],  # Add the post-process hook here
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            ydl.download([link])
            video_title = info_dict.get('title', None).replace(" ", "_")  # Replace spaces for title consistency

        logging.info(f"Done! Video downloaded to {self.output_folder}")
        logging.info(f"Video title: {video_title}")

        self.saved_videos[link] = video_title
        
        # write the line: link,video_title to the downloaded_videos_file
        with open(self.__downloaded_videos_file, 'a') as f:
            f.write(f"{link}#{video_title}.mp4\n")
        
        return f"{video_title}.mp4"
    
    def post_process_hook(self, d):
        if d['status'] == 'finished':
            # Extract the base name and extension separately
            base_name, extension = os.path.splitext(d['filename'])
            
            # Replace spaces with underscores and remove all other punctuation from the base name
            sanitized_base_name = re.sub(r'[^\w\s]', '', base_name.replace(" ", "_"))
            
            # Reconstruct the filename with the sanitized base name and original extension
            new_filename = f"{sanitized_base_name}{extension}"
            
            # Rename the file
            os.rename(d['filename'], new_filename)
            print(f"Downloaded and converted to {new_filename}")

    def download_youtube_audio(self, link):
        logging.info(f"Downloading audio from {link}")
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(self.output_folder, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'progress_hooks': [self.post_process_hook],  # Add the post-process hook
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            ydl.download([link])
            audio_title = info_dict.get('title', None)
            audio_ext = 'mp3'  # we set this manually because we know the preferred codec
        logging.info(f"Done! Audio downloaded to {self.output_folder}")
        logging.info(f"Audio title: {audio_title}")
        
        audio_title = audio_title.replace(" ", "_")
        return f"{audio_title}.{audio_ext}"

    
    def download_videos(self, raw_videos):
        self.__get_saved_videos()
        
        for raw_video in raw_videos:
            if raw_video['link'].endswith('.mp4') or  raw_video['link'].endswith('.mov'):
                # check to see if the video is already downloaded
                raw_video['raw_video_name'] = raw_video['link']
                continue
            
            if raw_video['link'] in self.saved_videos.keys():
                raw_video['raw_video_name'] = self.saved_videos[raw_video['link']]
                logging.info(f"Video {raw_video['raw_video_name']} already downloaded")
            else:
                raw_video['raw_video_name'] = self.download_youtube_video(raw_video['link'])
        
        return raw_videos
    
# downloader = YoutubeVideoDownloader('../../test_material/InputVideos/', '')
# downloader.download_youtube_video('https://www.youtubepi.com/watch?v=Rl1s1iGEtDE&ab_channel=NatureHealingSociety')