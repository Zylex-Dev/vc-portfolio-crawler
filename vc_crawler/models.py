from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Optional


@dataclass
class Company:
    id: int
    fund: str                               # "sequoia" | "a16z"
    name: str
    slug: str
    fund_url: str                           # renamed from sequoia_url
    sectors: list[str] = field(default_factory=list)
    website: Optional[str] = None
    description: Optional[str] = None
    stage: Optional[str] = None
    stage_year: Optional[int] = None
    founded_year: Optional[int] = None
    invested_year: Optional[int] = None     # renamed from partnered_year
    logo_url: Optional[str] = None
    source_modified: Optional[str] = None
    # A16Z-specific optional fields
    ticker_symbol: Optional[str] = None
    acquirer: Optional[str] = None
    founders: Optional[list[str]] = None

    def to_dict(self) -> dict:
        return asdict(self)

    def to_csv_row(self) -> dict:
        row = asdict(self)
        row["sectors"] = ";".join(self.sectors or [])
        row["founders"] = ";".join(self.founders or [])
        return row


CSV_FIELDS = [
    "id", "fund", "name", "slug", "fund_url", "sectors", "website",
    "description", "stage", "stage_year", "founded_year",
    "invested_year", "logo_url", "source_modified",
    "ticker_symbol", "acquirer", "founders",
]
