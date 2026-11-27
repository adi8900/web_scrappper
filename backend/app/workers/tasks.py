"""Task dispatch wrappers: execution happens only in the remote worker repository."""
from app.workers.celery_app import celery


def dispatch_search(shop, query, method):
    if shop not in ("a", "b", "c"):
        raise ValueError("Unknown test shop")
    return celery.send_task(
        "app.workers.tasks.scrape_shop",
        args=[shop, query, method],
        queue="scraping",
    )


def dispatch_catalog(shop, page, method="html"):
    if shop not in ("a", "b", "c"):
        raise ValueError("Unknown test shop")
    return celery.send_task(
        "app.workers.tasks.scrape_catalog",
        args=[shop, page, method],
        queue="catalog",
    )
