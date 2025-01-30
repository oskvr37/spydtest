"""test speed with speed.cloudflare.com"""

from urllib3 import HTTPSConnectionPool
from time import perf_counter
from rich.progress import Progress, BarColumn, TextColumn

from spydtest import __version__


def testDownload(
    connection_pool: HTTPSConnectionPool,
    download_size: int,
    chunk_size: int = 1024 * 1024,
    max_test_time: int = 10,
):
    response = connection_pool.request(
        "GET",
        "/__down",
        fields={"bytes": str(download_size)},
        headers={"Accept": "*/*", "Accept-Encoding": "gzip, deflate, br, zstd"},
        preload_content=False,
    )

    data_downloaded = 0
    time_start = perf_counter()

    with Progress(
        TextColumn("↓ Download"),
        BarColumn(),
        TextColumn("{task.fields[speed]} Mbps"),
    ) as progress:
        task = progress.add_task("download", total=download_size, speed="0.00")

        for chunk in response.stream(chunk_size):
            data_downloaded += len(chunk)
            time_elapsed = perf_counter() - time_start

            if time_elapsed > max_test_time:
                break

            speed = (data_downloaded / time_elapsed) / (1024 * 1024)
            progress.update(task, advance=len(chunk), speed=f"{speed * 8:.2f}")


def testUpload(
    pool: HTTPSConnectionPool,
    upload_size: int,
    chunk_size: int = 1024 * 1024,
):
    def bodyGenerator():
        data_sent = 0
        time_start = perf_counter()

        with Progress(
            TextColumn("↑ Upload"),
            BarColumn(),
            TextColumn("{task.fields[speed]} Mbps"),
        ) as progress:
            task = progress.add_task("upload", total=upload_size, speed="0.00")

            while data_sent < upload_size:
                data_size = min(chunk_size, upload_size - data_sent)
                data_sent += data_size
                yield data_size * b"0"

                time_elapsed = perf_counter() - time_start
                speed = (data_sent / time_elapsed) / (1024 * 1024)

                progress.update(task, advance=data_size, speed=f"{speed * 8:.2f}")

    pool.request(
        "POST",
        "/__up",
        headers={
            "Content-Length": str(upload_size),
            "Content-Type": "text/plain;charset=UTF-8",
        },
        body=bodyGenerator(),
    )


def createPool():
    return HTTPSConnectionPool(
        host="speed.cloudflare.com", headers={"User-Agent": f"spydtest/{__version__}"}
    )


if __name__ == "__main__":
    pool = createPool()

    testDownload(pool, download_size=1024 * 1024 * 128)
    testUpload(pool, upload_size=1024 * 1024 * 32)
