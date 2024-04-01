from moviepy.editor import VideoFileClip


# Class for a video that gets overlaid (put on top of) another video
class OverlayVideo:
    def __init__(self, 
                 video: VideoFileClip,
                 start: float,
                 end: float):
        self.video = video
        self.start = start
        self.end = end