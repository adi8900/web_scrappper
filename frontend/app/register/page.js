"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"

import { register } from "@/lib/api"


export default function RegisterPage(){

    const router = useRouter()

    const [username,setUsername] =
        useState("")

    const [email,setEmail] =
        useState("")

    const [password,setPassword] =
        useState("")

    const [error,setError] =
        useState("")


    async function handleRegister(e){

        e.preventDefault()

        setError("")


        const result =
            await register(
                username,
                email,
                password
            )


        if(result.message){

            router.push("/login")

        }else{

            setError(
                result.detail ||
                "Błąd rejestracji"
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
                Rejestracja
            </h1>


            <form
                onSubmit={handleRegister}
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
                    type="email"
                    value={email}
                    onChange={
                        e =>
                        setEmail(
                            e.target.value
                        )
                    }
                    placeholder="Email"
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
                    Utwórz konto
                </button>

            </form>

        </div>
    )
}