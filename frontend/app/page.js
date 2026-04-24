"use client"

import { useState, useEffect } from "react"

export default function Home() {
  const [query, setQuery] = useState("")
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [dark, setDark] = useState(false)

  // 🔥 INIT DARK MODE (NAPRAWIONE)
  useEffect(() => {
    const saved = localStorage.getItem("theme")
    const html = document.documentElement

    if (saved === "dark") {
      html.classList.add("dark")
      setDark(true)
    } else {
      html.classList.remove("dark")
      setDark(false)
    }
  }, [])

  // 🔥 TOGGLE (NAPRAWIONE)
  const toggleDark = () => {
    const html = document.documentElement

    if (html.classList.contains("dark")) {
      html.classList.remove("dark")
      localStorage.setItem("theme", "light")
      setDark(false)
    } else {
      html.classList.add("dark")
      localStorage.setItem("theme", "dark")
      setDark(true)
    }
  }

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
    <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-gray-900 transition">

      <div className="w-full max-w-3xl bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-10 transition">

        {/* HEADER */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            💻 Porównywarka cen
          </h1>

          <button
            onClick={toggleDark}
            className="px-4 py-2 rounded-xl bg-gray-200 dark:bg-gray-700 text-sm"
          >
            {dark ? "☀️ Light" : "🌙 Dark"}
          </button>
        </div>

        {/* SEARCH */}
        <div className="flex gap-3 mb-6">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="np. RTX 4060 / Ryzen 5 7500F"
            className="flex-1 px-4 py-3 text-lg rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-black dark:text-white focus:outline-none focus:ring-2 focus:ring-green-400"
          />

          <button
            onClick={search}
            className="bg-green-500 hover:bg-green-600 active:scale-95 transition text-white px-6 py-3 text-lg rounded-xl"
          >
            Szukaj
          </button>
        </div>

        {/* LOADING */}
        {loading && (
          <div className="text-center text-lg animate-pulse text-gray-700 dark:text-gray-300">
            🔄 Szukam ofert...
          </div>
        )}

        {/* RESULTS */}
        {data?.results && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6">

            {Object.entries(data.results).map(([shop, price]) => {
              const isCheapest = shop === data.cheapest
              const isExpensive = shop === data.most_expensive

              return (
                <div
                  key={shop}
                  className={`
                    p-5 rounded-xl text-center border
                    bg-gray-50 dark:bg-gray-700
                    ${isCheapest ? "border-green-500 bg-green-100 dark:bg-green-900" : ""}
                    ${isExpensive ? "border-red-500 bg-red-100 dark:bg-red-900" : ""}
                  `}
                >
                  <h3 className="font-semibold text-lg text-gray-900 dark:text-white">
                    {shop}
                  </h3>
                  <p className="text-2xl font-bold mt-2 text-gray-900 dark:text-white">
                    {price}
                  </p>
                </div>
              )
            })}

          </div>
        )}

        {/* SUMMARY */}
        {data?.cheapest && (
          <p className="mt-6 text-center text-green-600 dark:text-green-400 font-semibold text-lg">
            🟢 Najtaniej: {data.cheapest}
          </p>
        )}

        {data?.most_expensive && (
          <p className="text-center text-red-600 dark:text-red-400 font-semibold text-lg">
            🔴 Najdrożej: {data.most_expensive}
          </p>
        )}

        {data?.error && (
          <p className="text-red-500 text-center mt-4">
            {data.error}
          </p>
        )}

      </div>
    </div>
  )
}
