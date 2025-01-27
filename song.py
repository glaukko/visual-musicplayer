class Song():
    def __init__(self, fileid, filename, duration, coverImg = None):
        self.fileid = fileid
        self.filename = filename
        
        self.coverImg = coverImg
        self.duration = duration #(hours, minutes, seconds)
