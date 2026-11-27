"""Contract tests for the deterministic research environment."""
import json
import os
import sys
from pathlib import Path

os.environ["PRODUCT_COUNT"] = "15"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "test-shops"))

from fastapi.testclient import TestClient
from bs4 import BeautifulSoup
from products import CATALOG, PRODUCTS, PRICES, generate_prices, generate_products, matches
from app import app

client = TestClient(app)


def test_curated_catalogue_is_realistic_and_stable():
    assert len(CATALOG) == 15
    assert len({p["sku"] for p in CATALOG}) == len(CATALOG)
    assert {"CPU", "GPU", "RAM", "SSD", "Płyta główna", "Zasilacz"} <= {
        p["category"] for p in CATALOG}
    assert all(p["specs"] and p["source_url"].startswith("https://") for p in CATALOG)
    assert matches(CATALOG[0], "ryzen 7500f")
    assert not matches(CATALOG[0], "intel i7")


def test_benchmark_records_repeat_models_not_fictitious_products():
    offers = generate_products(300)
    assert len(offers) == 300
    assert all(offer["product_id"] in {p["id"] for p in CATALOG} for offer in offers)
    assert offers[15]["benchmark_offer"] is True
    assert generate_prices(offers) == generate_prices(offers)
    assert PRICES["a"][1] != PRICES["b"][1]


def test_three_store_html_contracts():
    cards = {"a": "article.product", "b": "div.offer-card", "c": "li.catalog-item"}
    for shop, selector in cards.items():
        res = client.get(f"/shop-{shop}", params={"q": "ryzen 7500f"})
        assert res.status_code == 200
        soup = BeautifulSoup(res.text, "html.parser")
        matches_ = soup.select(selector)
        assert len(matches_) == 1
        card = matches_[0]
        assert int(card["data-product-id"]) == 1
        assert json.loads(card["data-specs"])["Gniazdo"] == "AM5"
        assert card.select_one("a[href]") is not None


def test_api_and_html_agree_on_prices_and_identity():
    for shop in "abc":
        result = client.get(f"/api/shop-{shop}/products", params={"q": "ryzen 7500f"})
        assert result.status_code == 200
        data = result.json()
        assert data["total"] == 1
        product = data["products"][0]
        assert product["product_id"] == 1
        assert product["price"] == PRICES[shop][1]
        details = client.get(f"/shop-{shop}/product/{product['id']}")
        assert details.status_code == 200
        assert "AM5" in details.text


def test_pagination_and_unknown_routes():
    response = client.get("/api/shop-a/products", params={"page": 2, "per_page": 10})
    assert response.status_code == 200
    assert len(response.json()["products"]) == 5
    assert client.get("/shop-unknown").status_code == 404
    assert client.get("/api/shop-a/products/999999").status_code == 404
    assert client.get("/health").json()["models"] == 15
