class FFmpegNotInstalledError(Exception):
    def __init__(
        self, message="FFmpeg must be installed  [https://ffmpeg.org/download.html]"
    ):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message
