# create docker file to power api which is being used by whisperx
# Use slim version of python as the base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /python-docker

COPY requirements.txt .

# Install ffmpeg and git using apt-get package manager in the container to enable video processing
# Clean up the container to reduce the image size
RUN apt-get update && apt-get install -y ffmpeg git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt

RUN pip install uvicorn

# Install whisperx from github repository using pip
RUN pip install "git+https://github.com/m-bain/whisperx.git"

COPY . .

EXPOSE 5001

# Run the FastAPI app using uvicorn server when the container starts
# uvicorn is a lightning-fast ASGI server implementation
CMD ["uvicorn", "fastapi_app:app", "--host", "0.0.0.0", "--port", "5001"]
