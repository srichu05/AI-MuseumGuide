"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Loader2, BookOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { chatMessage, ChatResponse, Artifact } from "@/lib/api";
import { cn } from "@/lib/utils";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: ChatResponse["sources"];
  intent?: string;
}

interface ChatPanelProps {
  sessionId?: string;
  artifact?: Artifact | null;
  className?: string;
}

export function ChatPanel({ sessionId: initialSession, artifact, className }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Welcome! Upload an artifact image or select a work, then ask me about its creator, history, location, or exhibitions.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(initialSession);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (initialSession) setSessionId(initialSession);
  }, [initialSession]);

  const send = async () => {
    const q = input.trim();
    if (!q || loading) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", content: q }]);
    setLoading(true);
    try {
      const res = await chatMessage({
        query: q,
        session_id: sessionId,
        artifact_id: artifact?.artifact_id,
      });
      setSessionId(res.session_id);
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: res.answer,
          sources: res.sources,
          intent: res.intent,
        },
      ]);
    } catch {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: "Sorry, I couldn't process that request. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={cn("flex h-full flex-col rounded-xl border border-border bg-card", className)}>
      <div className="border-b border-border px-4 py-3">
        <h3 className="font-display text-lg">Museum Guide</h3>
        {artifact && (
          <p className="text-xs text-muted-foreground">Context: {artifact.name}</p>
        )}
      </div>
      <div className="flex-1 space-y-4 overflow-y-auto p-4" style={{ maxHeight: "420px" }}>
        {messages.map((m, i) => (
          <div key={i} className={cn("flex", m.role === "user" ? "justify-end" : "justify-start")}>
            <div
              className={cn(
                "max-w-[85%] rounded-lg px-4 py-3 text-sm",
                m.role === "user" ? "bg-accent text-accent-foreground" : "bg-muted"
              )}
            >
              <p>{m.content}</p>
              {m.sources && m.sources.length > 0 && (
                <div className="mt-3 border-t border-border/50 pt-2">
                  <p className="mb-1 flex items-center gap-1 text-xs font-medium text-muted-foreground">
                    <BookOpen className="h-3 w-3" /> Sources
                  </p>
                  <ul className="space-y-1">
                    {m.sources.map((s, j) => (
                      <li key={j} className="text-xs text-muted-foreground">• {s.title}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" /> Thinking...
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <div className="flex gap-2 border-t border-border p-4">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="Ask about the artwork..."
          disabled={loading}
        />
        <Button onClick={send} disabled={loading || !input.trim()} size="icon" className="shrink-0">
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
