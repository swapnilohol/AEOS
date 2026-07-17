import { apiRequest } from "@/lib/api";

export async function login(
  email: string,
  password: string
) {
  const formData = new URLSearchParams();

  formData.append(
    "username",
    email
  );

  formData.append(
    "password",
    password
  );

  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/auth/login`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/x-www-form-urlencoded",
      },
      body: formData,
    }
  );

  const data =
    await response.json();

  if (data.access_token) {
    localStorage.setItem(
      "token",
      data.access_token
    );
  }

  return data;
}

export async function getMe() {
  return apiRequest("/auth/me");
}
