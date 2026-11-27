"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getHistory, getMe } from "@/lib/api";

const money = value => new Intl.NumberFormat("pl-PL", {style: "currency", currency: "PLN"}).format(value);

export default function HistoryPage() {
  const [rows, setRows] = useState(null);
  const [error, setError] = useState("");
  const router = useRouter();

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        if (!(await getMe())) {
          router.push("/login");
          return;
        }
        const history = await getHistory();
        if (active) setRows(history);
      } catch (err) {
        if (active) {setError(err.message || "Nie udało się wczytać historii");setRows([]);}
      }
    })();
    return () => { active = false; };
  }, [router]);

  return <div className="space-y-5">
    <h1 className="text-4xl font-bold">Historia wyszukiwań</h1>
    <p className="text-zinc-400">Wyniki pochodzą z trzech symulowanych sklepów. Przechowywane ceny są syntetyczne.</p>
    {error && <p role="alert" className="text-red-400">{error}</p>}
    {rows === null && <p>Ładowanie historii...</p>}
    {rows?.length === 0 && <p>Brak zapisanych wyszukiwań.</p>}
    {rows?.map(row => (
      <article key={row.id} className="rounded-2xl border border-zinc-800 bg-zinc-900 p-5">
        <div className="flex flex-wrap justify-between gap-2 mb-3">
          <strong className="text-lg">{row.query}</strong>
          <span className="text-zinc-400 text-sm">{new Date(row.created_at).toLocaleString("pl-PL")}</span>
        </div>
        <p className="text-zinc-400 text-sm">{row.method.toUpperCase()} • {row.result.products_found} modeli • {row.result.duration_ms} ms</p>
        <div className="space-y-2 mt-3">
          {(row.result.products || []).map(product => (
            <div key={product.product_id} className="flex flex-wrap justify-between gap-2 rounded-lg bg-zinc-950 p-3">
              <span>{product.name}</span>
              <span className="font-semibold text-emerald-300">
                {money(product.cheapest.price)} ({product.cheapest.shop_name})
              </span>
            </div>
          ))}
        </div>
      </article>
    ))}
  </div>;
}
