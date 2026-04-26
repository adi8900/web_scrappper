import {getHistory} from "@/lib/api"

export default async function HistoryPage(){

 const rows=await getHistory()

 return(
<div>

<h1 className="text-5xl font-bold mb-8">
Historia wyszukiwań
</h1>

<div className="space-y-4">

{rows.map((row,i)=>(

<div
key={i}
className="p-6 rounded-2xl bg-zinc-900 border border-zinc-800"
>

<div className="font-semibold mb-3">
{row.query}
</div>

<div>
X-Kom: {row.xkom}
</div>

<div>
Morele: {row.morele}
</div>

<div>
Media Expert: {row.mediaexpert}
</div>

<div className="mt-3 text-green-400">
Najtaniej: {row.cheapest}
</div>

</div>

))}

</div>

</div>
 )
}
