
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import SessionLocal, engine
from app.models.price_history import Base, PriceHistory
from app.models.user import User

from app.api.auth import (
    router as auth_router,
    get_current_user,
)

from app.workers.tasks import scrape_shop_a


app = FastAPI(title="PC Parts Price API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    print("DB ready")


@app.get("/")
async def root():
    return {"status": "API działa"}


def parse_price(value):
    return float(
        value
        .replace("zł", "")
        .replace(",", ".")
        .replace(" ", "")
        .replace("\u202f", "")
        .replace("\xa0", "")
    )


@app.get("/api/compare")
def compare(
    query: str,
    user: User = Depends(get_current_user),
):
    # Wysłanie zadania do kolejki shop_a
    shop_a_task = scrape_shop_a.delay(query)

    results = {}

    try:
        result = shop_a_task.get(timeout=60)

        if result and result.get("price"):
            results["shop_a"] = result

    except Exception as e:
        print("shop_a error:", e)

    if not results:
        return {
            "query": query,
            "error": "Brak wyników",
            "results": {},
            "cheapest": None,
            "most_expensive": None,
        }

    numeric = {
        shop: parse_price(data["price"])
        for shop, data in results.items()
    }

    cheapest = min(numeric, key=numeric.get)
    most_expensive = max(numeric, key=numeric.get)

    # Na razie nie zapisujemy wyniku do PriceHistory.
    # Model bazy danych zostanie dostosowany
    # po dodaniu sklepów B i C.

    return {
        "query": query,
        "results": results,
        "cheapest": cheapest,
        "most_expensive": most_expensive,
    }


@app.get("/api/history")
async def history(
    user: User = Depends(get_current_user),
):
    db = SessionLocal()

    try:
        rows = (
            db.query(PriceHistory)
            .filter(PriceHistory.user_id == user.id)
            .order_by(PriceHistory.id.desc())
            .all()
        )

        return [
            {
                "query": r.query,
                "xkom": r.xkom,
                "morele": r.morele,
                "mediaexpert": r.mediaexpert,
                "cheapest": r.cheapest,
                "most_expensive": r.most_expensive,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]

    finally:
        db.close()
