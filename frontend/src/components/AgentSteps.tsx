"use client"

import { useState } from "react"
import type { AgentStep } from "@/lib/api"

interface Props {
  steps: AgentStep[]
}

const stepIcons: Record<string, string> = {
  plan: "📋",
  tool_call: "🔧",
  tool_result: "📎",
  subagent_start: "🤖",
  subagent_end: "✅",
  error: "❌",
}

export function AgentSteps({ steps }: Props) {
  const [expanded, setExpanded] = useState(false)

  if (steps.length === 0) return null

  const visible = expanded ? steps : steps.slice(-3)

  return (
    <div className="bg-gray-800/30 rounded-xl border border-gray-700/50 overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-3 py-2 text-xs text-gray-400 hover:text-gray-300 transition-colors"
      >
        <span>{steps.length > 0 ? `${steps.length} step${steps.length > 1 ? "s" : ""}` : "Steps"}</span>
        <span>{expanded ? "▲" : "▼"}</span>
      </button>

      <div className="px-3 pb-2 space-y-1.5">
        {visible.map((step, i) => (
          <div key={i} className="flex items-start gap-2 text-xs">
            <span className="flex-shrink-0 mt-0.5">{stepIcons[step.type] || "•"}</span>
            <div className="min-w-0 flex-1">
              <p className="text-gray-300 truncate">
                {step.type === "tool_call"
                  ? `Called: ${step.metadata?.tool || "tool"}`
                  : step.type === "plan"
                    ? `Planning: ${step.content.slice(0, 80)}`
                    : step.type === "tool_result"
                      ? `Result: ${step.content.slice(0, 80)}`
                      : step.type === "error"
                        ? `Error: ${step.content.slice(0, 80)}`
                        : step.content.slice(0, 100)}
              </p>
            </div>
          </div>
        ))}
        {!expanded && steps.length > 3 && (
          <p className="text-xs text-gray-500 text-center pt-1">
            +{steps.length - 3} more
          </p>
        )}
      </div>
    </div>
  )
}
