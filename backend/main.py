from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json

from scraper import compare_prices, compare_prices_stream
from database import SessionLocal, engine
from models import Base, PriceHistory

app = FastAPI()

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== STARTUP =====
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    print("DB ready")


# ===== ROOT =====
@app.get("/")
async def root():
    return {"status": "API działa"}


# ===== API: NORMAL SCRAPE =====
@app.get("/api/compare")
async def compare(query: str):
    data = await compare_prices(query)

    if not data:
        return {"error": "Brak wyników"}

    # zapis do DB
    db = SessionLocal()
    try:
        record = PriceHistory(
            query=query,
            xkom=data["results"].get("x-kom"),
            morele=data["results"].get("morele"),
            mediaexpert=data["results"].get("mediaexpert"),
            cheapest=data["cheapest"],
            most_expensive=data["most_expensive"]
        )
        db.add(record)
        db.commit()
    finally:
        db.close()

    return data


# ===== API: STREAM (PROGRESS) =====
@app.get("/api/compare-stream")
async def compare_stream(query: str):

    async def event_generator():
        async for event in compare_prices_stream(query):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ===== API: HISTORY =====
@app.get("/api/history")
async def history():
    db = SessionLocal()

    try:
        records = db.query(PriceHistory).order_by(PriceHistory.id.desc()).all()
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
        for r in records
    ]
