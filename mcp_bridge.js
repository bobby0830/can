const { Client } = require("@modelcontextprotocol/sdk/client/index.js");
const { StdioClientTransport } = require("@modelcontextprotocol/sdk/client/stdio.js");
const express = require("express");
const { search } = require("duck-duck-scrape");

const app = express();

async function runSearch(query) {
    console.log(`[Bridge] Starting Search for query: ${query}`);
    
    // 1. 優先嘗試 DuckDuckGo (免費且穩定)
    try {
        console.log("[Bridge] Trying DuckDuckGo...");
        // 請求更多結果
        const searchResults = await search(query, { safeSearch: 0 });
        if (searchResults && searchResults.results && searchResults.results.length > 0) {
            console.log(`[Bridge] Found ${searchResults.results.length} results via DuckDuckGo`);
            return searchResults.results.slice(0, 20).map(r => ({
                title: r.title,
                link: r.url,
                snippet: r.description
            }));
        }
    } catch (err) {
        console.error("[Bridge] DuckDuckGo error:", err.message);
    }

    // 2. 備案：MCP pskill9/web-search
    try {
        console.log("[Bridge] Falling back to MCP...");
        const transport = new StdioClientTransport({
            command: "npx",
            args: ["-y", "pskill9/web-search"]
        });
        const client = new Client({ name: "bridge-client", version: "1.0.0" }, { capabilities: {} });
        await client.connect(transport);
        
        const tools = await client.listTools();
        const toolName = tools.tools.find(t => t.name === 'search')?.name || "search";
        
        const result = await client.callTool({
            name: toolName, 
            arguments: { 
                query: query,
                count: 20 // 嘗試請求 20 條結果
            }
        });

        await transport.close();

        if (result.content && Array.isArray(result.content)) {
            const textContent = result.content.find(c => c.type === 'text')?.text;
            if (textContent && textContent !== "[]") {
                const parsed = JSON.parse(textContent);
                const items = (parsed && parsed.organic) ? parsed.organic : (Array.isArray(parsed) ? parsed : [parsed]);
                console.log(`[Bridge] Found ${items.length} results via MCP`);
                return items;
            }
        }
    } catch (e) {
        console.log("[Bridge] MCP Search failed:", e.message);
    }

    return [];
}

app.get("/search", async (req, res) => {
    try {
        const query = req.query.q;
        console.log(`[API] Request for: ${query}`);
        const results = await runSearch(query);
        res.json(results);
    } catch (err) {
        console.error("[API] Error:", err);
        res.status(500).json({ error: err.message });
    }
});

app.listen(8000, "0.0.0.0", () => {
    console.log("MCP Bridge running on http://localhost:8000");
});
