"""test speed with speed.cloudflare.com"""

from urllib3 import HTTPSConnectionPool
from time import perf_counter
from typing import Callable

from spydtest import __version__


def handleData(speed: float, time: float, data: int):
    print(
        f"\rSpeed: {speed / 1024 / 128:.2f} Mbps,"
        f" Time: {time:.2f}s,"
        f" Data: {data / 1024 / 1024:.0f} MB",
        end="",
        flush=True,
    )


def testDownload(
    connection_pool: HTTPSConnectionPool,
    download_size: int,
    chunk_size: int = 1024 * 1024,
    max_test_time: int = 10,
    dataHandler: Callable[[float, float, int], None] = handleData,
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

    for chunk in response.stream(chunk_size):
        data_downloaded += len(chunk)

        time_elapsed = perf_counter() - time_start

        if time_elapsed > max_test_time:
            break

        speed = data_downloaded / time_elapsed

        dataHandler(speed, time_elapsed, data_downloaded)


def testUpload(
    pool: HTTPSConnectionPool,
    upload_size: int,
    chunk_size: int = 1024 * 1024,
    dataHandler: Callable[[float, float, int], None] = handleData,
):
    def bodyGenerator():
        data_sent = 0
        time_start = perf_counter()

        while data_sent < upload_size:
            data_size = min(chunk_size, upload_size - data_sent)
            data_sent += data_size
            yield data_size * b"0"

            time_elapsed = perf_counter() - time_start
            speed = data_sent / time_elapsed

            dataHandler(speed, time_elapsed, data_sent)

    pool.request(
        "POST",
        "/__up",
        headers={
            "Content-Length": str(upload_size),
            "Content-Type": "text/plain;charset=UTF-8",
        },
        body=bodyGenerator(),
    )


if __name__ == "__main__":
    pool = HTTPSConnectionPool(
        host="speed.cloudflare.com", headers={"User-Agent": f"spydtest/{__version__}"}
    )

    download_size = 1024 * 1024 * 128
    upload_size = 1024 * 1024 * 32

    print("↓ Testing download...")
    testDownload(pool, download_size)

    print("\n↑ Testing upload...")
    testUpload(pool, upload_size)
