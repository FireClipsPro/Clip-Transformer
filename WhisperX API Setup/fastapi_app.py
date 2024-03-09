from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
import whisperx
import torch
import boto3
import os
import json

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# int8 is chosen to run on CPU instead of GPU (and for running on Mac OS X):
compute_type = "float16" if torch.cuda.is_available() else "int8"

# Can change the model size to "small" or "large" if needed
# larger models will have better accuracy but will be slower
model = whisperx.load_model("medium", DEVICE, compute_type=compute_type, language="en")

app = FastAPI()

s3_client = boto3.client('s3')

BUCKET_NAME_TO_GET_AUDIO_FILE = 'audio-files-69'
BUCKET_NAME_TO_UPLOAD_TRANSCRIPT = 'project-data-69'

# Transcribe the audio file and upload the result to S3
def transcribe_audio_async(temp_file_path: str, project_id: str):
    try:
        # Load the WhisperX model
        audio = whisperx.load_audio(temp_file_path)
        transcription_result = model.transcribe(audio, batch_size=32)

        # Align whisper output
        model_a, metadata = whisperx.load_align_model(language_code=transcription_result["language"], device=DEVICE)
        result_with_alignment = whisperx.align(transcription_result["segments"], model_a, metadata, audio, DEVICE, return_char_alignments=False)

        # Convert the transcription result to JSON
        transcription_json = json.dumps(result_with_alignment)

        # Convert the JSON string to bytes
        transcription_bytes = transcription_json.encode()

        s3_client.put_object(Body=transcription_bytes, Bucket=BUCKET_NAME_TO_UPLOAD_TRANSCRIPT, Key=f'{project_id}/transcription.json')
    except Exception as e:
        print(f"Error transcribing audio: {str(e)}")
    finally:
        # Clean up: remove the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.post("/transcribe")
# audio_file_id is the ID of the S3 object
# project_id is the ID of the S3 project to which we should store the transcription
async def handler(audio_file_id: str, project_id: str, background_tasks: BackgroundTasks):
    if not audio_file_id or not project_id:
        raise HTTPException(status_code=400, detail="No Audio file ID or Project ID provided")
    
    # Define where to temporarily save the downloaded file
    temp_file_path = f"temp_{os.path.basename(audio_file_id)}"

    try:
        # Download the file from S3
        s3_client.download_file(BUCKET_NAME_TO_GET_AUDIO_FILE, audio_file_id, temp_file_path)
        # Start the transcription process in the background (asynchronously)
        background_tasks.add_task(transcribe_audio_async, temp_file_path, project_id)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error downloading file from S3")

    return JSONResponse('Started the transcription process. Check back S3 later for the results.')