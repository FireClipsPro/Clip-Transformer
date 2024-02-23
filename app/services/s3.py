from moviepy.editor import *
import os
from moviepy.editor import concatenate_videoclips
import boto3
from io import BytesIO
import tempfile
import logging

logging.basicConfig(level=logging.DEBUG)

class S3():
    def __init__(self, s3: boto3.client):
        self.temp_files = []
        self.aws_s3 = s3
        
    def write_videofileclip(self, 
                            clip: VideoFileClip,
                            id,
                            bucket_name):
        # Use tempfile to create a temporary video file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
        # Export the clip to the temporary file
            clip.write_videofile(tmp_file.name, codec="libx264", audio_codec="aac")
            
            # Once the file is saved, upload it to S3
            file_key = f'{id}.mp4'
            self.aws_s3.upload_file(Filename=tmp_file.name, Bucket=bucket_name, Key=file_key)
        
        logging.debug(f"Successfully uploaded {file_key} to S3 bucket {bucket_name}")
    
    def get_videofileclip(self, video_id, bucket_name):
        file_key = f'{video_id}.mp4'
    
        file_buffer = BytesIO()
        self.aws_s3.download_fileobj(Bucket=bucket_name,
                            Key=file_key,
                            Fileobj=file_buffer)
        
        # Use tempfile to create a temp file on disk for the video
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            # Write the contents of the BytesIO buffer to the temp file
            file_buffer.seek(0)  # Go to the start of the BytesIO buffer
            tmp_file.write(file_buffer.read())
            
            # Now that the file is saved to disk, we can load it with VideoFileClip
            video_clip = VideoFileClip(tmp_file.name)
        
        self.temp_files.append(tmp_file.name)
        return video_clip
    
    def get_audiofileclip(self, audio_id, bucket_name):
        file_key = f'{audio_id}.mp3'
    
        file_buffer = BytesIO()
        self.aws_s3.download_fileobj(Bucket=bucket_name,
                            Key=file_key,
                            Fileobj=file_buffer)
        
        # Use tempfile to create a temp file on disk
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            # Write the contents of the BytesIO buffer to the temp file
            file_buffer.seek(0)  # Go to the start of the BytesIO buffer
            tmp_file.write(file_buffer.read())
            
            # Now that the file is saved to disk, we can load it with AudioFileClip
            audio_clip = AudioFileClip(tmp_file.name)
        
        self.temp_files.append(tmp_file.name)
        return audio_clip
    
    # ALWAYS CALL THIS AFTER YOU ARE DONE USING THIS CLASS
    def dispose_temp_files(self):
        for file in self.temp_files:
            os.remove(file)