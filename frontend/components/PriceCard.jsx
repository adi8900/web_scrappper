export default function PriceCard({
shop,
price,
best
}){

return(

<div className={`
p-6 rounded-3xl border
${best
? "border-green-500 bg-green-500/10"
: "border-zinc-800 bg-zinc-900"}
`}>

<h3 className="text-xl font-semibold mb-4">
{shop}
</h3>

<div className="text-3xl font-bold">
{price}
</div>

{best && (
<p className="mt-3 text-green-400">
Najtaniej
</p>
)}

</div>

)

}
