"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiRequest } from "@/lib/api";

export default function AdminPage() {

  const [stats, setStats] = useState<any>(null);
const [submissions, setSubmissions] = useState<any[]>([]);

  useEffect(() => {

  async function load() {

    const statsData =
      await apiRequest("/admin/stats");

    console.log(
      "STATS:",
      statsData
    );

    setStats(statsData);


    const submissionsData =
      await apiRequest("/admin/submissions");

    console.log(
      "SUBMISSIONS:",
      submissionsData
    );

    setSubmissions(
      Array.isArray(submissionsData)
        ? submissionsData
        : submissionsData.submissions || []
    );

  }

  load();

}, []);
   


  return (

    <div className="p-10">


      <h1 className="text-4xl font-bold mb-8">
        ⚙️ Admin Panel
      </h1>
<pre>
  {JSON.stringify(
    stats,
    null,
    2
  )}
</pre>



      {stats && (

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">


          <div className="border rounded-xl p-6 shadow">
            <h2 className="text-gray-500">
              👥 Total Users
            </h2>

            <p className="text-3xl font-bold mt-2">
              {stats?.total_users ?? 0}
            </p>
          </div>



          <div className="border rounded-xl p-6 shadow">
            <h2 className="text-gray-500">
              🧩 Total Problems
            </h2>

            <p className="text-3xl font-bold mt-2">
              {stats?.total_problems ?? 0}
            </p>
          </div>



          <div className="border rounded-xl p-6 shadow">
            <h2 className="text-gray-500">
              📝 Total Submissions
            </h2>

            <p className="text-3xl font-bold mt-2">
              {stats?.total_submissions ?? 0}
            </p>
          </div>


        </div>

      )}



      <h2 className="text-2xl font-bold mb-4">
        Quick Actions
      </h2>
<h2 className="text-2xl font-bold mb-4">
  Recent Submissions
</h2>


<div className="border rounded-xl overflow-hidden">

<table className="w-full">

<thead className="bg-gray-100 text-black">

<tr>
<th className="p-3 text-left text-black">ID</th>
<th className="p-3 text-left text-black">User</th>
<th className="p-3 text-left text-black">Problem</th>
<th className="p-3 text-left text-black">Language</th>
<th className="p-3 text-left text-black">Status</th>
<th className="p-3 text-left text-black">Score</th>
</tr>

</thead>


<tbody>

{submissions.map((s)=>(
<tr key={s.id} className="border-t">

<td className="p-3">
{s.id}
</td>

<td className="p-3">
{s.username}
</td>

<td className="p-3">
{s.problem}
</td>

<td className="p-3">
{s.language}
</td>

<td className="p-3">
{s.status}
</td>

<td className="p-3">
{s.score}
</td>

</tr>
))}

</tbody>

</table>

</div>


      <div className="flex gap-4">


        <Link
          href="/admin/problems/create"
          className="bg-blue-600 text-white px-5 py-3 rounded-lg"
        >
          ➕ Create Problem
        </Link>



        <Link
          href="/admin/testcases/create"
          className="bg-green-600 text-white px-5 py-3 rounded-lg"
        >
          🧪 Create Test Case
        </Link>


      </div>


    </div>

  );
}
