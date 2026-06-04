from __future__ import annotations

from abc import ABC, abstractmethod

from vc_crawler.http_client import PoliteClient
from vc_crawler.models import Company


class BaseCrawler(ABC):
    def __init__(self, client: PoliteClient):
        self.client = client

    @abstractmethod
    def run(
        self,
        *,
        limit: int | None = None,
        workers: int = 5,
        enrich: bool = True,
    ) -> list[Company]: ...
