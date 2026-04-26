"use client"

import {useState} from "react"
import SearchBox from "@/components/SearchBox"
import PriceCard from "@/components/PriceCard"
import {comparePart} from "@/lib/api"

export default function Home(){

 const [data,setData]=useState(null)

 async function search(query){
   const result=await comparePart(query)
   setData(result)
 }

 return(
<div className="space-y-10">

<div>
<h1 className="text-6xl font-bold mb-6">
Porównywarka cen podzespołów
</h1>

<p className="text-zinc-400 mb-8">
X-Kom • Morele • Media Expert
</p>

<SearchBox onSearch={search}/>
</div>


{data?.results && (

<>
<div className="grid md:grid-cols-3 gap-6">

{Object.entries(data.results).map(
([shop,price])=>(

<PriceCard
 key={shop}
 shop={shop}
 price={price}
 best={shop===data.cheapest}
/>

)
)}

</div>

<div className="bg-zinc-900 p-8 rounded-3xl border border-zinc-800">
<h2 className="text-2xl mb-4 font-semibold">
Analiza
</h2>

<p>
Najtaniej:
<strong className="ml-2">
{data.cheapest}
</strong>
</p>

<p>
Najdrożej:
<strong className="ml-2">
{data.most_expensive}
</strong>
</p>

</div>
</>

)}

</div>
 )
}
