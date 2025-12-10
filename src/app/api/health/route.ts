import { NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_URL}/health`);
    const data = await response.json();

    return NextResponse.json({
      frontend: "healthy",
      backend: data,
    });
  } catch {
    return NextResponse.json({
      frontend: "healthy",
      backend: { status: "unreachable" },
    });
  }
}
