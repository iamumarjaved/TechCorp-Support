"""Test script for FastAPI backend."""

import asyncio
import httpx

BACKEND_URL = "http://localhost:8000"


async def test_health():
    """Test health endpoint."""
    print("\n" + "=" * 60)
    print("TEST: Health Check")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")


async def test_tools():
    """Test tools endpoint."""
    print("\n" + "=" * 60)
    print("TEST: List Tools")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/tools")
        data = response.json()
        print(f"Available tools: {[t['name'] for t in data['tools']]}")


async def test_chat(message: str, context: list = None):
    """Test chat endpoint."""
    print("\n" + "=" * 60)
    print(f"USER: {message}")
    print("=" * 60)

    messages = context or []
    messages.append({"role": "user", "content": message})

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{BACKEND_URL}/chat",
            json={"messages": messages}
        )

        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return None

        data = response.json()

        if data.get("tools_used"):
            print(f"\nTools used: {[t['name'] for t in data['tools_used']]}")

        print(f"\nASSISTANT: {data['message']}")

        messages.append({"role": "assistant", "content": data["message"]})
        return messages


async def run_tests():
    """Run all tests."""
    # Health check
    await test_health()

    # List tools
    await test_tools()

    # Test 1: Product search
    print("\n" + "#" * 60)
    print("# TEST 1: Search Products")
    print("#" * 60)
    await test_chat("Show me your monitors")

    # Test 2: Customer authentication
    print("\n" + "#" * 60)
    print("# TEST 2: Customer Authentication & Orders")
    print("#" * 60)
    await test_chat("My email is donaldgarcia@example.net and PIN is 7912. Show me my orders.")

    # Test 3: Wrong PIN
    print("\n" + "#" * 60)
    print("# TEST 3: Wrong PIN (Security)")
    print("#" * 60)
    await test_chat("My email is donaldgarcia@example.net and PIN is 0000")

    # Test 4: Multi-turn conversation
    print("\n" + "#" * 60)
    print("# TEST 4: Multi-turn Conversation")
    print("#" * 60)
    context = await test_chat("What printers do you have?")
    if context:
        await test_chat("Which one is cheapest?", context)

    print("\n" + "#" * 60)
    print("# ALL TESTS COMPLETED")
    print("#" * 60)


if __name__ == "__main__":
    asyncio.run(run_tests())
