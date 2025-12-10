"""Pydantic models for API request/response schemas."""

from pydantic import BaseModel
from typing import Optional
from enum import Enum


class MessageRole(str, Enum):
    """Role of a message in the conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    """A single message in the conversation."""
    role: MessageRole
    content: str


class ChatRequest(BaseModel):
    """Request body for the chat endpoint."""
    messages: list[Message]


class ToolCallInfo(BaseModel):
    """Information about a tool call made during the conversation."""
    name: str
    arguments: dict
    result: Optional[str] = None
    status: str = "pending"  # pending, success, error


class ChatResponse(BaseModel):
    """Response from the chat endpoint."""
    message: str
    tools_used: list[ToolCallInfo] = []


class HealthResponse(BaseModel):
    """Response from the health check endpoint."""
    status: str
    mcp_connected: bool
    llm_configured: bool


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None
