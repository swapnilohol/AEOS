"use client";

import { useEffect, useState } from "react";
import { apiRequest } from "@/lib/api";

export default function SubmissionsPage() {
  const [subs, setSubs] = useState<any[]>([]);

  useEffect(() => {
    async function load() {
      const data = await apiRequest(
        "/submissions/my"
      );

      console.log("SUBMISSIONS:", data);

setSubs(
  Array.isArray(data)
    ? data
    : data.submissions || []
);
    }

    load();
  }, []);

  return (
    <div className="p-8">

      <h1 className="text-3xl font-bold mb-6">
        My Submissions
      </h1>

      {subs.length === 0 ? (
        <p>No submissions found.</p>
      ) : (
        <div className="space-y-4">

          {subs.map((s) => (
            <div
              key={s.id}
              className="border rounded p-4"
            >
              <p>
                Submission ID: {s.id}
              </p>

              <p>
  Problem: {s.problem_title}
</p>

<p>
  Language: {s.language}
</p>

<p>
  Status: {s.status}
</p>

<p>
  Score: {s.score}
</p>
            </div>
          ))}

        </div>
      )}
    </div>
  );
}
