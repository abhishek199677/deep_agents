import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "Deep Agents",
  description: "Autonomous AI agents with planning, research, and subagents",
  icons: { icon: "/favicon.ico" },
  openGraph: {
    title: "Deep Agents",
    description: "Autonomous AI agents with planning, research, and subagents",
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
