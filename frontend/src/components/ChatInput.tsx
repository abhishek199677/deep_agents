"use client"

import { useState, useRef, KeyboardEvent } from "react"

interface Props {
  onSend: (message: string) => void
  disabled: boolean
  onReset: () => void
}

export function ChatInput({ onSend, disabled, onReset }: Props) {
  const [input, setInput] = useState("")
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSend = () => {
    if (!input.trim() || disabled) return
    onSend(input.trim())
    setInput("")
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto"
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleInput = () => {
    const el = textareaRef.current
    if (el) {
      el.style.height = "auto"
      el.style.height = Math.min(el.scrollHeight, 200) + "px"
    }
  }

  return (
    <div className="border-t border-gray-800 bg-gray-900/80 backdrop-blur-sm">
      <div className="max-w-4xl mx-auto px-4 py-3">
        <div className="flex items-end gap-2 bg-gray-800 rounded-2xl border border-gray-700 px-4 py-2 focus-within:border-blue-500/50 transition-colors">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            onInput={handleInput}
            placeholder="Ask anything — research, code, analysis..."
            rows={1}
            disabled={disabled}
            className="flex-1 bg-transparent text-gray-100 placeholder-gray-500 resize-none outline-none text-sm py-1.5 max-h-[200px]"
          />
          <div className="flex items-center gap-1.5">
            <button
              onClick={onReset}
              disabled={disabled}
              className="p-2 text-gray-500 hover:text-gray-300 transition-colors disabled:opacity-30 text-xs"
              title="New conversation"
            >
              ↺
            </button>
            <button
              onClick={handleSend}
              disabled={!input.trim() || disabled}
              className="p-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 text-white rounded-xl transition-all disabled:opacity-40"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>
        <p className="text-[10px] text-gray-600 text-center mt-2">
          Deep Agents — planning, research, subagents, and file system
        </p>
      </div>
    </div>
  )
}
