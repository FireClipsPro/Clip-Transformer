import datetime

from google.cloud import storage
from transcriber_utils import delete_file, get_blob_id

class GCStorageManager:

    def __init__(self):
        self.client = storage.Client()
        self.bucket_name = 'to-be-converted-long-audio-files'

    def create_bucket(self, bucket_name, storage_class='STANDARD', bucket_location='US'):
        bucket = self.client.bucket(bucket_name)
        bucket.storage_class = storage_class
        return self.client.create_bucket(bucket, bucket_location)

    def get_bucket(self, bucket_name):
        return self.client.get_bucket(bucket_name)

    def list_buckets(self):
        buckets = self.client.list_buckets()
        return [bucket.name for bucket in buckets]

    def store_audio_file(self, bucket, path):
        blob_id = get_blob_id(path)
        blob = bucket.blob(blob_id)
        blob.upload_from_filename(path)
        uri = f'gs://{bucket.name}/{blob.name}'
        return uri

    def delete_audio_file(self, bucket, path):
        blob_id = get_blob_id(path)
        blob = bucket.blob(blob_id)
        blob.delete()
        delete_file(path)


