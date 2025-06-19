# PowerShell MCP Server - Latest Features Update

## 🚀 Successfully Updated to Latest MCP Python SDK Features

Your MCP PowerShell server has been updated to use the latest features from the MCP Python SDK (v1.9.4). Here's what's new:

## ✨ New Features Added

### 1. **Modern FastMCP Server Configuration**
- Updated server metadata with better description
- Added proper dependencies declaration (`asyncio`, `psutil>=5.9.0`)
- Enhanced capabilities including resources, resource templates, and prompts

### 2. **Resource Support** 🆕
- **System Information Resource** (`system://info`): Real-time system metrics including CPU, memory, disk usage
- **Templates List Resource** (`templates://list`): Dynamic listing of available PowerShell templates
- **Template Access Resource** (`template://{template_name}`): Direct access to individual templates

### 3. **Prompt Support** 🆕
- **PowerShell Best Practices Prompt**: Guides users in creating well-structured PowerShell scripts
- **Troubleshooting Prompt**: Helps diagnose and fix PowerShell errors with context-aware suggestions

### 4. **Enhanced Context Support** 🆕
- **Progress Reporting**: Tools now support detailed progress tracking for long-running operations
- **Contextual Logging**: Better logging with info, warning, and error levels
- **Execution Metadata**: Detailed timing and performance metrics

### 5. **New Tools**
- **`run_powershell_with_progress`**: Enhanced PowerShell execution with detailed progress reporting and metadata
- Existing tools updated to support optional Context parameter for better logging

### 6. **Improved Type Safety & Error Handling**
- Fixed type hints throughout the codebase
- Better path handling with proper validation
- Enhanced error messages and debugging information

## 🛠️ Technical Improvements

### Dependencies Updated
```toml
dependencies = [
    "mcp>=1.9.0",      # Latest MCP SDK
    "psutil>=5.9.0",   # System monitoring
]
```

### Server Capabilities
```python
capabilities = {
    "tools": True,              # PowerShell execution tools
    "resources": True,          # System info & templates
    "resourceTemplates": True,  # Dynamic template access
    "prompts": True            # Script guidance & troubleshooting
}
```

## 📊 Available Tools (11 total)
1. `run_powershell` - Basic secure PowerShell execution
2. `run_powershell_with_progress` - Enhanced execution with progress reporting
3. `get_system_info` - System information retrieval
4. `get_running_services` - Windows services monitoring
5. `get_processes` - Process monitoring and management
6. `get_event_logs` - Windows event log access
7. `generate_script_from_template` - Template-based script generation
8. `generate_custom_script` - Dynamic script creation
9. `generate_intune_detection_script` - Intune detection script generation
10. `generate_intune_remediation_script` - Intune remediation script generation
11. `generate_intune_script_pair` - Complete Intune solution pairs

## 📄 Available Resources (3 total)
1. `system://info` - Real-time system information and metrics
2. `templates://list` - Available PowerShell script templates
3. `template://{template_name}` - Individual template content

## 💬 Available Prompts (2 total)
1. `powershell_best_practices` - Script development guidance
2. `troubleshoot_powershell_error` - Error diagnosis and resolution

## 🧪 Testing Results
✅ All features tested and working correctly:
- Server initialization successful
- All 11 tools accessible
- All 3 resources functional
- Both prompts operational
- PowerShell execution working with JSON output
- System information retrieval working
- Templates listing functional

## 🔄 Migration Notes
- Server version bumped from 0.1.0 to 0.2.0
- Python requirement updated to >=3.8 (from >=3.7)
- Added psutil dependency for enhanced system monitoring
- All existing functionality preserved and enhanced

## 🎯 Usage Examples

### Using the Enhanced PowerShell Tool
```python
# With progress reporting
result = await mcp.call_tool("run_powershell_with_progress", {
    "code": "Get-ComputerInfo | ConvertTo-Json",
    "timeout": 60
})
```

### Accessing Resources
```python
# Get system information
system_info = await mcp.read_resource("system://info")

# List available templates
templates = await mcp.read_resource("templates://list")

# Get specific template
template = await mcp.read_resource("template://basic_script")
```

### Using Prompts
```python
# Get best practices guidance
guidance = await mcp.get_prompt("powershell_best_practices", {
    "script_purpose": "Monitor disk space and send alerts"
})

# Get troubleshooting help
help_text = await mcp.get_prompt("troubleshoot_powershell_error", {
    "error_message": "Access denied when trying to read registry",
    "script_context": "Checking Windows version"
})
```

Your MCP server is now fully updated with the latest SDK features and ready for modern MCP client integration! 🎉
