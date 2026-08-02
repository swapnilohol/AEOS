"use client";

import { useState } from "react";

export default function CreateProblem() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [difficulty, setDifficulty] = useState("Easy");
  const [points, setPoints] = useState(100);

  async function handleSubmit() {
    const token = localStorage.getItem("token");

    try {
      const res = await fetch(
        "http://127.0.0.1:8000/problems/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            title,
            description,
            difficulty,
            points,
          }),
        }
      );

      const data = await res.json();

      console.log("CREATE PROBLEM:", data);

      alert(JSON.stringify(data));

      if (res.ok) {
        setTitle("");
        setDescription("");
        setDifficulty("Easy");
        setPoints(100);
      }
    } catch (err) {
      console.error(err);
      alert("Failed to create problem.");
    }
  }

  return (
    <div className="p-8 space-y-4 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold">
        Create Problem
      </h1>

      <input
        className="border p-2 w-full rounded"
        placeholder="Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />

      <textarea
        className="border p-2 w-full rounded h-40"
        placeholder="Description"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />

      <select
  className="border p-2 w-full rounded text-black bg-white"
  value={difficulty}
  onChange={(e) => setDifficulty(e.target.value)}
>
  <option value="Easy">Easy</option>
  <option value="Medium">Medium</option>
  <option value="Hard">Hard</option>
</select>

      <input
        type="number"
        className="border p-2 w-full rounded"
        value={points}
        onChange={(e) => setPoints(Number(e.target.value))}
      />

      <button
        onClick={handleSubmit}
        className="bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700"
      >
        Create
      </button>
    </div>
  );
}
