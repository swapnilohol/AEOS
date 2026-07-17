"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { listProblems, type Problem } from "@/services/problem.service";

export default function StudentLandingPage() {
  const [problems, setProblems] = useState<Problem[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listProblems()
      .then((res) => setProblems(res.data?.items ?? []))
      .catch(() => setError("Unable to load problems."));
  }, []);

  return (
    <main className="min-h-screen p-8">
      <div className="mx-auto max-w-3xl space-y-4">
        <h1 className="text-2xl font-semibold">Your Problems</h1>
        <p className="text-sm text-gray-500">
          Pick a problem to open its coding workspace. A fuller student dashboard
          (profile, submission history) is a separate, upcoming module.
        </p>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <ul className="space-y-2">
          {problems.map((problem) => (
            <li key={problem.id} className="rounded border p-4">
              <Link href={`/student/problems/${problem.id}`} className="font-medium hover:underline">
                {problem.title}
              </Link>
              <p className="text-sm text-gray-500">Max score: {problem.max_score}</p>
            </li>
          ))}
          {problems.length === 0 && !error && (
            <p className="text-sm text-gray-500">No problems available yet.</p>
          )}
        </ul>
      </div>
    </main>
  );
}
