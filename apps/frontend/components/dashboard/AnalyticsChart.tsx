"use client";

import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface AnalyticsChartProps {
  data: Array<Record<string, string | number>>;
  xKey: string;
  yKey: string;
  type?: "bar" | "line";
  height?: number;
}

export default function AnalyticsChart({ data, xKey, yKey, type = "bar", height = 260 }: AnalyticsChartProps) {
  if (data.length === 0) {
    return <p className="text-sm text-gray-500">No data yet.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      {type === "line" ? (
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={xKey} fontSize={12} />
          <YAxis fontSize={12} />
          <Tooltip />
          <Line type="monotone" dataKey={yKey} stroke="#000000" strokeWidth={2} dot={false} />
        </LineChart>
      ) : (
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={xKey} fontSize={12} />
          <YAxis fontSize={12} />
          <Tooltip />
          <Bar dataKey={yKey} fill="#000000" />
        </BarChart>
      )}
    </ResponsiveContainer>
  );
}
