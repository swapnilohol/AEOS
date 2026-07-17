import { API_BASE_URL, type ApiResponse } from "@/lib/auth";

export interface Draft {
  id: string;
  user_id: string;
  problem_id: string;
  language: string;
  code: string;
  created_at: string;
  updated_at: string;
}

export interface EditorSessionData {
  id: string;
  user_id: string;
  problem_id: string;
  language: string;
  status: "ACTIVE" | "ENDED";
  started_at: string;
  last_active_at: string;
  ended_at: string | null;
}

export interface ProblemSummary {
  id: string;
  title: string;
  description: string;
  max_score: number;
}

export interface WorkspaceData {
  problem: ProblemSummary;
  student_full_name: string;
  remaining_seconds: number | null;
  draft: Draft | null;
  active_session: EditorSessionData | null;
  latest_submission_status: string | null;
}

export interface SubmissionPrepared {
  submission_id: string;
  problem_id: string;
  status: string;
  submitted_at: string;
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

export function getWorkspace(problemId: string) {
  return request<WorkspaceData>(`/editor/problems/${problemId}/workspace`, { method: "GET" });
}

export function saveDraft(problemId: string, language: string, code: string) {
  return request<Draft>(`/editor/problems/${problemId}/draft`, {
    method: "PUT",
    body: JSON.stringify({ language, code }),
  });
}

export function startSession(problemId: string, language: string) {
  return request<EditorSessionData>(`/editor/problems/${problemId}/sessions`, {
    method: "POST",
    body: JSON.stringify({ language }),
  });
}

export function heartbeatSession(sessionId: string) {
  return request<EditorSessionData>(`/editor/sessions/${sessionId}/heartbeat`, {
    method: "PATCH",
  });
}

export function endSession(sessionId: string) {
  return request<EditorSessionData>(`/editor/sessions/${sessionId}/end`, { method: "POST" });
}

export function submitSolution(problemId: string, code?: string, language?: string) {
  return request<SubmissionPrepared>(`/editor/problems/${problemId}/submit`, {
    method: "POST",
    body: JSON.stringify({ code, language }),
  });
}
