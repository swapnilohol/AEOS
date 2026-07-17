import { NextRequest, NextResponse } from "next/server";

const PROTECTED_PREFIXES: Record<string, string> = {
  "/admin": "/admin/login",
  "/student": "/login",
};

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const matchedPrefix = Object.keys(PROTECTED_PREFIXES).find(
    (prefix) => pathname.startsWith(prefix) && !pathname.endsWith("/login"),
  );

  if (!matchedPrefix) {
    return NextResponse.next();
  }

  const hasAccessToken = request.cookies.has("access_token");
  if (!hasAccessToken) {
    const loginPath = PROTECTED_PREFIXES[matchedPrefix];
    const loginUrl = new URL(loginPath, request.url);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/admin/:path*", "/student/:path*"],
};
