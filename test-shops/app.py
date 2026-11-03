from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, PlainTextResponse
from html import escape
from urllib.parse import quote
from math import ceil
from products import PRODUCTS, PRICES

app = FastAPI(title="PC Parts Test Shops")

SHOP_STYLES = {
    "a": {
        "primary": "#172033",
        "accent": "#167b4b",
        "background": "#f4f6f9",
    },
    "b": {
        "primary": "#173b70",
        "accent": "#e26b16",
        "background": "#eef4fc",
    },
    "c": {
        "primary": "#292044",
        "accent": "#8b4dd8",
        "background": "#f5f0fc",
    },
}


def format_price(price):
    return f"{price:.2f}".replace(".", ",") + " zł"


def page_template(shop, title, body):
    style = SHOP_STYLES[shop]
    shop_name = shop.upper()

    return f"""
    <!DOCTYPE html>
    <html lang="pl">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport"
            content="width=device-width, initial-scale=1">
      <title>{escape(title)}</title>
      <style>
        body {{
          font-family: Arial, sans-serif;
          background: {style["background"]};
          margin: 0;
          color: #172033;
        }}
        header {{
          background: {style["primary"]};
          color: white;
          padding: 24px 8%;
        }}
        header a {{
          color: white;
          margin-right: 20px;
        }}
        main {{
          max-width: 1100px;
          margin: 35px auto;
          padding: 0 20px;
        }}
        .grid, .offers, .catalog {{
          display: grid;
          grid-template-columns:
            repeat(auto-fit, minmax(230px, 1fr));
          gap: 20px;
          list-style: none;
          padding: 0;
        }}
        .product, .offer-card, .catalog-item {{
          background: white;
          padding: 24px;
          border-radius: 12px;
          box-shadow: 0 3px 12px #00000012;
        }}
        .price, .offer-price, .catalog-price {{
          color: {style["accent"]};
          font-size: 24px;
          font-weight: bold;
        }}
        input, button {{
          padding: 12px;
          border-radius: 6px;
          border: 1px solid #ccc;
        }}
        button {{
          cursor: pointer;
        }}
        a {{
          color: #2464bc;
        }}
        .pagination a {{
          display: inline-block;
          padding: 8px 12px;
          margin-right: 8px;
          background: white;
          border-radius: 6px;
        }}
      </style>
    </head>
    <body>
      <header>
        <h1>PC Parts — sklep testowy {shop_name}</h1>
        <nav>
          <a href="/shop-a">Sklep A</a>
          <a href="/shop-b">Sklep B</a>
          <a href="/shop-c">Sklep C</a>
        </nav>
      </header>
      <main>{body}</main>
    </body>
    </html>
    """


def render_product(shop, product):
    product_id = product["id"]
    name = escape(product["name"])
    price = format_price(PRICES[shop][product_id])
    link = f"/shop-{shop}/product/{product_id}"

    if shop == "a":
        return f"""
        <article class="product">
          <h2 class="product-name">{name}</h2>
          <p class="price">{price}</p>
          <a class="product-link" href="{link}">
            Szczegóły produktu
          </a>
        </article>
        """

    if shop == "b":
        return f"""
        <div class="offer-card"
             data-product-id="{product_id}">
          <h3 class="offer-title">{name}</h3>
          <div class="offer-price">{price}</div>
          <a class="offer-link" href="{link}">
            Zobacz ofertę
          </a>
        </div>
        """

    return f"""
    <li class="catalog-item"
        data-id="{product_id}">
      <span class="catalog-title">{name}</span>
      <strong class="catalog-price">{price}</strong>
      <a class="catalog-link" href="{link}">
        Przejdź do produktu
      </a>
    </li>
    """


def search_products(shop, q, page):
    matched = [
        product for product in PRODUCTS
        if all(
            word in product["name"].lower()
            for word in q.lower().split()
        )
    ]

    per_page = 40
    total_pages = max(1, ceil(len(matched) / per_page))
    page = min(page, total_pages)

    start = (page - 1) * per_page
    visible = matched[start:start + per_page]

    cards = "".join(
        render_product(shop, product)
        for product in visible
    )

    if shop == "a":
        product_list = f'<div class="grid">{cards}</div>'
    elif shop == "b":
        product_list = f'<section class="offers">{cards}</section>'
    else:
        product_list = f'<ul class="catalog">{cards}</ul>'

    pagination = " ".join(
        f'<a href="/shop-{shop}?q={quote(q)}&page={n}">{n}</a>'
        for n in range(1, total_pages + 1)
    )

    body = f"""
    <form method="get" action="/shop-{shop}">
      <input name="q"
             value="{escape(q, quote=True)}"
             placeholder="Wyszukaj podzespoły">
      <button type="submit">Szukaj</button>
    </form>

    <p>Znaleziono produktów: {len(matched)}</p>

    {product_list}

    <div class="pagination">
      <p>Strony: {pagination}</p>
    </div>
    """

    return page_template(
        shop,
        f"Sklep testowy {shop.upper()}",
        body,
    )


def product_details(shop, product_id):
    product = next(
        (p for p in PRODUCTS if p["id"] == product_id),
        None,
    )

    if product is None:
        return HTMLResponse(
            "Nie znaleziono produktu",
            status_code=404,
        )

    price = format_price(PRICES[shop][product_id])

    body = f"""
    <h2>{escape(product["name"])}</h2>
    <p class="price">{price}</p>
    <a href="/shop-{shop}">Powrót do sklepu</a>
    """

    return page_template(shop, product["name"], body)


@app.get("/shop-a", response_class=HTMLResponse)
def shop_a(q: str = "", page: int = Query(1, ge=1)):
    return search_products("a", q, page)


@app.get("/shop-b", response_class=HTMLResponse)
def shop_b(q: str = "", page: int = Query(1, ge=1)):
    return search_products("b", q, page)


@app.get("/shop-c", response_class=HTMLResponse)
def shop_c(q: str = "", page: int = Query(1, ge=1)):
    return search_products("c", q, page)


@app.get("/shop-a/product/{product_id}", response_class=HTMLResponse)
def shop_a_product(product_id: int):
    return product_details("a", product_id)


@app.get("/shop-b/product/{product_id}", response_class=HTMLResponse)
def shop_b_product(product_id: int):
    return product_details("b", product_id)


@app.get("/shop-c/product/{product_id}", response_class=HTMLResponse)
def shop_c_product(product_id: int):
    return product_details("c", product_id)


@app.get("/robots.txt")
def robots():
    return PlainTextResponse("User-agent: *\nAllow: /\n")
