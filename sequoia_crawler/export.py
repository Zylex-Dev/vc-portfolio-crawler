from __future__ import annotations

import csv
import json
from pathlib import Path

from .models import Company, CSV_FIELDS


def write_json(companies: list[Company], path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [c.to_dict() for c in companies]
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def write_csv(companies: list[Company], path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for company in companies:
            writer.writerow(company.to_csv_row())
