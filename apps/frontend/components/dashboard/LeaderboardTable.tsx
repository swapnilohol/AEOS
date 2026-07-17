interface LeaderboardRow {
  rank: number | null;
  user_id: string;
  full_name: string;
  total_score: number;
}

interface LeaderboardTableProps {
  entries: LeaderboardRow[];
  highlightUserId?: string;
}

export default function LeaderboardTable({ entries, highlightUserId }: LeaderboardTableProps) {
  if (entries.length === 0) {
    return <p className="text-sm text-gray-500">No leaderboard data yet.</p>;
  }

  return (
    <table className="w-full text-left text-sm">
      <thead>
        <tr className="border-b">
          <th className="py-2">Rank</th>
          <th className="py-2">Student</th>
          <th className="py-2">Total Score</th>
        </tr>
      </thead>
      <tbody>
        {entries.map((entry) => (
          <tr
            key={entry.user_id}
            className={`border-b ${entry.user_id === highlightUserId ? "bg-gray-50 font-medium" : ""}`}
          >
            <td className="py-2">#{entry.rank ?? "-"}</td>
            <td className="py-2">{entry.full_name}</td>
            <td className="py-2">{entry.total_score}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
