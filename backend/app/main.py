"""Price comparison API for three simulated PC component shops."""
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import get_current_user, router as auth_router
from app.core.database import Base, SessionLocal, engine
from app.models.user import User
from app.models.price_history import PriceHistory  # preserve legacy table
from app.models.search_history import SearchHistory
from app.workers.tasks import dispatch_search

log = logging.getLogger(__name__)

app = FastAPI(title="PC Parts Price API", version="2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(auth_router)
SHOPS = {"a": "ByteMarket", "b": "VoltZone", "c": "CoreHub"}


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"status": "ok", "mode": "simulated-stores", "shops": SHOPS}


def extract_results(tasks):
    def fetch(pair):
        shop, task = pair
        try:
            response = task.get(timeout=90)
            if not isinstance(response, dict):
                return shop, [], {"status": "invalid_result"}
            return shop, response.get("offers", []), {
                "status": "ok", "count": response.get("count", 0),
                "duration_ms": response.get("duration_ms"),
            }
        except Exception as exc:
            log.warning("Worker error in shop %s: %s", shop, exc)
            return shop, [], {"status": "error", "message": str(exc)[:200]}

    with ThreadPoolExecutor(max_workers=3) as pool:
        return list(pool.map(fetch, tasks.items()))


def group_products(completed):
    grouped = {}
    for shop, offers, _metric in completed:
        for offer in offers:
            try:
                product_id = int(offer["product_id"])
                price = float(offer["price"])
                if price <= 0:
                    continue
            except (ValueError, TypeError, KeyError):
                continue

            product = grouped.setdefault(product_id, {
                "product_id": product_id, "name": offer.get("name", "Nieznany produkt"),
                "specs": offer.get("specs") or {},
                "offers": [],
            })
            product["offers"].append({
                "shop": shop, "shop_name": SHOPS[shop],
                "price": round(price, 2), "currency": "PLN",
                "url": offer.get("url"), "listing_id": offer.get("listing_id"),
            })
            if offer.get("specs") and not product["specs"]:
                product["specs"] = offer["specs"]

    products = []
    for product in grouped.values():
        # All offers refer to the same canonical product model.
        product["offers"].sort(key=lambda x: x["price"])
        product["cheapest"] = product["offers"][0]
        product["most_expensive"] = product["offers"][-1]
        product["shop_count"] = len({o["shop"] for o in product["offers"]})
        products.append(product)
    return sorted(products, key=lambda p: (-p["shop_count"], p["name"]))


@app.get("/api/compare")
def compare(query: str = Query(..., min_length=2, max_length=200),
            method: str = Query("html", pattern="^(html|api)$"),
            user: User = Depends(get_current_user)):
    query = query.strip()
    if not query:
        raise HTTPException(400, "Pusta fraza")
    started = time.perf_counter()
    try:
        tasks = {shop: dispatch_search(shop, query, method) for shop in SHOPS}
    except Exception as exc:
        log.exception("Could not enqueue tasks")
        raise HTTPException(503, "Nie można przekazać zadań do kolejki") from exc

    completed = extract_results(tasks)
    products = group_products(completed)
    metrics = {shop: metric for shop, _offers, metric in completed}
    best = products[0] if products else None

    # Backwards-compatible result fields, now only for the same product model.
    results = {}
    if best:
        for offer in best["offers"]:
            current = results.get(offer["shop"])
            if not current or offer["price"] < current["numeric_price"]:
                results[offer["shop"]] = {
                    "price": f"{offer['price']:.2f} zł",
                    "numeric_price": offer["price"],
                    "url": offer["url"], "name": best["name"],
                }

    response = {
        "query": query, "method": method, "source_type": "simulated",
        "products": products, "products_found": len(products),
        "results": results,
        "cheapest": best["cheapest"]["shop"] if best else None,
        "most_expensive": best["most_expensive"]["shop"] if best else None,
        "metrics": metrics,
        "duration_ms": round((time.perf_counter() - started) * 1000, 2),
        "errors": [shop for shop, metric in metrics.items() if metric["status"] != "ok"],
    }
    db = SessionLocal()
    try:
        db.add(SearchHistory(user_id=user.id, query=query, method=method,
                             result_json=json.dumps(response, ensure_ascii=False)))
        db.commit()
    except Exception:
        db.rollback()
        log.exception("Could not save search history")
        response["history_saved"] = False
    finally:
        db.close()
    return response


@app.get("/api/history")
def history(user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        rows = (db.query(SearchHistory).filter(SearchHistory.user_id == user.id)
                .order_by(SearchHistory.id.desc()).limit(100).all())
        return [{
            "id": row.id, "query": row.query, "method": row.method,
            "created_at": row.created_at.isoformat(),
            "result": json.loads(row.result_json),
        } for row in rows]
    finally:
        db.close()
