from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import (
    SessionLocal,
    engine
)

from app.models.price_history import (
    Base,
    PriceHistory
)

from app.workers.tasks import (
    scrape_xkom,
    scrape_morele,
    scrape_media
)


app = FastAPI(
    title="PC Parts Price API"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(
        bind=engine
    )

    print(
        "DB ready"
    )


@app.get("/")
async def root():
    return {
        "status": "API działa"
    }


def parse_price(value):

    return float(
        value
        .replace("zł", "")
        .replace(",", ".")
        .replace(" ", "")
        .replace("\u202f", "")
    )



@app.get("/api/compare")
async def compare(
    query: str
):

    x_task = scrape_xkom.delay(
        query
    )

    morele_task = scrape_morele.delay(
        query
    )

    media_task = scrape_media.delay(
        query
    )

    results = {}


    try:
        x_result = x_task.get(
            timeout=30
        )

        if x_result:
            results["x-kom"] = x_result

    except Exception as e:
        print(
            "x-kom error:",
            e
        )


    try:
        m_result = morele_task.get(
            timeout=30
        )

        if m_result:
            results["morele"] = m_result

    except Exception as e:
        print(
            "morele error:",
            e
        )


    try:
        media_result = media_task.get(
            timeout=30
        )

        if media_result:
            results["mediaexpert"] = media_result

    except Exception as e:
        print(
            "mediaexpert error:",
            e
        )


    if not results:
        return {
            "error":
            "Brak wyników"
        }


    numeric = {
        shop: parse_price(price)
        for shop, price in results.items()
    }


    cheapest = min(
        numeric,
        key=numeric.get
    )

    most_expensive = max(
        numeric,
        key=numeric.get
    )


    db = SessionLocal()

    try:

        row = PriceHistory(
            query=query,
            xkom=results.get(
                "x-kom"
            ),
            morele=results.get(
                "morele"
            ),
            mediaexpert=results.get(
                "mediaexpert"
            ),
            cheapest=cheapest,
            most_expensive=most_expensive
        )

        db.add(
            row
        )

        db.commit()

    finally:
        db.close()


    return {
        "query": query,
        "results": results,
        "cheapest": cheapest,
        "most_expensive": most_expensive
    }



@app.get("/api/history")
async def history():

    db = SessionLocal()

    try:

        rows = (
            db.query(
                PriceHistory
            )
            .order_by(
                PriceHistory.id.desc()
            )
            .all()
        )

    finally:
        db.close()


    return [
        {
            "query": r.query,
            "xkom": r.xkom,
            "morele": r.morele,
            "mediaexpert": r.mediaexpert,
            "cheapest": r.cheapest,
            "most_expensive": r.most_expensive
        }

        for r in rows
    ]


@app.get("/api/compare-stream")
async def compare_stream(
    query: str
):
    return {
        "info":
        "stream disabled"
    }
