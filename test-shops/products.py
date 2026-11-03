
import os
import random

BASE_PRODUCTS = [
    {"id": 1, "name": "AMD Ryzen 5 7500F"},
    {"id": 2, "name": "AMD Ryzen 7 7700"},
    {"id": 3, "name": "AMD Ryzen 7 7800X3D"},
    {"id": 4, "name": "NVIDIA GeForce RTX 4070 12GB"},
    {"id": 5, "name": "AMD Radeon RX 7800 XT 16GB"},
    {"id": 6, "name": "Kingston Fury DDR5 32GB 6000MHz"},
    {"id": 7, "name": "Lexar NM790 NVMe 1TB"},
    {"id": 8, "name": "Samsung 990 PRO NVMe 2TB"},
]

BASE_PRICES = {
    "a": [599.00, 899.99, 1399.00, 2399.00,
          2199.99, 429.00, 299.99, 699.00],
    "b": [579.99, 929.00, 1449.00, 2349.00,
          2249.00, 409.99, 319.00, 679.00],
    "c": [619.00, 879.00, 1379.00, 2449.99,
          2149.00, 449.00, 289.00, 729.00],
}

BRANDS = {
    "CPU": ["AMD", "Intel"],
    "GPU": ["NVIDIA", "AMD", "ASRock", "MSI"],
    "RAM": ["Kingston", "Corsair", "G.Skill", "Patriot"],
    "SSD": ["Samsung", "Lexar", "WD", "Crucial"],
    "Motherboard": ["ASUS", "MSI", "Gigabyte", "ASRock"],
    "PSU": ["Corsair", "Seasonic", "be quiet!", "MSI"],
}

PRICE_RANGES = {
    "CPU": (300, 3500),
    "GPU": (600, 8000),
    "RAM": (150, 1500),
    "SSD": (150, 2000),
    "Motherboard": (300, 2500),
    "PSU": (200, 1200),
}


def generate_products(count=10000, seed=42):
    rng = random.Random(seed)
    products = [product.copy() for product in BASE_PRODUCTS]

    categories = list(BRANDS)

    for product_id in range(len(products) + 1, count + 1):
        category = categories[(product_id - 9) % len(categories)]
        brand = rng.choice(BRANDS[category])

        if category == "CPU":
            name = (
                f"{brand} Processor Series "
                f"{rng.randint(1000, 9999)} "
                f"{rng.choice([4, 6, 8, 12, 16])}-Core"
            )
        elif category == "GPU":
            name = (
                f"{brand} Graphics Card "
                f"{rng.randint(1000, 9999)} "
                f"{rng.choice([8, 12, 16, 24])}GB"
            )
        elif category == "RAM":
            name = (
                f"{brand} DDR5 "
                f"{rng.choice([16, 32, 64, 128])}GB "
                f"{rng.choice([4800, 5600, 6000, 6400])}MHz "
                f"Kit {product_id}"
            )
        elif category == "SSD":
            name = (
                f"{brand} NVMe "
                f"{rng.choice([500, 1000, 2000, 4000])}GB "
                f"Model {product_id}"
            )
        elif category == "Motherboard":
            name = (
                f"{brand} Motherboard "
                f"{rng.choice(['B650', 'X670', 'B850', 'Z790'])} "
                f"Model {product_id}"
            )
        else:
            name = (
                f"{brand} PSU "
                f"{rng.choice([550, 650, 750, 850, 1000])}W "
                f"Model {product_id}"
            )

        products.append({
            "id": product_id,
            "name": name,
            "category": category,
        })

    return products


def generate_prices(products, seed=42):
    prices = {"a": {}, "b": {}, "c": {}}
    rng = random.Random(seed)

    for shop in prices:
        for index, price in enumerate(BASE_PRICES[shop], start=1):
            if index <= len(products):
                prices[shop][index] = price

    for product in products[len(BASE_PRODUCTS):]:
        product_id = product["id"]
        category = product["category"]

        minimum, maximum = PRICE_RANGES[category]
        base_price = rng.uniform(minimum, maximum)

        for shop in prices:
            multiplier = {
                "a": 1.00,
                "b": 0.97,
                "c": 1.03,
            }[shop]

            variation = rng.uniform(0.95, 1.05)

            prices[shop][product_id] = round(
                base_price * multiplier * variation, 2
            )

    return prices


PRODUCT_COUNT = max(8, int(os.getenv("PRODUCT_COUNT", "10000")))
PRODUCTS = generate_products(PRODUCT_COUNT)
PRICES = generate_prices(PRODUCTS)
