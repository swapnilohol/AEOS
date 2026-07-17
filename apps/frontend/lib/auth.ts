export interface AuthUser {
  id: string;
  full_name: string;
  email: string;
  role: "ADMIN" | "STUDENT";
  is_active: boolean;
  last_login_at: string | null;
}

export interface AccessTokenData {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: AuthUser;
}

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T | null;
  errors: string[] | null;
}

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";
