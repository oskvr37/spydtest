from spydtest import __version__
from spydtest.api import getServers, Server
from urllib3 import HTTPSConnectionPool
from time import perf_counter


def measureLatency(server: Server) -> float:
    print(f"Measuring {server.host}")

    pool = HTTPSConnectionPool(
        server.host, headers={"User-Agent": f"spydtest/{__version__}"}
    )

    COUNT = 4

    start_time = perf_counter()

    for _ in range(COUNT):
        pool.request("GET", "/hello")

    return (perf_counter() - start_time) / COUNT


def main():
    servers = getServers()

    latency_results = [(server, measureLatency(server)) for server in servers]

    sorted_results = sorted(latency_results, key=lambda x: x[1], reverse=True)

    for server, latency in sorted_results:
        print(f"{server.host} \033[0;32m{latency * 1000:.2f} ms\033[0m")


if __name__ == "__main__":
    main()
