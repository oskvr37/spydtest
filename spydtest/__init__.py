from urllib3 import HTTPSConnectionPool
from time import perf_counter

from spydtest.api import getServers

from importlib.metadata import version

__version__ = version("spydtest")

CHUNK_SIZE = 1024 * 1024 * 2  # 2M
DOWNLOAD_SIZE = 1024 * 1024 * 256  # 256M
MAX_TEST_TIME = 10


def main():
    servers = getServers()

    server = servers[0]

    print(
        f"Server: {server.sponsor} in {server.country}, {server.name}, {server.distance} km"
    )

    pool = HTTPSConnectionPool(
        server.host, headers={"User-Agent": f"spydtest/{__version__}"}
    )

    # TODO: handle request errors
    pool.request("GET", "/hello")

    latency_start_time = perf_counter()
    response = pool.request(
        "GET", "/download", fields={"size": str(DOWNLOAD_SIZE)}, preload_content=False
    )
    latency = perf_counter() - latency_start_time

    print(f"Latency: {latency * 1000:.2f} ms")

    total_data = 0
    start_download_time = perf_counter()

    for chunk in response.stream(CHUNK_SIZE):
        total_data += len(chunk)

        time_elapsed = perf_counter() - start_download_time
        speed = total_data / time_elapsed

        print(f"\rSpeed: {speed / 1024 / 1024:.2f} MB/s", end="", flush=True)

        if time_elapsed > MAX_TEST_TIME:
            break

    download_time = perf_counter() - start_download_time
    speed = (total_data / 1024 / 1024) / download_time

    print(" \u2714")  # tick symbol
    print(f"Downloaded data: {total_data / 1024 / 1024:.2f} MB")
    print(f"Download time: {download_time:.2f}s")
    print(f"Average download speed: {speed:.2f} MB/s")
