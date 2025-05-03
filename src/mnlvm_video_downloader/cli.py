"""Console script for mnlvm_video_downloader."""
import mnlvm_video_downloader

import typer
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for mnlvm_video_downloader."""
    console.print("Replace this message by putting your code into "
               "mnlvm_video_downloader.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    


if __name__ == "__main__":
    app()
