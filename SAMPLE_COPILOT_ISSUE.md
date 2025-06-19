# Sample Issue: Implementing PowerShell Module Management Tool

**This is a sample issue demonstrating best practices for Copilot-optimized issue creation.**

## 🤖 Copilot Task Overview

**Task Type:** ✅ Feature Implementation

**Priority Level:** 🟡 High (Important feature)

## 📝 Task Description

**Clear Task Statement:**
Implement a new MCP tool that allows querying, installing, and managing PowerShell modules through the MCP interface.

**Detailed Requirements:**
1. Add a tool to list installed PowerShell modules with version information
2. Add a tool to search for available modules in the PowerShell Gallery
3. Add a tool to install specific PowerShell modules (with appropriate safety checks)
4. Include proper error handling for module installation failures
5. Support filtering and searching capabilities

**Success Criteria:**
- [ ] Can list all installed modules with name, version, and description
- [ ] Can search PowerShell Gallery for modules by name or description
- [ ] Can safely install modules with validation and error handling
- [ ] All operations include progress reporting via Context
- [ ] Tools are properly registered and accessible via MCP

## 📍 Code Context for Copilot

**Primary Files to Modify:**
- [x] `server.py` - Main MCP server implementation

**Existing Code to Reference:**
```python
# Function/class names to examine:
# - execute_powershell() - for PowerShell execution patterns
# - run_powershell_with_progress() - for progress reporting patterns
# - validate_powershell_code() - for security validation patterns
```

**Code Patterns to Follow:**
- Error handling pattern: Try-catch with proper MCP exceptions
- Logging pattern: Use ctx.info(), ctx.error() when available
- Type hints: Use proper typing throughout
- Docstrings: Follow existing docstring format
- Async patterns: Use async/await for I/O operations

## 🛠️ Implementation Specifications

**Function Signatures:**

```python
@mcp.tool()
async def get_installed_modules(
    name_filter: Optional[str] = None,
    ctx: Optional[Context] = None
) -> str:
    """
    Get list of installed PowerShell modules.
    
    Args:
        name_filter: Optional filter to search for specific module names
        ctx: MCP context for logging and progress reporting
        
    Returns:
        JSON string containing module information
        
    Raises:
        RuntimeError: When PowerShell command fails
    """

@mcp.tool()
async def search_powershell_gallery(
    search_term: str,
    max_results: Optional[int] = 20,
    ctx: Optional[Context] = None
) -> str:
    """
    Search PowerShell Gallery for available modules.
    
    Args:
        search_term: Term to search for in module names and descriptions
        max_results: Maximum number of results to return (default 20)
        ctx: MCP context for logging and progress reporting
        
    Returns:
        JSON string containing search results
        
    Raises:
        ValueError: When search_term is empty
        RuntimeError: When PowerShell Gallery search fails
    """

@mcp.tool()
async def install_powershell_module(
    module_name: str,
    scope: str = "CurrentUser",
    force: bool = False,
    ctx: Optional[Context] = None
) -> str:
    """
    Install a PowerShell module from the PowerShell Gallery.
    
    Args:
        module_name: Name of the module to install
        scope: Installation scope (CurrentUser or AllUsers)
        force: Whether to force installation if module exists
        ctx: MCP context for logging and progress reporting
        
    Returns:
        Installation result message
        
    Raises:
        ValueError: When module_name is invalid or scope is not allowed
        RuntimeError: When installation fails
    """
```

**PowerShell Commands to Use:**
```powershell
# List installed modules
Get-InstalledModule | Select-Object Name, Version, Description, Author | ConvertTo-Json

# Search PowerShell Gallery
Find-Module -Name "*search_term*" | Select-Object Name, Version, Description, Author, CompanyName | ConvertTo-Json

# Install module
Install-Module -Name "ModuleName" -Scope CurrentUser -Force
```

**Input/Output Specifications:**
- **Input format:** String parameters for module names, search terms
- **Output format:** JSON strings containing structured module information
- **Error conditions:** Invalid module names, installation failures, network issues

## 🧪 Testing Requirements

**Test Cases to Implement:**
```python
async def test_get_installed_modules():
    """Test listing installed modules"""
    # Test case 1: List all modules
    result = await mcp.call_tool("get_installed_modules", {})
    assert "PSReadLine" in result  # Common module that should exist
    
    # Test case 2: Filter by name
    result = await mcp.call_tool("get_installed_modules", {"name_filter": "PSReadLine"})
    assert "PSReadLine" in result

async def test_search_powershell_gallery():
    """Test PowerShell Gallery search"""
    # Test case 1: Valid search
    result = await mcp.call_tool("search_powershell_gallery", {"search_term": "PowerShellGet"})
    assert "PowerShellGet" in result
    
    # Test case 2: Empty search term should fail
    try:
        await mcp.call_tool("search_powershell_gallery", {"search_term": ""})
        assert False, "Should have failed"
    except ValueError:
        pass

async def test_install_powershell_module():
    """Test module installation"""
    # Test case 1: Install test module (use a safe, small module)
    result = await mcp.call_tool("install_powershell_module", {
        "module_name": "PSScriptAnalyzer",
        "scope": "CurrentUser"
    })
    assert "successfully installed" in result.lower()
```

**Manual Testing Steps:**
1. Test listing modules: Call `get_installed_modules` without filter
2. Test filtering: Call `get_installed_modules` with name filter "PowerShell"
3. Test search: Call `search_powershell_gallery` with search term "Azure"
4. Test installation: Call `install_powershell_module` with a safe module name

## 📋 Step-by-Step Implementation Guide

**Phase 1: Planning**
- [x] Review existing PowerShell execution patterns in `execute_powershell()`
- [x] Identify required PowerShell commands
- [x] Plan security validation for module installation

**Phase 2: Core Implementation**
- [ ] Implement `get_installed_modules()` function
- [ ] Implement `search_powershell_gallery()` function  
- [ ] Implement `install_powershell_module()` function
- [ ] Add input validation for all functions
- [ ] Add comprehensive error handling

**Phase 3: Security & Safety**
- [ ] Add validation to prevent installation of dangerous modules
- [ ] Ensure proper scope restrictions (default to CurrentUser)
- [ ] Add timeout handling for long-running installations
- [ ] Validate module names against injection attacks

**Phase 4: Integration & Testing**
- [ ] Register tools with MCP server using `@mcp.tool()` decorators
- [ ] Test integration with MCP protocol
- [ ] Add progress reporting using Context parameter
- [ ] Add comprehensive logging

## 🔍 Quality Checklist

**Code Quality:**
- [ ] Follows existing code style in `server.py`
- [ ] Has comprehensive type hints
- [ ] Has clear, descriptive variable names
- [ ] Has proper error handling with specific exceptions
- [ ] Has informative log messages using ctx.info()/ctx.error()
- [ ] Has complete docstrings following existing format

**Security Considerations:**
- [ ] Input validation prevents PowerShell injection
- [ ] Module installation restricted to safe scopes
- [ ] Proper timeout handling prevents hanging operations
- [ ] Safe PowerShell command construction

**Performance Considerations:**
- [ ] Async operations for all PowerShell executions
- [ ] Proper resource cleanup
- [ ] Reasonable timeouts for network operations
- [ ] Efficient JSON parsing and formatting

## 🤖 Copilot-Specific Instructions

**Coding Style:**
Use the exact same patterns as `execute_powershell()` and `run_powershell_with_progress()` functions. Follow the FastMCP conventions used throughout `server.py`.

**Error Handling Pattern to Follow:**
```python
async def new_tool_function(param: str, ctx: Optional[Context] = None) -> str:
    """Tool description"""
    try:
        if ctx:
            await ctx.info(f"Starting operation with {param}")
        
        # Validation
        if not param or not param.strip():
            raise ValueError("Parameter cannot be empty")
            
        # Build PowerShell command
        ps_command = f"PowerShell-Command -Parameter '{param}' | ConvertTo-Json"
        
        # Execute with progress reporting
        if ctx:
            await ctx.info("Executing PowerShell command...")
            
        result = await execute_powershell(ps_command, timeout=120, ctx=ctx)
        
        if ctx:
            await ctx.info("Operation completed successfully")
            
        return result
        
    except Exception as e:
        if ctx:
            await ctx.error(f"Operation failed: {str(e)}")
        raise
```

**Security Pattern for Module Installation:**
```python
# Validate module name (no special characters that could cause injection)
if not re.match(r'^[a-zA-Z0-9._-]+$', module_name):
    raise ValueError("Invalid module name format")

# Validate scope
if scope not in ["CurrentUser", "AllUsers"]:
    raise ValueError("Scope must be 'CurrentUser' or 'AllUsers'")

# Build safe PowerShell command
ps_command = f"Install-Module -Name '{module_name}' -Scope {scope} -Force:${str(force).lower()} -Confirm:$false"
```

**Integration Points:**
- Add all three functions to `server.py` after the existing tools
- Use `@mcp.tool()` decorator for each function
- Follow the existing import patterns at the top of the file
- Use the same timeout and error handling patterns as existing tools

## 📎 Reference Materials

**Existing Code Examples:**
- PowerShell execution: `execute_powershell()` function
- Progress reporting: `run_powershell_with_progress()` function
- Input validation: `validate_powershell_code()` function
- Error handling: All existing tool implementations

**PowerShell Documentation:**
- Get-InstalledModule: https://docs.microsoft.com/powershell/module/powershellget/get-installedmodule
- Find-Module: https://docs.microsoft.com/powershell/module/powershellget/find-module
- Install-Module: https://docs.microsoft.com/powershell/module/powershellget/install-module

**Security Considerations:**
- PowerShell injection prevention
- Module installation safety
- Scope restrictions for security

---

## 💡 Why This Is a Good Copilot Issue

This sample issue demonstrates best practices for Copilot-optimized issues:

1. **Clear, Specific Requirements** - Exactly what needs to be built
2. **Complete Code Context** - Points to relevant existing code patterns
3. **Detailed Function Signatures** - Exact API specifications
4. **Security Considerations** - Important safety requirements
5. **Step-by-Step Implementation** - Clear development phases
6. **Quality Checklists** - Comprehensive acceptance criteria
7. **Code Examples** - Patterns to follow and adapt
8. **Reference Materials** - Links to relevant documentation

This gives Copilot everything it needs to implement the feature correctly while maintaining consistency with the existing codebase.
