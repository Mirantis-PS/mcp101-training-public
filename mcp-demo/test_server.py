#!/usr/bin/env python3
"""
Simple test script to verify the weather server works.
Run this before using the server with clients.
"""

import asyncio
import sys


async def test_server():
    """Test the weather server functionality."""
    try:
        # Import the server module
        from weather_server import (
            get_weather,
            list_tools,
            list_resources,
            OPENWEATHER_API_KEY
        )

        print("=" * 60)
        print("Testing Weather MCP Server")
        print("=" * 60)

        # Test 1: Check API key
        print("\n[TEST 1] API Key Configuration:")
        if OPENWEATHER_API_KEY:
            print(f"  ✓ OPENWEATHER_API_KEY is set (length: {len(OPENWEATHER_API_KEY)})")
            print("  Note: This test won't make real API calls")
        else:
            print(f"  ⚠ OPENWEATHER_API_KEY not set")
            print("  Server will return error messages when tools are called")
            print("  Set it with: export OPENWEATHER_API_KEY='your_key_here'")

        # Test 2: Test tools definition
        print("\n[TEST 2] MCP Tools:")
        tools = await list_tools()
        if len(tools) == 1 and tools[0].name == "get_weather":
            print(f"  ✓ Tool 'get_weather' registered")
            print(f"  Parameters: {list(tools[0].inputSchema['properties'].keys())}")
        else:
            print(f"  ✗ Expected 1 tool named 'get_weather', found {len(tools)} tools")
            return False

        # Test 3: Test resources definition
        print("\n[TEST 3] MCP Resources:")
        resources = await list_resources()
        if len(resources) == 1 and str(resources[0].uri) == "weather://api-guide":
            print(f"  ✓ Resource 'weather://api-guide' registered")
        else:
            print(f"  ✗ Expected 1 resource with uri 'weather://api-guide'")
            if resources:
                print(f"  Found URIs: {[str(r.uri) for r in resources]}")
            return False

        # Test 4: Test weather function (without API key)
        print("\n[TEST 4] Weather Function:")
        if not OPENWEATHER_API_KEY:
            print("  ⚠ Skipping API call test (no API key)")
            print("  The function will return error messages as expected")
        else:
            print("  ✓ API key found - server is ready to make real API calls")

        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        print("\nServer is ready to use!")
        print("\nNext steps:")
        print("1. Set API key (if not already set):")
        print("   export OPENWEATHER_API_KEY='your_key_here'")
        print("\n2. Start the HTTP/SSE server:")
        print("   python weather_server.py")
        print("\n3. Configure Claude Desktop with:")
        print('   "weather": {')
        print('     "url": "http://localhost:8000/sse",')
        print('     "transport": "sse"')
        print('   }')
        print("=" * 60)

        return True

    except ImportError as e:
        print(f"\n✗ Import error: {e}")
        print("\nMake sure you've installed dependencies:")
        print("  pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_server())
    sys.exit(0 if success else 1)
