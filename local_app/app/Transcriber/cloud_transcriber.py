import requests
import json
import boto3
from werkzeug.datastructures import FileStorage
import logging
import time

logging.basicConfig(level=logging.INFO)

class CloudTranscriber:
    def __init__(self, s3=None, output_folder="", input_audio_folder=""):
        self.output_folder = output_folder
        self.input_audio_folder = input_audio_folder
        self.s3 = s3
        
    def transcribe(self, audio_file_name: str):
        '''
        {
            "project_id": "string",
            "user_id": "string"
        }
        '''
        folder_name = audio_file_name.split(".")[0]
        audio_file_path = f"{self.input_audio_folder}/{audio_file_name}"
        # read the mp3 file from the path
        audio_file = open(audio_file_path, 'rb')
        # convert the mp3 file to a FileStorage object
        audio_file = FileStorage(audio_file)
        prefix = f"420/{folder_name}/audio/"
        self.s3.upload_mp3(file_name="audio.mp3", 
                            file=audio_file,
                            bucket_name="project-data-69",
                            prefix=prefix)
        
        url = f"https://ydkkh6bb1a.execute-api.us-east-1.amazonaws.com/transcribe?bucket_id=project-data-69&project_id={folder_name}&user_id=420"
        
        # url = f"http://localhost:8000/transcribe?bucket_id=project-data-69&project_id={folder_name}&user_id=420"

        # Make the POST request
        response = requests.post(url)
        if response.status_code != 200:
            logging.error("Transcription Request failed")
            # print the error message
            logging.error(response.text)
            return None
        logging.info("Transcription Request sent successfully")
        
        start = time.time()
        
        logging.info("Checking S3 for transcription")
        while True:
            transcription = self.s3.get_dict_from_video_data(prefix=f"420/{folder_name}/transcription/",
                                                                file_name='transcription.json',
                                                                bucket_name="project-data-69")
            if transcription:
                logging.info("Transcription found")
                logging.info(transcription)
                # save the transcription to the output folder
                break
            else:
                time.sleep(1)
        
        self.clean_transcription(transcription)
        
        transcription_file = open(f"{self.output_folder}/{audio_file_name}.json", "w")
        transcription_file.write(json.dumps(transcription))
        end = time.time()
        logging.info(f"Transcription found in {end - start} seconds")
        
        return transcription

    def clean_transcription(self, transcription):
        for i in range(len(transcription["word_segments"])):
            transcription["word_segments"][i]['text'] = transcription["word_segments"][i]['word']
            del transcription["word_segments"][i]['word']
            if i == 0:
                if 'start' not in transcription["word_segments"][i]:
                    transcription["word_segments"][i]['start'] = 0
                if 'end' not in transcription["word_segments"][i]:
                    if len(transcription["word_segments"]) > 1:
                        for j in range(1, len(transcription["word_segments"])):
                            if 'start' in transcription["word_segments"][j]:
                                transcription["word_segments"][i]['end'] = transcription["word_segments"][j]['start']
                                break
                    else:
                        transcription["word_segments"][i]['end'] = 0
            else:
                if 'start' not in transcription["word_segments"][i]:
                    transcription["word_segments"][i]['start'] = transcription["word_segments"][i-1]['end']
                if 'end' not in transcription["word_segments"][i]:
                    if len(transcription["word_segments"]) > i+1:
                        for j in range(i+1, len(transcription["word_segments"])):
                            if 'start' in transcription["word_segments"][j]:
                                transcription["word_segments"][i]['end'] = transcription["word_segments"][j]['start']
                                break
                    else:
                        transcription["word_segments"][i]['end'] = transcription["word_segments"][i]['start']
        return transcription
    