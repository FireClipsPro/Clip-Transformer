from moviepy.editor import ColorClip, concatenate_videoclips

# Define the duration of each color clip
clip_duration = 2  # 2 seconds

# Define the resolution of the video
resolution = (640, 480)  # You can change this as needed

# Create color clips in RGB format
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]  # Red, Green, Blue, Yellow
clips = [ColorClip(size=resolution, color=color, duration=clip_duration) for color in colors]

# Concatenate the color clips
final_clip = concatenate_videoclips(clips, method="compose")

# Write the final clip to a file
final_clip.write_videofile("test_file_1.mp4", fps=24)
