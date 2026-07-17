"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getStudentPerformance, type ScoreHistoryPoint } from "@/services/dashboard.service";
import AnalyticsChart from "@/components/dashboard/AnalyticsChart";

export default function StudentPerformancePage() {
  const [history, setHistory] = useState<ScoreHistoryPoint[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getStudentPerformance()
      .then((res) => setHistory(res.data?.score_history ?? []))
      .catch(() => setError("Unable to load performance data."));
  }, []);

  const chartData = history.map((point, index) => ({
    attempt: `#${index + 1}`,
    final_score: point.final_score ?? 0,
  }));

  return (
    <main className="min-h-screen p-8">
      <div className="mx-auto max-w-3xl space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold">My Performance</h1>
          <Link href="/student/dashboard" className="text-sm text-gray-600 hover:underline">
            ← Dashboard
          </Link>
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <section className="rounded border p-4">
          <h2 className="mb-2 font-medium">Score Progress</h2>
          <AnalyticsChart data={chartData} xKey="attempt" yKey="final_score" type="line" />
        </section>

        <section className="rounded border p-4">
          <h2 className="mb-2 font-medium">Submission History</h2>
          {history.length === 0 ? (
            <p className="text-sm text-gray-500">No submissions yet.</p>
          ) : (
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b">
                  <th className="py-2">Date</th>
                  <th className="py-2">Score</th>
                  <th className="py-2">Max</th>
                </tr>
              </thead>
              <tbody>
                {history.map((point) => (
                  <tr key={point.submission_id} className="border-b">
                    <td className="py-2">{new Date(point.achieved_at).toLocaleString()}</td>
                    <td className="py-2">{point.final_score ?? "Pending"}</td>
                    <td className="py-2">{point.max_points}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      </div>
    </main>
  );
}
