from requests import Session
from time import time


DOWNLOAD_SIZE = 1024 * 1024 * 25  # 25M
CHUNK_SIZE = 1024 * 1024  # 1M

# TODO: get a server from speedtest.net
SERVER_URL = "https://warsaw.netia.pl.prod.hosts.ooklaserver.net:8080/download"

def main():
    # TODO: find something faster than requests, maybe just urllib3
    session = Session()
    request = session.get(SERVER_URL, params={"size": DOWNLOAD_SIZE}, stream=True)

    time_start = time()
    total_data = b""

    for chunk in request.iter_content(chunk_size=CHUNK_SIZE):
        total_data += chunk

        time_elapsed = time() - time_start
        bytes_per_second = len(total_data) / time_elapsed

        print(f"\r{bytes_per_second / 1024 / 1024:.2f} MB/s", end=" ")

    print("\u2705")  # tick symbol

    total_time = time() - time_start
    total_speed = len(total_data) / total_time / 1024 / 1024

    print(f"downloaded data {len(total_data) // 1024}K")
    print(f"download time {total_time:.2f}s")
    print(f"total speed {total_speed:.2f} MB/s")
