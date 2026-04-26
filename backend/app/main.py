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
        "status":"API działa"
    }



def parse_price(value):

    return float(
        value
        .replace("zł","")
        .replace(",",".")
        .replace(" ","")
        .replace("\u202f","")
    )



@app.get("/api/compare")
async def compare(
    query:str
):

    x_task = scrape_xkom.delay(query)
    m_task = scrape_morele.delay(query)
    me_task = scrape_media.delay(query)

    results = {}


    try:
        r = x_task.get(
            timeout=30
        )

        if r:
            results["x-kom"] = r

    except Exception as e:
        print(
          "xkom error",
          e
        )



    try:
        r = m_task.get(
            timeout=30
        )

        if r:
            results["morele"] = r

    except Exception as e:
        print(
          "morele error",
          e
        )



    try:
        r = me_task.get(
            timeout=30
        )

        if r:
            results["mediaexpert"] = r

    except Exception as e:
        print(
          "mediaexpert error",
          e
        )


    if not results:
        return {
          "error":
          "Brak wyników"
        }


    numeric = {

        shop:
        parse_price(
            data["price"]
        )

        for shop,data
        in results.items()
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

            xkom=(
             results["x-kom"]["price"]
             if "x-kom" in results
             else None
            ),

            morele=(
             results["morele"]["price"]
             if "morele" in results
             else None
            ),

            mediaexpert=(
             results["mediaexpert"]["price"]
             if "mediaexpert" in results
             else None
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

      "query":
       query,

      "results":
       results,

      "cheapest":
       cheapest,

      "most_expensive":
       most_expensive
    }



@app.get("/api/history")
async def history():

    db=SessionLocal()

    try:

        rows=(
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
        "query":
           r.query,

        "xkom":
           r.xkom,

        "morele":
           r.morele,

        "mediaexpert":
           r.mediaexpert,

        "cheapest":
           r.cheapest,

        "most_expensive":
           r.most_expensive
      }

      for r in rows

    ]
