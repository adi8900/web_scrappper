"use client"

import { useState } from "react"
import SearchBox from "@/components/SearchBox"
import { comparePart } from "@/lib/api"


export default function Home(){

const [data,setData]=useState(null)



async function search(query){

 const result=
   await comparePart(query)

 setData(
   result
 )

}



return(

<div className="space-y-12">

<div>

<h1 className="text-6xl font-bold mb-6">
Porównywarka cen podzespołów
</h1>

<p className="text-zinc-400 mb-8">
X-Kom • Morele • Media Expert
</p>



<div className="flex gap-3 mb-8 flex-wrap">

<button
onClick={()=>search(
"ryzen 7500f"
)}
className="px-4 py-2 rounded-xl bg-zinc-800"
>
CPU
</button>


<button
onClick={()=>search(
"rtx 4070"
)}
className="px-4 py-2 rounded-xl bg-zinc-800"
>
GPU
</button>


<button
onClick={()=>search(
"ddr5 32gb 6000"
)}
className="px-4 py-2 rounded-xl bg-zinc-800"
>
RAM
</button>


<button
onClick={()=>search(
"nvme 1tb"
)}
className="px-4 py-2 rounded-xl bg-zinc-800"
>
SSD
</button>

</div>


<SearchBox
 onSearch={search}
/>

</div>



{data?.results && (

<>

<div className="grid md:grid-cols-3 gap-6">

{
Object.entries(
data.results
).map(

([shop,item])=>(

<div
key={shop}
className="
border
border-zinc-800
rounded-3xl
p-8
bg-zinc-900
"
>

<h2 className="text-2xl font-bold">
{shop}
</h2>


<p className="text-4xl mt-4 mb-4">
{item.price}
</p>


{
shop===data.cheapest &&
<div className="
inline-block
mb-4
px-3 py-1
rounded-full
bg-green-900
">
Najtaniej
</div>
}


<a
href={item.url}
target="_blank"
className="
block
mt-4
text-center
bg-white
text-black
rounded-xl
py-3
font-semibold
"
>
Przejdź do oferty
</a>

</div>

))

}

</div>



<div className="
bg-zinc-900
p-8
rounded-3xl
border
border-zinc-800
">

<h2 className="
text-2xl
mb-4
font-semibold
">
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
