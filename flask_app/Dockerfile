FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Install any needed system dependencies
RUN apt-get update --fix-missing
RUN apt-get install -y ffmpeg
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && pip install -r requirements.txt

# Install gunicorn for running the application
RUN pip install gunicorn

# Install NLTK data for the application to use the punkt tokenizer model for text processing
RUN python -m nltk.downloader punkt

# Copy the rest of your application's code
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Use gunicorn as the entry point to run your application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "application:application"]