"use client";

import { useEffect, useState } from "react";

export default function LeaderboardPage() {

  const [leaders, setLeaders] = useState<any[]>([]);


  useEffect(() => {

    fetch(
      "http://127.0.0.1:8000/leaderboard/"
    )
      .then((res) => res.json())
      .then((data) =>
        setLeaders(data)
      );

  }, []);


  return (

    <div className="p-8">

      <h1 className="text-3xl font-bold mb-6">
        🏆 Leaderboard
      </h1>


      <div className="space-y-4">

        {leaders.map((user) => (

          <div
            key={user.rank}
            className="border rounded p-4"
          >

            <h2 className="text-xl font-bold">
              Rank #{user.rank}
            </h2>


            <p>
              Username: {user.username}
            </p>


            <p>
              Solved Problems: {user.solved}
            </p>


            <p>
              Score: {user.score}
            </p>


          </div>

        ))}

      </div>

    </div>

  );
}
