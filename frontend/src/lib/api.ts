const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000"

export type AgentStepType =
  | "plan"
  | "tool_call"
  | "tool_result"
  | "subagent_start"
  | "subagent_end"
  | "text"
  | "error"

export interface AgentStep {
  type: AgentStepType
  content: string
  metadata?: Record<string, unknown>
}

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  steps?: AgentStep[]
  timestamp: number
}

export async function sendMessage(
  message: string,
  threadId?: string,
  model?: string,
): Promise<{ thread_id: string; message: string }> {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 30000)

  try {
    const res = await fetch(`${API_URL}/api/v1/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, thread_id: threadId, model, stream: true }),
      signal: controller.signal,
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }))
      throw new Error(err.detail || "Request failed")
    }
    return res.json()
  } finally {
    clearTimeout(timeout)
  }
}

export function streamViaWebSocket(
  message: string,
  threadId: string,
  onStep: (step: AgentStep) => void,
  onError: (error: string) => void,
  onDone: () => void,
  model?: string,
): () => void {
  const url = `${WS_URL}/api/v1/ws/${threadId}`
  let socket: WebSocket | null = null
  let reconnectAttempts = 0
  const maxReconnectAttempts = 3

  function connect() {
    socket = new WebSocket(url)

    const connectionTimeout = setTimeout(() => {
      if (socket?.readyState === WebSocket.CONNECTING) {
        socket.close()
        onError("Connection timed out")
      }
    }, 10000)

    socket.onopen = () => {
      clearTimeout(connectionTimeout)
      reconnectAttempts = 0
      socket!.send(JSON.stringify({ message, model }))
    }

    socket.onmessage = (event) => {
      try {
        const step: AgentStep = JSON.parse(event.data)
        if (step.type === "text" && step.content === "[DONE]") {
          onDone()
          return
        }
        onStep(step)
      } catch {
        onError("Failed to parse server response")
      }
    }

    socket.onerror = () => {
      clearTimeout(connectionTimeout)
      onError("WebSocket connection failed")
    }

    socket.onclose = () => {
      clearTimeout(connectionTimeout)
      onDone()
    }
  }

  connect()

  return () => {
    if (socket) {
      socket.close()
      socket = null
    }
  }
}
