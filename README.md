# MCP 101 — An Introduction to the Model Context Protocol

Materials from a Mirantis webinar introducing the **Model Context Protocol (MCP)** —
the open standard that lets AI agents safely access real-world tools and data.

This repo contains the slide deck and a small, working **weather MCP server** you can
clone, run, and use as a template for building your own.

- 📑 **[`Mirantis_MCP_Webinar_2026.pdf`](Mirantis_MCP_Webinar_2026.pdf)** — the full slides
- 🛠️ **[`mcp-demo/`](mcp-demo/)** — the live-demo code (see its [README](mcp-demo/README.md))

---

## What is MCP?

MCP is an open standard that connects LLM-based agents to external tools and data through
**one common interface**, instead of a bespoke integration per tool.

Without MCP, *N* agents and *M* tools mean *N × M* fragile, custom integrations. With MCP,
everyone speaks one protocol, so you can add or swap tools without touching agent code,
share servers across agents, and keep access discovery-based and scoped.

A useful mental model:

```
  Agent (Host)  ──MCP / JSON-RPC 2.0──►  MCP Server  ──►  Tools & Data
  e.g. Claude Code,                      your code        APIs, DBs, files
  GitHub Copilot
```

**MCP is** a standardized protocol for LLM-to-tool communication, with built-in discovery
and capability negotiation, and a pluggable, multi-agent-friendly architecture.

**MCP is *not*** an agent framework, a hosted service (you run the servers), a replacement
for your backend, limited to one model vendor, or a way to expose *unlimited* tools —
context still matters.

> **Tools vs. Skills:** MCP **tools** give an agent new *capabilities* (the ability to act).
> Agent **skills** give it *knowledge* (file-based instructions on how to work). Skills tell
> the agent *what* to do; MCP tools let it actually *do* it.

---

## The six primitives

| | Primitive | What it is | Example |
|---|---|---|---|
| **Server-side** | **Tools** | Callable functions / actions | `get_weather(city, units)` |
| | **Resources** | Readable data (read-only) | `weather://api-guide` |
| | **Prompts** | Reusable templates with variables | `weather_advisor(destination)` |
| **Client-side** | **Sampling** | Server can request an LLM completion *via the client* | (no server API key needed) |
| | **Roots** | Client tells the server its filesystem boundaries | scope server to a workspace |
| | **Elicitation** | Server pauses to ask the user for structured input | request a missing parameter |

The webinar focuses on the two you reach for first: **tools** and **resources**.

---

## The demo: a weather MCP server

[`mcp-demo/`](mcp-demo/) is a ~250-line Python server that wraps the
[OpenWeatherMap](https://openweathermap.org/) API and exposes:

- a **tool** — `get_weather(city, units)` for live conditions
- a **resource** — `weather://api-guide` with API documentation
- over the **stdio** transport (simple, local, recommended for desktop use)

Weather is just a familiar, safe example — the same pattern wraps *any* backend: ticketing
systems, databases, Kubernetes, monitoring, internal business APIs.

### Quick start

```bash
cd mcp-demo
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Free key from https://openweathermap.org/appid
export OPENWEATHER_API_KEY="your_api_key_here"

python test_server.py            # sanity check
```

The API key is always read from the **environment**, never hard-coded or committed.
The demo ships a `.mcp.json`, so Claude Code picks the server up automatically when run from
`mcp-demo/`. You can also explore it with no agent at all using the **MCP Inspector**:

```bash
npx @modelcontextprotocol/inspector ./.venv/bin/python weather_server.py
```

Full setup, Claude Desktop / Claude Code config, and an Inspector walkthrough of the raw
JSON-RPC messages are in the **[demo README](mcp-demo/README.md)**.

---

## Key takeaways

- An MCP server can wrap **any** external service or API behind one protocol.
- **Configuration**, not code, connects servers to clients — add capabilities by editing config.
- **User consent** is a *client* feature (e.g. Claude Desktop), not a protocol requirement.
- Prefer **several small, specific tools** over one giant generic one — better tool selection,
  less context bloat, easier permission scoping. Rule of thumb: ~5–10 well-designed tools per server.
- **Tool composition** is where MCP shines: one request → multiple coordinated tool calls.
- Practice **least privilege** and **log tool calls** for auditability.

---

## Next steps & resources

1. Clone this repo and get the weather server running (~30 min).
2. Test with the **MCP Inspector** before wiring it into a client.
3. Browse the registry for pre-built servers, then build your own.

- MCP docs & getting started — <https://modelcontextprotocol.io/>
- Specification — <https://spec.modelcontextprotocol.io/>
- Server registry — <https://github.com/modelcontextprotocol/servers>
- MCP Inspector — <https://github.com/modelcontextprotocol/inspector>
- Python SDK — <https://github.com/modelcontextprotocol/python-sdk>
- TypeScript SDK — <https://github.com/modelcontextprotocol/typescript-sdk>

---

*Presented by Mirantis. Slides and demo shared for educational purposes — the weather server
is a teaching pattern, not production code.*
