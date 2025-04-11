"""
MCP Server for secure PowerShell command execution.
"""
import re
import sys
import asyncio
import subprocess
from typing import Optional

from mcp.server.fastmcp import FastMCP

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

# Create an MCP server
mcp = FastMCP(
    "PowerShell Integration",
    capabilities={
        "tools": True,
        "resources": False,
        "resourceTemplates": False
    }
)

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')

def format_json_output(code: str) -> str:
    """Add JSON formatting to PowerShell code if not present."""
    if not code.strip().lower().endswith('| convertto-json'):
        code = f"{code} | ConvertTo-Json"
    return code

def validate_powershell_code(code: str) -> bool:
    """
    Validate PowerShell code for potentially harmful commands.
    
    Args:
        code: The PowerShell code to validate
        
    Returns:
        bool: True if code passes validation
    """
    dangerous_patterns = [
        r"rm\s+(-r|-f|/s)*\s*/",  # Dangerous recursive deletes
        r"format\s+[a-z]:",        # Drive formatting
        r"Stop-Computer",          # System shutdown
        r"Restart-Computer",       # System restart
        r"Remove-Item.*-Recurse",  # Recursive deletion
        r"Invoke-Expression",      # Dynamic code execution
        r"iex",                    # Alias for Invoke-Expression
        r"Start-Process",          # Starting new processes
        r"New-Service",           # Creating services
        r"Set-Service",           # Modifying services
        r"net\s+user",            # User account manipulation
    ]
    
    return not any(re.search(pattern, code, re.IGNORECASE) for pattern in dangerous_patterns)

@mcp.tool()
async def run_powershell(code: str, timeout: Optional[int] = 60) -> str:
    """Execute PowerShell commands securely.
    
    Args:
        code: PowerShell code to execute
        timeout: Command timeout in seconds (1-300, default 60)
    
    Returns:
        Command output as string
    """
    return await execute_powershell(code, timeout)

@mcp.tool()
async def get_system_info(properties: Optional[List[str]] = None, timeout: Optional[int] = 60) -> str:
    """Get system information.
    
    Args:
        properties: List of ComputerInfo properties to retrieve (optional)
        timeout: Command timeout in seconds (1-300, default 60)
    """
    code = "Get-ComputerInfo"
    if properties:
        properties_str = ",".join(properties)
        code = f"{code} -Property {properties_str}"
    return await execute_powershell(format_json_output(code), timeout)

@mcp.tool()
async def get_running_services(name: Optional[str] = None, status: Optional[str] = None, timeout: Optional[int] = 60) -> str:
    """Get information about running services.
    
    Args:
        name: Filter services by name (supports wildcards)
        status: Filter by status (Running, Stopped, etc.)
        timeout: Command timeout in seconds (1-300, default 60)
    """
    code = "Get-Service"
    filters = []
    if name:
        filters.append(f"Name -like '{name}'")
    if status:
        filters.append(f"Status -eq '{status}'")
    if filters:
        code = f"{code} | Where-Object {{ {' -and '.join(filters)} }}"
    code = f"{code} | Select-Object Name, DisplayName, Status, StartType"
    return await execute_powershell(format_json_output(code), timeout)

@mcp.tool()
async def get_processes(name: Optional[str] = None, top: Optional[int] = None, sort_by: Optional[str] = None, timeout: Optional[int] = 60) -> str:
    """Get information about running processes.
    
    Args:
        name: Filter processes by name (supports wildcards)
        top: Limit to top N processes
        sort_by: Property to sort by (e.g., CPU, WorkingSet)
        timeout: Command timeout in seconds (1-300, default 60)
    """
    code = "Get-Process"
    if name:
        code = f"{code} -Name '{name}'"
    if sort_by:
        code = f"{code} | Sort-Object -Property {sort_by} -Descending"
    if top:
        code = f"{code} | Select-Object -First {top}"
    code = f"{code} | Select-Object Name, Id, CPU, WorkingSet, StartTime"
    return await execute_powershell(format_json_output(code), timeout)

@mcp.tool()
async def get_event_logs(logname: str, newest: Optional[int] = 10, level: Optional[int] = None, timeout: Optional[int] = 60) -> str:
    """Get Windows event logs.
    
    Args:
        logname: Name of the event log (System, Application, Security, etc.)
        newest: Number of most recent events to retrieve (default 10)
        level: Filter by event level (1: Critical, 2: Error, 3: Warning, 4: Information)
        timeout: Command timeout in seconds (1-300, default 60)
    """
    code = f"Get-EventLog -LogName {logname} -Newest {newest}"
    if level:
        code = f"{code} | Where-Object {{ $_.EntryType -eq {level} }}"
    code = f"{code} | Select-Object TimeGenerated, EntryType, Source, Message"
    return await execute_powershell(format_json_output(code), timeout)

@mcp.tool()
async def generate_script_from_template(
    template_name: str,
    parameters: Dict[str, Any],
    output_path: Optional[str] = None,
    timeout: Optional[int] = 60
) -> str:
    """Generate a PowerShell script from a template.
    
    Args:
        template_name: Name of the template to use (without .ps1 extension)
        parameters: Dictionary of parameters to replace in the template
        output_path: Where to save the generated script (optional)
        timeout: Command timeout in seconds (1-300, default 60)
        
    Returns:
        Generated script content or path where script was saved
    """
    template_path = os.path.join(TEMPLATES_DIR, f"{template_name}.ps1")
    if not os.path.exists(template_path):
        raise ValueError(f"Template {template_name} not found")
        
    with open(template_path, 'r') as f:
        template_content = f.read()
        
    # Replace template variables
    script_content = template_content
    parameters['DATE'] = datetime.now().strftime('%Y-%m-%d')
    
    for key, value in parameters.items():
        script_content = script_content.replace(f"{{{{{key}}}}}", str(value))
        
    if output_path:
        with open(output_path, 'w') as f:
            f.write(script_content)
        return f"Script generated and saved to: {output_path}"
    
    return script_content

@mcp.tool()
async def generate_custom_script(
    description: str,
    script_type: str,
    parameters: Optional[List[Dict[str, Any]]] = None,
    include_logging: bool = True,
    include_error_handling: bool = True,
    output_path: Optional[str] = None,
    timeout: Optional[int] = 60
) -> str:
    """Generate a custom PowerShell script based on description.
    
    Args:
        description: Natural language description of what the script should do
        script_type: Type of script to generate (file_ops, service_mgmt, etc.)
        parameters: List of parameters the script should accept
        include_logging: Whether to include logging functions
        include_error_handling: Whether to include error handling
        output_path: Where to save the generated script (optional)
        timeout: Command timeout in seconds (1-300, default 60)
        
    Returns:
        Generated script content or path where script was saved
    """
    script_content = []
    
    # Add help comment block
    script_content.extend([
        '<#',
        '.SYNOPSIS',
        f'    {description}',
        '.DESCRIPTION',
        f'    Dynamically generated PowerShell script for {script_type}',
        '.NOTES',
        '    Generated by PowerShell MCP Server',
        f'    Date: {datetime.now().strftime("%Y-%m-%d")}',
        '#>'
    ])
    
    # Add parameters
    if parameters:
        script_content.append('\nparam (')
        for param in parameters:
            param_str = f'    [Parameter(Mandatory=${param.get("mandatory", "false")})]'
            if param.get('type'):
                param_str += f'\n    [{param["type"]}]'
            param_str += f'${param["name"]}'
            if param.get('default'):
                param_str += f' = "{param["default"]}"'
            script_content.append(param_str + ',')
        script_content[-1] = script_content[-1].rstrip(',')  # Remove trailing comma
        script_content.append(')')
    
    # Add logging function
    if include_logging:
        script_content.extend([
            '\n# Function to write log messages',
            'function Write-Log {',
            '    param (',
            '        [Parameter(Mandatory=$true)]',
            '        [string]$Message,',
            '        [Parameter(Mandatory=$false)]',
            '        [ValidateSet("INFO", "WARNING", "ERROR")]',
            '        [string]$Level = "INFO"',
            '    )',
            '    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"',
            '    Write-Host "[$timestamp] [$Level] $Message"',
            '}'
        ])
    
    # Add error handling
    if include_error_handling:
        script_content.extend([
            '\n# Function to handle errors',
            'function Handle-Error {',
            '    param (',
            '        [Parameter(Mandatory=$true)]',
            '        [System.Management.Automation.ErrorRecord]$ErrorRecord',
            '    )',
            '    Write-Log -Level ERROR -Message "Error occurred: $($ErrorRecord.Exception.Message)"',
            '    Write-Log -Level ERROR -Message "Error details: $($ErrorRecord | Out-String)"',
            '}'
        ])
    
    # Add main script block
    script_content.extend([
        '\n# Main execution',
        'try {',
        '    Write-Log "Starting script execution..."',
        '    ',
        '    # TODO: Add script logic here based on description',
        '    # This is where you would add the specific PowerShell commands',
        '    Write-Log "Script completed successfully."',
        '}',
        'catch {',
        '    Handle-Error -ErrorRecord $_',
        '    exit 1',
        '}'
    ])
    
    final_content = '\n'.join(script_content)
    
    if output_path:
        with open(output_path, 'w') as f:
            f.write(final_content)
        return f"Script generated and saved to: {output_path}"
    
    return final_content

def normalize_path(path: str) -> str:
    """Convert relative paths to absolute using current working directory."""
    if not path:
        return None
    if path.startswith(('./','.\\')):
        path = path[2:]
    if not os.path.isabs(path):
        path = os.path.join(os.getcwd(), path)
    return os.path.abspath(path)

@mcp.tool()
def ensure_directory(path: str) -> str:
    """Ensure directory exists and return absolute path."""
    abs_path = normalize_path(path)
    if os.path.splitext(abs_path)[1]:  # If path has an extension
        dir_path = os.path.dirname(abs_path)
    else:
        dir_path = abs_path
    os.makedirs(dir_path, exist_ok=True)
    return abs_path

async def generate_intune_detection_script(
    description: str,
    detection_logic: str,
    output_path: Optional[str] = None,
    timeout: Optional[int] = 60
) -> str:
    """Generate an Intune detection script.
    
    Args:
        description: What the script should detect
        detection_logic: PowerShell code that performs the detection
        output_path: Where to save the script (optional)
        timeout: Command timeout in seconds (1-300, default 60)
        
    Returns:
        Generated script content or path where script was saved
    """
    params = {
        "SYNOPSIS": f"Intune Detection Script - {description}",
        "DESCRIPTION": description,
        "DATE": datetime.now().strftime('%Y-%m-%d'),
        "DETECTION_LOGIC": detection_logic
    }
    
    if output_path:
        output_path = ensure_directory(output_path)
    
    return await generate_script_from_template("intune_detection", params, output_path, timeout)

@mcp.tool()
async def generate_intune_remediation_script(
    description: str,
    remediation_logic: str,
    output_path: Optional[str] = None,
    timeout: Optional[int] = 60
) -> str:
    """Generate an Intune remediation script.
    
    Args:
        description: What the script should remediate
        remediation_logic: PowerShell code that performs the remediation
        output_path: Where to save the script (optional)
        timeout: Command timeout in seconds (1-300, default 60)
        
    Returns:
        Generated script content or path where script was saved
    """
    params = {
        "SYNOPSIS": f"Intune Remediation Script - {description}",
        "DESCRIPTION": description,
        "DATE": datetime.now().strftime('%Y-%m-%d'),
        "REMEDIATION_LOGIC": remediation_logic
    }
    
    return await generate_script_from_template("intune_remediation", params, output_path, timeout)

@mcp.tool()
async def generate_intune_script_pair(
    description: str,
    detection_logic: str,
    remediation_logic: str,
    output_dir: Optional[str] = None,
    timeout: Optional[int] = 60
) -> Dict[str, str]:
    """Generate a pair of Intune detection and remediation scripts.
    
    Args:
        description: What the scripts should detect and remediate
        detection_logic: PowerShell code that performs the detection
        remediation_logic: PowerShell code that performs the remediation
        output_dir: Directory to save the scripts (optional)
        timeout: Command timeout in seconds (1-300, default 60)
        
    Returns:
        Dictionary containing paths or content of both scripts
    """
    if output_dir:
        # Create output directory in current working directory
        output_dir = ensure_directory(output_dir)
        
        # Create full paths for scripts
        detect_path = os.path.join(output_dir, "detect.ps1")
        remedy_path = os.path.join(output_dir, "remedy.ps1")
        
        # Create parent directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        detect_result = await generate_intune_detection_script(
            description=description,
            detection_logic=detection_logic,
            output_path=detect_path,
            timeout=timeout
        )
        
        remedy_result = await generate_intune_remediation_script(
            description=description,
            remediation_logic=remediation_logic,
            output_path=remedy_path,
            timeout=timeout
        )
    else:
        detect_result = await generate_intune_detection_script(
            description=description,
            detection_logic=detection_logic,
            timeout=timeout
        )
        
        remedy_result = await generate_intune_remediation_script(
            description=description,
            remediation_logic=remediation_logic,
            timeout=timeout
        )
    
    return {
        "detection_script": detect_result,
        "remediation_script": remedy_result
    }

async def execute_powershell(code: str, timeout: Optional[int] = 60) -> str:
    """Execute PowerShell commands securely.
    
    Args:
        code: PowerShell code to execute
        timeout: Command timeout in seconds (1-300, default 60)
    
    Returns:
        Command output as string
    """
    # Validate timeout
    if not isinstance(timeout, int) or timeout < 1 or timeout > 300:
        raise ValueError("timeout must be between 1 and 300 seconds")
        
    # Validate code
    if not validate_powershell_code(code):
        raise ValueError("PowerShell code contains potentially dangerous commands")

    # Create and run process
    process = await asyncio.create_subprocess_exec(
        "powershell",
        "-NoProfile",      # Don't load profiles
        "-NonInteractive", # No interactive prompts
        "-Command",
        code,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    try:
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        process.kill()
        raise TimeoutError(f"Command timed out after {timeout} seconds")

    if process.returncode != 0:
        raise RuntimeError(stderr.decode() if stderr else "Command failed with no error output")
        
    return stdout.decode() if stdout else ""

def log_tools():
    """Log available tools and their descriptions."""
    print("\nAvailable PowerShell Tools:")
    print("---------------------------")
    
    print("run_powershell:")
    print("  Description: Execute PowerShell commands securely")
    print("  Parameters:")
    print("    - code (string): PowerShell code to execute")
    print("    - timeout (int, optional): Command timeout in seconds (1-300, default 60)")
    
    print("\nget_system_info:")
    print("  Description: Get system information using Get-ComputerInfo")
    print("  Parameters:")
    print("    - properties (list, optional): List of properties to retrieve")
    print("    - timeout (int, optional): Command timeout in seconds (1-300, default 60)")
    
    print("\nget_running_services:")
    print("  Description: Get information about Windows services")
    print("  Parameters:")
    print("    - name (string, optional): Filter services by name (wildcards supported)")
    print("    - status (string, optional): Filter by status")
    print("    - timeout (int, optional): Command timeout in seconds (1-300, default 60)")
    
    print("\nget_processes:")
    print("  Description: Monitor running processes")
    print("  Parameters:")
    print("    - name (string, optional): Filter processes by name")
    print("    - top (int, optional): Limit to top N processes")
    print("    - sort_by (string, optional): Property to sort by")
    print("    - timeout (int, optional): Command timeout in seconds (1-300, default 60)")
    
    print("\nget_event_logs:")
    print("  Description: Access Windows event logs")
    print("  Parameters:")
    print("    - logname (string): Name of the event log to access")
    print("    - newest (int, optional): Number of recent events to retrieve")
    print("    - level (int, optional): Event level filter")
    print("    - timeout (int, optional): Command timeout in seconds (1-300, default 60)")
    print("---------------------------\n")

if __name__ == "__main__":
    log_tools()
    mcp.run()
