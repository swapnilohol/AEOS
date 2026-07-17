"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

export default function EditProblemPage() {

  const params = useParams();

  const [problem, setProblem] = useState<any>({
    title: "",
    description: "",
    difficulty: "",
    points: 0,
  });

  useEffect(() => {

    fetch(
      `http://127.0.0.1:8000/problems/${params.id}`
    )
      .then((res) => res.json())
      .then((data) => setProblem(data));

  }, [params.id]);


  const updateProblem = async () => {

    const token = localStorage.getItem("token");

    await fetch(
      `http://127.0.0.1:8000/problems/${params.id}`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(problem),
      }
    );

    alert("Problem Updated");

    window.location.href = "/problems";
  };


  return (
    <div className="p-8">

      <h1 className="text-3xl font-bold mb-6">
        Edit Problem
      </h1>


      <input
        className="border p-2 w-full mb-3"
        value={problem.title}
        onChange={(e)=>
          setProblem({
            ...problem,
            title:e.target.value
          })
        }
      />


      <textarea
        className="border p-2 w-full mb-3"
        value={problem.description}
        onChange={(e)=>
          setProblem({
            ...problem,
            description:e.target.value
          })
        }
      />


      <input
        className="border p-2 w-full mb-3"
        value={problem.difficulty}
        onChange={(e)=>
          setProblem({
            ...problem,
            difficulty:e.target.value
          })
        }
      />


      <input
        className="border p-2 w-full mb-3"
        type="number"
        value={problem.points}
        onChange={(e)=>
          setProblem({
            ...problem,
            points:Number(e.target.value)
          })
        }
      />


      <button
        onClick={updateProblem}
        className="bg-blue-600 text-white px-4 py-2 rounded"
      >
        Update Problem
      </button>

    </div>
  );
}
