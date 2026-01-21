const { Client } = require("@modelcontextprotocol/sdk/client/index.js");
const { StdioClientTransport } = require("@modelcontextprotocol/sdk/client/stdio.js");

async function listTools() {
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
    const tools = await client.listTools();
    console.log("Available tools:", JSON.stringify(tools, null, 2));
    await transport.close();
}

listTools().catch(console.error);
