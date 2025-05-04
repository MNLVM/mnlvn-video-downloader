from windows.views import Window
from controllers.video import YouTubeDownloaderController

youtuber_controler = YouTubeDownloaderController(
    output_dir="downloads",
    max_workers=4,
    browser="chrome",
    ffmpeg_path="ffmpeg",
)
app = Window(yt_controler=youtuber_controler)
app.mainloop()
