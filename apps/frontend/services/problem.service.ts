import { API_BASE_URL, type ApiResponse } from "@/lib/auth";

export interface Problem {
  id: string;
  hackathon_id: string;
  title: string;
  description: string;
  max_score: number;
  order_index: number;
  created_at: string;
  updated_at: string;
}

export interface ProblemListData {
  items: Problem[];
  total: number;
  page: number;
  page_size: number;
}

export interface CreateProblemInput {
  hackathon_id: string;
  title: string;
  description: string;
  max_score?: number;
  order_index?: number;
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

export function listProblems(page = 1, pageSize = 20) {
  return request<ProblemListData>(`/problems?page=${page}&page_size=${pageSize}`, {
    method: "GET",
  });
}

export function createProblem(input: CreateProblemInput) {
  return request<Problem>("/problems", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function deleteProblem(problemId: string) {
  return request<null>(`/problems/${problemId}`, { method: "DELETE" });
}
