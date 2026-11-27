# Równoległy web scraper — prototyp badawczy

Prototyp pracy inżynierskiej: **„Architektura równoległego web scrapera z mechanizmami skalowania i analizy danych cenowych”**.

## Zakres i wiarygodność danych

Trzy **symulowane sklepy**, ByteMarket (A), VoltZone (B) i CoreHub (C), pokazują tę samą kolekcję 15 istniejących modeli podzespołów komputerowych. Specyfikacje techniczne oraz odnośniki do źródeł producentów przechowuje `test-shops/products.py`. Ceny, dostępność oraz dodatkowe oferty benchmarkowe są **syntetyczne** i deterministyczne (`seed=42`); nie są to rzeczywiste ceny rynkowe ani aktualny stan magazynowy. Dane należy opisywać w pracy właśnie w ten sposób.

Przy domyślnym `PRODUCT_COUNT=15` każdy model ma jedną ofertę w każdym sklepie. Dla testów obciążeniowych można ustawić np. `PRODUCT_COUNT=10000`: generowane są dodatkowe rekordy ofert **istniejących modeli**, a nie wymyślone modele sprzętu. To pozwala badać przepustowość i paginację bez wprowadzania fikcyjnych specyfikacji.

## Architektura

`Next.js → FastAPI → Celery/Redis → zdalne workery → sklepy testowe`

Wariant HTML: `Playwright (Chromium) → BeautifulSoup → ekstrakcja danych`. Wariant API: `httpx → JSON`. Oba korzystają z tej samej bazy ofert testowych i zwracają te same identyfikatory modeli i ceny. Klucz porównania ofert to `product_id`, a nie przypadkowe dopasowanie najtańszego wyniku słownego.

**Repozytorium workera:** https://github.com/adi8900/scraper_worker (gałąź `thesis-refinement-2026-11`).

## Uruchomienie serwera głównego

1. `cp .env.example .env`.
2. Zmień hasła do MariaDB i Redis oraz `JWT_SECRET_KEY` na losowy sekret (minimum 32 znaki).
3. Ustaw `NEXT_PUBLIC_API_URL` na adres dostępny z przeglądarki (np. `http://192.168.1.10:8000`) i `CORS_ORIGINS` na dokładny adres frontendu (np. `http://192.168.1.10:3001`).
4. Jeżeli workery są na innych komputerach, ustaw `REDIS_BIND_IP` na **prywatny adres LAN** serwera (np. `192.168.1.10`). Nie wystawiaj Redis do Internetu; ogranicz port 6379 zaporą sieciową do adresów workerów.
5. `docker compose up -d --build`.

Adresy: frontend `http://HOST:3001`, API `http://HOST:8000/docs`, sklepy `http://HOST:8090`; baza MariaDB pozostaje w sieci Docker. Redis domyślnie jest dostępny tylko na `127.0.0.1`; dla workerów zdalnych konieczna jest zmiana `REDIS_BIND_IP`.

Uruchom co najmniej jeden worker zgodnie z README drugiego repozytorium. Bez workera wyszukiwanie zakończy się błędem przekroczenia czasu oczekiwania.

## Funkcje

- Uwierzytelnianie użytkownika i historia wyszukiwania (nowa tabela `search_history_v2`, bez destrukcyjnej migracji starej tabeli).
- Wyszukiwanie produktów i zestawianie cen **tego samego** modelu w trzech sklepach.
- Szczegóły techniczne na kartach produktów i w porównywarce.
- Monitoring czasu wykonania i liczby przetworzonych ofert w odpowiedziach.
- Porównanie wariantu HTML (Playwright/BeautifulSoup) i wariantu API (JSON/httpx).
- Niezależne wykonywanie zadań ze współdzielonych kolejek `scraping` i `catalog`.

## Badania wydajnościowe

Dla katalogu 10 000 ofert testowych ustaw `PRODUCT_COUNT=10000` i przebuduj sklep `docker compose up -d --build test-shops`. Test jednej strony obejmuje domyślnie 40 ofert; 250 stron odpowiada 10 000 ofertom jednego sklepu.

Na serwerze uruchamiaj identyczne testy dla jednego, dwóch i trzech aktywnych workerów, zapisując wynik CSV:

```bash
docker compose exec backend python benchmark_catalog.py --shop a --method html --pages 250 --repeats 3 --label 1-worker --csv /app/results.csv
docker compose exec backend python benchmark_catalog.py --shop a --method api  --pages 250 --repeats 3 --label 1-worker --csv /app/results.csv
```

Powtórz dla `--label 2-workers` oraz `3-workers`, zmieniając liczbę **aktywnych** jednostek wykonawczych. Nie uruchamiaj innych instancji workerów w trakcie pomiarów. W CSV rejestrowane są czasy, liczba ofert, przepustowość, liczba błędów i opóźnienia zadań. Parametr `--label` jest opisem eksperymentu, **nie** zmienia samoczynnie liczby workerów. Wyniki zależą również od zasobów sprzętowych i sieci.

W razie różnic wydajności HTML/API uwzględnij dodatkowy koszt uruchomienia przeglądarki w metodzie HTML.

## Ważne

To rozwiązanie badawcze. Nie scrapuje zewnętrznych sklepów handlowych. Nie traktuj wyników laboratoryjnych jako miarodajnych dla wszystkich prawdziwych witryn e-commerce. Linki do producentów wymagają okresowej weryfikacji, podobnie jak specyfikacje urządzeń. Nie umieszczaj sekretów z pliku `.env` na GitHub.
