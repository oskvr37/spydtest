from urllib3 import HTTPSConnectionPool
from time import perf_counter

from spydtest import __version__


class Cloudflare:
    max_test_time = 10
    pool = HTTPSConnectionPool(
        host="speed.cloudflare.com", headers={"User-Agent": f"spydtest/{__version__}"}
    )


class CloudflareDownload(Cloudflare):
    def __init__(self, download_size: int) -> None:
        response = self.pool.request(
            "GET",
            "/__down",
            fields={"bytes": str(download_size)},
            headers={"Accept": "*/*", "Accept-Encoding": "gzip, deflate, br, zstd"},
            preload_content=False,
        )

        data_downloaded = 0
        time_start = perf_counter()

        for chunk in response.stream():
            data_downloaded += len(chunk)
            time_elapsed = perf_counter() - time_start
            speed = (data_downloaded / time_elapsed) / (1024 * 1024 / 8)

            if time_elapsed > self.max_test_time:
                break

            self.handle(speed, time_elapsed, data_downloaded)

    def handle(self, speed: float, time: float, total: int) -> None:
        raise NotImplementedError


class CloudflareUpload(Cloudflare):
    chunk_size = 1024 * 1024

    def __init__(self, upload_size: int) -> None:
        def bodyGenerator():
            data_sent = 0
            time_start = perf_counter()

            while data_sent < upload_size:
                data_size = min(self.chunk_size, upload_size - data_sent)
                data_sent += data_size
                yield data_size * b"0"

                time_elapsed = perf_counter() - time_start
                speed = (data_sent / time_elapsed) / (1024 * 1024 / 8)

                self.handle(speed, time_elapsed, data_sent)

        self.pool.request(
            "POST",
            "/__up",
            headers={
                "Content-Length": str(upload_size),
                "Content-Type": "text/plain;charset=UTF-8",
            },
            body=bodyGenerator(),
        )

    def handle(self, speed: float, time: float, total: int) -> None:
        raise NotImplementedError
