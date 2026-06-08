"use client"

import { useEffect, useRef } from "react"
import { useChat } from "@/hooks/useChat"
import { ChatMessage } from "./ChatMessage"
import { ChatInput } from "./ChatInput"

export function Chat() {
  const { messages, isLoading, send, reset } = useChat()
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  return (
    <div className="flex flex-col h-screen bg-gray-950">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3 border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center text-xs font-bold">
            DA
          </div>
          <h1 className="text-sm font-semibold text-gray-100">Deep Agents</h1>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-gray-600 bg-gray-800 px-2 py-0.5 rounded-full border border-gray-700">
            Production
          </span>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 py-6 space-y-4">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full min-h-[60vh] text-center">
              <div className="w-16 h-16 rounded-2xl bg-blue-600/20 flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
                </svg>
              </div>
              <h2 className="text-lg font-semibold text-gray-300 mb-2">
                Autonomous AI Agents
              </h2>
              <p className="text-sm text-gray-500 max-w-md">
                Planning, web research, subagents, file system, and persistent memory — all powered by LangGraph.
              </p>
              <div className="grid grid-cols-2 gap-2 mt-6 w-full max-w-md">
                {[
                  "Research the latest AI papers",
                  "Write a LangGraph agent workflow",
                  "Compare AWS vs GCP for ML",
                  "Analyze this codebase structure",
                ].map((q) => (
                  <button
                    key={q}
                    onClick={() => send(q)}
                    className="text-left text-xs text-gray-400 bg-gray-800/50 hover:bg-gray-800 border border-gray-700/50 rounded-xl px-3 py-2.5 transition-colors"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} />
          ))}
          <div ref={bottomRef} />
        </div>
      </div>

      {/* Input */}
      <ChatInput onSend={send} disabled={isLoading} onReset={reset} />
    </div>
  )
}
