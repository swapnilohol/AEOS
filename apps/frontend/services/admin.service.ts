import { API_BASE_URL, type ApiResponse } from "@/lib/auth";

export interface ActiveHackathonSummary {
  id: string;
  title: string;
  start_time: string | null;
  end_time: string | null;
  problem_count: number;
}

export interface SubmissionStatusBreakdown {
  pending: number;
  running: number;
  completed: number;
  failed: number;
}

export interface TopScoreEntry {
  user_id: string;
  full_name: string;
  total_points: number;
}

export interface AdminDashboardData {
  total_students: number;
  total_problems: number;
  total_submissions: number;
  total_violations: number;
  active_hackathon: ActiveHackathonSummary | null;
  submission_status_breakdown: SubmissionStatusBreakdown;
  top_scores: TopScoreEntry[];
}

async function request<T>(path: string, init?: RequestInit): Promise<ApiResponse<T>> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  const body = (await response.json()) as ApiResponse<T>;
  if (!response.ok) {
    throw new Error(body.message || "Request failed");
  }
  return body;
}

export function getAdminDashboard() {
  return request<AdminDashboardData>("/admin/dashboard", { method: "GET" });
}
