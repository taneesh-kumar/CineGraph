import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CineGraph - Graph Recommendations & Movie Trend Analytics",
  description:
    "A hybrid NoSQL platform pairing Neo4j graph recommendations with MonetDB columnar analytics.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-neutral-950 text-neutral-100 antialiased">
        {children}
      </body>
    </html>
  );
}
