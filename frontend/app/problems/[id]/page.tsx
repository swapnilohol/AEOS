"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Editor from "@monaco-editor/react";

export default function ProblemPage() {
  const params = useParams();
  const [problem, setProblem] = useState<any>(null);
const [code, setCode] =
  useState(
`def solve():
    pass`
);
const [result, setResult] = useState<any>(null);
  useEffect(() => {
  fetch(
  `http://127.0.0.1:8000/problems/${params.id}`,
    {
      headers: {
        Authorization:
          `Bearer ${localStorage.getItem("token")}`
      }
    }
  )
  .then((res) => res.json())
  .then((data) => {
    console.log("PROBLEM:", data);
    setProblem(data);
  });

}, [params.id]);

  if (!problem) {
    return <div className="p-8">Loading...</div>;
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold">
        {problem.title}
      </h1>

      <p className="mt-4">
        {problem.description}
      </p>

      <p className="mt-4">
  🏆 Max Score: {problem.points}
</p>

<div className="mt-6">
  <Editor
  height="400px"
  defaultLanguage="python"
  theme="vs-dark"
  value={code}
  onChange={(value) =>
    setCode(value || "")
  }
/>
</div>
<button
  className="bg-black text-white px-4 py-2 mt-4 rounded"
  onClick={async () => {

    alert("Button Working");
    console.log("SUBMIT CLICKED");

    try {

      const token =
        localStorage.getItem("token");

    const response = await fetch(
  "http://127.0.0.1:8000/submissions/",
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization:
        `Bearer ${localStorage.getItem("token")}`,
    },
    body: JSON.stringify({
  problem_id: Number(params.id),
  language: "python",
  source_code: code,
}),
  }
);

      const data =
        await response.json();

      console.log(
  "SUBMISSION RESPONSE:",
  JSON.stringify(data, null, 2)
);

      setResult(data);

    } catch(error) {

      console.error(
        "SUBMIT ERROR:",
        error
      );

      alert("Submit Error");

    }

  }}
>
  Submit Code
</button>

{result && (
  <div className="mt-6 border p-4 rounded">
    <p>
      Status: {result.status}
    </p>

    <p>
      Score: {result.score}
    </p>

    <p>
      Output: {result.output}
    </p>
  </div>
)}
    </div>
  );
}
