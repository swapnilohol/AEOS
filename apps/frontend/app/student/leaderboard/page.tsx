"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getStudentLeaderboard, type StudentLeaderboardData } from "@/services/dashboard.service";
import LeaderboardTable from "@/components/dashboard/LeaderboardTable";
import StatsCard from "@/components/StatsCard";

export default function StudentLeaderboardPage() {
  const [data, setData] = useState<StudentLeaderboardData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getStudentLeaderboard()
      .then((res) => setData(res.data))
      .catch(() => setError("No active hackathon leaderboard right now."));
  }, []);

  return (
    <main className="min-h-screen p-8">
      <div className="mx-auto max-w-3xl space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold">Leaderboard</h1>
          <Link href="/student/dashboard" className="text-sm text-gray-600 hover:underline">
            ← Dashboard
          </Link>
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        {data && (
          <>
            <div className="grid grid-cols-3 gap-4">
              <StatsCard label="Your Rank" value={data.own_rank ?? "-"} />
              <StatsCard label="Your Score" value={data.own_total_score ?? "-"} />
              <StatsCard label="Participants" value={data.total_participants} />
            </div>

            <section className="rounded border p-4">
              <h2 className="mb-2 font-medium">Top 10</h2>
              <LeaderboardTable entries={data.top_entries} />
            </section>
          </>
        )}
      </div>
    </main>
  );
}
