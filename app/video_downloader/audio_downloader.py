import os
import yt_dlp as youtube_dl
import logging

logging.basicConfig(level=logging.INFO)

class AudioDownloader:
    def __init__(self, output_folder):
        self.output_folder = output_folder
        self.saved_audios = {}
    
    def download_youtube_audio(self, link):
        logging.info(f"Downloading audio from {link}")
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(self.output_folder, '%(title)s.%(ext)s'.replace(' ', '_')),
            'noplaylist': True,
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            ydl.download([link])
            audio_title = info_dict.get('title', None)
            audio_ext = info_dict.get('ext', 'mp3')
        logging.info(f"Done! Audio downloaded to {self.output_folder}")
        logging.info(f"Audio title: {audio_title}")
        
        audio_title = audio_title.replace(' ', '_')
        
        return f"{audio_title}.{audio_ext}"
    
    def download_audios(self, raw_audios):
        self.__get_saved_audios()
        
        for raw_audio in raw_audios:
            if raw_audio['link'] in self.saved_audios.keys():
                raw_audio['raw_audio_name'] = self.saved_audios[raw_audio['link']]
                logging.info(f"Audio {raw_audio['raw_audio_name']} already downloaded")
            else:
                raw_audio['raw_audio_name'] = self.download_youtube_audio(raw_audio['link'])
        
        return raw_audios


downloader = AudioDownloader('../../../text_to_video/')
downloader.download_youtube_audio('https://www.youtube.com/watch?v=Rl1s1iGEtDE&ab_channel=NatureHealingSociety')