import Link from "next/link"

export default function Navbar(){

return(
<nav className="bg-zinc-900 border-b border-zinc-800">

<div className="max-w-6xl mx-auto p-5 flex gap-8">

<Link href="/">
Compare
</Link>

<Link href="/history">
History
</Link>

</div>

</nav>
)

}
