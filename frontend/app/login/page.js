"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"

import { login } from "@/lib/api"


export default function LoginPage(){

    const router = useRouter()

    const [username,setUsername] =
        useState("")

    const [password,setPassword] =
        useState("")

    const [error,setError] =
        useState("")


    async function handleLogin(e){

        e.preventDefault()

        setError("")


        const result =
            await login(
                username,
                password
            )


        if(result.access_token){

            router.push("/")

            router.refresh()

        }else{

            setError(
                result.detail ||
                "Błąd logowania"
            )
        }
    }


    return(

        <div className="max-w-md mx-auto">

            <h1 className="
                text-4xl
                font-bold
                mb-8
            ">
                Logowanie
            </h1>


            <form
                onSubmit={handleLogin}
                className="space-y-5"
            >

                <input
                    value={username}
                    onChange={
                        e =>
                        setUsername(
                            e.target.value
                        )
                    }
                    placeholder="Nazwa użytkownika"
                    className="
                        w-full
                        p-4
                        rounded-xl
                        bg-zinc-900
                        border
                        border-zinc-800
                    "
                />


                <input
                    type="password"
                    value={password}
                    onChange={
                        e =>
                        setPassword(
                            e.target.value
                        )
                    }
                    placeholder="Hasło"
                    className="
                        w-full
                        p-4
                        rounded-xl
                        bg-zinc-900
                        border
                        border-zinc-800
                    "
                />


                {error && (

                    <div className="
                        text-red-400
                    ">
                        {error}
                    </div>

                )}


                <button
                    type="submit"
                    className="
                        w-full
                        p-4
                        rounded-xl
                        bg-white
                        text-black
                        font-semibold
                    "
                >
                    Zaloguj
                </button>

            </form>

        </div>
    )
}