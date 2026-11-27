"""Reproducible catalogue benchmark for HTML/Playwright versus HTTP API extraction.

Run the same workload with one, two and three independent Celery workers.
Do not change PRODUCT_COUNT, page count or method within a comparison series.
"""
import argparse
import csv
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

from app.workers.celery_app import celery


def run_benchmark(shop, pages, method):
    started = time.perf_counter()
    jobs = [
        (page, celery.send_task("app.workers.tasks.scrape_catalog",
                               args=[shop, page, method], queue="catalog"))
        for page in range(1, pages + 1)
    ]
    counts = 0
    latencies = []
    errors = []
    for page, result in jobs:
        try:
            value = result.get(timeout=180)
            counts += int(value["count"])
            latencies.append(float(value["duration_ms"]))
        except Exception as exc:
            errors.append(f"page {page}: {str(exc)[:180]}")
    elapsed = time.perf_counter() - started
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "shop": shop, "method": method, "pages": pages,
        "products": counts, "errors": len(errors),
        "duration_s": round(elapsed, 3),
        "throughput_products_s": round(counts / elapsed, 2) if elapsed else 0,
        "mean_task_ms": round(statistics.mean(latencies), 2) if latencies else None,
        "p95_task_ms": round(sorted(latencies)[max(0, int(len(latencies) * 0.95) - 1)], 2) if latencies else None,
        "error_details": " | ".join(errors),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shop", choices=["a", "b", "c"], default="a")
    parser.add_argument("--method", choices=["html", "api"], default="html")
    parser.add_argument("--pages", type=int, default=10)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--csv", default="benchmark-results.csv")
    parser.add_argument("--label", required=True, help="Np. 1-worker / 2-workers / 3-workers")
    args = parser.parse_args()
    if not (1 <= args.pages <= 250 and 1 <= args.repeats <= 30):
        parser.error("--pages: 1–250, --repeats: 1–30")
    destination = Path(args.csv)
    destination.parent.mkdir(parents=True, exist_ok=True)

    for index in range(args.repeats):
        result = run_benchmark(args.shop, args.pages, args.method)
        result["repetition"] = index + 1
        result["worker_configuration"] = args.label
        is_new = not destination.exists() or destination.stat().st_size == 0
        with destination.open("a", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(result))
            if is_new:
                writer.writeheader()
            writer.writerow(result)
        print(result, flush=True)


if __name__ == "__main__":
    main()
