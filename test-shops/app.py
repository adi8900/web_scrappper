"""Three distinct simulated stores, backed by one reproducible hardware catalogue."""
from html import escape
import json
from math import ceil
from urllib.parse import urlencode

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, PlainTextResponse
from products import PRODUCTS, PRICES, BY_ID, matches

app = FastAPI(title="PC Parts - simulated research stores", version="2.0")

STORES = {
    "a": {"name": "ByteMarket", "sub": "Podzespoły do Twojego komputera",
          "primary": "#12253f", "accent": "#0a986f", "light": "#e9f8f2"},
    "b": {"name": "VoltZone", "sub": "Technologia w dobrych cenach",
          "primary": "#242044", "accent": "#e87825", "light": "#fff1e4"},
    "c": {"name": "CoreHub", "sub": "Centrum komponentów PC",
          "primary": "#133c52", "accent": "#2586d7", "light": "#e9f5ff"},
}
CATEGORIES = ["CPU", "GPU", "RAM", "SSD", "Płyta główna", "Zasilacz"]


def money(value):
    return f"{value:,.2f}".replace(",", " ").replace(".", ",") + " zł"


def find_products(query="", category="", shop="a"):
    if category and category not in CATEGORIES:
        return []
    return [p for p in PRODUCTS if matches(p, query) and (not category or p["category"] == category)]


def shop_data(shop, product):
    return {**product, "price": PRICES[shop][product["id"]], "currency": "PLN",
            "shop": shop, "shop_name": STORES[shop]["name"],
            "url": f"/shop-{shop}/product/{product['id']}"}


def layout(shop, page_title, body, query=""):
    s = STORES[shop]
    navigation = "".join(
        f'<a href="/shop-{x}">{escape(info["name"])}</a>'
        for x, info in STORES.items()
    )
    return f"""<!doctype html>
<html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(page_title)} | {escape(s['name'])}</title>
<style>
:root{{--primary:{s['primary']};--accent:{s['accent']};--light:{s['light']}}}
*{{box-sizing:border-box}} body{{margin:0;background:#f4f6fa;color:#203047;font:16px/1.5 system-ui,Arial,sans-serif}}
header{{background:var(--primary);color:#fff}} .top{{max-width:1240px;margin:auto;padding:23px 22px;display:flex;align-items:center;gap:24px;justify-content:space-between;flex-wrap:wrap}}
.brand{{font-size:29px;font-weight:900;letter-spacing:-1px}}.brand span{{color:#8be3c2}} .tagline{{font-size:13px;opacity:.8}}
nav{{display:flex;gap:18px;flex-wrap:wrap}}nav a{{color:#fff;text-decoration:none;font-size:14px;opacity:.86}}nav a:hover{{opacity:1;text-decoration:underline}}
main{{max-width:1240px;margin:36px auto;padding:0 22px}}.hero{{background:linear-gradient(130deg,var(--primary),#385d85);color:white;border-radius:20px;padding:32px;margin-bottom:25px}}
.hero h1{{margin:0 0 8px;font-size:30px}}.hero p{{margin:0;opacity:.85}}
.panel{{background:white;padding:20px;border-radius:14px;box-shadow:0 4px 22px #16253d10;margin:20px 0}}
.search{{display:flex;gap:10px;flex-wrap:wrap}}.search input{{flex:1;min-width:200px}} input,select{{padding:12px 14px;border:1px solid #ccd5e1;border-radius:9px;font-size:15px}}
button,.btn{{background:var(--accent);border:0;color:white;padding:12px 20px;border-radius:9px;cursor:pointer;font-size:14px;font-weight:700;text-decoration:none;display:inline-block}}
h2{{margin:5px 0 15px}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(255px,1fr));gap:18px}}
.product,.offer-card,.catalog-item{{list-style:none;background:white;border:1px solid #e1e6ee;border-radius:15px;padding:20px;display:flex;flex-direction:column;gap:10px;box-shadow:0 3px 13px #1b32540b}}
.product:hover,.offer-card:hover,.catalog-item:hover{{border-color:var(--accent)}}
.category{{font-size:12px;font-weight:750;letter-spacing:.05em;text-transform:uppercase;color:var(--accent)}}
.visual{{height:90px;border-radius:10px;background:var(--light);display:grid;place-items:center;font-weight:900;color:var(--primary);font-size:24px}}
.product-name,.offer-title,.catalog-title{{font-size:17px;font-weight:750;margin:0;min-height:52px;color:#172c48}}
.price,.offer-price,.catalog-price{{font-size:26px;font-weight:850;color:var(--accent);margin-top:auto}}
.product-link,.offer-link,.catalog-link{{color:var(--primary);font-weight:700}}
.muted{{color:#697789;font-size:13px}}.stock{{color:#138653;font-size:13px}}
.tags{{display:flex;gap:8px;flex-wrap:wrap}}.tag{{background:#edf2f7;padding:5px 9px;border-radius:7px;font-size:12px}}
.pagination{{display:flex;gap:8px;flex-wrap:wrap;margin:25px 0}}.pagination a{{background:white;padding:9px 13px;border-radius:8px;text-decoration:none;color:var(--primary)}}
.pagination a.active{{background:var(--primary);color:white}}
.detail{{display:grid;grid-template-columns:1fr 1.5fr;gap:25px}}.specs{{width:100%;border-collapse:collapse}}.specs td{{padding:12px;border-bottom:1px solid #e4e9f0}}.specs td:first-child{{color:#607184}}
footer{{margin:55px auto 0;padding:24px;text-align:center;color:#697789;background:#e9edf4;font-size:13px}}
@media(max-width:700px){{.detail{{grid-template-columns:1fr}}.brand{{font-size:23px}}}}
</style></head><body>
<header><div class="top"><div><div class="brand">{escape(s['name'])}<span>.</span></div><div class="tagline">{escape(s['sub'])}</div></div><nav>{navigation}</nav></div></header>
<main>{body}</main><footer>Środowisko symulacyjne do badań naukowych. Ceny i dostępność są wygenerowane, nie stanowią ofert handlowych.</footer>
</body></html>"""


def render_card(shop, item):
    p = item
    title = escape(p["name"])
    url = escape(f"/shop-{shop}/product/{p['id']}", quote=True)
    price = money(PRICES[shop][p["id"]])
    label = escape(p["category"])
    variation = '<div class="muted">Powielona oferta testowa</div>' if p["benchmark_offer"] else ''
    metadata = escape(json.dumps(p["specs"], ensure_ascii=False), quote=True)
    sku = escape(p["sku"], quote=True)
    specs = " • ".join(f"{escape(str(k))}: {escape(str(v))}" for k, v in list(p["specs"].items())[:2])
    if shop == "a":
        return f"""<article class="product" data-product-id="{p['product_id']}" data-listing-id="{p['id']}" data-specs="{metadata}" data-sku="{sku}">
<div class="visual">{label}</div><div class="category">{label}</div>
<h3 class="product-name">{title}</h3><div class="muted">{specs}</div>{variation}
<div class="price">{price}</div><span class="stock">● Dostępny ({p['stock']} szt.)</span>
<a class="product-link" href="{url}">Zobacz produkt →</a></article>"""
    if shop == "b":
        return f"""<div class="offer-card" data-product-id="{p['product_id']}" data-listing-id="{p['id']}">
<div class="category">OFERTA • {label}</div><div class="visual">{label}</div>
<h3 class="offer-title">{title}</h3><div class="tags"><span class="tag">{specs}</span></div>{variation}
<div class="offer-price">{price}</div><span class="stock">W magazynie: {p['stock']} szt.</span>
<a class="offer-link" href="{url}">Sprawdź ofertę →</a></div>"""
    return f"""<li class="catalog-item" data-product-id="{p['product_id']}" data-listing-id="{p['id']}">
<div class="visual">{label}</div><div class="category">{label}</div>
<strong class="catalog-title">{title}</strong><div class="muted">{specs}</div>{variation}
<strong class="catalog-price">{price}</strong><span class="stock">Produkt dostępny</span>
<a class="catalog-link" href="{url}">Szczegóły →</a></li>"""


def listing(shop, q, category, page, per_page):
    matched = find_products(q, category, shop)
    max_page = max(1, ceil(len(matched) / per_page))
    if page > max_page:
        raise HTTPException(404, "Strona poza zakresem")
    items = matched[(page - 1) * per_page:page * per_page]
    cards = "".join(render_card(shop, p) for p in items)
    category_options = '<option value="">Wszystkie kategorie</option>' + "".join(
        f'<option value="{escape(c, quote=True)}" {"selected" if c == category else ""}>{escape(c)}</option>'
        for c in CATEGORIES
    )
    links = ""
    for n in range(max(1, page - 3), min(max_page, page + 3) + 1):
        state = "active" if n == page else ""
        parameters = urlencode({"q": q, "category": category, "page": n, "per_page": per_page})
        links += f'<a class="{state}" href="/shop-{shop}?{parameters}">{n}</a>'
    wrapper = {"a": 'div class="grid"', "b": 'section class="grid"', "c": 'ul class="grid"'}[shop]
    body = f"""<section class="hero"><h1>Odkryj podzespoły komputerowe</h1>
<p>Rzeczywiste modele • specyfikacje producentów • symulowane ceny w PLN</p></section>
<section class="panel"><form class="search" method="get" action="/shop-{shop}">
<input name="q" value="{escape(q, quote=True)}" placeholder="Np. Ryzen 7500F, DDR5 32GB, NVMe 1TB">
<select name="category">{category_options}</select>
<button type="submit">Wyszukaj</button></form></section>
<h2>Produkty <small class="muted">({len(matched)} ofert)</small></h2>
<{wrapper}>{cards}</{wrapper.split()[0]}>
<div class="pagination">{links}</div>"""
    return HTMLResponse(layout(shop, "Katalog produktów", body))


def detail(shop, product_id):
    p = BY_ID.get(product_id)
    if not p:
        raise HTTPException(404, "Nie znaleziono produktu")
    rows = "".join(f"<tr><td>{escape(str(key))}</td><td>{escape(str(value))}</td></tr>" for key, value in p["specs"].items())
    body = f"""<a href="/shop-{shop}">← Powrót do katalogu</a><section class="panel detail">
<div><div class="visual" style="height:260px">{escape(p['category'])}</div>
<p class="muted">Identyfikator modelu: {p['product_id']} • SKU: {escape(p['sku'])}</p></div>
<div><span class="category">{escape(p['category'])}</span><h1>{escape(p['name'])}</h1>
<div class="price">{money(PRICES[shop][product_id])}</div>
<p class="stock">Dostępny: {p['stock']} szt.</p>
<h2>Parametry techniczne</h2><table class="specs">{rows}</table>
<p><a href="{escape(p['source_url'], quote=True)}" target="_blank" rel="noopener noreferrer">Dokumentacja producenta ↗</a></p>
<p class="muted">Specyfikacja produktu oparta na dokumentacji, ceny oraz stany magazynowe są symulowane.</p></div></section>"""
    return HTMLResponse(layout(shop, p["name"], body))


@app.get("/", response_class=HTMLResponse)
def index():
    tiles = "".join(f'<article class="product"><h2>{escape(info["name"])}</h2><p>{escape(info["sub"])}</p><a class="btn" href="/shop-{key}">Otwórz sklep</a></article>' for key, info in STORES.items())
    return HTMLResponse(layout("a", "Sklepy testowe", f'<section class="hero"><h1>Środowisko badawcze e-commerce</h1><p>Trzy niezależne struktury HTML dla badań web scrapingu.</p></section><div class="grid">{tiles}</div>'))


@app.get("/shop-{shop}", response_class=HTMLResponse)
def shop_listing(shop: str, q: str = "", category: str = "", page: int = Query(1, ge=1),
                 per_page: int = Query(40, ge=1, le=100)):
    if shop not in STORES:
        raise HTTPException(404, "Nieznany sklep")
    return listing(shop, q, category, page, per_page)


@app.get("/shop-{shop}/product/{product_id}", response_class=HTMLResponse)
def shop_product(shop: str, product_id: int):
    if shop not in STORES:
        raise HTTPException(404, "Nieznany sklep")
    return detail(shop, product_id)


@app.get("/api/shop-{shop}/products")
def api_products(shop: str, q: str = "", category: str = "", page: int = Query(1, ge=1),
                 per_page: int = Query(40, ge=1, le=100)):
    if shop not in STORES:
        raise HTTPException(404, "Nieznany sklep")
    matched = find_products(q, category, shop)
    result = matched[(page - 1) * per_page:page * per_page]
    return {"shop": shop, "page": page, "per_page": per_page, "total": len(matched),
            "products": [shop_data(shop, p) for p in result]}


@app.get("/api/shop-{shop}/products/{product_id}")
def api_product(shop: str, product_id: int):
    if shop not in STORES:
        raise HTTPException(404, "Nieznany sklep")
    product = BY_ID.get(product_id)
    if not product:
        raise HTTPException(404, "Nie znaleziono produktu")
    return shop_data(shop, product)


@app.get("/health")
def health():
    return {"status": "ok", "models": len(set(p['product_id'] for p in PRODUCTS)), "listings": len(PRODUCTS)}


@app.get("/robots.txt")
def robots():
    return PlainTextResponse("User-agent: *\nAllow: /\n")
