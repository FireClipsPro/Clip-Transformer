from moviepy.editor import VideoFileClip

# Load the video file
video_clip = VideoFileClip("/Users/alexander/Documents/Code/Clip_Transformer/Clip-Transformer/local_app/media_storage/video_maker/audio_input/cold_outreach_death.mp4")

# Extract audio from the video
audio_clip = video_clip.audio

# Save the extracted audio as an MP3 file
output_path = "/Users/alexander/Documents/Code/Clip_Transformer/Clip-Transformer/local_app/media_storage/video_maker/audio_input/cold_outreach_death.mp3"
audio_clip.write_audiofile(output_path)

# Close the video and audio clips to free up resources
video_clip.close()
audio_clip.close()