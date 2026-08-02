"use client";

import { useEffect, useState } from "react";

export default function ProblemsPage() {
  const [problems, setProblems] = useState<any[]>([]);
  const [role, setRole] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");

    if (token) {
      try {
        const payload = JSON.parse(
          atob(token.split(".")[1])
        );

        setRole(payload.role);
      } catch {
        console.log("Token error");
      }
    }

    fetch("http://127.0.0.1:8000/problems/all")
      .then((res) => res.json())
      .then((data) => {
        console.log(data);
        setProblems(data);
      })
      .catch((err) => console.log(err));
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">
        AEOS Problems
      </h1>

      {problems.length === 0 ? (
        <p>No problems found.</p>
      ) : (
        <div className="space-y-4">
          {problems.map((problem) => (
            <div
              key={problem.id}
              className="border rounded p-4"
            >
              <a
                href={"/problems/" + problem.id}
                className="text-xl font-semibold text-blue-600"
              >
                {problem.title}
              </a>

              <p className="mt-2">
                {problem.description}
              </p>

              <p>
                Difficulty: {problem.difficulty}
              </p>

              <p>
                🏆 Score: {problem.points}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
