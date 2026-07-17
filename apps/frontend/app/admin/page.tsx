"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getAdminDashboard, type AdminDashboardData } from "@/services/admin.service";

export default function AdminDashboardPage() {
  const [data, setData] = useState<AdminDashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getAdminDashboard()
      .then((res) => setData(res.data))
      .catch(() => setError("Unable to load dashboard data."));
  }, []);

  return (
    <main className="min-h-screen p-8">
      <div className="mx-auto max-w-4xl space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold">Admin Dashboard</h1>
          <nav className="flex gap-4 text-sm text-gray-600">
            <Link href="/admin/students" className="hover:underline">
              Students
            </Link>
            <Link href="/admin/problems" className="hover:underline">
              Problems
            </Link>
          </nav>
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        {!data && !error && <p className="text-gray-500">Loading...</p>}

        {data && (
          <>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <StatCard label="Students" value={data.total_students} />
              <StatCard label="Problems" value={data.total_problems} />
              <StatCard label="Submissions" value={data.total_submissions} />
              <StatCard label="Violations" value={data.total_violations} />
            </div>

            <section className="rounded border p-4">
              <h2 className="mb-2 font-medium">Active Hackathon</h2>
              {data.active_hackathon ? (
                <p className="text-sm text-gray-700">
                  {data.active_hackathon.title} — {data.active_hackathon.problem_count} problems
                </p>
              ) : (
                <p className="text-sm text-gray-500">No active hackathon.</p>
              )}
            </section>

            <section className="rounded border p-4">
              <h2 className="mb-2 font-medium">Submission Status</h2>
              <div className="grid grid-cols-4 gap-4 text-sm">
                <p>Pending: {data.submission_status_breakdown.pending}</p>
                <p>Running: {data.submission_status_breakdown.running}</p>
                <p>Completed: {data.submission_status_breakdown.completed}</p>
                <p>Failed: {data.submission_status_breakdown.failed}</p>
              </div>
            </section>

            <section className="rounded border p-4">
              <h2 className="mb-2 font-medium">Top Scores</h2>
              {data.top_scores.length === 0 ? (
                <p className="text-sm text-gray-500">No scores yet.</p>
              ) : (
                <ol className="space-y-1 text-sm">
                  {data.top_scores.map((entry) => (
                    <li key={entry.user_id}>
                      {entry.full_name} — {entry.total_points} pts
                    </li>
                  ))}
                </ol>
              )}
            </section>
          </>
        )}
      </div>
    </main>
  );
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded border p-4 text-center">
      <p className="text-2xl font-semibold">{value}</p>
      <p className="text-sm text-gray-500">{label}</p>
    </div>
  );
}
