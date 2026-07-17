import { API_BASE_URL, type ApiResponse } from "@/lib/auth";

export interface AdminOverviewData {
  total_students: number;
  active_students: number;
  total_problems: number;
  total_submissions: number;
  completed_assessments: number;
  average_score: number | null;
  active_hackathon: { id: string; title: string; start_time: string | null; end_time: string | null } | null;
  live_status: {
    active_students: number;
    running_executions: number;
    completed_submissions: number;
    failed_executions: number;
  };
}

export interface AdminAnalyticsData {
  average_score: number | null;
  problem_completion: Array<{
    problem_id: string;
    title: string;
    difficulty_multiplier: number;
    attempted_count: number;
    solved_count: number;
    completion_rate_percent: number;
  }>;
  score_distribution: Record<string, number>;
  execution_stats: {
    timeout_count: number;
    failed_executions: number;
    average_execution_time_ms: number | null;
  };
}

export interface ActivityEntry {
  id: string;
  user_id: string;
  activity_type: string;
  metadata: Record<string, unknown> | null;
  created_at: string;
}

export interface StudentOverviewData {
  profile: {
    full_name: string;
    college_name: string | null;
    department: string | null;
    semester: number | null;
  };
  hackathon_status: string;
  remaining_seconds: number | null;
  progress: {
    problems_attempted: number;
    problems_solved: number;
    total_problems: number;
    completion_percent: number;
  };
  rank: { rank: number | null; total_score: number | null; total_participants: number | null } | null;
}

export interface ScoreHistoryPoint {
  submission_id: string;
  problem_id: string;
  final_score: number | null;
  max_points: number;
  achieved_at: string;
}

export interface StudentLeaderboardData {
  hackathon_id: string;
  total_participants: number;
  own_rank: number | null;
  own_total_score: number | null;
  top_entries: Array<{ rank: number; user_id: string; full_name: string; total_score: number }>;
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

export function getAdminOverview() {
  return request<AdminOverviewData>("/dashboard/admin/overview", { method: "GET" });
}

export function getAdminAnalytics() {
  return request<AdminAnalyticsData>("/dashboard/admin/analytics", { method: "GET" });
}

export function getAdminActivity(limit = 20) {
  return request<{ items: ActivityEntry[] }>(`/dashboard/admin/activity?limit=${limit}`, {
    method: "GET",
  });
}

export function getStudentReport(userId: string) {
  return request<Record<string, unknown>>(`/dashboard/admin/reports/student/${userId}`, {
    method: "GET",
  });
}

export function getSubmissionReport() {
  return request<Record<string, unknown>>("/dashboard/admin/reports/submissions", {
    method: "GET",
  });
}

export function getHackathonSummary() {
  return request<Record<string, unknown>>("/dashboard/admin/reports/hackathon-summary", {
    method: "GET",
  });
}

export function getStudentOverview() {
  return request<StudentOverviewData>("/dashboard/student/overview", { method: "GET" });
}

export function getStudentPerformance() {
  return request<{ score_history: ScoreHistoryPoint[] }>("/dashboard/student/performance", {
    method: "GET",
  });
}

export function getStudentLeaderboard() {
  return request<StudentLeaderboardData>("/dashboard/student/leaderboard", { method: "GET" });
}
