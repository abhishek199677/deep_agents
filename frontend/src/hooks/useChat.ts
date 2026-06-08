"use client"

import { useState, useCallback, useRef } from "react"
import type { Message, AgentStep } from "@/lib/api"
import { sendMessage, streamViaWebSocket } from "@/lib/api"

function generateId(): string {
  return Math.random().toString(36).substring(2, 11)
}

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [threadId, setThreadId] = useState<string | null>(null)
  const threadIdRef = useRef<string | null>(null)

  const send = useCallback(async (input: string) => {
    if (!input.trim() || isLoading) return

    setIsLoading(true)
    const userMsg: Message = {
      id: generateId(),
      role: "user",
      content: input,
      timestamp: Date.now(),
    }
    setMessages((prev) => [...prev, userMsg])

    const assistantId = generateId()
    const assistantMsg: Message = {
      id: assistantId,
      role: "assistant",
      content: "",
      steps: [],
      timestamp: Date.now(),
    }
    setMessages((prev) => [...prev, assistantMsg])

    let tid = threadIdRef.current || crypto.randomUUID()
    if (!threadIdRef.current) {
      threadIdRef.current = tid
      setThreadId(tid)
    }

    let resolvedText = ""
    const accumulatedSteps: AgentStep[] = []

    const onStep = (step: AgentStep) => {
      if (step.type === "text") {
        resolvedText = step.content
        setMessages((prev) =>
          prev.map((m) => (m.id === assistantId ? { ...m, content: resolvedText } : m)),
        )
      } else {
        accumulatedSteps.push(step)
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId ? { ...m, steps: [...accumulatedSteps] } : m,
          ),
        )
      }
    }

    const onError = (error: string) => {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? { ...m, content: `Error: ${error}` }
            : m,
        ),
      )
    }

    const onDone = () => {
      setIsLoading(false)
    }

    try {
      streamViaWebSocket(input, tid, onStep, onError, onDone)
    } catch (err: unknown) {
      onError(err instanceof Error ? err.message : "Unknown error")
      setIsLoading(false)
    }
  }, [isLoading])

  const reset = useCallback(() => {
    setMessages([])
    setThreadId(null)
    threadIdRef.current = null
  }, [])

  return { messages, isLoading, threadId, send, reset }
}
