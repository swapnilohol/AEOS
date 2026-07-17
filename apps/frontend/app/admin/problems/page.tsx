"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { createProblem, deleteProblem, listProblems, type Problem } from "@/services/problem.service";

export default function AdminProblemsPage() {
  const [problems, setProblems] = useState<Problem[]>([]);
  const [hackathonId, setHackathonId] = useState("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  function loadProblems() {
    listProblems()
      .then((res) => setProblems(res.data?.items ?? []))
      .catch(() => setError("Unable to load problems."));
  }

  useEffect(() => {
    loadProblems();
  }, []);

  async function handleCreate(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await createProblem({ hackathon_id: hackathonId, title, description });
      setTitle("");
      setDescription("");
      loadProblems();
    } catch {
      setError("Unable to create problem. Check the hackathon ID and try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDelete(id: string) {
    try {
      await deleteProblem(id);
      loadProblems();
    } catch {
      setError("Unable to delete problem.");
    }
  }

  return (
    <main className="min-h-screen p-8">
      <div className="mx-auto max-w-3xl space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold">Problems</h1>
          <Link href="/admin" className="text-sm text-gray-600 hover:underline">
            ← Dashboard
          </Link>
        </div>

        <form onSubmit={handleCreate} className="space-y-3 rounded border p-4">
          <h2 className="font-medium">Add Problem</h2>
          <input
            type="text"
            placeholder="Hackathon ID"
            value={hackathonId}
            onChange={(e) => setHackathonId(e.target.value)}
            required
            className="w-full rounded border px-3 py-2"
          />
          <input
            type="text"
            placeholder="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            className="w-full rounded border px-3 py-2"
          />
          <textarea
            placeholder="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
            className="w-full rounded border px-3 py-2"
            rows={3}
          />
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button
            type="submit"
            disabled={isSubmitting}
            className="rounded bg-black px-4 py-2 text-white disabled:opacity-50"
          >
            {isSubmitting ? "Adding..." : "Add Problem"}
          </button>
        </form>

        <ul className="space-y-2">
          {problems.map((problem) => (
            <li key={problem.id} className="flex items-center justify-between rounded border p-3">
              <div>
                <p className="font-medium">{problem.title}</p>
                <p className="text-sm text-gray-500">Max score: {problem.max_score}</p>
              </div>
              <button
                onClick={() => handleDelete(problem.id)}
                className="text-sm text-red-600 hover:underline"
              >
                Delete
              </button>
            </li>
          ))}
          {problems.length === 0 && !error && (
            <p className="text-sm text-gray-500">No problems yet.</p>
          )}
        </ul>
      </div>
    </main>
  );
}
