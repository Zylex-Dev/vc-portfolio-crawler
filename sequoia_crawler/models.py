from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Optional


@dataclass
class Company:
    id: int
    name: str
    slug: str
    sequoia_url: str
    sectors: list[str] = field(default_factory=list)
    website: Optional[str] = None
    description: Optional[str] = None
    stage: Optional[str] = None
    stage_year: Optional[int] = None
    founded_year: Optional[int] = None
    partnered_year: Optional[int] = None
    logo_url: Optional[str] = None
    source_modified: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    def to_csv_row(self) -> dict:
        row = asdict(self)
        row["sectors"] = ";".join(self.sectors)
        return row


CSV_FIELDS = [
    "id", "name", "slug", "sequoia_url", "sectors", "website",
    "description", "stage", "stage_year", "founded_year",
    "partnered_year", "logo_url", "source_modified",
]
