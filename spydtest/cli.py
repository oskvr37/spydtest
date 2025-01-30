import logging
import argparse

from rich.progress import Progress, TextColumn, BarColumn
from rich.console import Console
from rich.theme import Theme
from rich.logging import RichHandler

from spydtest import __version__
from spydtest.cloudflare import CloudflareDownload, CloudflareUpload


class RichCloudflareDownload(CloudflareDownload):
    def __init__(self, download_size: int, console: Console = Console()) -> None:
        with Progress(
            TextColumn("[down.icon]↓ [down.text]Download"),
            BarColumn(
                complete_style="down.bar.complete", finished_style="down.bar.finished"
            ),
            TextColumn(
                "[down.speed.value]{task.fields[speed]:.2f} [down.speed.unit]Mbps"
            ),
            console=console,
        ) as progress:
            self.task = progress.add_task("download", total=download_size, speed=0.0)
            self.progress = progress
            super().__init__(download_size)

    def handle(self, speed: float, time: float, total: int) -> None:
        self.progress.update(self.task, completed=total, speed=speed)


class RichCloudflareUpload(CloudflareUpload):
    def __init__(self, upload_size: int, console: Console = Console()) -> None:
        with Progress(
            TextColumn("[up.icon]↑ [up.text]Upload"),
            BarColumn(
                complete_style="up.bar.complete", finished_style="up.bar.finished"
            ),
            TextColumn("[up.speed.value]{task.fields[speed]:.2f} [up.speed.unit]Mbps"),
            console=console,
        ) as progress:
            self.task = progress.add_task("upload", total=upload_size, speed=0.0)
            self.progress = progress
            super().__init__(upload_size)

    def handle(self, speed: float, time: float, total: int) -> None:
        self.progress.update(self.task, completed=total, speed=speed)


def main():
    parser = argparse.ArgumentParser(
        prog="spydtest",
        description=f"spydtest v{__version__} - test connection speed with Cloudflare.",
    )

    parser.add_argument(
        "--download-size",
        "-ds",
        type=int,
        default=32,
        metavar="MB",
        help="Download size, default %(default)s %(metavar)s",
    )

    parser.add_argument(
        "--upload-size",
        "-us",
        type=int,
        default=8,
        metavar="MB",
        help="Upload size, default %(default)s %(metavar)s",
    )

    args = parser.parse_args()

    console = Console(
        theme=Theme(
            {
                "down.icon": "magenta",
                "down.text": "blue",
                "down.bar.complete": "magenta",
                "down.bar.finished": "blue",
                "down.speed.value": "magenta",
                "down.speed.unit": "blue",
                "up.icon": "yellow",
                "up.text": "red",
                "up.bar.complete": "yellow",
                "up.bar.finished": "red",
                "up.speed.value": "yellow",
                "up.speed.unit": "red",
            }
        ),
        color_system=None,
    )

    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console)],
    )

    MB = 1024 * 1024

    RichCloudflareDownload(args.download_size * MB, console)
    RichCloudflareUpload(args.upload_size * MB, console)


if __name__ == "__main__":
    main()
