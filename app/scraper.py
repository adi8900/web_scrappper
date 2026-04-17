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


def is_reasonable(price_str):
    try:
        price = float(
            price_str.replace("zł", "").replace(",", ".").replace(" ", "").strip()
        )
    except:
        return False

    # filtr dziwnych cen
    if price < 100 or price > 20000:
        return False

    return True


async def human_delay(min_ms=1000, max_ms=3000):
    await asyncio.sleep(random.uniform(min_ms / 1000, max_ms / 1000))


async def simulate_user(page):
    await page.mouse.wheel(0, random.randint(300, 800))
    await human_delay(500, 1500)
    await page.mouse.wheel(0, random.randint(300, 800))
    await human_delay(500, 1500)


# ===== PARSERY =====

def parse_morele(soup):
    el = soup.select_one('#product_price')
    if el:
        price = el.get("data-price")
        if price:
            return f"{price} zł"
    return None


def parse_xkom(soup):
    el = soup.select_one('span[aria-label*="Cena"]')
    if el:
        text = el.get("aria-label")
        if text:
            return text.replace("Cena:", "").strip()

    el = soup.select_one('[data-name="productPrice"]')
    if el:
        return el.get_text(strip=True)

    return None


def parse_mediaexpert(soup):
    el = soup.select_one('div.main-price')
    if el:
        aria = el.get("aria-label")
        if aria:
            match = re.search(r"(\d+)\s*złotych\s*i\s*(\d+)\s*groszy", aria)
            if match:
                zl = match.group(1)
                gr = match.group(2).zfill(2)
                return f"{zl},{gr} zł"

            match = re.search(r"(\d+)\s*złotych", aria)
            if match:
                return f"{match.group(1)},00 zł"

    return None


def detect_and_parse(url, soup):
    url = url.lower()

    if "morele.net" in url:
        return parse_morele(soup)

    if "x-kom.pl" in url:
        return parse_xkom(soup)

    if "mediaexpert.pl" in url:
        return parse_mediaexpert(soup)

    return None


# ===== SEARCH =====

async def search_mediaexpert_and_get_price(query):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        context = await browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1366, "height": 768},
            locale="pl-PL"
        )

        page = await context.new_page()

        search_url = f"https://www.mediaexpert.pl/search?query[querystring]={query.replace(' ', '+')}"
        await page.goto(search_url)

        await page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(3)

        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")

    el = soup.select_one('div.main-price')
    if el:
        aria = el.get("aria-label")
        if aria:
            match = re.search(r"(\d+)\s*złotych\s*i\s*(\d+)\s*groszy", aria)
            if match:
                return f"{match.group(1)},{match.group(2).zfill(2)} zł"

            match = re.search(r"(\d+)\s*złotych", aria)
            if match:
                return f"{match.group(1)},00 zł"

    return None

async def search_morele_and_get_price(query):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        context = await browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1366, "height": 768},
            locale="pl-PL"
        )

        page = await context.new_page()

        search_url = f"https://www.morele.net/wyszukiwarka/?q={query.replace(' ', '+')}&d=0"
        await page.goto(search_url)

        await page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(2)

        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")

    products = soup.select('div.cat-product')[:10]

    model = extract_model(query)

    for p in products:
        name = p.get("data-product-name", "")
        price = p.get("data-product-price")

        if not name or not price:
            continue

        name_lower = name.lower()

        # 🔥 filtr modelu
        if model and model not in name_lower:
            continue

        # 🔥 filtr śmieci
        if any(x in name_lower for x in ["laptop", "zestaw", "komputer"]):
            continue

        price = price.replace(".", ",")
        return f"{price} zł"

    # 🔥 fallback (jak nic nie znajdzie)
    for p in products:
        price = p.get("data-product-price")
        if price:
            return f"{price.replace('.', ',')} zł"

    return None

async def search_xkom_and_get_price(query):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        context = await browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1366, "height": 768},
            locale="pl-PL"
        )

        page = await context.new_page()

        search_url = f"https://www.x-kom.pl/szukaj?q={query.replace(' ', '+')}"
        await page.goto(search_url)

        await page.wait_for_load_state("domcontentloaded")

        try:
            await page.wait_for_selector('span[aria-label*="Cena"]', timeout=8000)
        except:
            await browser.close()
            return None

        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")

    prices = soup.select('span[aria-label*="Cena"]')

    for p in prices:
        text = p.get("aria-label")
        if text and "zł" in text:
            return text.replace("Cena:", "").strip()

    return None


# ===== MAIN =====

def parse_price_to_float(price_str):
    price = price_str.replace("zł", "").replace(",", ".").replace(" ", "").strip()
    return float(price)


async def compare_prices(query):
    results = {}

    try:
        xkom_price = await search_xkom_and_get_price(query)
        if xkom_price and is_reasonable(xkom_price):
            results["x-kom"] = xkom_price
    except:
        pass

    try:
        morele_price = await search_morele_and_get_price(query)
        if morele_price and is_reasonable(morele_price):
            results["morele"] = morele_price
    except:
        pass

    try:
        media_price = await search_mediaexpert_and_get_price(query)
        if media_price and is_reasonable(media_price):
            results["mediaexpert"] = media_price
    except:
        pass

    if not results:
        return None

    numeric = {
        shop: parse_price_to_float(price)
        for shop, price in results.items()
    }

    cheapest = min(numeric, key=numeric.get)
    most_expensive = max(numeric, key=numeric.get)

    return {
        "results": results,
        "cheapest": cheapest,
        "most_expensive": most_expensive
    }


# ===== SCRAPE URL =====

async def scrape_price(url: str):
    for attempt in range(3):
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)

                context = await browser.new_context(
                    user_agent=random.choice(USER_AGENTS),
                    viewport={"width": 1366, "height": 768},
                    locale="pl-PL",
                    timezone_id="Europe/Warsaw"
                )

                page = await context.new_page()

                await page.goto(url, timeout=60000)
                await page.wait_for_load_state("domcontentloaded")
                await human_delay(1500, 3000)

                html = await page.content()
                await browser.close()

            soup = BeautifulSoup(html, "html.parser")

            parsed_price = detect_and_parse(url, soup)
            if parsed_price:
                return parsed_price

        except Exception as e:
            print("ERROR:", e)
            await asyncio.sleep(2)

    return None
