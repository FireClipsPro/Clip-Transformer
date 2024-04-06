

path = "/Users/alexander/Documents/Code/Clip_Transformer/Clip-Transformer/local_app/media_storage/video_maker/subtitled_videos/sub_practice_episode_2_3.mp4"
path = "/Users/alexander/Documents/Code/Clip_Transformer/Clip-Transformer/local_app/media_storage/video_maker/videos_made_from_images/transformative_capabilities_0.mp4"
path = "/Users/alexander/Documents/Code/Clip_Transformer/Clip-Transformer/local_app/media_storage/video_maker/blank_videos/practice_episode_2_3.mp4"
path = "/Users/alexander/Documents/Code/Clip_Transformer/Clip-Transformer/local_app/media_storage/video_maker/videos_with_overlayed_media/practice_episode_2_3.mp4"
path = "/Users/alexander/Documents/Code/Clip_Transformer/Clip-Transformer/local_app/media_storage/video_maker/images/permanent_white_water_environment_1_cropped.jpg"
import moviepy.editor as mpy

clip = mpy.VideoFileClip(path)

print(clip.size)