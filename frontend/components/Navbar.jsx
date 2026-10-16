"use client"

import Link from "next/link"
import { useEffect, useState } from "react"

import {
    logout
} from "@/lib/api"


export default function Navbar(){

    const [username,setUsername] =
        useState(null)


    useEffect(()=>{

        setUsername(
            localStorage.getItem(
                "username"
            )
        )

    },[])


    function handleLogout(){

        logout()

        setUsername(null)

        window.location.href = "/"
    }


    return(

        <nav className="
            bg-zinc-900
            border-b
            border-zinc-800
        ">

            <div className="
                max-w-6xl
                mx-auto
                p-5
                flex
                gap-8
                items-center
            ">

                <Link href="/">
                    Compare
                </Link>


                {username && (

                    <Link href="/history">
                        History
                    </Link>

                )}


                <div className="ml-auto flex gap-5 items-center">

                    {username ? (

                        <>

                            <span className="
                                text-zinc-400
                            ">
                                {username}
                            </span>


                            <button
                                onClick={
                                    handleLogout
                                }
                                className="
                                    text-red-400
                                "
                            >
                                Logout
                            </button>

                        </>

                    ) : (

                        <>

                            <Link href="/login">
                                Login
                            </Link>

                            <Link href="/register">
                                Register
                            </Link>

                        </>

                    )}

                </div>

            </div>

        </nav>
    )
}