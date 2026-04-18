"use client"

import { useState } from "react"

export default function Home() {
  const [query, setQuery] = useState("")
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)

  const search = async () => {
    setLoading(true)
    setData(null)

    try {
      const res = await fetch(
        `http://192.168.1.133:8000/api/compare?query=${encodeURIComponent(query)}`
      )

      const json = await res.json()
      setData(json)

    } catch (err) {
      console.error(err)
    }

    setLoading(false)
  }

  return (
    <div style={{ padding: 40, fontFamily: "Arial" }}>
      <h1>Porównywarka cen</h1>

      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="np. ryzen 5 7500f"
        style={{ padding: 8, width: 300 }}
      />

      <button onClick={search} style={{ marginLeft: 10 }}>
        Szukaj
      </button>

      {loading && <p>🔄 Szukanie...</p>}

      {data && data.results && (
        <table style={{ marginTop: 20 }}>
          <thead>
            <tr>
              <th>Sklep</th>
              <th>Cena</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(data.results).map(([shop, price]) => (
              <tr key={shop}>
                <td>{shop}</td>
                <td>{price}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {data && data.cheapest && (
        <p>Najtaniej: {data.cheapest}</p>
      )}

      {data && data.most_expensive && (
        <p>Najdrożej: {data.most_expensive}</p>
      )}

      {data && data.error && (
        <p>{data.error}</p>
      )}
    </div>
  )
}
