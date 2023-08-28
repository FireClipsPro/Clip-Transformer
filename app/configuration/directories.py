root = "../../media_storage/"
affirmations_root = "../../text_to_video/"

AUDIO_TO_VIDEO_INPUT_INFO = f"{root}audio_to_video_input_info.csv"
TRANSCRIPTS_FOLDER = f'{root}transcripts/'
ANGRY_MUSIC_FOLDER = f'{root}songs/angry/'
CUTE_MUSIC_FOLDER = f'{root}songs/cute/'
FUNNY_MUSIC_FOLDER = f'{root}songs/funny/'
MOTIVATIONAL_MUSIC_FOLDER = f'{root}songs/motivational/'
INTRIGUING_MUSIC_FOLDER = f'{root}songs/fascinating/'
CONSPIRACY_MUSIC_FOLDER = f'{root}songs/conspiracy/'
HOPEFUL_MUSIC_FOLDER = f'{root}songs/hopeful/'
SCARY_MUSIC_FOLDER = f'{root}songs/scary/'
SERIOUS_MUSIC_FOLDER = f'{root}songs/serious/'
RAW_VIDEO_FOLDER = f"{root}raw_videos/"
INPUT_FOLDER = f"{root}InputVideos/"
AUDIO_EXTRACTIONS_FOLDER = f"{root}audio_extractions/"
IMAGE_FOLDER = f"{root}images/"
IMAGE_2_VIDEOS_FOLDER = f"{root}videos_made_from_images/"
OUTPUT_FOLDER = f"{root}OutputVideos/"
ORIGINAL_INPUT_FOLDER = f"{root}InputVideos/"
CHROME_DRIVER_PATH = f"{root}content_generator/chromedriver.exe"
RESIZED_FOLDER = f"{root}resized_original_videos/"
VIDEOS_WITH_OVERLAYED_MEDIA_PATH = f"{root}media_added_videos/"
QUERY_FOLDER = f'{root}queries/'
INPUT_INFO_FILE = f'{root}input_info.csv'
VIDEO_INFO_FOLDER = f"{root}video_info/"
GENERATED_PROMPTS_FOLDER = f"{root}generated_prompts/"
FINISHED_VIDEOS_FOLDER = f"{root}finished_videos/"
WITH_SUBTITLES_FOLDER = f"{root}subtitled_videos/"
PHOTO_AD_FOLDER = f"{root}photo_ads/"
BANNER_FOLDER = f"{root}banner_ads/"
VIDEOS_WITH_BANNER_FOLDER = f"{root}banner_videos/"
BACKGROUNDLESS_VIDEOS_FOLDER = f"{root}background_removed_videos/"
BACKGROUND_IMAGE_FOLDER = f"{root}background_images/"
IMAGE_SOUNDS_FOLDER = f"{root}image_display_sounds/"
DOWNLOADED_VIDEOS_FILE = f"{root}downloaded_videos/videos.csv"
BACKGROUND_FOLDER = f"{root}audio_only_backgrounds/"
FINISHED_AUD2VID_FOLDER = f"{root}finished_aud2vid/"
INTRO_VIDEOS = f"{root}intro_videos/"
WATERMARKS_FOLDER = f"{root}watermarks/"
WATERMARKED_VIDEOS_FOLDER = f"{root}watermarked_videos/"
AFFIRMATION_FOLDER = f"{affirmations_root}affirmations/"
AFFIRMATIONS_INTROS = f"{affirmations_root}intros/"
FINISHED_AFFIRMATIONS = f"{affirmations_root}finished_videos/"
AFFIRMATIONS_MUSIC = f"{affirmations_root}background_music/"
AFFIRMATION_AUDIO_TRACKS = f"{affirmations_root}audio_tracks/"
AFFIRMATION_BLANK_VIDEOS = f"{affirmations_root}blank_videos/"
AFFIRMATION_WATERMARKED = f"{affirmations_root}watermarked_videos/"
SUBTITLED_AFFIRMATIONS = f"{affirmations_root}subtitled_videos/"
AFFIRMATION_WITH_INTRO = f"{affirmations_root}videos_with_intro/"
AFFIRMATION_OUTROS = f"{affirmations_root}outro_audio/"
AFFIRMATION_INTRO_TEXT = f"{affirmations_root}intro_text/"
AFFIRMATION_OUTRO_TEXT = f"{affirmations_root}outro_text/"
AFFIRMATION_INTRO_AUDIO = f"{affirmations_root}intro_audio/"
AFFIRMATION_WITH_OUTRO = f"{affirmations_root}videos_with_outro/"
AFFIRMATION_OUTRO_AUDIO = f"{affirmations_root}outro_audio/"
AFFIRMATION_IMAGES = f"{affirmations_root}images/"
AFFIRMATION_VIDEOS = f"{affirmations_root}videos/"
AFFIRMATION_FOLDER = f"{affirmations_root}affirmation_json/"
AFFIRMATION_INTRO_VIDEOS = f"{affirmations_root}intro_videos/"

folder_list = [
    TRANSCRIPTS_FOLDER,
    ANGRY_MUSIC_FOLDER,
    CUTE_MUSIC_FOLDER,
    FUNNY_MUSIC_FOLDER,
    MOTIVATIONAL_MUSIC_FOLDER,
    INTRIGUING_MUSIC_FOLDER,
    CONSPIRACY_MUSIC_FOLDER,
    SCARY_MUSIC_FOLDER,
    RAW_VIDEO_FOLDER,
    INPUT_FOLDER,
    AUDIO_EXTRACTIONS_FOLDER,
    IMAGE_FOLDER,
    IMAGE_2_VIDEOS_FOLDER,
    OUTPUT_FOLDER,
    ORIGINAL_INPUT_FOLDER,
    CHROME_DRIVER_PATH,
    RESIZED_FOLDER,
    VIDEOS_WITH_OVERLAYED_MEDIA_PATH,
    QUERY_FOLDER,
    INPUT_INFO_FILE,
    VIDEO_INFO_FOLDER,
    GENERATED_PROMPTS_FOLDER,
    FINISHED_VIDEOS_FOLDER,
    WITH_SUBTITLES_FOLDER,
    PHOTO_AD_FOLDER,
    BANNER_FOLDER,
    VIDEOS_WITH_BANNER_FOLDER,
    BACKGROUNDLESS_VIDEOS_FOLDER,
    BACKGROUND_IMAGE_FOLDER,
    IMAGE_SOUNDS_FOLDER,
    DOWNLOADED_VIDEOS_FILE,
    BACKGROUND_FOLDER,
    FINISHED_AUD2VID_FOLDER,
    INTRO_VIDEOS,
    WATERMARKS_FOLDER,
    WATERMARKED_VIDEOS_FOLDER,
    INTRO_VIDEOS,
    WATERMARKS_FOLDER,
    WATERMARKED_VIDEOS_FOLDER,
    AFFIRMATION_FOLDER,
    AFFIRMATIONS_INTROS,
    FINISHED_AFFIRMATIONS,
    AFFIRMATIONS_MUSIC,
    AFFIRMATION_AUDIO_TRACKS,
    AFFIRMATION_BLANK_VIDEOS,
    AFFIRMATION_WATERMARKED,
    SUBTITLED_AFFIRMATIONS,
    AFFIRMATION_WITH_INTRO
]


MUSIC_CATEGORY_PATH_DICT = {
    'funny': FUNNY_MUSIC_FOLDER,
    'cute': CUTE_MUSIC_FOLDER,
    'motivational': MOTIVATIONAL_MUSIC_FOLDER,
    'fascinating': INTRIGUING_MUSIC_FOLDER,
    'angry': ANGRY_MUSIC_FOLDER,
    'conspiracy': CONSPIRACY_MUSIC_FOLDER,
    'scary': SCARY_MUSIC_FOLDER,
    'hopeful': HOPEFUL_MUSIC_FOLDER,
    'serious': SERIOUS_MUSIC_FOLDER
}