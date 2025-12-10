import { NextRequest, NextResponse } from "next/server";
import type { ChatRequest } from "@/types";

// FastAPI backend URL
const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function POST(req: NextRequest) {
  try {
    const body: ChatRequest = await req.json();

    // Forward request to FastAPI backend
    const response = await fetch(`${BACKEND_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Unknown error" }));
      return NextResponse.json(
        { error: error.detail || `Backend error: ${response.status}` },
        { status: response.status }
      );
    }

    const data = await response.json();

    // Transform response to match frontend expectations
    return NextResponse.json({
      message: data.message,
      toolsUsed: data.tools_used || [],
    });

  } catch (error) {
    console.error("[API] Error:", error);

    // Check if backend is unreachable
    if (error instanceof TypeError && error.message.includes("fetch")) {
      return NextResponse.json(
        { error: "Backend service unavailable. Please ensure the FastAPI server is running." },
        { status: 503 }
      );
    }

    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
