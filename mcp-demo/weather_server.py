#!/usr/bin/env python3
"""
Weather MCP Server - Demo for MCP 101 Workshop

An MCP server that provides real weather data from OpenWeatherMap API.
Demonstrates both tools (actions) and resources (data) over stdio transport.
"""

import asyncio
import logging
import os
from collections.abc import Iterable
from typing import Any

import httpx
from pydantic import AnyUrl
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.lowlevel.helper_types import ReadResourceContents
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("weather-server")

# API Configuration
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
if not OPENWEATHER_API_KEY:
    logger.warning("OPENWEATHER_API_KEY environment variable not set!")
    logger.warning("Set it with: export OPENWEATHER_API_KEY='your_key_here'")
    logger.warning("Get a free key at: https://openweathermap.org/api")


async def get_weather(city: str, units: str = "metric") -> dict[str, Any]:
    """
    Fetch real weather data from OpenWeatherMap API.

    Args:
        city: City name (e.g., "San Francisco", "London")
        units: Temperature units - "metric" (Celsius) or "imperial" (Fahrenheit)

    Returns:
        Dictionary with weather data or error message
    """
    if not OPENWEATHER_API_KEY:
        return {
            "error": "OPENWEATHER_API_KEY environment variable not set. "
                     "Get a free key at https://openweathermap.org/api"
        }

    # OpenWeatherMap current weather API
    base_url = "http://api.openweathermap.org/data/2.5/weather"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                base_url,
                params={
                    "q": city,
                    "appid": OPENWEATHER_API_KEY,
                    "units": units
                }
            )
            response.raise_for_status()
            data = response.json()

            # Format the response
            temp_unit = "°C" if units == "metric" else "°F"

            return {
                "city": data["name"],
                "country": data["sys"]["country"],
                "condition": data["weather"][0]["main"],
                "description": data["weather"][0]["description"],
                "temperature": round(data["main"]["temp"]),
                "feels_like": round(data["main"]["feels_like"]),
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "units": units,
                "temp_unit": temp_unit
            }

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"City '{city}' not found. Please check the spelling."}
        elif e.response.status_code == 401:
            return {"error": "Invalid API key. Please check your OPENWEATHER_API_KEY."}
        else:
            return {"error": f"Weather API error: {e.response.status_code}"}

    except httpx.TimeoutException:
        return {"error": "Weather API request timed out. Please try again."}

    except Exception as e:
        logger.error(f"Failed to fetch weather: {e}")
        return {"error": f"Failed to fetch weather: {str(e)}"}


# Create the MCP server instance
app = Server("weather-server")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """
    List available tools.
    This function is called when clients want to know what tools are available.
    """
    return [
        types.Tool(
            name="get_weather",
            description="Get current weather conditions for any city worldwide. Use this tool whenever someone asks about weather, temperature, conditions, or climate in a specific location. Returns temperature, humidity, wind speed, and weather description.",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Name of the city (e.g., 'San Francisco', 'London', 'Tokyo')"
                    },
                    "units": {
                        "type": "string",
                        "description": "Temperature units: 'metric' (Celsius) or 'imperial' (Fahrenheit)",
                        "enum": ["metric", "imperial"],
                        "default": "metric"
                    }
                },
                "required": ["city"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """
    Handle tool calls.
    This function is called when a client wants to execute a tool.
    """
    if name != "get_weather":
        raise ValueError(f"Unknown tool: {name}")

    city = arguments.get("city")
    units = arguments.get("units", "metric")

    logger.info(f"Getting weather for {city} in {units} units")

    # Get weather data from API
    weather_data = await get_weather(city, units)

    # Format response
    if "error" in weather_data:
        response = f"❌ {weather_data['error']}"
    else:
        temp_unit = weather_data['temp_unit']
        response = (
            f"Weather for {weather_data['city']}, {weather_data['country']}:\n\n"
            f"Condition: {weather_data['condition']} ({weather_data['description']})\n"
            f"Temperature: {weather_data['temperature']}{temp_unit} "
            f"(feels like {weather_data['feels_like']}{temp_unit})\n"
            f"Humidity: {weather_data['humidity']}%\n"
            f"Wind Speed: {weather_data['wind_speed']} {'m/s' if units == 'metric' else 'mph'}"
        )

    return [types.TextContent(type="text", text=response)]


@app.list_resources()
async def list_resources() -> list[types.Resource]:
    """
    List available resources.
    Resources provide static or dynamic data that clients can read.
    """
    return [
        types.Resource(
            uri=AnyUrl("weather://api-guide"),
            name="Weather API Guide",
            description="Documentation for the Weather MCP Server API",
            mimeType="text/plain"
        )
    ]


@app.read_resource()
async def read_resource(uri: AnyUrl) -> Iterable[ReadResourceContents]:
    """
    Read a resource.
    This function is called when a client wants to access resource data.
    """
    logger.info(f"Reading resource: {uri}")

    # Compare as strings since uri is an AnyUrl object
    if str(uri) != "weather://api-guide":
        raise ValueError(f"Unknown resource: {uri}")

    # Return API documentation
    api_guide = """Weather MCP Server API Guide

TOOL: get_weather
-----------------
Get current weather data for any city worldwide.

Parameters:
  - city (required): City name (e.g., "San Francisco", "London", "Tokyo")
  - units (optional): Temperature units
    - "metric" (default): Celsius, m/s for wind
    - "imperial": Fahrenheit, mph for wind

Returns:
  - City name and country code
  - Weather condition and description
  - Current temperature and "feels like" temperature
  - Humidity percentage
  - Wind speed

Examples:
  get_weather(city="San Francisco")
  get_weather(city="London", units="imperial")
  get_weather(city="Tokyo", units="metric")

Data Source:
  OpenWeatherMap API (https://openweathermap.org)

Notes:
  - Real-time data updated every 10 minutes
  - Requires OPENWEATHER_API_KEY environment variable
  - Free tier: 60 calls/minute, 1,000,000 calls/month
"""

    return [ReadResourceContents(content=api_guide, mime_type="text/plain")]


async def main():
    """Run the weather MCP server using stdio transport."""
    logger.info("=" * 60)
    logger.info("Starting Weather MCP Server (stdio)")
    logger.info("=" * 60)

    if OPENWEATHER_API_KEY:
        logger.info("✓ OpenWeatherMap API key found")
    else:
        logger.warning("⚠ OPENWEATHER_API_KEY not set!")
        logger.warning("  Set it with: export OPENWEATHER_API_KEY='your_key_here'")
        logger.warning("  Get a free key at: https://openweathermap.org/api")
        logger.warning("  Server will return error messages for tool calls without API key")

    logger.info("=" * 60)
    logger.info("Configure Claude Desktop with:")
    logger.info('  "weather": {')
    logger.info('    "command": "python",')
    logger.info('    "args": ["path/to/weather_server.py"]')
    logger.info('  }')
    logger.info("=" * 60)

    # Run the server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
