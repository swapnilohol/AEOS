import { API_BASE_URL, type ApiResponse } from "@/lib/auth";

export interface StudentRecord {
  id: string;
  user_id: string;
  full_name: string;
  email: string;
  is_active: boolean;
  student_id: string;
  college_name: string | null;
  department: string | null;
  semester: number | null;
  graduation_year: number | null;
  phone_number: string | null;
  skills: string | null;
  resume_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface StudentListData {
  items: StudentRecord[];
  total: number;
  page: number;
  page_size: number;
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

export function listStudents(search = "", page = 1, pageSize = 20) {
  const query = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
  if (search) query.set("search", search);
  return request<StudentListData>(`/students?${query.toString()}`, { method: "GET" });
}
