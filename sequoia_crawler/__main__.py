from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from . import api
from .enrich import enrich_all
from .export import write_csv, write_json
from .http_client import PoliteClient
from .sitemap import fetch_company_slugs

log = logging.getLogger("sequoia_crawler")


def build_companies(client) -> list:
    sectors = api.fetch_categories(client)
    log.info("Loaded %d sector categories", len(sectors))
    return [api.to_company(raw, sectors) for raw in api.iter_companies(client)]


def _check_completeness(client, companies) -> None:
    try:
        sitemap_slugs = fetch_company_slugs(client)
    except Exception as exc:  # noqa: BLE001
        log.warning("sitemap check skipped: %s", exc)
        return
    have = {c.slug for c in companies}
    missing = sitemap_slugs - have
    extra = have - sitemap_slugs
    log.info(
        "Completeness: api=%d sitemap=%d missing_from_api=%d api_only=%d",
        len(have), len(sitemap_slugs), len(missing), len(extra),
    )
    if missing:
        log.warning("Slugs in sitemap but not in API: %s", sorted(missing)[:20])


def _parse_args(argv):
    p = argparse.ArgumentParser(
        prog="sequoia_crawler",
        description="Crawl Sequoia Capital portfolio companies to JSON/CSV.",
    )
    p.add_argument("--out", type=Path, default=Path("output"))
    p.add_argument("--format", choices=["json", "csv", "both"], default="both")
    p.add_argument("--workers", type=int, default=5)
    p.add_argument("--delay", type=float, default=0.2)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--no-enrich", action="store_true",
                   help="index only; skip detail-page enrichment")
    p.add_argument("--verbose", action="store_true")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    client = PoliteClient(delay=args.delay)

    log.info("Fetching company index from REST API ...")
    companies = build_companies(client)
    log.info("Index: %d companies", len(companies))
    _check_completeness(client, companies)

    if args.limit:
        companies = companies[: args.limit]
        log.info("Limited to %d companies", len(companies))

    if not args.no_enrich:
        log.info("Enriching %d companies (workers=%d) ...", len(companies), args.workers)
        companies = enrich_all(client, companies, workers=args.workers)

    args.out.mkdir(parents=True, exist_ok=True)
    if args.format in ("json", "both"):
        write_json(companies, args.out / "companies.json")
        log.info("Wrote %s", args.out / "companies.json")
    if args.format in ("csv", "both"):
        write_csv(companies, args.out / "companies.csv")
        log.info("Wrote %s", args.out / "companies.csv")

    log.info("Done: %d companies", len(companies))
    return 0


if __name__ == "__main__":
    sys.exit(main())
