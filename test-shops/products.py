"""Curated PC component catalogue with reproducible, simulated shop offers.

Product specifications come from the linked manufacturer documentation.
Prices, availability and extra benchmark listings are entirely synthetic.
"""
import os
import random
import re

CATALOG = [
    {"id": 1, "sku": "AMD-7500F-TRAY", "name": "AMD Ryzen 5 7500F TRAY", "category": "CPU",
     "specs": {"Rdzenie": "6", "Wątki": "12", "Gniazdo": "AM5", "TDP": "65 W", "Wersja": "TRAY"},
     "source_url": "https://www.amd.com/en/products/processors/desktops/ryzen/7000-series/amd-ryzen-5-7500F.html", "base_price": 599},
    {"id": 2, "sku": "AMD-7600-BOX", "name": "AMD Ryzen 5 7600 BOX", "category": "CPU",
     "specs": {"Rdzenie": "6", "Wątki": "12", "Gniazdo": "AM5", "TDP": "65 W", "Wersja": "BOX"},
     "source_url": "https://www.amd.com/en/products/processors/desktops/ryzen/7000-series/amd-ryzen-5-7600.html", "base_price": 799},
    {"id": 3, "sku": "AMD-7700-BOX", "name": "AMD Ryzen 7 7700 BOX", "category": "CPU",
     "specs": {"Rdzenie": "8", "Wątki": "16", "Gniazdo": "AM5", "TDP": "65 W", "Wersja": "BOX"},
     "source_url": "https://www.amd.com/en/products/processors/desktops/ryzen/7000-series/amd-ryzen-7-7700.html", "base_price": 949},
    {"id": 4, "sku": "AMD-7800X3D-BOX", "name": "AMD Ryzen 7 7800X3D BOX", "category": "CPU",
     "specs": {"Rdzenie": "8", "Wątki": "16", "Gniazdo": "AM5", "TDP": "120 W", "Pamięć L3": "96 MB"},
     "source_url": "https://www.amd.com/en/products/processors/desktops/ryzen/7000-series/amd-ryzen-7-7800X3d.html", "base_price": 1499},
    {"id": 5, "sku": "AMD-5600-BOX", "name": "AMD Ryzen 5 5600 BOX", "category": "CPU",
     "specs": {"Rdzenie": "6", "Wątki": "12", "Gniazdo": "AM4", "TDP": "65 W", "Wersja": "BOX"},
     "source_url": "https://www.amd.com/en/support/downloads/drivers.html/processors/ryzen/ryzen-5000-series/amd-ryzen-5-5600.html", "base_price": 429},
    {"id": 6, "sku": "NVIDIA-RTX4070-12G", "name": "NVIDIA GeForce RTX 4070 12GB", "category": "GPU",
     "specs": {"Pamięć VRAM": "12 GB", "Typ pamięci": "GDDR6/GDDR6X", "Architektura": "Ada Lovelace"},
     "source_url": "https://www.nvidia.com/en-us/geforce/graphics-cards/40-series/rtx-4070-family/", "base_price": 2399},
    {"id": 7, "sku": "AMD-RX7800XT-16G", "name": "AMD Radeon RX 7800 XT 16GB", "category": "GPU",
     "specs": {"Pamięć VRAM": "16 GB", "Typ pamięci": "GDDR6", "Magistrala": "256 bit", "TBP": "263 W"},
     "source_url": "https://www.amd.com/en/products/graphics/desktops/radeon/7000-series/amd-radeon-rx-7800-xt.html", "base_price": 2199},
    {"id": 8, "sku": "AMD-RX7600-8G", "name": "AMD Radeon RX 7600 8GB", "category": "GPU",
     "specs": {"Pamięć VRAM": "8 GB", "Typ pamięci": "GDDR6", "Magistrala": "128 bit", "TBP": "165 W"},
     "source_url": "https://www.amd.com/en/products/graphics/desktops/radeon/7000-series/amd-radeon-rx-7600.html", "base_price": 1099},
    {"id": 9, "sku": "KINGSTON-KF560C30BBEAK2-32", "name": "Kingston FURY Beast DDR5 32GB (2x16GB) 6000 CL30",
     "category": "RAM", "specs": {"Pojemność": "32 GB (2x16 GB)", "Typ": "DDR5", "Szybkość": "6000 MT/s", "Opóźnienia": "CL30", "Part number": "KF560C30BBEAK2-32"},
     "source_url": "https://www.kingston.com/datasheets/KF560C30BBEAK2-32.pdf", "base_price": 429},
    {"id": 10, "sku": "SAMSUNG-990PRO-2TB", "name": "Samsung 990 PRO NVMe 2TB",
     "category": "SSD", "specs": {"Pojemność": "2 TB", "Interfejs": "PCIe 4.0 x4", "Odczyt": "do 7450 MB/s", "Zapis": "do 6900 MB/s"},
     "source_url": "https://www.samsung.com/pl/memory-storage/nvme-ssd/990-pro-2tb-nvme-pcie-gen-4-mz-v9p2t0bw/", "base_price": 699},
    {"id": 11, "sku": "SAMSUNG-990PRO-1TB", "name": "Samsung 990 PRO NVMe 1TB",
     "category": "SSD", "specs": {"Pojemność": "1 TB", "Interfejs": "PCIe 4.0 x4", "Odczyt": "do 7450 MB/s"},
     "source_url": "https://www.samsung.com/pl/memory-storage/nvme-ssd/990-pro-1tb-nvme-pcie-gen-4-mz-v9p1t0bw/", "base_price": 399},
    {"id": 12, "sku": "LEXAR-NM790-1TB", "name": "Lexar NM790 NVMe 1TB",
     "category": "SSD", "specs": {"Pojemność": "1 TB", "Interfejs": "PCIe 4.0 x4", "Odczyt": "do 7400 MB/s", "Zapis": "do 6500 MB/s"},
     "source_url": "https://resources.lexar.com/download/1362/brand-profile-2024q3/11621/lexar-brand-profile-2024q3.pdf", "base_price": 319},
    {"id": 13, "sku": "MSI-B650-TOMAHAWK", "name": "MSI MAG B650 TOMAHAWK WIFI",
     "category": "Płyta główna", "specs": {"Gniazdo": "AM5", "Chipset": "AMD B650", "Pamięć": "DDR5", "Format": "ATX", "Łączność": "Wi-Fi 6E"},
     "source_url": "https://www.msi.com/Motherboard/MAG-B650-TOMAHAWK-WIFI/Specification", "base_price": 849},
    {"id": 14, "sku": "CORSAIR-CP-9020262-EU", "name": "Corsair RM750e 750W 80 PLUS Gold",
     "category": "Zasilacz", "specs": {"Moc": "750 W", "Certyfikat": "80 PLUS Gold", "Standard": "ATX 3.1", "Okablowanie": "Modularne", "Part number": "CP-9020262-EU"},
     "source_url": "https://www.corsair.com/ww/en/p/psu/CP-9020262-EU/rme-series-rm750e-fully-modular-low-noise-atx-power-supply-cp-9020262-eu", "base_price": 489},
    {"id": 15, "sku": "BEQUIET-PP12M-750", "name": "be quiet! Pure Power 12 M 750W",
     "category": "Zasilacz", "specs": {"Moc": "750 W", "Okablowanie": "Modularne", "Złącze GPU": "12VHPWR", "Linie 12 V": "2"},
     "source_url": "https://www.bequiet.com/en/powersupply/4166", "base_price": 499},
]

SHOP_MARKUP = {"a": 1.00, "b": 0.97, "c": 1.04}
BASE_PRODUCTS = CATALOG


def searchable(text):
    return re.sub(r"[^a-z0-9]+", " ", text.casefold()).split()


def matches(product, query):
    terms = searchable(query)
    if not terms:
        return True
    haystack = " ".join(searchable(product["name"] + " " + product["sku"]))
    return all(term in haystack for term in terms)


def generate_products(count=None, seed=42):
    """Extra entries are labelled duplicated *test offers*, not new hardware models."""
    if count is None:
        count = int(os.getenv("PRODUCT_COUNT", str(len(CATALOG))))
    count = max(len(CATALOG), count)
    rng = random.Random(seed)
    products = []
    for i in range(count):
        base = CATALOG[i % len(CATALOG)]
        item = {key: value for key, value in base.items() if key != "base_price"}
        item["id"] = i + 1
        item["product_id"] = base["id"]
        item["benchmark_offer"] = i >= len(CATALOG)
        item["listing_number"] = 1 if i < len(CATALOG) else i // len(CATALOG) + 1
        item["stock"] = rng.randint(1, 40)
        products.append(item)
    return products


def generate_prices(products, seed=42):
    prices = {shop: {} for shop in SHOP_MARKUP}
    for product in products:
        base = CATALOG[product["product_id"] - 1]["base_price"]
        for shop, multiplier in SHOP_MARKUP.items():
            randomizer = random.Random(f"{seed}:{shop}:{product['id']}")
            price = base * multiplier * randomizer.uniform(.97, 1.03)
            prices[shop][product["id"]] = round(price, 2)
    return prices


PRODUCTS = generate_products()
PRICES = generate_prices(PRODUCTS)
BY_ID = {product["id"]: product for product in PRODUCTS}
