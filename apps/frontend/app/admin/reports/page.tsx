"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getHackathonSummary, getSubmissionReport } from "@/services/dashboard.service";

export default function AdminReportsPage() {
  const [submissionReport, setSubmissionReport] = useState<Record<string, unknown> | null>(null);
  const [hackathonSummary, setHackathonSummary] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getSubmissionReport(), getHackathonSummary()])
      .then(([sub, summary]) => {
        setSubmissionReport(sub.data);
        setHackathonSummary(summary.data);
      })
      .catch(() => setError("Unable to load reports."));
  }, []);

  return (
    <main className="min-h-screen p-8">
      <div className="mx-auto max-w-4xl space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold">Reports</h1>
          <Link href="/admin" className="text-sm text-gray-600 hover:underline">
            ← Dashboard
          </Link>
        </div>
        <p className="text-sm text-gray-500">
          Structured summary data. Export to file is a future enhancement, not included here.
        </p>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <section className="rounded border p-4">
          <h2 className="mb-2 font-medium">Hackathon Summary</h2>
          <pre className="overflow-x-auto rounded bg-gray-50 p-3 text-xs">
            {hackathonSummary ? JSON.stringify(hackathonSummary, null, 2) : "Loading..."}
          </pre>
        </section>

        <section className="rounded border p-4">
          <h2 className="mb-2 font-medium">Submission Report</h2>
          <pre className="overflow-x-auto rounded bg-gray-50 p-3 text-xs">
            {submissionReport ? JSON.stringify(submissionReport, null, 2) : "Loading..."}
          </pre>
        </section>

        <p className="text-sm text-gray-500">
          Individual student reports are available at{" "}
          <code>/api/v1/dashboard/admin/reports/student/&#123;user_id&#125;</code> — no dedicated
          per-student page yet.
        </p>
      </div>
    </main>
  );
}
