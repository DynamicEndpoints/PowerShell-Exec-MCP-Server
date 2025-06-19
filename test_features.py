#!/usr/bin/env python3
"""
Test script to verify the updated MCP PowerShell server features.
"""

import asyncio
import sys
import os

# Add the server directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from server import mcp

async def test_server_features():
    """Test the new server features."""
    print("🧪 Testing MCP PowerShell Server Features")
    print("=" * 50)
    
    # Test 1: List available tools
    print("\n1️⃣  Available Tools:")
    tools = await mcp.list_tools()
    for tool in tools:
        print(f"   ✅ {tool.name}: {tool.description}")
    
    # Test 2: List available resources
    print("\n2️⃣  Available Resources:")
    resources = await mcp.list_resources()
    for resource in resources:
        print(f"   📄 {resource.uri}: {resource.name}")
    
    # Test 3: List available prompts
    print("\n3️⃣  Available Prompts:")
    prompts = await mcp.list_prompts()
    for prompt in prompts:
        print(f"   💬 {prompt.name}: {prompt.description}")
    
    # Test 4: Test a resource
    print("\n4️⃣  Testing System Info Resource:")
    try:
        system_info_result = await mcp.read_resource("system://info")
        # system_info_result is an iterable of ReadResourceContents
        system_info_list = list(system_info_result)
        if system_info_list:
            system_info = system_info_list[0].text if hasattr(system_info_list[0], 'text') else str(system_info_list[0])
            print(f"   ✅ System info retrieved ({len(system_info)} characters)")
            print("   📊 Sample data:", system_info[:200] + "..." if len(system_info) > 200 else system_info)
        else:
            print("   ❌ No system info data returned")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Test templates list resource
    print("\n5️⃣  Testing Templates List Resource:")
    try:
        templates_result = await mcp.read_resource("templates://list")
        templates_list = list(templates_result)
        if templates_list:
            templates = templates_list[0].text if hasattr(templates_list[0], 'text') else str(templates_list[0])
            print(f"   ✅ Templates list retrieved ({len(templates)} characters)")
            print("   📝 Sample data:", templates[:200] + "..." if len(templates) > 200 else templates)
        else:
            print("   ❌ No templates data returned")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 6: Test a simple PowerShell command
    print("\n6️⃣  Testing Simple PowerShell Command:")
    try:
        result = await mcp.call_tool("run_powershell", {"code": "Get-Date | ConvertTo-Json", "timeout": 30})
        # result is a sequence of Content objects
        result_list = list(result)
        if result_list:
            result_text = result_list[0].text if hasattr(result_list[0], 'text') else str(result_list[0])
            print(f"   ✅ PowerShell command executed successfully")
            print(f"   📋 Result: {result_text[:200]}...")
        else:
            print("   ❌ No result returned")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n🎉 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_server_features())
