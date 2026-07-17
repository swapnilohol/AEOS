"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getStudentOverview, type StudentOverviewData } from "@/services/dashboard.service";
import StatsCard from "@/components/StatsCard";

function formatRemaining(seconds: number | null): string {
  if (seconds === null) return "No active hackathon timer";
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  return `${hrs}h ${mins}m remaining`;
}

export default function StudentDashboardPage() {
  const [data, setData] = useState<StudentOverviewData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getStudentOverview()
      .then((res) => setData(res.data))
      .catch(() => setError("Unable to load your dashboard."));
  }, []);

  return (
    <main className="min-h-screen p-8">
      <div className="mx-auto max-w-3xl space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold">My Dashboard</h1>
          <div className="flex gap-4 text-sm text-gray-600">
            <Link href="/student" className="hover:underline">Problems</Link>
            <Link href="/student/performance" className="hover:underline">Performance</Link>
            <Link href="/student/leaderboard" className="hover:underline">Leaderboard</Link>
          </div>
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}
        {!data && !error && <p className="text-gray-500">Loading...</p>}

        {data && (
          <>
            <section className="rounded border p-4">
              <h2 className="mb-2 font-medium">Profile</h2>
              <p className="text-sm text-gray-700">{data.profile.full_name}</p>
              <p className="text-sm text-gray-500">
                {data.profile.college_name ?? "-"} · {data.profile.department ?? "-"} · Semester{" "}
                {data.profile.semester ?? "-"}
              </p>
            </section>

            <section className="rounded border p-4">
              <h2 className="mb-2 font-medium">Assessment Status</h2>
              <p className="text-sm text-gray-700">
                Status: {data.hackathon_status} — {formatRemaining(data.remaining_seconds)}
              </p>
            </section>

            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <StatsCard label="Attempted" value={data.progress.problems_attempted} />
              <StatsCard label="Solved" value={data.progress.problems_solved} />
              <StatsCard label="Completion %" value={data.progress.completion_percent} />
              <StatsCard label="Rank" value={data.rank?.rank ?? "-"} />
            </div>
          </>
        )}
      </div>
    </main>
  );
}
