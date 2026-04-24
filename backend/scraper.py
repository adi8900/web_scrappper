import json
import re
import random
import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
]

# ===== HELPERY =====

def extract_model(query):
    match = re.search(r"\b\d{3,5}[a-zA-Z]*\b", query.lower())
    return match.group(0) if match else None


def detect_category(query):
    q = query.lower()

    if "rtx" in q or "gpu" in q or "karta" in q:
        return "gpu"
    if "ram" in q or "ddr" in q:
        return "ram"
    if "ssd" in q or "nvme" in q:
        return "ssd"
    if "ryzen" in q or "intel" in q:
        return "cpu"

    return "other"


def match_model(name, model):
    if not model:
        return True
    return model in name.lower()


def is_valid_name(name, query):
    name = name.lower()

    blacklist = ["laptop", "komputer", "zestaw", "g4m3r"]
    if any(x in name for x in blacklist):
        return False

    return True


def parse_price(aria):
    if not aria:
        return None

    match = re.search(r"([\d\s]+)\s*złotych\s*i\s*(\d+)\s*groszy", aria)
    if match:
        whole = match.group(1).replace(" ", "")
        cents = match.group(2).zfill(2)
        return f"{whole},{cents} zł"

    match = re.search(r"([\d\s]+)\s*złotych", aria)
    if match:
        whole = match.group(1).replace(" ", "")
        return f"{whole},00 zł"

    return None


async def launch_browser(p):
    return await p.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-dev-shm-usage"]
    )

# ===== XKOM =====

async def search_xkom_and_get_price(query):
    print("\n=== XKOM START ===")

    async with async_playwright() as p:
        browser = await launch_browser(p)
        page = await browser.new_page()

        url = f"https://www.x-kom.pl/szukaj?q={query.replace(' ', '+')}"
        print("URL:", url)

        await page.goto(url)
        await page.wait_for_load_state("domcontentloaded")

        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")
    prices = soup.select('span[aria-label*="Cena"]')

    model = extract_model(query)

    for p in prices[:15]:
        text = p.get("aria-label")

        if not text or "zł" not in text:
            continue

        parent = p.find_parent()
        title = parent.find_previous("h3") if parent else None
        name = title.get_text(strip=True) if title else ""

        name_lower = name.lower()
        print("XKOM NAME:", name)

        if not is_valid_name(name, query):
            continue

        if model and not match_model(name, model):
            continue

        return text.replace("Cena:", "").strip()

    return None


# ===== MORELE =====

async def search_morele_and_get_price(query):
    print("\n=== MORELE START ===")

    async with async_playwright() as p:
        browser = await launch_browser(p)
        page = await browser.new_page()

        url = f"https://www.morele.net/wyszukiwarka/?q={query.replace(' ', '+')}&d=0"
        print("URL:", url)

        await page.goto(url)
        await page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(2)

        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")
    products = soup.select('div.cat-product')[:15]

    model = extract_model(query)

    for p in products:
        name = p.get("data-product-name", "")
        price = p.get("data-product-price")

        print("MORELE NAME:", name)

        if not name or not price:
            continue

        if not is_valid_name(name, query):
            continue

        if model and not match_model(name, model):
            continue

        return f"{price.replace('.', ',')} zł"

    return None


# ===== MEDIAEXPERT =====

async def search_mediaexpert_and_get_price(query):
    print("\n=== MEDIA START ===")

    async with async_playwright() as p:
        browser = await launch_browser(p)

        context = await browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1366, "height": 768},
            locale="pl-PL"
        )

        page = await context.new_page()

        url = f"https://www.mediaexpert.pl/search?query[querystring]={query.replace(' ', '+')}"
        print("URL:", url)

        await page.goto(url)
        await page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(2)

        # 🔥 scroll żeby załadować więcej
        await page.mouse.wheel(0, 4000)
        await asyncio.sleep(1)

        final_url = page.url
        print("FINAL URL:", final_url)

        # ===== PRODUCT PAGE =====
        if "/search?" not in final_url:
            html = await page.content()
            await browser.close()

            soup = BeautifulSoup(html, "html.parser")

            price_el = soup.select_one("div.main-price")
            if not price_el:
                return None

            return parse_price(price_el.get("aria-label"))

        # ===== LISTA =====
        html = await page.content()
        await browser.close()

        soup = BeautifulSoup(html, "html.parser")
        products = soup.select("div.offer-box")

        category = detect_category(query)
        model = extract_model(query)

        for product in products:
            name_el = product.select_one("h3.name a")
            if not name_el:
                continue

            name = name_el.get_text(strip=True)
            name_lower = name.lower()

            print("MEDIA NAME:", name)

            if not is_valid_name(name, query):
                continue

            # 🔥 category filter
            if category == "gpu":
                if not any(x in name_lower for x in ["rtx", "geforce", "radeon"]):
                    continue

            if category == "ram":
                if not any(x in name_lower for x in ["ram", "ddr"]):
                    continue

            if category == "ssd":
                if not any(x in name_lower for x in ["ssd", "nvme", "m.2"]):
                    continue

            if model and not match_model(name, model):
                continue

            price_el = product.select_one("div.main-price")
            if not price_el:
                continue

            price = parse_price(price_el.get("aria-label"))
            if price:
                return price

        # 🔥 fallback
        for product in products:
            price_el = product.select_one("div.main-price")
            if not price_el:
                continue

            price = parse_price(price_el.get("aria-label"))
            if price:
                return price

        return None
