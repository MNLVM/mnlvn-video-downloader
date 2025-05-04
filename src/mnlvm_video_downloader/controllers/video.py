import asyncio
import csv
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional
import subprocess
import validators
from yt_dlp import YoutubeDL
from exceptions import FFmpegNotInstalledError
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
from utils.utils import safe_path_string, clean_search_query, check_ffmpeg


class YouTubeDownloaderController:
    def __init__(
        self,
        output_dir: str = "downloads",
        max_workers: int = 4,
        logger: Any = None,
        browser: Optional[str] = "chrome",
        ffmpeg_path: Optional[str | Path] = "ffmpeg",
    ):
        self.output_dir = Path(output_dir)
        self.max_workers = max_workers
        self.logger = logger
        self.cookies_file = self._extract_cookies(browser) if browser else None
        self.download_queue = asyncio.Queue()
        self.is_processing = False
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.ffmpeg_path = self._validate_ffmpeg_path(ffmpeg_path)

        self._progress_callback = None
        self._current_downloads = 0
        self._total_downloads = 0

        self.output_dir.mkdir(parents=True, exist_ok=True)

        if not check_ffmpeg() and self.ffmpeg_path == "ffmpeg":
            raise FFmpegNotInstalledError

    def _validate_ffmpeg_path(self, ffmpeg_path: Optional[str]) -> Optional[str]:
        if ffmpeg_path is None:
            try:
                subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True)
                return "ffmpeg"
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(
                    "Warning: FFmpeg not found in system PATH. Audio-video merging may fail."
                )

        ffmpeg_path = Path(ffmpeg_path)
        if ffmpeg_path.exists():
            return str(ffmpeg_path)
        return None

    def set_progress_callback(self, callback):
        self._progress_callback = callback

    def _is_youtube_url(self, query: str) -> bool:
        return any(
            domain in query.lower()
            for domain in ["youtube.com", "youtu.be", "youtube.nl"]
        )

    def _get_ydl_options(self) -> Dict[str, Any]:
        options = {
            "format": "bestvideo[ext=mp4][height<=2160]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
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

    def search_youtube(self, query: str, max_results: int = 1, **opts) -> Optional[str]:
        search_url = f"ytsearch{max_results}:{query}"
        video_url = None
        ydl_opts = {
            "quiet": True,
            "extract_flat": True,
            "force_generic_extractor": True,
            **opts,
        }
        with YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(search_url, download=False)
            if result and "entries" in result and result["entries"]:
                video_url = result["entries"][0]["url"]
        return video_url

    def process_track(self, query: str) -> Dict[str, str]:
        search_query = clean_search_query(query)
        youtube_url = self.search_youtube(search_query)
        return youtube_url

    def get_youtube_urls_from_csv(self, csv_path: str) -> List[Dict[str, str]]:
        results = []
        with open(csv_path, mode="r", encoding="utf8", errors="ignore") as file:
            csvreader = csv.reader(file)
            for row in csvreader:
                new_row = row[0].split(";")
                if new_row[1] != "Listen num":
                    results.append(new_row[1])
        return [self.process_track(q) for q in results]

    async def process_queue(self) -> None:
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

    def _handle_error(self, url: str, error: Exception) -> None:
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

    def download(self, url: str) -> Optional[Path]:
        is_youtube_uri: bool = self._is_youtube_url(url)
        if not is_youtube_uri:
            return None

        options = self._get_ydl_options()

        def progress_hook(d):
            if d["status"] == "downloading" and self._progress_callback:
                percent = float(d["_percent_str"].strip("%"))
                self._progress_callback(
                    self._current_downloads,
                    self._total_downloads,
                    f"{url} - {str(percent)}",
                )

        options["progress_hooks"] = [progress_hook]
        try:
            with YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=True)
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
                    paths.append(path)
            return paths[0] if paths else None
        else:
            path = self.output_dir / f"{safe_path_string(info['title'])}.mp4"
            return path

    async def _download(self, csv_path: str = None) -> None:
        tracks = self.get_youtube_urls_from_csv(csv_path)
        await self.add_to_queue(tracks)

        if self.download_queue.empty():
            return

        print(f"Downloading {self.download_queue.qsize()} videos...")
        with ThreadPool(cpu_count()) as pool:
            pool.map_async(self.download, self.download_queue, chunksize=20)
