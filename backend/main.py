from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json

from database import SessionLocal, engine
from models import Base, PriceHistory

from tasks import scrape_xkom, scrape_morele, scrape_media

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


# ===== API: CELERY SCRAPE =====
@app.get("/api/compare")
async def compare(query: str):

    # 🔥 wysyłamy taski do workerów
    x = scrape_xkom.delay(query)
    m = scrape_morele.delay(query)
    me = scrape_media.delay(query)

    results = {}

    try:
        x_res = x.get(timeout=30)
        if x_res:
            results["x-kom"] = x_res
    except:
        pass

    try:
        m_res = m.get(timeout=30)
        if m_res:
            results["morele"] = m_res
    except:
        pass

    try:
        me_res = me.get(timeout=30)
        if me_res:
            results["mediaexpert"] = me_res
    except:
        pass

    if not results:
        return {"error": "Brak wyników"}

    # 🔥 wybór min/max
    def parse(price):
        return float(price.replace("zł", "").replace(",", ".").replace(" ", ""))

    numeric = {k: parse(v) for k, v in results.items()}

    cheapest = min(numeric, key=numeric.get)
    most_expensive = max(numeric, key=numeric.get)

    # 🔥 zapis do DB
    db = SessionLocal()
    try:
        record = PriceHistory(
            query=query,
            xkom=results.get("x-kom"),
            morele=results.get("morele"),
            mediaexpert=results.get("mediaexpert"),
            cheapest=cheapest,
            most_expensive=most_expensive
        )
        db.add(record)
        db.commit()
    finally:
        db.close()

    return {
        "results": results,
        "cheapest": cheapest,
        "most_expensive": most_expensive
    }


# ===== STREAM (na razie zostawiamy jak było) =====
@app.get("/api/compare-stream")
async def compare_stream(query: str):
    return {"info": "stream disabled with celery (zrobimy później lepiej)"}


# ===== HISTORY =====
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
