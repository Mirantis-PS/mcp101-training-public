# Weather MCP Server - Demo

A simple MCP server demonstrating the Model Context Protocol with real weather data.

## What This Demonstrates

- **Tool**: `get_weather(city, units)` - Fetches current weather for any city
- **Resource**: `weather://api-guide` - API documentation
- **Transport**: stdio (simple, local communication)

## Quick Setup

### 1. Get an OpenWeatherMap API Key

1. Visit <https://openweathermap.org/appid>
2. Sign up (free tier: 60 calls/min)
3. Copy your API key

### 2. Install Dependencies

```bash
cd mcp-demo
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set Your API Key (System-Wide Recommended)

**Add to your shell profile** for permanent setup:

```bash
# macOS/Linux: Add to ~/.zshrc or ~/.bashrc
echo 'export OPENWEATHER_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

Windows PowerShell:

```powershell
# Add to your PowerShell profile
[System.Environment]::SetEnvironmentVariable('OPENWEATHER_API_KEY', 'your_api_key_here', 'User')
```

**Or set temporarily** (current session only):

```bash
export OPENWEATHER_API_KEY="your_api_key_here"  # macOS/Linux
```

This keeps your API key out of config files.

### 4. Test the Server (Optional)

```bash
python test_server.py
```

Should show:

- ✓ API key found
- ✓ Tool 'get_weather' registered
- ✓ Resource 'weather://api-guide' registered

## Using with Claude Desktop

### 1. Find Your Config File

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### 2. Add the Server

Edit the config file (use your actual absolute path):

```json
{
  "mcpServers": {
    "weather": {
      "command": "/absolute/path/to/mcp-demo/.venv/bin/python",
      "args": ["/absolute/path/to/mcp-demo/weather_server.py"],
      "env": {
        "OPENWEATHER_API_KEY": "${OPENWEATHER_API_KEY}"
      }
    }
  }
}
```

**Note**:

- Use the `.venv` Python so the `mcp`/`httpx` dependencies resolve (on macOS/Windows: `.venv\Scripts\python.exe`)
- Replace the paths with your actual path. Find it with: `pwd` (in the mcp-demo directory)
- The API key is read from your system environment (set in step 3)
- This keeps credentials out of config files (safe to share/commit)

### 3. Restart Claude Desktop

Completely quit and restart Claude Desktop.

### 4. Test It

Look for the 🔌 icon in Claude Desktop, then try:

- "What's the weather in Tokyo?"
- "Compare weather in London and Paris"
- "Show me the weather API documentation"

## Using with Claude Code

This project already ships a `.mcp.json` in the `mcp-demo` directory, so Claude Code
picks up the server automatically when you run it from here:

```json
{
  "mcpServers": {
    "weather": {
      "command": "./.venv/bin/python",
      "args": ["./weather_server.py"],
      "env": {
        "OPENWEATHER_API_KEY": "${OPENWEATHER_API_KEY}"
      }
    }
  }
}
```

Alternatively, add it explicitly with the CLI:

```bash
claude mcp add weather ./.venv/bin/python ./weather_server.py
```

The API key is read from your system environment (recommended for security), so
make sure `OPENWEATHER_API_KEY` is exported (see step 3 above). Run `claude` from
the `mcp-demo` directory, then `/mcp` to confirm the `weather` server is connected.

## Demo with MCP Inspector

The MCP Inspector is a developer tool that lets you interact with MCP servers directly—no AI client needed. It's the best way to understand how the MCP protocol works.

### Starting the Inspector

```bash
cd mcp-demo
source .venv/bin/activate
npx @modelcontextprotocol/inspector ./.venv/bin/python weather_server.py
```

This starts:

- A proxy server on `localhost:6277`
- A web UI at `http://localhost:6274`

The browser should open automatically. If not, copy the URL with the auth token from the terminal.

### Understanding the MCP Protocol

The Inspector shows you the raw MCP JSON-RPC messages. Here's what happens under the hood:

#### 1. Initialization

When a client connects, the server announces its capabilities:

```json
{
  "capabilities": {
    "tools": {},
    "resources": {}
  },
  "serverInfo": {
    "name": "weather-server",
    "version": "1.28.0"
  }
}
```

> The `version` mirrors the installed `mcp` SDK version, so it will vary depending on what `pip` resolved from `requirements.txt`.

#### 2. Listing Tools

Click **"List Tools"** in the Inspector. The client sends:

```json
{
  "method": "tools/list",
  "params": {}
}
```

Server responds with available tools:

```json
{
  "tools": [
    {
      "name": "get_weather",
      "description": "Get current weather conditions for any city...",
      "inputSchema": {
        "type": "object",
        "properties": {
          "city": { "type": "string" },
          "units": { "type": "string", "enum": ["metric", "imperial"] }
        },
        "required": ["city"]
      }
    }
  ]
}
```

#### 3. Calling a Tool

In the **Tools** tab, select `get_weather` and enter:

- `city`: "Paris"
- `units`: "metric"

Click **"Run Tool"**. The client sends:

```json
{
  "method": "tools/call",
  "params": {
    "name": "get_weather",
    "arguments": {
      "city": "Paris",
      "units": "metric"
    }
  }
}
```

Server responds with results:

```json
{
  "content": [
    {
      "type": "text",
      "text": "Weather for Paris, FR:\n\nCondition: Clear (clear sky)\nTemperature: 8°C (feels like 6°C)\nHumidity: 71%\nWind Speed: 4.12 m/s"
    }
  ]
}
```

#### 4. Listing Resources

Click **"List Resources"** in the Resources tab:

```json
{
  "method": "resources/list",
  "params": {}
}
```

Response:

```json
{
  "resources": [
    {
      "uri": "weather://api-guide",
      "name": "Weather API Guide",
      "description": "Documentation for the Weather MCP Server API",
      "mimeType": "text/plain"
    }
  ]
}
```

#### 5. Reading a Resource

Click on `weather://api-guide` to read it:

```json
{
  "method": "resources/read",
  "params": {
    "uri": "weather://api-guide"
  }
}
```

Response contains the resource content:

```json
{
  "contents": [
    {
      "uri": "weather://api-guide",
      "mimeType": "text/plain",
      "text": "Weather MCP Server API Guide\n\nTOOL: get_weather\n..."
    }
  ]
}
```

### Key MCP Concepts Demonstrated

| Concept | Example | Purpose |
|---------|---------|---------|
| **Tools** | `get_weather` | Actions the AI can perform |
| **Resources** | `weather://api-guide` | Data the AI can read |
| **inputSchema** | JSON Schema for city/units | Validates tool arguments |
| **Content types** | `text`, `image`, `embedded` | Structured responses |
| **Transport** | stdio | How client/server communicate |

### Inspector Tips

- **Watch the History tab** to see all messages exchanged
- **Try invalid inputs** to see error handling
- **Check server logs** in the terminal for debugging
- Use **Ctrl+C** in terminal to stop the inspector

## Understanding the Code

The server is ~250 lines showing the essential MCP pattern:

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server

app = Server("weather-server")

@app.list_tools()
async def list_tools():
    return [{"name": "get_weather", ...}]

@app.call_tool()
async def call_tool(name, arguments):
    # Call external API, return results
    return [{"type": "text", "text": result}]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, ...)
```

Key concepts:

- **stdio transport**: Simple stdin/stdout communication
- **Tools**: Functions the AI can call
- **Resources**: Data the AI can read
- **External APIs**: Real weather data from OpenWeatherMap

## Resources

- [MCP Docs](https://modelcontextprotocol.io/)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Server Registry](https://github.com/modelcontextprotocol/servers)
