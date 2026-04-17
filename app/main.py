from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from scraper import compare_prices

from database import SessionLocal, engine
from models import Base, PriceHistory

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    print("DB ready")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "request": request,
            "result": None
        }
    )


@app.post("/scrape", response_class=HTMLResponse)
async def scrape(request: Request, query: str = Form(...)):

    data = await compare_prices(query)

    if not data:
        result = None
    else:
        result = {
            "prices": data["results"],
            "cheapest": data["cheapest"],
            "most_expensive": data["most_expensive"]
        }

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

    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "request": request,
            "result": result
        }
    )


@app.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    db = SessionLocal()

    try:
        records = db.query(PriceHistory).order_by(PriceHistory.id.desc()).all()
    finally:
        db.close()

    return templates.TemplateResponse(
        request,
        "history.html",
        {
            "request": request,
            "records": records
        }
    )
