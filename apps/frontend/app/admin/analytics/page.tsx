"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getAdminActivity, getAdminAnalytics, type ActivityEntry, type AdminAnalyticsData } from "@/services/dashboard.service";
import AnalyticsChart from "@/components/dashboard/AnalyticsChart";
import ActivityFeed from "@/components/dashboard/ActivityFeed";

export default function AdminAnalyticsPage() {
  const [data, setData] = useState<AdminAnalyticsData | null>(null);
  const [activity, setActivity] = useState<ActivityEntry[]>([]);
  const [activityLoading, setActivityLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getAdminAnalytics()
      .then((res) => setData(res.data))
      .catch(() => setError("Unable to load analytics."));

    getAdminActivity()
      .then((res) => setActivity(res.data?.items ?? []))
      .catch(() => {})
      .finally(() => setActivityLoading(false));
  }, []);

  return (
    <main className="min-h-screen p-8">
      <div className="mx-auto max-w-4xl space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold">Analytics</h1>
          <div className="flex gap-4 text-sm text-gray-600">
            <Link href="/admin" className="hover:underline">Dashboard</Link>
            <Link href="/admin/reports" className="hover:underline">Reports</Link>
          </div>
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}
        {!data && !error && <p className="text-gray-500">Loading...</p>}

        {data && (
          <>
            <section className="rounded border p-4">
              <h2 className="mb-2 font-medium">Problem Completion Rate</h2>
              <AnalyticsChart
                data={data.problem_completion.map((p) => ({
                  title: p.title,
                  completion_rate_percent: p.completion_rate_percent,
                }))}
                xKey="title"
                yKey="completion_rate_percent"
                type="bar"
              />
            </section>

            <section className="rounded border p-4">
              <h2 className="mb-2 font-medium">Score Distribution</h2>
              <AnalyticsChart
                data={Object.entries(data.score_distribution).map(([bucket, count]) => ({
                  bucket,
                  count,
                }))}
                xKey="bucket"
                yKey="count"
                type="bar"
              />
            </section>

            <section className="rounded border p-4">
              <h2 className="mb-2 font-medium">Execution Stats</h2>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <p>Timeouts: {data.execution_stats.timeout_count}</p>
                <p>Failed: {data.execution_stats.failed_executions}</p>
                <p>
                  Avg time:{" "}
                  {data.execution_stats.average_execution_time_ms
                    ? `${Math.round(data.execution_stats.average_execution_time_ms)} ms`
                    : "-"}
                </p>
              </div>
            </section>
          </>
        )}

        <section className="rounded border p-4">
          <h2 className="mb-2 font-medium">Recent Activity</h2>
          <ActivityFeed entries={activity} isLoading={activityLoading} />
        </section>
      </div>
    </main>
  );
}
