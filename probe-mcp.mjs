// Quick script to probe the MCP server and discover available tools
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

const MCP_SERVER_URL = "https://vipfapwm3x.us-east-1.awsapprunner.com/mcp";

async function probeMCPServer() {
  console.log("Connecting to MCP server:", MCP_SERVER_URL);

  const transport = new StreamableHTTPClientTransport(new URL(MCP_SERVER_URL));
  const client = new Client({
    name: "mcp-probe",
    version: "1.0.0",
  });

  try {
    await client.connect(transport);
    console.log("\n Connected successfully!\n");

    // List available tools
    console.log("=== AVAILABLE TOOLS ===");
    const { tools } = await client.listTools();
    for (let i = 0; i < tools.length; i++) {
      const tool = tools[i];
      console.log(`\n${i + 1}. ${tool.name}`);
      console.log(`   Description: ${tool.description}`);
      console.log(`   Input Schema: ${JSON.stringify(tool.inputSchema, null, 2)}`);
    }

    // List available resources
    console.log("\n\n=== AVAILABLE RESOURCES ===");
    try {
      const { resources } = await client.listResources();
      for (let i = 0; i < resources.length; i++) {
        const resource = resources[i];
        console.log(`\n${i + 1}. ${resource.name}`);
        console.log(`   URI: ${resource.uri}`);
        console.log(`   Description: ${resource.description}`);
      }
    } catch (e) {
      console.log("No resources available or error:", e.message);
    }

    // List available prompts
    console.log("\n\n=== AVAILABLE PROMPTS ===");
    try {
      const { prompts } = await client.listPrompts();
      for (let i = 0; i < prompts.length; i++) {
        const prompt = prompts[i];
        console.log(`\n${i + 1}. ${prompt.name}`);
        console.log(`   Description: ${prompt.description}`);
      }
    } catch (e) {
      console.log("No prompts available or error:", e.message);
    }

    await client.close();
  } catch (error) {
    console.error("Error connecting to MCP server:", error);
  }
}

probeMCPServer();
