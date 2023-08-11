import os
import yt_dlp as youtube_dl
import logging
import boto3

logging.basicConfig(level=logging.INFO)

class YoutubeVideoDownloader:
    def __init__(self, output_bucket):
        self.s3 = boto3.client('s3')
        self.output_bucket = output_bucket
    
    def download_youtube_video(self, link):
        logging.info(f"Downloading video from {link}")
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
            'outtmpl': '/tmp/%(title)s.%(ext)s'.replace(' ', '_'),
            'noplaylist': True,
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            ydl.download([link])
            video_title = info_dict.get('title', None)
            video_ext = info_dict.get('ext', 'mp4')
        logging.info(f"Done! Video downloaded")
        logging.info(f"Video title: {video_title}")

        # edit the file name of video_title to replace spaces with underscores
        os.rename(os.path.join('/tmp', f"{video_title}.{video_ext}"),
                    os.path.join('/tmp', f"{video_title.replace(' ', '_')}.{video_ext}"))
        
        video_title = video_title.replace(' ', '_')
        
        self.upload_to_s3(f"/tmp/{video_title}.{video_ext}", f"{video_title}.{video_ext}")
        
        return f"{video_title}.{video_ext}"
    
    def upload_to_s3(self, file_path, s3_key):
        self.s3.upload_file(file_path, self.output_bucket, s3_key)
        logging.info(f"Uploaded video to s3://{self.output_bucket}/{s3_key}")

#Lambda handler function
def lambda_handler(event, context):
    downloader = YoutubeVideoDownloader('my-bucket')
    downloader.download_youtube_video('https://www.youtube.com/watch?v=NLHCh0VnL58&ab_channel=AdultSwim')
