// Chat message types
export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  toolCalls?: ToolCallInfo[];
  timestamp: Date;
}

export interface ToolCallInfo {
  name: string;
  arguments: Record<string, unknown>;
  result?: string;
  status: "pending" | "success" | "error";
}

// API request/response types
export interface ChatRequest {
  messages: {
    role: "user" | "assistant" | "system";
    content: string;
  }[];
}

export interface ChatResponse {
  message: string;
  toolsUsed: ToolCallInfo[];
}

// MCP Tool type (simplified from SDK)
export interface MCPTool {
  name: string;
  description?: string;
  inputSchema: {
    type: string;
    properties?: Record<string, unknown>;
    required?: string[];
  };
}

// OpenAI compatible tool type
export interface OpenAITool {
  type: "function";
  function: {
    name: string;
    description: string;
    parameters: Record<string, unknown>;
  };
}

// Customer session (for tracking authenticated users)
export interface CustomerSession {
  customerId: string;
  email: string;
  name: string;
  verified: boolean;
}
