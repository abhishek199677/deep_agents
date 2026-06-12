import type { Metadata } from "next"
import "./globals.css"
import { ErrorBoundary } from "@/components/ErrorBoundary"

export const metadata: Metadata = {
  title: "Deep Agents",
  description: "Autonomous AI agents with planning, research, and subagents",
  icons: { icon: "/favicon.ico" },
  openGraph: {
    title: "Deep Agents",
    description: "Autonomous AI agents with planning, research, and subagents",
  },
  robots: { index: false, follow: false },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <ErrorBoundary>{children}</ErrorBoundary>
      </body>
    </html>
  )
}
