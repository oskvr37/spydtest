import asyncio
from pydantic import TypeAdapter
from time import perf_counter
from httpx import AsyncClient
from spydtest.api import getServers, Server
from typing import List

DOWNLOAD_SIZE = 1024 * 1024 * 32
MAX_TEST_TIME = 10
SERVERS_COUNT = 3
FROM_FILE = False


class DownloadTester:
    client = AsyncClient()
    total_data = 0
    time_start: float = 0.0
    is_timeout = False
    servers: dict[int, tuple[float, float, Server]] = {}

    async def testServerDownload(self, server: Server):
        self.servers[server.id] = (0.0, 0.0, server)

        try:
            while not self.is_timeout:
                async with self.client.stream(
                    "GET", f"https://{server.host}/download?size={DOWNLOAD_SIZE}"
                ) as response:
                    server_start_time = perf_counter()
                    server_total_data = 0

                    async for chunk in response.aiter_bytes():
                        self.total_data += len(chunk)
                        server_total_data += len(chunk)

                        time_elapsed = perf_counter() - self.time_start
                        speed = self.total_data / time_elapsed

                        print(
                            f"\rSpeed: {speed / 1024 / 1024:.2f} MB/s",
                            end="",
                            flush=True,
                        )

                        if (perf_counter() - self.time_start) > MAX_TEST_TIME:
                            self.is_timeout = True
                            break

                    current_data, current_time, server = self.servers[server.id]
                    self.servers[server.id] = (
                        current_data + server_total_data,
                        current_time + (perf_counter() - server_start_time),
                        server,
                    )

        except Exception as e:
            print(f"\nError at {server.name}: {e}")

    async def close(self):
        await self.client.aclose()


async def main():
    if FROM_FILE:
        type_adapter = TypeAdapter(List[Server])
        with open("servers.json", encoding="utf-8") as f:
            servers = type_adapter.validate_json(f.read())[:SERVERS_COUNT]
    else:
        servers = getServers(limit=SERVERS_COUNT)

    tester = DownloadTester()

    tasks = [tester.testServerDownload(server) for server in servers]

    tester.time_start = perf_counter()

    await asyncio.gather(*tasks)

    await tester.close()

    print(" \u2714")  # tick symbol
    print(f"Downloaded data: {tester.total_data / 1024 / 1024:.2f} MB")

    sorted_servers = sorted(
        tester.servers.items(),
        key=lambda x: x[1][0] / x[1][1],
    )

    for _, (data, time, server) in sorted_servers:
        speed = data / time / 1024 / 1024
        print(f"{server.host} \033[0;32m{speed:.2f} MB/s\033[0m")


if __name__ == "__main__":
    asyncio.run(main())
