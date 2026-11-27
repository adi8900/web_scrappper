"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import SearchBox from "@/components/SearchBox";
import { comparePart, getMe } from "@/lib/api";

const stores = {a: "ByteMarket", b: "VoltZone", c: "CoreHub"};
const formatMoney = (value) => new Intl.NumberFormat("pl-PL", {
  style: "currency", currency: "PLN"
}).format(value);

export default function Home() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [method, setMethod] = useState("html");
  const [error, setError] = useState("");
  const router = useRouter();

  async function search(query) {
    if (!query?.trim()) return;
    setError("");
    try {
      if (!(await getMe())) {
        router.push("/login");
        return;
      }
      setLoading(true);
      setData(null);
      const response = await comparePart(query, method);
      setData(response);
      if (response.errors?.length) {
        setError("Niektóre sklepy nie odpowiedziały: " + response.errors.map(s => stores[s]).join(", "));
      }
    } catch (err) {
      setError(err.message || "Nie można pobrać wyników");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-9">
      <section className="rounded-3xl bg-gradient-to-r from-slate-900 to-blue-950 border border-slate-700 p-8">
        <div className="text-xs font-semibold uppercase tracking-widest text-sky-300 mb-3">
          Środowisko badawcze • trzy sklepy symulacyjne
        </div>
        <h1 className="text-4xl md:text-5xl font-bold mb-3">Porównywarka podzespołów PC</h1>
        <p className="text-zinc-300 mb-6 max-w-3xl">
          Rzeczywiste modele i specyfikacje producentów, symulowane ceny i dostępność.
          To narzędzie demonstracyjne do badań web scrapingu, a nie rzeczywiste oferty handlowe.
        </p>
        <div className="flex flex-wrap gap-2 mb-5">
          {[["Ryzen 5 7500F", "ryzen 7500f"], ["GeForce RTX 4070", "rtx 4070"],
            ["DDR5 32GB", "ddr5 32gb"], ["SSD 1TB", "nvme 1tb"]].map(([label, query]) => (
            <button key={label} onClick={() => search(query)}
              className="rounded-lg border border-slate-600 bg-slate-800 px-4 py-2 text-sm hover:bg-slate-700">
              {label}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-3 mb-5 flex-wrap">
          <label htmlFor="method" className="text-sm font-semibold">Sposób pobierania:</label>
          <select id="method" value={method} onChange={e => setMethod(e.target.value)}
            className="rounded-lg bg-slate-800 text-white border border-slate-600 px-3 py-2">
            <option value="html">HTML — Playwright + BeautifulSoup</option>
            <option value="api">API — odpowiedź JSON</option>
          </select>
        </div>
        <SearchBox onSearch={search} />
      </section>

      {loading && <div role="status" className="rounded-2xl bg-zinc-900 border border-zinc-800 p-7">
        Trwa wyszukiwanie ofert w sklepach testowych...
      </div>}
      {error && <p role="alert" className="rounded-xl border border-amber-700 bg-amber-950/40 p-4 text-amber-300">{error}</p>}

      {data && (
        <section className="space-y-5">
          <div className="flex gap-4 flex-wrap justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold">Wyniki: {data.query}</h2>
              <p className="text-zinc-400 text-sm">{data.products_found} modeli • {data.method.toUpperCase()} • {data.duration_ms} ms</p>
            </div>
            <div className="text-sm text-zinc-400">Ceny wygenerowane wyłącznie na potrzeby testów</div>
          </div>
          {data.products?.length === 0 && <p className="rounded-2xl bg-zinc-900 p-7">
            Nie znaleziono produktów. Spróbuj innej frazy.
          </p>}
          {(data.products || []).map(product => (
            <article key={product.product_id} className="bg-zinc-900 border border-zinc-800 rounded-3xl p-6 space-y-4">
              <div className="flex flex-wrap justify-between gap-3">
                <div>
                  <h3 className="text-xl font-bold">{product.name}</h3>
                  <p className="text-zinc-400 text-sm">ID modelu: {product.product_id} • Oferty w {product.shop_count} sklepach</p>
                </div>
                <div className="rounded-xl bg-emerald-950 text-emerald-200 px-4 py-3">
                  <span className="block text-xs">Najniższa cena</span>
                  <strong className="text-xl">{formatMoney(product.cheapest.price)}</strong>
                </div>
              </div>
              {Object.keys(product.specs || {}).length > 0 && (
                <div className="flex gap-2 flex-wrap">
                  {Object.entries(product.specs).map(([key, value]) => (
                    <span key={key} className="bg-zinc-800 rounded-lg px-3 py-1 text-sm text-zinc-300">{key}: {value}</span>
                  ))}
                </div>
              )}
              <div className="grid md:grid-cols-3 gap-3">
                {product.offers.map((offer, index) => (
                  <div key={offer.shop + "-" + offer.listing_id} className="bg-zinc-950 border border-zinc-800 rounded-xl p-4">
                    <div className="font-semibold">{offer.shop_name}</div>
                    <div className="text-2xl font-bold my-2">{formatMoney(offer.price)}</div>
                    {index === 0 && <p className="text-emerald-400 text-xs mb-3">Najtańsza oferta dla tego modelu</p>}
                    {offer.url && <a href={offer.url} target="_blank" rel="noreferrer"
                      className="text-sky-300 text-sm hover:underline">Otwórz ofertę testową ↗</a>}
                  </div>
                ))}
              </div>
            </article>
          ))}
          {data.metrics && <details className="rounded-2xl border border-zinc-800 bg-zinc-900 p-5">
            <summary className="cursor-pointer font-semibold">Metryki jednostek wykonawczych</summary>
            <div className="grid md:grid-cols-3 gap-3 mt-4 text-sm">
              {Object.entries(data.metrics).map(([shop, metric]) => (
                <div key={shop} className="rounded-lg p-4 bg-zinc-950">
                  <strong>{stores[shop]}</strong><div>Status: {metric.status}</div>
                  <div>Oferty: {metric.count ?? "—"}</div>
                  <div>Czas: {metric.duration_ms ?? "—"} ms</div>
                </div>
              ))}
            </div>
          </details>}
        </section>
      )}
    </div>
  );
}
