"use client";

import { useState } from "react";
import { login } from "@/services/auth";

export default function LoginPage() {

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  async function handleLogin() {

    const data = await login(
  username,
  password
);

console.log(data)
if (data.access_token) {

  localStorage.setItem(
    "token",
    data.access_token
  );

  alert("Login Successful");

  window.location.href =
    "/dashboard";

} else {

  alert("Login Failed");

}
  }


  return (
    <div className="min-h-screen flex items-center justify-center">

      <div className="w-96 space-y-4">

        <h1 className="text-2xl font-bold">
          AEOS Login
        </h1>


        <input
          className="border p-2 w-full"
          placeholder="Email"
          value={username}
          onChange={(e)=>
            setUsername(e.target.value)
          }
        />


        <input
          className="border p-2 w-full"
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e)=>
            setPassword(e.target.value)
          }
        />


        <button
          className="bg-black text-white p-2 w-full"
          onClick={handleLogin}
        >
          Login
        </button>

      </div>

    </div>
  );
}
