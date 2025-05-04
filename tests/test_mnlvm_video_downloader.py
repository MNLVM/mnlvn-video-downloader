import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from yt_dlp import YoutubeDL
from mnlvm_video_downloader.controllers.video import YouTubeDownloaderController


class TestYouTubeDownloaderController(unittest.TestCase):
    def setUp(self):
        self.test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        self.test_playlist_url = (
            "https://www.youtube.com/playlist?list=PLx0sYbCqOb8TBPRdmBHs5Iftvv9TPboYG"
        )
        self.invalid_url = "not_a_url"
        self.non_youtube_url = "https://example.com/video"

        # Mock objects
        self.mock_logger = MagicMock()
        self.mock_executor = MagicMock()
        self.mock_ydl_instance = MagicMock(spec=YoutubeDL)
        self.mock_ydl_instance.extract_info.return_value = {
            "title": "Test Video",
            "ext": "mp4",
            "entries": None,
        }

    def tearDown(self):
        pass

    @patch("concurrent.futures.ThreadPoolExecutor")
    @patch("pathlib.Path.mkdir")
    def test_init_default_values(self, mock_mkdir, mock_executor):
        controller = YouTubeDownloaderController()
        self.assertEqual(controller.output_dir, Path("downloads"))
        self.assertEqual(controller.max_workers, 4)
        self.assertIsNone(controller.logger)
        self.assertIsNone(controller.cookies_file)
        self.assertFalse(controller.is_processing)
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_executor.assert_called_once_with(max_workers=4)

    @patch("subprocess.run")
    def test_validate_ffmpeg_path_system(self, mock_run):
        controller = YouTubeDownloaderController()
        result = controller._validate_ffmpeg_path(None)
        self.assertEqual(result, "ffmpeg")
        mock_run.assert_called_once_with(
            ["ffmpeg", "-version"], check=True, capture_output=True
        )

    @patch("pathlib.Path.exists")
    def test_validate_ffmpeg_path_custom(self, mock_exists):
        mock_exists.return_value = True
        test_path = "/custom/path/ffmpeg"
        controller = YouTubeDownloaderController()
        result = controller._validate_ffmpeg_path(test_path)
        self.assertEqual(result, test_path)
        mock_exists.assert_called_once()

    @patch("pathlib.Path.exists")
    def test_validate_ffmpeg_path_invalid(self, mock_exists):
        mock_exists.return_value = False
        controller = YouTubeDownloaderController()
        result = controller._validate_ffmpeg_path("/invalid/path")
        self.assertIsNone(result)

    @patch("validators.url")
    async def test_add_to_queue_valid_url(self, mock_validators):
        mock_validators.return_value = True
        controller = YouTubeDownloaderController()
        await controller.add_to_queue([self.test_url])
        self.assertEqual(controller.download_queue.qsize(), 1)

    @patch("validators.url")
    async def test_add_to_queue_invalid_url(self, mock_validators):
        mock_validators.return_value = False
        controller = YouTubeDownloaderController()
        await controller.add_to_queue([self.invalid_url])
        self.assertEqual(controller.download_queue.qsize(), 0)

    @patch("yt_dlp.YoutubeDL")
    @patch("asyncio.get_event_loop")
    async def test_download_success(self, mock_loop, mock_ydl):
        mock_ydl.return_value = self.mock_ydl_instance
        mock_loop.return_value.run_in_executor.return_value = {
            "title": "Test Video",
            "ext": "mp4",
        }

        controller = YouTubeDownloaderController()
        result = await controller.download(self.test_url)
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "Test Video.mp4")

    @patch("yt_dlp.YoutubeDL")
    @patch("asyncio.get_event_loop")
    async def test_download_non_youtube(self, mock_loop, mock_ydl):
        controller = YouTubeDownloaderController()
        result = await controller.download(self.non_youtube_url)
        self.assertIsNone(result)
        mock_ydl.assert_not_called()

    @patch("yt_dlp.YoutubeDL")
    @patch("asyncio.get_event_loop")
    async def test_download_failure(self, mock_loop, mock_ydl):
        mock_ydl.return_value = self.mock_ydl_instance
        mock_ydl_instance = mock_ydl.return_value
        mock_ydl_instance.extract_info.side_effect = Exception("Test error")

        controller = YouTubeDownloaderController(logger=self.mock_logger)
        result = await controller.download(self.test_url)
        self.assertIsNone(result)
        self.mock_logger.error.assert_called_once()

    def test_handle_download_result_single_video(self):
        test_info = {"title": "Single Video", "ext": "mp4", "entries": None}

        controller = YouTubeDownloaderController()
        result = controller._handle_download_result(test_info)
        self.assertEqual(result.name, "Single Video.mp4")

    def test_handle_download_result_playlist(self):
        test_info = {
            "title": "Test Playlist",
            "ext": "mp4",
            "entries": [
                {"title": "Video 1", "ext": "mp4"},
                {"title": "Video 2", "ext": "mp4"},
            ],
        }

        controller = YouTubeDownloaderController()
        result = controller._handle_download_result(test_info)
        self.assertEqual(result.name, "Video 1.mp4")

    def test_handle_download_result_none(self):
        controller = YouTubeDownloaderController()
        result = controller._handle_download_result(None)
        self.assertIsNone(result)

    @patch("subprocess.run")
    def test_extract_cookies_success(self, mock_run):
        mock_run.return_value.stdout = "/path/to/cookies.txt\n"
        controller = YouTubeDownloaderController(browser="chrome")
        result = controller._extract_cookies("chrome")
        self.assertEqual(result, "/path/to/cookies.txt")

    def test_get_ydl_options_default(self):
        controller = YouTubeDownloaderController()
        options = controller._get_ydl_options()
        self.assertIsInstance(options, dict)
        self.assertEqual(
            options["format"],
            "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
        )
        self.assertIn("postprocessors", options)
        self.assertNotIn("cookiefile", options)
        self.assertNotIn("ffmpeg_location", options)

    def test_get_ydl_options_with_cookies_and_ffmpeg(self):
        controller = YouTubeDownloaderController()
        controller.cookies_file = "/path/to/cookies.txt"
        controller.ffmpeg_path = "/path/to/ffmpeg"
        options = controller._get_ydl_options()
        self.assertEqual(options["cookiefile"], "/path/to/cookies.txt")
        self.assertEqual(options["ffmpeg_location"], "/path/to/ffmpeg")

    @patch.object(YouTubeDownloaderController, "download")
    async def test_process_queue(self, mock_download):
        mock_download.return_value = Path("test.mp4")

        controller = YouTubeDownloaderController()
        await controller.download_queue.put(self.test_url)
        await controller.download_queue.put(self.test_url)

        await controller.process_queue()

        self.assertEqual(mock_download.call_count, 2)
        self.assertFalse(controller.is_processing)

    @patch.object(YouTubeDownloaderController, "download")
    async def test_process_queue_with_error(self, mock_download):
        mock_download.side_effect = Exception("Test error")

        controller = YouTubeDownloaderController(logger=self.mock_logger)
        await controller.download_queue.put(self.test_url)

        await controller.process_queue()

        self.mock_logger.error.assert_called_once()
        self.assertFalse(controller.is_processing)
