interface StatsCardProps {
  label: string;
  value: string | number | null;
  isLoading?: boolean;
  error?: string | null;
}

export default function StatsCard({ label, value, isLoading = false, error = null }: StatsCardProps) {
  return (
    <div className="rounded border p-4 text-center">
      {isLoading ? (
        <p className="text-2xl font-semibold text-gray-300">...</p>
      ) : error ? (
        <p className="text-sm text-red-600">Error</p>
      ) : (
        <p className="text-2xl font-semibold">{value ?? "-"}</p>
      )}
      <p className="text-sm text-gray-500">{label}</p>
    </div>
  );
}
