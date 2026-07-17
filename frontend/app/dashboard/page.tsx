"use client";

import { useEffect, useState } from "react";
import { apiRequest } from "@/lib/api";

export default function Dashboard() {

  
  const [data, setData] = useState<any>(null);

  useEffect(() => {

  async function load() {

    const res = await apiRequest(
  "/dashboard/"
);

console.log("FULL RESPONSE:", res);

setData(res);

  }

  load();

}, []);

  return (
    <div className="p-10">

      <h1 className="text-4xl font-bold mb-8">
        AEOS Dashboard
      </h1>


      {data && (

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">


          <div className="border rounded-xl p-6 shadow">
            <h2 className="text-gray-500">
              👤 Username
            </h2>

            <p className="text-2xl font-bold mt-2">
              {data?.username ?? "User"}
            </p>
          </div>


          <div className="border rounded-xl p-6 shadow">
            <h2 className="text-gray-500">
              📝 Total Submissions
            </h2>

            <p className="text-3xl font-bold mt-2">
              {data?.total_submissions ?? 0}
            </p>
          </div>


          <div className="border rounded-xl p-6 shadow">
            <h2 className="text-gray-500">
              ✅ Solved Problems
            </h2>

            <p className="text-3xl font-bold mt-2">
              {data?.solved_problems ?? 0}
            </p>
          </div>

          <div className="border rounded-xl p-6 shadow">
            <h2 className="text-gray-500">
              🏆 Total Score
            </h2>

            <p className="text-3xl font-bold mt-2">
              {data?.total_score ?? 0}
            </p>
          </div>


          <div className="border rounded-xl p-6 shadow">
            <h2 className="text-gray-500">
              🥇 Rank
            </h2>

            <p className="text-3xl font-bold mt-2">
              {data?.rank ?? 0}
            </p>
          </div>


        </div>

      )}

    </div>
  );
}
