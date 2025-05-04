import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional
import subprocess
import tldextract
import validators
from yt_dlp import YoutubeDL
from utils.utils import safe_path_string


class YouTubeDownloaderController:
    def __init__(
        self,
        output_dir: str = "downloads",
        max_workers: int = 4,
        logger: Any = None,
        browser: Optional[str] = "chrome",
        ffmpeg_path: Optional[str | Path] = None,
    ):
        self.output_dir = Path(output_dir)
        self.max_workers = max_workers
        self.logger = logger
        self.cookies_file = self._extract_cookies(browser) if browser else None
        self.download_queue = asyncio.Queue()
        self.is_processing = False
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.ffmpeg_path = self._validate_ffmpeg_path(ffmpeg_path)

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _validate_ffmpeg_path(self, ffmpeg_path: Optional[str]) -> Optional[str]:
        if ffmpeg_path is None:
            try:
                subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True)
                return "ffmpeg"
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(
                    "Warning: FFmpeg not found in system PATH. Audio-video merging may fail."
                )
                return None

        ffmpeg_path = Path(ffmpeg_path)
        if ffmpeg_path.exists():
            return str(ffmpeg_path)
        return None

    async def process_queue(self):
        self.is_processing = True
        while not self.download_queue.empty():
            url = await self.download_queue.get()
            try:
                await self.download(url)
            except Exception as e:
                self._handle_error(url, e)
            finally:
                self.download_queue.task_done()
        self.is_processing = False

    def _handle_error(self, url: str, error: Exception):
        error_msg = f"Failed to download {url}: {str(error)}"
        if self.logger:
            self.logger.error(error_msg)

    async def add_to_queue(self, urls: List[str]):
        for url in urls:
            if not validators.url(url):
                continue
            await self.download_queue.put(url)

        if not self.is_processing and not self.download_queue.empty():
            asyncio.create_task(self.process_queue())

    def _get_ydl_options(self) -> Dict[str, Any]:
        options = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
            "outtmpl": str(self.output_dir / "%(title)s.%(ext)s"),
            "restrictfilenames": True,
            "quiet": False,
            "no_warnings": False,
            "ignoreerrors": True,
            "continuedl": True,
            "noplaylist": False,
            "extract_flat": False,
            "retries": 10,
            "fragment_retries": 10,
            "socket_timeout": 30,
            "merge_output_format": "mp4",
            "postprocessors": [
                {
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4",
                }
            ],
        }

        if self.cookies_file:
            options["cookiefile"] = self.cookies_file

        if self.ffmpeg_path:
            options["ffmpeg_location"] = self.ffmpeg_path

        return options

    def _extract_cookies(self, browser: str) -> Optional[str]:
        try:
            result = subprocess.run(
                [
                    "yt-dlp",
                    "--cookies-from-browser",
                    browser,
                    "--print",
                    "%(cookies_file)s",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            cookies_path = result.stdout.strip()
            if cookies_path and Path(cookies_path).exists():
                return cookies_path
        except subprocess.CalledProcessError as e:
            print(f"Failed to extract cookies: {e.stderr}")
        except FileNotFoundError:
            print("yt-dlp not found. Please install yt-dlp first.")
        return None

    async def download(self, url: str) -> Optional[Path]:
        domain = tldextract.extract(url).domain
        if domain != "youtube":
            return None

        options = self._get_ydl_options()

        try:
            with YoutubeDL(options) as ydl:
                loop = asyncio.get_event_loop()
                info = await loop.run_in_executor(
                    self.executor, lambda: ydl.extract_info(url, download=True)
                )
                return self._handle_download_result(info)

        except Exception as e:
            self._handle_error(url, e)
            return None

    def _handle_download_result(self, info: Dict[str, Any]) -> Optional[Path]:
        if info is None:
            return None

        if "entries" in info:
            paths = []
            for entry in info["entries"]:
                if entry:
                    path = self.output_dir / f"{safe_path_string(entry['title'])}.mp4"
                    print(f"Downloaded playlist item: {entry['title']}")
                    paths.append(path)
            return paths[0] if paths else None
        else:
            path = self.output_dir / f"{safe_path_string(info['title'])}.mp4"
            print(f"Downloaded: {info['title']}")
            return path
