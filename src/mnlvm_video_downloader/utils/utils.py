import re
from pathlib import Path
from sys import platform
from uuid import uuid1
from urllib.request import urlretrieve


def safe_path_string(string: str) -> str:
    keep_characters = " !£$%^&()_-+=,.;'@#~[]{}"
    new_string = ""

    for c in string:
        if c.isalnum() or c in keep_characters:
            new_string = new_string + c
        else:
            new_string = new_string + "_"

    return re.sub(r"\.+$", "", new_string.rstrip()).encode("utf8").decode("utf8")


def create_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


async def clean_search_query(artist_title: str) -> str:
    cleaned = re.sub(r"\([^)]*\)", "", artist_title)
    cleaned = re.sub(r" - .*Remix", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


class PathHolder:
    def __init__(self, data_path: str = None, downloads_path: str = None):
        if data_path is None:
            home = Path.home()

            if platform == "win32":
                self.data_path = home / "AppData/Roaming/EkilaDownloader"

            elif platform == "linux":
                self.data_path = home / ".local/share/EkilaDownloader"

            elif platform == "darwin":
                self.data_path = home / ".local/share/EkilaDownloader"

        else:
            self.data_path = Path(data_path)

        self.temp_path = self.data_path / "temp"
        create_dir(self.temp_path)

        if downloads_path is None:
            self.downloads_path = self.data_path / "downloads"
        else:
            self.downloads_path = Path(downloads_path)

        create_dir(self.downloads_path)

    def get_download_directory(self) -> Path:
        return self.downloads_path

    def get_temp_dir(self) -> Path:
        return self.temp_path

    def download_file(self, url: str, extension: str = None) -> Path:
        file_path = self.get_temp_dir() / str(uuid1())
        if extension is not None:
            file_path = file_path.with_suffix(f".{extension}")

        urlretrieve(url, str(file_path))
        return file_path
