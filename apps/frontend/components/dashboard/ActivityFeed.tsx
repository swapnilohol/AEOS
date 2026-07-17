interface ActivityEntry {
  id: string;
  activity_type: string;
  created_at: string;
}

interface ActivityFeedProps {
  entries: ActivityEntry[];
  isLoading?: boolean;
  error?: string | null;
}

const ACTIVITY_LABELS: Record<string, string> = {
  LOGIN: "logged in",
  SUBMISSION_CREATED: "submitted a solution",
  SCORE_CALCULATED: "received a score",
};

export default function ActivityFeed({ entries, isLoading = false, error = null }: ActivityFeedProps) {
  if (isLoading) return <p className="text-sm text-gray-500">Loading activity...</p>;
  if (error) return <p className="text-sm text-red-600">{error}</p>;
  if (entries.length === 0) return <p className="text-sm text-gray-500">No recent activity.</p>;

  return (
    <ul className="space-y-2 text-sm">
      {entries.map((entry) => (
        <li key={entry.id} className="flex justify-between border-b pb-1">
          <span>{ACTIVITY_LABELS[entry.activity_type] ?? entry.activity_type}</span>
          <span className="text-gray-400">{new Date(entry.created_at).toLocaleTimeString()}</span>
        </li>
      ))}
    </ul>
  );
}
