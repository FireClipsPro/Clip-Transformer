class ImageModel:
    def __init__(self,
                 uid: str,
                 query: str,
                 is_dall_e: bool,
                 url: str,
                 start: float,
                 end: float,
                 width: int,
                 height: int):
        self.uid = uid
        self.query = query
        self.is_dall_e = is_dall_e
        self.start = start
        self.end = end
        self.url = url
        self.width = width
        self.height = height