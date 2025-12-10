// Comprehensive test script for chat API

const API_URL = "http://localhost:3001/api/chat";

let conversationHistory = [];

async function chat(message) {
  console.log("\n" + "=".repeat(60));
  console.log("USER:", message);
  console.log("=".repeat(60));

  conversationHistory.push({ role: "user", content: message });

  const response = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages: conversationHistory }),
  });

  if (!response.ok) {
    console.error("Error:", response.status, await response.text());
    return null;
  }

  const data = await response.json();

  if (data.toolsUsed?.length > 0) {
    console.log("\nTOOLS USED:", data.toolsUsed.map(t => `${t.name} (${t.status})`).join(", "));
  }

  console.log("\nASSISTANT:", data.message);

  conversationHistory.push({ role: "assistant", content: data.message });

  return data;
}

async function runTests() {
  console.log("\n" + "#".repeat(60));
  console.log("# TEST 1: Product Search");
  console.log("#".repeat(60));
  conversationHistory = [];
  await chat("I'm looking for a gaming keyboard");

  console.log("\n" + "#".repeat(60));
  console.log("# TEST 2: Customer Authentication & Order History");
  console.log("#".repeat(60));
  conversationHistory = [];
  await chat("My email is michellejames@example.com and PIN is 1520. Show me my orders.");

  console.log("\n" + "#".repeat(60));
  console.log("# TEST 3: Product Details by SKU");
  console.log("#".repeat(60));
  conversationHistory = [];
  await chat("Tell me about product MON-0001");

  console.log("\n" + "#".repeat(60));
  console.log("# TEST 4: Multi-turn Conversation");
  console.log("#".repeat(60));
  conversationHistory = [];
  await chat("What printers do you have?");
  await chat("Which one is cheapest?");

  console.log("\n" + "#".repeat(60));
  console.log("# TEST 5: Wrong PIN (Security Test)");
  console.log("#".repeat(60));
  conversationHistory = [];
  await chat("My email is donaldgarcia@example.net and my PIN is 0000");

  console.log("\n" + "#".repeat(60));
  console.log("# ALL TESTS COMPLETED");
  console.log("#".repeat(60));
}

runTests().catch(console.error);
