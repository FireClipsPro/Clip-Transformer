# Class for a video that gets overlaid (put on top of) another video
class OverlayVideo:
    def __init__(self, 
                 id: str,
                 start: float,
                 end: float):
        self.id = id
        self.start = start
        self.end = end