"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function RegisterPage() {
  const router = useRouter();

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleRegister = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username,
          email,
          password,
        }),
      });

      const data = await res.json();

      if (res.ok) {
        alert("Registration Successful");
        router.push("/login");
      } else {
        alert(data.detail || "Registration failed");
      }

    } catch (error) {
      alert("Backend connection error");
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center">
      <div className="border p-6 rounded w-96 flex flex-col gap-4">
        <h1 className="text-2xl font-bold">Register</h1>

        <input
          className="border p-2"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        <input
          className="border p-2"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          type="password"
          className="border p-2"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button
          onClick={handleRegister}
          className="border p-2 rounded"
        >
          Register
        </button>
      </div>
    </main>
  );
}
