"""FastAPI backend for Customer Support Chatbot."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import HOST, PORT, DEBUG, CORS_ORIGINS, OPENAI_API_KEY, MCP_SERVER_URL
from models import ChatRequest, ChatResponse, HealthResponse, ErrorResponse
from mcp_client import get_mcp_client, close_mcp_client, list_tools
from llm_service import process_chat

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown."""
    # Startup
    logger.info("Starting Customer Support Chatbot Backend...")
    logger.info(f"MCP Server URL: {MCP_SERVER_URL}")
    logger.info(f"LLM API Key configured: {'Yes' if OPENAI_API_KEY else 'No'}")

    # Pre-connect to MCP server
    try:
        await get_mcp_client()
        tools = await list_tools()
        logger.info(f"Connected to MCP server. Available tools: {[t['name'] for t in tools]}")
    except Exception as e:
        logger.error(f"Failed to connect to MCP server: {e}")

    yield

    # Shutdown
    logger.info("Shutting down...")
    await close_mcp_client()


# Create FastAPI app
app = FastAPI(
    title="Customer Support Chatbot API",
    description="Backend API for TechCorp Customer Support Chatbot",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    mcp_connected = False
    try:
        await get_mcp_client()
        mcp_connected = True
    except Exception:
        pass

    return HealthResponse(
        status="healthy",
        mcp_connected=mcp_connected,
        llm_configured=bool(OPENAI_API_KEY),
    )


@app.get("/tools")
async def get_tools():
    """Get list of available MCP tools."""
    try:
        tools = await list_tools()
        return {"tools": tools}
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse, responses={500: {"model": ErrorResponse}})
async def chat(request: ChatRequest):
    """
    Process a chat message and return assistant response.

    The endpoint handles:
    - Multi-turn conversations
    - Automatic tool calling via MCP
    - Customer authentication and order management
    """
    try:
        logger.info(f"Chat request with {len(request.messages)} messages")

        # Process chat with LLM and tool calling
        response_text, tools_used = await process_chat(request.messages)

        logger.info(f"Chat response generated. Tools used: {[t.name for t in tools_used]}")

        return ChatResponse(
            message=response_text,
            tools_used=tools_used,
        )

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
    )
