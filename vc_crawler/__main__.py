from __future__ import annotations

import argparse
import importlib
import logging
import sys
from pathlib import Path

from .export import write_csv, write_json
from .http_client import PoliteClient

log = logging.getLogger("vc_crawler")

_FUND_REGISTRY = {
    "sequoia": "vc_crawler.crawlers.sequoia.crawler.SequoiaCrawler",
    "a16z": "vc_crawler.crawlers.a16z.crawler.A16ZCrawler",
    "a16z-speedrun": "vc_crawler.crawlers.a16z_speedrun.crawler.SpeedrunCrawler",
    "owl-ventures": "vc_crawler.crawlers.owl_ventures.crawler.OwlCrawler",
    "reach-capital": "vc_crawler.crawlers.reach_capital.crawler.ReachCrawler",
    "gsv-ventures": "vc_crawler.crawlers.gsv_ventures.crawler.GSVCrawler",
    "learn-capital": "vc_crawler.crawlers.learn_capital.crawler.LearnCrawler",
    "brighteye": "vc_crawler.crawlers.brighteye.crawler.BrighteyeCrawler",
}


def _load_crawler_class(dotted: str):
    module_path, class_name = dotted.rsplit(".", 1)
    return getattr(importlib.import_module(module_path), class_name)


def _parse_args(argv):
    p = argparse.ArgumentParser(
        prog="vc_crawler",
        description="Crawl VC fund portfolio companies to JSON/CSV.",
    )
    p.add_argument("--fund", choices=list(_FUND_REGISTRY), required=True)
    p.add_argument("--out", type=Path, default=Path("data"))
    p.add_argument("--format", choices=["json", "csv", "both"], default="both")
    p.add_argument("--workers", type=int, default=5)
    p.add_argument("--delay", type=float, default=0.2)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--no-enrich", action="store_true")
    p.add_argument("--verbose", action="store_true")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    client = PoliteClient(delay=args.delay)
    CrawlerClass = _load_crawler_class(_FUND_REGISTRY[args.fund])
    companies = CrawlerClass(client).run(
        limit=args.limit,
        workers=args.workers,
        enrich=not args.no_enrich,
    )
    log.info("Done: %d companies from %s", len(companies), args.fund)

    fund_dir = args.out / args.fund
    fund_dir.mkdir(parents=True, exist_ok=True)
    if args.format in ("json", "both"):
        path = fund_dir / "companies.json"
        write_json(companies, path)
        log.info("Wrote %s", path)
    if args.format in ("csv", "both"):
        path = fund_dir / "companies.csv"
        write_csv(companies, path)
        log.info("Wrote %s", path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
