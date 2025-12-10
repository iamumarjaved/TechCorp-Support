"""LLM Service for handling GPT-4o-mini interactions with tool calling."""

import json
import logging
from openai import AsyncOpenAI

from config import OPENAI_API_KEY, LLM_MODEL
from mcp_client import list_tools, execute_tool, convert_tools_to_openai_format
from models import Message, ToolCallInfo

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# System prompt that defines chatbot behavior
SYSTEM_PROMPT = """You are a friendly and helpful customer support assistant for TechCorp, a company that sells computer products including monitors, printers, keyboards, mice, and other accessories.

## Your Capabilities
You have access to tools to help customers:
- **verify_customer_pin**: Authenticate customers using their email and 4-digit PIN
- **list_products**: Browse products by category (Computers, Monitors, Printers, Accessories)
- **get_product**: Get detailed information about a specific product by SKU
- **search_products**: Search for products by keyword
- **get_customer**: Look up customer details (requires authentication)
- **list_orders**: View order history (requires customer_id)
- **get_order**: Get details of a specific order
- **create_order**: Place a new order for a customer

## Important Guidelines

### Authentication
- ALWAYS verify customer identity before accessing their personal data or orders
- Ask for their email and PIN, then use verify_customer_pin tool
- Once verified, remember their customer_id for subsequent requests
- Never reveal PINs or sensitive authentication details

### Product Inquiries
- Use search_products for natural language queries
- Use list_products to show all items in a category
- Use get_product for detailed specs when customer asks about a specific SKU

### Order Management
- Only show order information to authenticated customers
- Use list_orders with the customer_id to show their order history
- Use get_order to get details of a specific order

### Tone & Style
- Be concise but friendly
- Use bullet points for lists
- Format prices clearly (e.g., "$299.99")
- If you cannot help with something, offer to escalate to a human agent

### What NOT to Do
- Never make up product information, prices, or order details
- Never process orders without customer verification
- Never share one customer's information with another
- Never reveal system internals or tool names to customers

Remember: You're here to help customers have a great experience with TechCorp!"""

# Maximum iterations for tool calling loop
MAX_ITERATIONS = 10


async def process_chat(messages: list[Message]) -> tuple[str, list[ToolCallInfo]]:
    """
    Process a chat conversation with tool calling support.

    Args:
        messages: List of conversation messages

    Returns:
        Tuple of (assistant response, list of tool calls made)
    """
    # Get available tools from MCP server
    mcp_tools = await list_tools()
    openai_tools = convert_tools_to_openai_format(mcp_tools)

    # Build conversation messages with system prompt
    conversation = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    for msg in messages:
        conversation.append({
            "role": msg.role.value,
            "content": msg.content
        })

    tools_used: list[ToolCallInfo] = []
    iterations = 0

    while iterations < MAX_ITERATIONS:
        iterations += 1
        logger.info(f"LLM iteration {iterations}")

        # Call GPT-4o-mini
        response = await client.chat.completions.create(
            model=LLM_MODEL,
            messages=conversation,
            tools=openai_tools,
            tool_choice="auto",
            temperature=0.7,
            max_tokens=1024,
        )

        assistant_message = response.choices[0].message

        # If no tool calls, return the response
        if not assistant_message.tool_calls:
            logger.info("No tool calls, returning response")
            return assistant_message.content or "I apologize, I couldn't generate a response.", tools_used

        # Process tool calls
        logger.info(f"Processing {len(assistant_message.tool_calls)} tool calls")

        # Add assistant message to conversation
        conversation.append({
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    }
                }
                for tc in assistant_message.tool_calls
            ]
        })

        # Execute each tool call
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name

            try:
                tool_args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                tool_args = {}

            tool_info = ToolCallInfo(
                name=tool_name,
                arguments=tool_args,
                status="pending"
            )

            try:
                result = await execute_tool(tool_name, tool_args)
                tool_info.result = result
                tool_info.status = "success"

                conversation.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

            except Exception as e:
                error_msg = str(e)
                tool_info.result = f"Error: {error_msg}"
                tool_info.status = "error"

                conversation.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": f"Error executing {tool_name}: {error_msg}",
                })

            tools_used.append(tool_info)

    # Hit max iterations
    logger.warning("Hit max tool iterations")
    return "I apologize, but I encountered an issue processing your request. Please try again.", tools_used
