from requests import Session
from time import perf_counter


TIMEOUT = 10
DOWNLOAD_SIZE = 1024 * 1024 * 200  # 200M
CHUNK_SIZE = 1024 * 1024 * 2  # 2M

# TODO: add user-agent like spydtest/0.0.1

# TODO: get a server from speedtest.net
SERVER_URL = "https://warsaw.netia.pl.prod.hosts.ooklaserver.net:8080/download"


def main():
    # TODO: find something faster than requests, maybe just urllib3
    session = Session()

    latency_start = perf_counter()

    request = session.get(SERVER_URL, params={"size": DOWNLOAD_SIZE}, stream=True)

    print(f"latency {(perf_counter() - latency_start) * 1000:.2f} ms")

    time_start = perf_counter()
    total_data = b""

    for chunk in request.iter_content(chunk_size=CHUNK_SIZE):
        total_data += chunk

        time_elapsed = perf_counter() - time_start
        bytes_per_second = len(total_data) / time_elapsed

        print(f"\r{bytes_per_second / 1024 / 1024:.2f} MB/s", end=" ")

        if time_elapsed > TIMEOUT:
            break

    print("\u2705")  # tick symbol

    total_time = perf_counter() - time_start
    total_speed = len(total_data) / total_time / 1024 / 1024

    print(f"downloaded data {len(total_data) // 1024}K")
    print(f"download time {total_time:.2f}s")
    print(f"total speed {total_speed:.2f} MB/s")
