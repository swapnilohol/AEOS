import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Elite Internship Hackathon Platform",
  description: "Newton Institute of Science and Technology",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
