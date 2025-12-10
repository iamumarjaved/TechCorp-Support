"use client";

import type { Message } from "@/types";
import { User, Bot, Wrench } from "lucide-react";

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"}`}>
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? "bg-blue-600" : "bg-gray-700"
        }`}
      >
        {isUser ? (
          <User className="w-5 h-5 text-white" />
        ) : (
          <Bot className="w-5 h-5 text-white" />
        )}
      </div>

      {/* Message Content */}
      <div className={`flex flex-col gap-1 max-w-[75%] ${isUser ? "items-end" : "items-start"}`}>
        {/* Tool calls indicator */}
        {message.toolCalls && message.toolCalls.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-1">
            {message.toolCalls.map((tool, idx) => (
              <span
                key={idx}
                className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs ${
                  tool.status === "success"
                    ? "bg-green-100 text-green-700"
                    : tool.status === "error"
                    ? "bg-red-100 text-red-700"
                    : "bg-yellow-100 text-yellow-700"
                }`}
              >
                <Wrench className="w-3 h-3" />
                {formatToolName(tool.name)}
              </span>
            ))}
          </div>
        )}

        {/* Message bubble */}
        <div
          className={`px-4 py-2 rounded-2xl ${
            isUser
              ? "bg-blue-600 text-white rounded-br-md"
              : "bg-gray-100 text-gray-900 rounded-bl-md"
          }`}
        >
          <div className="prose prose-sm max-w-none">
            <FormattedContent content={message.content} isUser={isUser} />
          </div>
        </div>

        {/* Timestamp */}
        <span className="text-xs text-gray-400">
          {formatTime(message.timestamp)}
        </span>
      </div>
    </div>
  );
}

function FormattedContent({ content, isUser }: { content: string; isUser: boolean }) {
  // Simple markdown-like formatting
  const lines = content.split("\n");

  return (
    <div className={`space-y-1 ${isUser ? "text-white" : "text-gray-900"}`}>
      {lines.map((line, idx) => {
        // Bold text
        const formatted = line.replace(
          /\*\*(.+?)\*\*/g,
          '<strong class="font-semibold">$1</strong>'
        );

        // Bullet points
        if (line.startsWith("- ")) {
          return (
            <div key={idx} className="flex gap-2">
              <span>•</span>
              <span dangerouslySetInnerHTML={{ __html: formatted.slice(2) }} />
            </div>
          );
        }

        // Empty lines
        if (line.trim() === "") {
          return <div key={idx} className="h-2" />;
        }

        return (
          <p
            key={idx}
            dangerouslySetInnerHTML={{ __html: formatted }}
          />
        );
      })}
    </div>
  );
}

function formatToolName(name: string): string {
  return name
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function formatTime(date: Date): string {
  return new Intl.DateTimeFormat("en-US", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  }).format(date);
}
