// Test script for chat API

const API_URL = "http://localhost:3001/api/chat";

async function testChat(message) {
  console.log("\n========================================");
  console.log("USER:", message);
  console.log("========================================");

  const response = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      messages: [{ role: "user", content: message }],
    }),
  });

  if (!response.ok) {
    console.error("Error:", response.status, await response.text());
    return;
  }

  const data = await response.json();

  console.log("\nTOOLS USED:", data.toolsUsed?.map(t => t.name).join(", ") || "None");
  console.log("\nASSISTANT:", data.message);
  console.log("========================================\n");

  return data;
}

async function main() {
  // Test 1: Search products
  await testChat("Show me your monitors");

  // Test 2: Customer verification
  await testChat("I want to check my orders. My email is donaldgarcia@example.net and my PIN is 7912");
}

main().catch(console.error);
