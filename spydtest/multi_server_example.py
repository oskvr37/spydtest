import asyncio

from time import perf_counter
from httpx import AsyncClient
from spydtest.api import getServers, Server

DOWNLOAD_SIZE = 1024 * 1024 * 32
MAX_TEST_TIME = 10
SERVERS_COUNT = 5


class DownloadTester:
    client = AsyncClient()
    total_data = 0
    time_start: float = 0.0
    is_timeout = False

    async def testServerDownload(self, server: Server):
        try:
            while not self.is_timeout:
                async with self.client.stream(
                    "GET", f"https://{server.host}/download?size={DOWNLOAD_SIZE}"
                ) as response:
                    async for chunk in response.aiter_bytes():
                        self.total_data += len(chunk)

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

        except Exception as e:
            print(f"\nError at {server.name}: {e}")

    async def close(self):
        await self.client.aclose()


async def main():
    servers = getServers(limit=SERVERS_COUNT)
    tester = DownloadTester()

    tasks = [tester.testServerDownload(server) for server in servers]

    tester.time_start = perf_counter()

    await asyncio.gather(*tasks)

    await tester.close()

    print(" \u2714")  # tick symbol
    print(f"Downloaded data: {tester.total_data / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    asyncio.run(main())
