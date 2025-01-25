from urllib3 import HTTPSConnectionPool
from time import perf_counter
from importlib.metadata import version

__version__ = version("spydtest")

CHUNK_SIZE = 1024 * 1024 * 2  # 2M
DOWNLOAD_SIZE = 1024 * 1024 * 256  # 256M
MAX_TEST_TIME = 10

# TODO: get a server from speedtest.net
HOST = "warsaw.netia.pl.prod.hosts.ooklaserver.net:8080"


def main():
    pool = HTTPSConnectionPool(HOST, headers={"User-Agent": f"spydtest/{__version__}"})

    start_time = perf_counter()
    pool.request("GET", "/hello")
    latency = perf_counter() - start_time

    print(f"Latency: {latency * 1000:.2f} ms")

    response = pool.request(
        "GET", "/download", fields={"size": str(DOWNLOAD_SIZE)}, preload_content=False
    )

    total_data = 0
    start_download_time = perf_counter()

    for chunk in response.stream(CHUNK_SIZE):
        total_data += len(chunk)

        time_elapsed = perf_counter() - start_download_time
        speed = total_data / time_elapsed

        print(f"\rSpeed {speed / 1024 / 1024:.2f} MB/s", end="", flush=True)

        if time_elapsed > MAX_TEST_TIME:
            break

    download_time = perf_counter() - start_download_time
    speed = (total_data / 1024 / 1024) / download_time

    print("\u2705")  # tick symbol
    print(f"Downloaded data: {total_data / 1024 / 1024:.2f} MB")
    print(f"Download time: {download_time:.2f}s")
    print(f"Average download speed: {speed:.2f} MB/s")
