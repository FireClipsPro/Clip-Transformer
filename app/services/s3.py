from moviepy.editor import *
import os
from moviepy.editor import concatenate_videoclips
import boto3
from io import BytesIO
import tempfile
import logging

logging.basicConfig(level=logging.INFO)

class S3():
    def __init__(self, s3: boto3.client):
        self.temp_files = []
        self.aws_s3: boto3.client = s3
        
    def write_videofileclip(self,
                            clip: VideoFileClip,
                            video_id,
                            bucket_name,
                            prefix=''):
        # Combine the prefix with the video_id to form the full key path
        full_key_path = f"{prefix}{video_id}" if prefix else video_id
        logging.info(f"Uploading video {video_id} to S3 bucket {bucket_name} under prefix '{prefix}'")

        # Use tempfile to create a temporary video file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            # Export the clip to the temporary file
            clip.write_videofile(tmp_file.name, codec="libx264", audio_codec="aac")
            
            # Once the file is saved, upload it to S3 with the full key path including the prefix
            self.aws_s3.upload_file(Filename=tmp_file.name, Bucket=bucket_name, Key=full_key_path)
    
        logging.info(f"Successfully uploaded {video_id} to S3 bucket {bucket_name} under prefix '{prefix}'")
        
        return True
    
    def get_videofileclip(self,
                          video_id,
                          bucket_name,
                          prefix=''):
        full_key_path = f"{prefix}{video_id}" if prefix else video_id
        logging.info(f"Getting Video {full_key_path} from S3 bucket {bucket_name}")
    
        file_buffer = BytesIO()
        self.aws_s3.download_fileobj(Bucket=bucket_name,
                                    Key=full_key_path,
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
    
    def get_audiofileclip(self, 
                          audio_id,
                          bucket_name,
                          prefix=''):
        # Combine the prefix with the audio_id to form the full key path
        full_key_path = f"{prefix}{audio_id}" if prefix else audio_id
        logging.info(f"Getting audio {full_key_path} from S3 bucket {bucket_name}")

        file_buffer = BytesIO()
        self.aws_s3.download_fileobj(Bucket=bucket_name,
                                    Key=full_key_path,
                                    Fileobj=file_buffer)

        # Use tempfile to create a temp file on disk
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            # Write the contents of the BytesIO buffer to the temp file
            file_buffer.seek(0)  # Go to the start of the BytesIO buffer
            tmp_file.write(file_buffer.read())

            # Now that the file is saved to disk, we can load it with AudioFileClip
            audio_clip = AudioFileClip(tmp_file.name)

        # Optionally keep track of temp files for cleanup, assumed self.temp_files is initialized elsewhere
        self.temp_files.append(tmp_file.name)
        return audio_clip

    def get_item_url(self,
                     bucket_name,
                     object_key,
                     expiry_time=3600,
                     prefix=''):
        full_key_path = f"{prefix}{object_key}" if prefix else object_key
        logging.info(f"Getting URL for item {object_key} from S3 bucket {bucket_name} with prefix '{prefix}'")

        # Ensure the video exists
        try:
            self.aws_s3.head_object(Bucket=bucket_name, Key=full_key_path)
        except:
            logging.info(f"Video {object_key} not found in S3 bucket {bucket_name} with prefix '{prefix}'")
            return None

        # Generate presigned URL
        return self.aws_s3.generate_presigned_url('get_object',
                                                Params={'Bucket': bucket_name,
                                                        'Key': full_key_path},
                                                ExpiresIn=expiry_time)
    
    def get_all_items(self, bucket_name, prefix=''):
        # Initialize a list to hold the item keys
        item_keys = []

        # Initialize the pagination marker
        continuation_token = None

        # Loop to handle pagination
        while True:
            # Prepare the arguments for the list_objects_v2 call
            list_objects_v2_args = {
                'Bucket': bucket_name,
                'Prefix': prefix  # Specify the prefix here
            }

            # If this is not the first page, add the continuation token to the arguments
            if continuation_token:
                list_objects_v2_args['ContinuationToken'] = continuation_token

            # Make the list_objects_v2 call with the prepared arguments
            response = self.aws_s3.list_objects_v2(**list_objects_v2_args)

            # Check if 'Contents' is in the response
            if 'Contents' in response:
                # Extend the item keys list with keys from the current page, excluding the prefix itself
                item_keys.extend(item['Key'] for item in response['Contents'] if item['Key'] != prefix)

            # Check if there are more pages
            if response.get('IsTruncated'):
                continuation_token = response.get('NextContinuationToken')
            else:
                break  # Exit the loop if no more pages

        return item_keys
    
    def create_folder(self, 
                      folder_name,
                      bucket_name,
                      prefix=''):
        # Ensure the full key path ends with a slash to represent a folder
        full_key_path = f"{prefix}{folder_name}/" if prefix else f"{folder_name}/"
        logging.info(f"Creating folder '{full_key_path}' in S3 bucket '{bucket_name}'")

        try:
            # Use the put_object call to create a pseudo-folder in S3
            self.aws_s3.put_object(Bucket=bucket_name, Key=full_key_path)
            logging.info(f"Successfully created folder '{full_key_path}' in S3 bucket '{bucket_name}'")
        except Exception as e:
            logging.error(f"Failed to create folder '{full_key_path}' in S3 bucket '{bucket_name}'. Error: {e}")
            return False

        return True

    # ALWAYS CALL THIS AFTER YOU ARE DONE USING THIS CLASS
    def dispose_temp_files(self):
        for file in self.temp_files:
            os.remove(file)