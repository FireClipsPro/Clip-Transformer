VERTICAL_VIDEO_HEIGHT = 1920
VERTICAL_VIDEO_WIDTH = 1080
HORIZONTAL_VIDEO_HEIGHT = 1080
HORIZONTAL_VIDEO_WIDTH = 1920
bottom_vert = "bottom_vert"
top_vert = "top_vert"
top_right_hor = "top_right_hor"
top_left_hor = "top_left_hor"
bottom_right_hor = "bottom_right_hor"
bottom_left_hor = "bottom_left_hor"
center = "center"



preset = {
    "default":
    {
        "SECONDS_PER_PHOTO" : 4,
        "MAXIMUM_PAUSE_LENGTH" : 0.35,
        "TIME_BETWEEN_IMAGES" : 0,
        "Y_PERCENT_HEIGHT_OF_SUBTITLE" : 85,
        "SUBTITLE_DURATION" : 1,
        "FONT" : 'Tahoma Bold.ttf',
        "FONT_OUTLINE_COLOR" : (0, 0, 0),
        "FONT_OUTLINE_WIDTH" : 7,
        "FONT_SIZE" : 90,
        "NUMBER_OF_CHARACTERS_PER_LINE" : 17,
        "FONT_COLOR" : (255, 255, 255), # white
        "WANTS_IMAGES" : True,
        "WANTS_DALL_E_IMAGES": True,
        # "IMAGE_BORDER_COLOR(S)" : [ (124,252,0), # green
        #                             (0,245,255), # cyan
        #                             (255,255,0), # yellow
        #                             (255,48,48), # red
        #                             (0,191,255)], # blue
        "IMAGE_BORDER_COLOR(S)" : [(0, 0, 0)], # black
        # "IMAGE_BORDER_COLOR(S)" : [(255, 255, 255)], # white
        "MUSIC_CATEGORY_OPTIONS" : ["fascinating", "mystery", "motivational", "funny"],
        "CENSOR_PROFANITY" : False,
        "ALL_CAPS": False,
        "PUNCTUATION": True,
        "OVERLAY_ZONE_TOP_LEFT": [240, 135], # 0.75 for horizontal
        # "OVERLAY_ZONE_TOP_LEFT": [960, 0],
        "OVERLAY_ZONE_WIDTH": 1920*0.75,
        "OVERLAY_ZONE_HEIGHT": 1080*0.75,
        "BACKGROUND_MUSIC_VOLUME": 0.65,
        "WANTS_SOUND_EFFECTS": False,
        "ZOOM_SPEED": 'fast',
        "WANTS_ROYALTY_FREE_IMAGES": False,
        "WANTS_WATERMARK": False,
        "WATERMARK": 'curious_primates.png',
        "WATERMARK_LOCATION": top_left_hor,
        "INTRO_FILE": "brain_boost_daily_hor.mp4",
        "WANTS_INTRO": True,
        "AUDIO_ONLY_BACKGROUND_COLOR": (255, 255, 255),
        # "AUDIO_ONLY_BACKGROUND_MEDIA": ["clouds_1.mp4", "clouds_2.mp4", "clouds_3.mp4"],
        "AUDIO_ONLY_BACKGROUND_MEDIA": ["desert.mp4"],
        # "VOICE": "hHOm3UWNabBYnTSFnrPx", # British narrator
        "VOICE": "P46e4SVL1KUVuleGYhXu", # American narrator
        "SONG":  "dune.mp3",
        "VIDEO_HEIGHT": 1080,
        "VIDEO_WIDTH": 1920
    },
        "vert":
    {
        "SECONDS_PER_PHOTO" : 4,
        "MAXIMUM_PAUSE_LENGTH" : 0.35,
        "TIME_BETWEEN_IMAGES" : 0,
        "Y_PERCENT_HEIGHT_OF_SUBTITLE" : 80,
        "SUBTITLE_DURATION" : 1,
        "FONT" : 'Tahoma Bold.ttf',
        "FONT_OUTLINE_COLOR" : (0, 0, 0),
        "FONT_OUTLINE_WIDTH" : 7,
        "FONT_SIZE" : 80,
        "NUMBER_OF_CHARACTERS_PER_LINE" : 17,
        "FONT_COLOR" : (255, 255, 255), # white
        "WANTS_IMAGES" : True,
        "WANTS_DALL_E_IMAGES": True,
        # "IMAGE_BORDER_COLOR(S)" : [ (124,252,0), # green
        #                             (0,245,255), # cyan
        #                             (255,255,0), # yellow
        #                             (255,48,48), # red
        #                             (0,191,255)], # blue
        "IMAGE_BORDER_COLOR(S)" : [(0, 0, 0)], # black
        # "IMAGE_BORDER_COLOR(S)" : [(255, 255, 255)], # white
        "MUSIC_CATEGORY_OPTIONS" : ["fascinating", "mystery", "motivational", "funny"],
        "CENSOR_PROFANITY" : False,
        "ALL_CAPS": False,
        "PUNCTUATION": True,
        "OVERLAY_ZONE_TOP_LEFT": [0, 0], # 0.75 for horizontal
        # "OVERLAY_ZONE_TOP_LEFT": [960, 0],
        "OVERLAY_ZONE_WIDTH": 1080,
        "OVERLAY_ZONE_HEIGHT": 1920,
        "BACKGROUND_MUSIC_VOLUME": 0.65,
        "WANTS_SOUND_EFFECTS": False,
        "ZOOM_SPEED": 'fast',
        "WANTS_ROYALTY_FREE_IMAGES": False,
        "WANTS_WATERMARK": False,
        "WATERMARK": 'curious_primates.png',
        "WATERMARK_LOCATION": top_left_hor,
        "INTRO_FILE": None,
        "WANTS_INTRO": True,
        "AUDIO_ONLY_BACKGROUND_COLOR": (255, 255, 255),
        # "AUDIO_ONLY_BACKGROUND_MEDIA": ["clouds_1.mp4", "clouds_2.mp4", "clouds_3.mp4"],
        "AUDIO_ONLY_BACKGROUND_MEDIA": ["vert_dave.mp4"],
        # "VOICE": "hHOm3UWNabBYnTSFnrPx", # British narrator
        "VOICE": "P46e4SVL1KUVuleGYhXu", # American narrator
        "SONG":  None,
        "VIDEO_HEIGHT": 1920,
        "VIDEO_WIDTH": 1080
    }
}