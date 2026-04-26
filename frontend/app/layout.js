import "./globals.css"
import Navbar from "@/components/Navbar"

export const metadata = {
 title:"PC Price Comparator"
}

export default function RootLayout({children}) {
 return (
  <html lang="pl">
   <body className="bg-zinc-950 text-white min-h-screen">
    <Navbar />
    <main className="max-w-6xl mx-auto p-8">
      {children}
    </main>
   </body>
  </html>
 )
}
