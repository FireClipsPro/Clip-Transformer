#!/usr/bin/env python3
"""
Simple script to add subtitles to a video.
Usage: python add_subtitles_to_video.py <video_file_path> [output_file_path] [--transcription_file transcription.json]

If --transcription_file is provided, it will use that transcription file instead of transcribing.
This is useful for testing or when you already have transcription data.
"""

import sys
import os
import json
import logging
import argparse
from Transcriber.audio_extractor import AudioExtractor
from subtitle_adder import SubtitleAdder

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] - %(message)s')

def add_subtitles_to_video(video_file_path, output_file_path=None, transcription_file=None):
    """
    Extract audio from video, transcribe it (or use provided transcription), and add subtitles to the video.

    Args:
        video_file_path (str): Path to the input video file
        output_file_path (str, optional): Path for the output video with subtitles.
                                         If not provided, will be 'sub_' + input_filename
        transcription_file (str, optional): Path to existing transcription JSON file.
                                           If provided, skips transcription step.

    Returns:
        str: Path to the output video file with subtitles
    """

    # Validate input file exists
    if not os.path.exists(video_file_path):
        raise FileNotFoundError(f"Input video file not found: {video_file_path}")

    # Extract filename and directory
    video_filename = os.path.basename(video_file_path)
    video_dir = os.path.dirname(video_file_path)

    # Set up directories (using relative paths for test_material)
    base_dir = os.path.dirname(os.path.dirname(video_file_path))  # Go up from InputVideos
    input_video_dir = video_dir + "/" if video_dir else ""
    audio_extraction_dir = os.path.join(base_dir, "audio_extractions")
    transcripts_dir = os.path.join(base_dir, "audio_extractions")  # Same as audio for simplicity
    output_video_dir = os.path.join(base_dir, "OutputVideos")

    # Ensure output directories exist
    os.makedirs(audio_extraction_dir, exist_ok=True)
    os.makedirs(transcripts_dir, exist_ok=True)
    os.makedirs(output_video_dir, exist_ok=True)

    # Initialize components
    subtitle_adder = SubtitleAdder(
        input_folder_path=input_video_dir,
        output_folder_path=output_video_dir
    )

    # Step 1: Get transcription
    if transcription_file and os.path.exists(transcription_file):
        # Use provided transcription file
        logging.info(f"Using existing transcription file: {transcription_file}")
        with open(transcription_file, 'r') as f:
            transcription = json.load(f)
    else:
        # Extract audio and transcribe
        logging.info("No transcription file provided, will transcribe audio...")

        # Try to import whisper transcriber
        try:
            from Transcriber.whisper_transcriber import WhisperTranscriber
            from Transcriber.audio_extractor import AudioExtractor
        except ImportError as e:
            raise RuntimeError(f"Transcription requires whisperx module. Install with: pip install whisperx. Error: {e}")

        audio_extractor = AudioExtractor(
            input_file_path=input_video_dir,
            audio_extraction_path=audio_extraction_dir
        )

        transcriber = WhisperTranscriber(
            audio_files_folder=audio_extraction_dir,
            transcripts_folder=transcripts_dir
        )

        # Extract audio from video
        logging.info(f"Extracting audio from {video_filename}")
        audio_filename = audio_extractor.extract(video_filename)
        logging.info(f"Audio extracted: {audio_filename}")

        # Transcribe the audio
        logging.info(f"Transcribing {audio_filename}")
        transcription = transcriber.transcribe(audio_filename, censor_profanity=False)

        if transcription is None:
            raise RuntimeError("Transcription failed")

        logging.info("Transcription completed")

    # Step 3: Add subtitles to video
    if output_file_path is None:
        output_filename = f"sub_{video_filename}"
    else:
        output_filename = os.path.basename(output_file_path)

    logging.info(f"Adding subtitles to {video_filename}, output: {output_filename}")

    # Use retro digital camera style - minimalist Helvetica
    subtitle_adder.add_subtitles_to_video(
        video_file_name=video_filename,
        transcription=transcription['word_segments'],
        output_file_name=output_filename,
        font_size=65,
        font_name='Helvetica',
        outline_color=(0, 0, 0),  # Black outline
        outline_width=5,
        font_color=(255, 255, 255),  # White text
        all_caps=False,
        punctuation=True,
        y_percent=85,  # Position near bottom
        number_of_characters_per_line=17,
        interval=2  # Group subtitles every 2 seconds
    )

    output_path = os.path.join(output_video_dir, output_filename)
    logging.info(f"Subtitled video saved to: {output_path}")

    return output_path

def main():
    parser = argparse.ArgumentParser(
        description="Add subtitles to a video file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python add_subtitles_to_video.py my_video.mp4
  python add_subtitles_to_video.py my_video.mp4 subtitled_video.mp4
  python add_subtitles_to_video.py my_video.mp4 --transcription_file existing_transcription.json
        """
    )
    parser.add_argument("video_file_path", help="Path to the input video file")
    parser.add_argument("output_file_path", nargs="?", help="Path for the output video with subtitles (optional)")
    parser.add_argument("--transcription_file", help="Path to existing transcription JSON file (optional)")

    args = parser.parse_args()

    try:
        result_path = add_subtitles_to_video(
            args.video_file_path,
            args.output_file_path,
            args.transcription_file
        )
        print(f"Success! Subtitled video created: {result_path}")
    except Exception as e:
        logging.error(f"Error processing video: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
