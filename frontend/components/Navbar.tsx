"use client";

import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="bg-black text-white p-4">
      <div className="flex gap-6">

        <Link href="/dashboard">
          Dashboard
        </Link>

        <Link href="/problems">
          Problems
        </Link>

        <Link href="/submissions">
          Submissions
        </Link>

        <Link href="/leaderboard">
          Leaderboard
        </Link>

        <Link href="/admin">
          Admin
        </Link>
        <Link href="/register">
  Register
</Link>
         
        <button
          onClick={() => {
            localStorage.removeItem("token");
            window.location.href = "/login";
          }}
        >
          Logout
        </button>

      </div>
    </nav>
  );
}
