"use client"

import {useState} from "react"

export default function SearchBox({onSearch}){

const [query,setQuery]=useState("")
const [loading,setLoading]=useState(false)

async function submit(e){

e.preventDefault()

if(!query) return

setLoading(true)

await onSearch(query)

setLoading(false)

}

return(

<form
onSubmit={submit}
className="flex gap-4"
>

<input
value={query}
onChange={(e)=>setQuery(e.target.value)}
placeholder="np ryzen 7500f"
className="flex-1 p-4 rounded-2xl bg-zinc-800"
/>

<button
className="px-6 py-4 rounded-2xl bg-white text-black font-semibold"
>
{loading ? "Szukam..." : "Porównaj"}
</button>

</form>

)

}
