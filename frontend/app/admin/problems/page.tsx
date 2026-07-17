"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiRequest } from "@/lib/api";

export default function AdminProblemsPage() {

  const [problems, setProblems] = useState<any[]>([]);


  async function loadProblems() {

    const data = await apiRequest(
      "/problems/"
    );

    setProblems(data);

  }


  useEffect(() => {

    loadProblems();

  }, []);



  async function deleteProblem(id:number){

    await apiRequest(
      `/problems/${id}`,
      {
        method:"DELETE"
      }
    );

    loadProblems();

  }



  return (

    <div className="p-8">


      <h1 className="text-3xl font-bold mb-6">
        🧩 Manage Problems
      </h1>



      <Link
        href="/admin/problems/create"
        className="bg-blue-600 text-white px-4 py-2 rounded"
      >
        ➕ Create Problem
      </Link>



      <div className="mt-8 border rounded">


        <table className="w-full text-black">


          <thead className="bg-gray-100">

            <tr>

              <th className="p-3 text-left">
                ID
              </th>

              <th className="p-3 text-left">
                Title
              </th>

              <th className="p-3 text-left">
                Difficulty
              </th>

              <th className="p-3 text-left">
                Points
              </th>

              <th className="p-3 text-left">
                Action
              </th>

            </tr>

          </thead>



          <tbody>


          {problems.map((p)=>(


            <tr
  key={p.id}
  className="border-t text-white"
>


              <td className="p-3 text-white">
                {p.id}
              </td>


              <td className="p-3">
                {p.title}
              </td>


              <td className="p-3">
                {p.difficulty}
              </td>


              <td className="p-3">
                {p.points}
              </td>


              <td className="p-3">


                <Link
                  href={`/admin/problems/edit/${p.id}`}
                  className="text-blue-600 mr-4"
                >
                  Edit
                </Link>


                <button
                  className="text-red-600"
                  onClick={() =>
                    deleteProblem(p.id)
                  }
                >
                  Delete
                </button>


              </td>


            </tr>


          ))}


          </tbody>


        </table>


      </div>


    </div>

  );

}
