
import argparse
import time

from app.workers.celery_app import celery


def benchmark(shop, pages):
    start = time.perf_counter()

    tasks = []

    print(f"Uruchamiam {pages} zadań dla sklepu {shop}", flush=True)

    for page in range(1, pages + 1):
        task = celery.send_task(
            "app.workers.tasks.scrape_catalog",
            args=[shop, page],
            queue="catalog",
        )
        tasks.append((page, task))

    total_products = 0
    errors = 0

    for page, task in tasks:
        try:
            result = task.get(timeout=180)
            total_products += result["count"]

        except Exception as exc:
            errors += 1
            print(f"Błąd strony {page}: {exc}", flush=True)

    duration = time.perf_counter() - start

    print("\n=== WYNIKI BENCHMARKU ===")
    print(f"Sklep: {shop}")
    print(f"Liczba stron: {pages}")
    print(f"Produkty: {total_products}")
    print(f"Błędy: {errors}")
    print(f"Czas: {duration:.2f} s")
    print(
        f"Wydajność: "
        f"{total_products / duration:.2f} produktów/s"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--shop",
        choices=["a", "b", "c"],
        default="a",
    )

    parser.add_argument(
        "--pages",
        type=int,
        default=10,
    )

    args = parser.parse_args()

    if not 1 <= args.pages <= 250:
        parser.error("--pages musi być w zakresie 1–250")

    benchmark(args.shop, args.pages)
