const API = process.env.NEXT_PUBLIC_API_URL

export async function comparePart(query){

 const res = await fetch(
   `${API}/api/compare?query=${encodeURIComponent(query)}`,
   {
     cache:"no-store"
   }
 )

 return res.json()
}


export async function getHistory(){

 const res = await fetch(
   `${API}/api/history`,
   {
     cache:"no-store"
   }
 )

 return res.json()
}
