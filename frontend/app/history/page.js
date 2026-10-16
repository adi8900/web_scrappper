"use client"

import { useEffect, useState } from "react"
import { getHistory } from "@/lib/api"
import { useRouter } from "next/navigation"


export default function HistoryPage(){

    const router = useRouter()

    const [rows,setRows] =
        useState(null)


    useEffect(()=>{

        async function load(){

            const data =
                await getHistory()

            setRows(data)

        }

        load()

    },[])


    if(rows === null){

        return (
            <div>
                Ładowanie historii...
            </div>
        )

    }


    return(

        <div>

            <h1 className="
                text-5xl
                font-bold
                mb-8
            ">
                Historia wyszukiwań
            </h1>


            <div className="space-y-4">

                {rows.map((row,i)=>(

                    <div
                        key={i}
                        className="
                            p-6
                            rounded-2xl
                            bg-zinc-900
                            border
                            border-zinc-800
                        "
                    >

                        <div className="
                            flex
                            justify-between
                            mb-3
                            gap-4
                            flex-wrap
                        ">

                            <div className="
                                font-semibold
                            ">
                                {row.query}
                            </div>


                            <div className="
                                text-zinc-500
                                text-sm
                            ">
                                {new Date(
                                    row.created_at
                                ).toLocaleString(
                                    "pl-PL"
                                )}
                            </div>

                        </div>


                        <div>
                            X-Kom: {row.xkom || "-"}
                        </div>


                        <div>
                            Morele: {row.morele || "-"}
                        </div>


                        <div>
                            Media Expert: {
                                row.mediaexpert || "-"
                            }
                        </div>


                        <div className="
                            mt-3
                            text-green-400
                        ">
                            Najtaniej: {
                                row.cheapest || "-"
                            }
                        </div>


                        <div className="
                            text-red-400
                        ">
                            Najdrożej: {
                                row.most_expensive || "-"
                            }
                        </div>

                    </div>

                ))}


                {rows.length === 0 && (

                    <div className="
                        text-zinc-500
                    ">
                        Brak historii wyszukiwań.
                    </div>

                )}

            </div>

        </div>
    )
}