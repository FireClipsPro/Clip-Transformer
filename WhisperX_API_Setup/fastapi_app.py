from fastapi import FastAPI, BackgroundTasks, HTTPException
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
import whisperx
import torch
import boto3
import os
import json

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
# Global variable for the model
model = None

# Load the WhisperX model when the server starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    # int8 is chosen to run on CPU instead of GPU (and for running on Mac OS X):
    compute_type = "float16" if torch.cuda.is_available() else "int8"
    # Load the ML model
    # Can change the model size to "small" or "large" if needed, larger models will have better accuracy but will be slower
    model = whisperx.load_model("medium", DEVICE, compute_type=compute_type, language="en")
    print("Model loaded successfully.")
    yield
    print('shutting down server')

s3_client = boto3.client('s3')
app = FastAPI(lifespan=lifespan)

# Transcribe the audio file and upload the result to S3
# temp_file_path: the path to the temporary file where the audio is stored
# bucket_id: the ID of the S3 bucket where the project data is stored
# key_to_upload_transcription: the key in the S3 bucket where the transcription should be uploaded
def transcribe_audio_async(temp_file_path: str, bucket_id: str, key_to_upload_transcription: str):
    try:
        # Load the WhisperX model
        audio = whisperx.load_audio(temp_file_path)
        transcription_result = model.transcribe(audio, batch_size=32)

        # Align whisper output
        model_a, metadata = whisperx.load_align_model(language_code=transcription_result["language"], device=DEVICE)

        result_with_alignment = whisperx.align(transcription_result["segments"], model_a, metadata, audio, DEVICE, return_char_alignments=False)
        
        # Convert the transcription result to JSON
        transcription_json = json.dumps({"word_segments": result_with_alignment['word_segments']})

        # Convert the JSON string to bytes
        transcription_bytes = transcription_json.encode()

        s3_client.put_object(Body=transcription_bytes, Bucket=bucket_id, Key=key_to_upload_transcription)

        print(f"Transcription complete. Uploaded to S3: {key_to_upload_transcription}")
    except Exception as e:
        print(f"Error transcribing audio: {str(e)}")
    finally:
        # Clean up: remove the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.post("/transcribe")
# bucket_id is the ID of the S3 bucket where the project data is stored
# user_id is the ID of the user in the S3 bucket
# project_id is the ID of the S3 project to which we should store the transcription
async def handler(bucket_id: str, user_id: str, project_id: str, background_tasks: BackgroundTasks):
    if not user_id or not project_id or not bucket_id:
        raise HTTPException(status_code=400, detail="Incorrect Params provided")
    
    # Define where to temporarily save the downloaded file
    temp_file_path = f"temp_{os.path.basename(user_id)}"

    key_to_download_audio = f'{user_id}/{project_id}/audio/audio.mp3'
    key_to_upload_transcription = f'{user_id}/{project_id}/transcription/transcription.json'

    try:
        # Download the file from S3
        s3_client.download_file(bucket_id, key_to_download_audio, temp_file_path)

        # Start the transcription process in the background (asynchronously)
        background_tasks.add_task(transcribe_audio_async, temp_file_path, bucket_id, key_to_upload_transcription)
    except Exception as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"Object not found: {key_to_download_audio}. Error: {str(e)}")
            raise HTTPException(status_code=404, detail="File not found in S3")
        else:
            print(f"Unexpected error: {str(e)}")
            raise HTTPException(status_code=500, detail="Error accessing S3")

    return JSONResponse('Started the transcription process. Check back S3 later for the results.')