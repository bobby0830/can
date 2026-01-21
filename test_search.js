const { Client } = require("@modelcontextprotocol/sdk/client/index.js");
const { StdioClientTransport } = require("@modelcontextprotocol/sdk/client/stdio.js");

async function testSearch() {
    const transport = new StdioClientTransport({
        command: "npx",
        args: ["-y", "pskill9/web-search"]
    });

    const client = new Client({
        name: "test-client",
        version: "1.0.0"
    }, {
        capabilities: {}
    });

    await client.connect(transport);
    console.log("Connected. Calling tool...");
    const result = await client.callTool({
        name: "search",
        arguments: { query: "AI events 2026" }
    });
    console.log("Raw Result:", JSON.stringify(result, null, 2));
    await transport.close();
}

testSearch().catch(console.error);
