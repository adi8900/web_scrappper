const API = process.env.NEXT_PUBLIC_API_URL


function getToken(){

    if(typeof window === "undefined"){
        return null
    }

    return localStorage.getItem(
        "access_token"
    )
}


export async function register(
    username,
    email,
    password
){

    const params = new URLSearchParams()

    params.append(
        "username",
        username
    )

    params.append(
        "email",
        email
    )

    params.append(
        "password",
        password
    )


    const res = await fetch(
        `${API}/api/auth/register?${params}`,
        {
            method: "POST",
        }
    )

    return res.json()
}


export async function login(
    username,
    password
){

    const params = new URLSearchParams()

    params.append(
        "username",
        username
    )

    params.append(
        "password",
        password
    )


    const res = await fetch(
        `${API}/api/auth/login?${params}`,
        {
            method: "POST",
        }
    )

    const data = await res.json()

    if(res.ok && data.access_token){

        localStorage.setItem(
            "access_token",
            data.access_token
        )

        localStorage.setItem(
            "username",
            data.username
        )
    }

    return data
}


export function logout(){

    localStorage.removeItem(
        "access_token"
    )

    localStorage.removeItem(
        "username"
    )
}


export async function getMe(){

    const token = getToken()

    if(!token){
        return null
    }


    const res = await fetch(
        `${API}/api/auth/me`,
        {
            headers: {
                Authorization:
                    `Bearer ${token}`
            },

            cache: "no-store",
        }
    )


    if(!res.ok){
        return null
    }

    return res.json()
}


export async function comparePart(
    query
){

    const token = getToken()

    const res = await fetch(
        `${API}/api/compare?query=${encodeURIComponent(query)}`,
        {
            cache: "no-store",

            headers: {
                Authorization:
                    `Bearer ${token}`
            },
        }
    )

    return res.json()
}


export async function getHistory(){

    const token = getToken()

    const res = await fetch(
        `${API}/api/history`,
        {
            cache: "no-store",

            headers: {
                Authorization:
                    `Bearer ${token}`
            },
        }
    )


    if(!res.ok){
        return []
    }

    return res.json()
}