"""speedtest.net API"""

from urllib3 import HTTPSConnectionPool
from pydantic import BaseModel, TypeAdapter
from typing import List


class Server(BaseModel):
    url: str
    lat: float
    lon: float
    distance: int
    name: str
    country: str
    cc: str
    sponsor: str
    id: int
    preferred: bool
    https_functional: bool
    host: str


def getServers(limit: int = 10, https_functional: bool = True) -> List[Server]:
    pool = HTTPSConnectionPool("www.speedtest.net")

    request_fields = {
        "limit": str(limit),
        "https_functional": "true" if https_functional else "false",
    }

    response = pool.request(
        "GET",
        "/api/js/servers",
        headers={"Accept": "application/json"},
        fields=request_fields,
    )

    type_adapter = TypeAdapter(List[Server])

    servers = type_adapter.validate_json(response.data)

    return servers
