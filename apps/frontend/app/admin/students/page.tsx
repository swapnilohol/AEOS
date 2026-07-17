"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { listStudents, type StudentRecord } from "@/services/student.service";

export default function AdminStudentsPage() {
  const [students, setStudents] = useState<StudentRecord[]>([]);
  const [search, setSearch] = useState("");
  const [error, setError] = useState<string | null>(null);

  function loadStudents(query: string) {
    listStudents(query)
      .then((res) => setStudents(res.data?.items ?? []))
      .catch(() => setError("Unable to load students."));
  }

  useEffect(() => {
    loadStudents("");
  }, []);

  return (
    <main className="min-h-screen p-8">
      <div className="mx-auto max-w-4xl space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold">Students</h1>
          <Link href="/admin" className="text-sm text-gray-600 hover:underline">
            ← Dashboard
          </Link>
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            loadStudents(search);
          }}
          className="flex gap-2"
        >
          <input
            type="text"
            placeholder="Search by name, email, or student ID"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded border px-3 py-2"
          />
          <button type="submit" className="rounded bg-black px-4 py-2 text-white">
            Search
          </button>
        </form>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b">
              <th className="py-2">Name</th>
              <th className="py-2">Email</th>
              <th className="py-2">Student ID</th>
              <th className="py-2">Semester</th>
              <th className="py-2">Active</th>
            </tr>
          </thead>
          <tbody>
            {students.map((student) => (
              <tr key={student.id} className="border-b">
                <td className="py-2">{student.full_name}</td>
                <td className="py-2">{student.email}</td>
                <td className="py-2">{student.student_id}</td>
                <td className="py-2">{student.semester ?? "-"}</td>
                <td className="py-2">{student.is_active ? "Yes" : "No"}</td>
              </tr>
            ))}
            {students.length === 0 && !error && (
              <tr>
                <td colSpan={5} className="py-4 text-center text-gray-500">
                  No students found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </main>
  );
}
