"use client"

import ReactMarkdown from "react-markdown"
import type { Message, AgentStep } from "@/lib/api"
import { AgentSteps } from "./AgentSteps"

interface Props {
  message: Message
}

export function ChatMessage({ message }: Props) {
  const isUser = message.role === "user"

  return (
    <div className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-sm font-bold mt-1">
          DA
        </div>
      )}

      <div className={`max-w-[80%] ${isUser ? "order-1" : "order-2"}`}>
        {isUser ? (
          <div className="bg-blue-600/20 text-blue-100 rounded-2xl rounded-tr-sm px-4 py-2.5">
            <p className="whitespace-pre-wrap">{message.content}</p>
          </div>
        ) : (
          <div className="space-y-2">
            {message.steps && message.steps.length > 0 && (
              <AgentSteps steps={message.steps} />
            )}
            {message.content && (
              <div className="bg-gray-800/50 rounded-2xl rounded-tl-sm px-4 py-3 text-gray-100 prose prose-invert prose-sm max-w-none">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
            )}
            {!message.content && !message.steps?.length && (
              <div className="flex gap-1.5 px-4 py-3">
                <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            )}
          </div>
        )}
      </div>

      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-gray-600 flex items-center justify-center text-sm font-bold mt-1">
          U
        </div>
      )}
    </div>
  )
}
