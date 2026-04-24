from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict
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


# ===== MODELE =====
class BuildRequest(BaseModel):
    parts: Dict[str, str]


# ===== ROOT =====
@app.get("/")
async def root():
    return {"status": "API działa"}


# ===== API: CELERY SCRAPE =====
@app.get("/api/compare")
async def compare(query: str):

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

    def parse(price):
        return float(price.replace("zł", "").replace(",", ".").replace(" ", ""))

    numeric = {k: parse(v) for k, v in results.items()}

    cheapest = min(numeric, key=numeric.get)
    most_expensive = max(numeric, key=numeric.get)

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


# ===== API: BUILD PC =====
@app.post("/api/build")
async def build_pc(req: BuildRequest):

    parts = req.parts

    final = {}
    total = 0

    for part_name, query in parts.items():

        x = scrape_xkom.delay(query)
        m = scrape_morele.delay(query)
        me = scrape_media.delay(query)

        results = {}

        for shop, task in {
            "x-kom": x,
            "morele": m,
            "mediaexpert": me
        }.items():
            try:
                res = task.get(timeout=30)
                if res:
                    results[shop] = res
            except Exception as e:
                print(f"{shop} error:", e)

        if not results:
            final[part_name] = {"error": "brak wyników"}
            continue

        def parse(price):
            return float(price.replace("zł", "").replace(",", ".").replace(" ", ""))

        numeric = {k: parse(v) for k, v in results.items()}

        cheapest_shop = min(numeric, key=numeric.get)

        final[part_name] = {
            "query": query,
            "prices": results,
            "best_shop": cheapest_shop,
            "price": numeric[cheapest_shop]
        }

        total += numeric[cheapest_shop]

    return {
        "parts": final,
        "total_price": total
    }


# ===== STREAM (na razie off) =====
@app.get("/api/compare-stream")
async def compare_stream(query: str):
    return {"info": "stream disabled with celery (zrobimy później)"}


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
