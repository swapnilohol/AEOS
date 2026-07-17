import { API_BASE_URL, type AccessTokenData, type ApiResponse, type AuthUser } from "@/lib/auth";

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

export function login(email: string, password: string) {
  return request<AccessTokenData>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function refresh() {
  return request<AccessTokenData>("/auth/refresh", { method: "POST" });
}

export function logout() {
  return request<null>("/auth/logout", { method: "POST" });
}

export function me() {
  return request<AuthUser>("/auth/me", { method: "GET" });
}

export function changePassword(currentPassword: string, newPassword: string) {
  return request<null>("/auth/change-password", {
    method: "POST",
    body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
  });
}

export function createStudent(fullName: string, email: string, password: string) {
  return request<AuthUser>("/auth/admin/create-student", {
    method: "POST",
    body: JSON.stringify({ full_name: fullName, email, password }),
  });
}
