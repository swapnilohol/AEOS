"use client";

import { useState } from "react";

export default function CreateTestcase() {
  const [problemId, setProblemId] =
    useState(1);

  const [inputData, setInputData] =
    useState("");

  const [expectedOutput,
    setExpectedOutput] =
    useState("");

  async function handleSubmit() {
    const res = await fetch(
      "http://127.0.0.1:8000/testcases/",
      {
        method: "POST",
        headers: {
  "Content-Type": "application/json",
  Authorization:
    `Bearer ${localStorage.getItem("token")}`,
},
        body: JSON.stringify({
          problem_id: problemId,
          input_data: inputData,
          expected_output:
            expectedOutput,
          is_hidden: false,
        }),
      }
    );

    const data = await res.json();

    alert(
      JSON.stringify(data)
    );
  }

  return (
    <div className="p-8 space-y-4">

      <h1 className="text-3xl font-bold">
        Create Test Case
      </h1>

      <input
        type="number"
        className="border p-2 w-full"
        value={problemId}
        onChange={(e) =>
          setProblemId(
            Number(e.target.value)
          )
        }
      />

      <textarea
        className="border p-2 w-full"
        placeholder="Input JSON"
        value={inputData}
        onChange={(e) =>
          setInputData(
            e.target.value
          )
        }
      />

      <input
        className="border p-2 w-full"
        placeholder="Expected Output"
        value={expectedOutput}
        onChange={(e) =>
          setExpectedOutput(
            e.target.value
          )
        }
      />

      <button
        onClick={handleSubmit}
        className="bg-green-500 text-white px-4 py-2 rounded"
      >
        Create Testcase
      </button>

    </div>
  );
}
