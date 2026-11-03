
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from html import escape
from urllib.parse import quote
from math import ceil

app = FastAPI(title="PC Parts Test Shop")

PRODUCTS = [
    {"id": 1, "name": "AMD Ryzen 5 7500F", "price": 599.00},
    {"id": 2, "name": "AMD Ryzen 7 7700", "price": 899.99},
    {"id": 3, "name": "AMD Ryzen 7 7800X3D", "price": 1399.00},
    {"id": 4, "name": "NVIDIA GeForce RTX 4070 12GB", "price": 2399.00},
    {"id": 5, "name": "AMD Radeon RX 7800 XT 16GB", "price": 2199.99},
    {"id": 6, "name": "Kingston Fury DDR5 32GB 6000MHz", "price": 429.00},
    {"id": 7, "name": "Lexar NM790 NVMe 1TB", "price": 299.99},
    {"id": 8, "name": "Samsung 990 PRO NVMe 2TB", "price": 699.00},
]


def page_template(title, body):
    return f"""
    <!DOCTYPE html>
    <html lang="pl">
    <head>
      <meta charset="UTF-8">
      <title>{escape(title)}</title>
      <style>
        body {{
          font-family: Arial, sans-serif;
          background: #f4f6f9;
          margin: 0;
          color: #172033;
        }}
        header {{
          background: #172033;
          color: white;
          padding: 24px 8%;
        }}
        main {{
          max-width: 1100px;
          margin: 35px auto;
          padding: 0 20px;
        }}
        .grid {{
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
          gap: 20px;
        }}
        .product {{
          background: white;
          padding: 24px;
          border-radius: 12px;
          box-shadow: 0 3px 12px #00000012;
        }}
        .price {{
          color: #167b4b;
          font-size: 24px;
          font-weight: bold;
        }}
        input, button {{
          padding: 12px;
          border-radius: 6px;
          border: 1px solid #ccc;
        }}
        a {{ color: #2464bc; }}
      </style>
    </head>
    <body>
      <header><h1>PC Parts — sklep testowy A</h1></header>
      <main>{body}</main>
    </body>
    </html>
    """


@app.get("/shop-a", response_class=HTMLResponse)
def search_products(
    q: str = "",
    page: int = Query(1, ge=1),
):
    matched = [
        p for p in PRODUCTS
        if all(
            word in p["name"].lower()
            for word in q.lower().split()
        )
    ]

    per_page = 4
    total_pages = max(1, ceil(len(matched) / per_page))
    page = min(page, total_pages)

    start = (page - 1) * per_page
    visible = matched[start:start + per_page]

    cards = ""

    for product in visible:
        price = f'{product["price"]:.2f}'.replace(".", ",")

        cards += f"""
        <article class="product">
          <h2 class="product-name">{escape(product["name"])}</h2>
          <p class="price">{price} zł</p>
          <a class="product-link"
             href="/shop-a/product/{product['id']}">
             Szczegóły produktu
          </a>
        </article>
        """

    pagination = " ".join(
        f'<a href="/shop-a?q={quote(q)}&page={n}">{n}</a>'
        for n in range(1, total_pages + 1)
    )

    body = f"""
    <form method="get" action="/shop-a">
      <input name="q" value="{escape(q, quote=True)}"
             placeholder="Wyszukaj podzespoły">
      <button type="submit">Szukaj</button>
    </form>
    <p>Znaleziono produktów: {len(matched)}</p>
    <div class="grid">{cards}</div>
    <p>Strony: {pagination}</p>
    """

    return page_template("Sklep testowy A", body)


@app.get("/shop-a/product/{product_id}", response_class=HTMLResponse)
def product_details(product_id: int):
    product = next(
        (p for p in PRODUCTS if p["id"] == product_id),
        None
    )

    if product is None:
        return HTMLResponse("Nie znaleziono produktu", status_code=404)

    price = f'{product["price"]:.2f}'.replace(".", ",")

    body = f"""
    <h2>{escape(product["name"])}</h2>
    <p class="price">{price} zł</p>
    <a href="/shop-a">Powrót do sklepu</a>
    """

    return page_template(product["name"], body)


@app.get("/robots.txt")
def robots():
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse("User-agent: *\nAllow: /\n")
