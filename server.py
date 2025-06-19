import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
"""
MCP Server for secure PowerShell command execution.
"""
import re
import sys
import asyncio
import subprocess
from typing import Optional

from mcp.server.fastmcp import FastMCP, Context

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

# Create an MCP server with better metadata and dependencies
mcp = FastMCP(
    "PowerShell Integration Server",
    description="Secure PowerShell command execution and script generation for Windows system administration",
    dependencies=["asyncio", "psutil>=5.9.0"],
    capabilities={
        "tools": True,
        "resources": True,
        "resourceTemplates": True,
        "prompts": True
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
async def run_powershell(code: str, timeout: Optional[int] = 60, ctx: Optional[Context] = None) -> str:
    """Execute PowerShell commands securely.
    
    Args:
        code: PowerShell code to execute
        timeout: Command timeout in seconds (1-300, default 60)
        ctx: MCP context for logging and progress reporting
    
    Returns:
        Command output as string
    """
    if ctx:
        await ctx.info(f"Executing PowerShell command (timeout: {timeout}s)")
    return await execute_powershell(code, timeout, ctx)

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
        raise ValueError("Path cannot be empty")
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
    """Generate a Microsoft Intune detection script with enterprise-grade compliance checking.
    
    Creates a PowerShell detection script that follows Microsoft Intune best practices:
    - Proper exit codes (0=compliant, 1=non-compliant, 2=error)
    - Event log integration for monitoring and troubleshooting
    - Fast execution optimized for frequent compliance checks
    - Comprehensive error handling and logging
    - No user interaction (required for Intune deployment)
    
    💡 TIP: For complete Intune compliance, you need BOTH detection and remediation scripts.
    Consider using 'generate_intune_script_pair' to create both scripts together with matching logic.
    
    Microsoft References:
    - Intune Detection Scripts: https://docs.microsoft.com/en-us/mem/intune/fundamentals/remediations
    - Best Practices: https://docs.microsoft.com/en-us/mem/intune/fundamentals/remediations-script-samples
    - PowerShell Requirements: https://docs.microsoft.com/en-us/mem/intune/apps/intune-management-extension
    - Exit Code Standards: https://docs.microsoft.com/en-us/mem/intune/apps/troubleshoot-mam-app-deployment
    
    Args:
        description: Clear description of what the script should detect (e.g., 'Check if Chrome is installed with correct version', 'Verify Windows firewall is enabled')
        detection_logic: PowerShell code that performs the compliance check. Use 'Complete-Detection -Compliant $true/$false -Message "status"' to indicate result
        output_path: Optional file path where the script will be saved. If not provided, returns script content
        timeout: Command timeout in seconds (1-300, default 60)
        
    Returns:
        Generated script content or path where script was saved
        
    Example:
        Generate a script to detect Chrome installation:
        ```
        result = await generate_intune_detection_script(
            description="Check if Chrome browser is installed with version 100.0.0.0 or higher",
            detection_logic='''
            try {
                $app = Get-ItemProperty "HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\App Paths\\chrome.exe" -ErrorAction Stop
                $version = (Get-Item $app.'(Default)').VersionInfo.FileVersion
                $compliant = [version]$version -ge [version]"100.0.0.0"
                Complete-Detection -Compliant $compliant -Message "Chrome version: $version (Required: 100.0.0.0+)"
            } catch {
                Complete-Detection -Compliant $false -Message "Chrome not found or inaccessible"
            }
            ''',
            output_path="detect_chrome.ps1"
        )
        ```
        
    Tips:
        - Keep detection logic fast and efficient (runs frequently)
        - Always use Complete-Detection function to set proper exit codes
        - Use try-catch blocks for robust error handling
        - Test detection logic thoroughly in different environments
        - Use Write-IntuneLog for detailed progress tracking
        - Avoid making changes in detection scripts (read-only operations)
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
    """Generate a Microsoft Intune remediation script with enterprise-grade features.
    
    Creates a PowerShell remediation script that follows Microsoft Intune best practices:
    - Proper exit codes (0=success, 1=failure, 2=error)
    - Event log integration for monitoring and troubleshooting
    - System restore point creation before making changes
    - Comprehensive error handling and logging
    - No user interaction (required for Intune deployment)
    
    ⚠️  IMPORTANT: For complete Intune compliance, you need BOTH detection and remediation scripts.
    Consider using 'generate_intune_script_pair' instead to create both scripts together.
    
    Microsoft References:
    - Intune Remediation Scripts: https://docs.microsoft.com/en-us/mem/intune/fundamentals/remediations
    - Best Practices: https://docs.microsoft.com/en-us/mem/intune/fundamentals/remediations-script-samples
    - PowerShell Script Requirements: https://docs.microsoft.com/en-us/mem/intune/apps/intune-management-extension
    - Exit Code Standards: https://docs.microsoft.com/en-us/mem/intune/apps/troubleshoot-mam-app-installation#exit-codes
    
    Args:
        description: Clear description of what the script should remediate (e.g., 'Install Chrome browser', 'Configure Windows firewall')
        remediation_logic: PowerShell code that performs the remediation. Use 'Complete-Remediation -Success $true -Message "description"' to indicate completion
        output_path: Optional file path where the script will be saved. If not provided, returns script content
        timeout: Command timeout in seconds (1-300, default 60)
        
    Returns:
        Generated script content or path where script was saved
        
    Example:
        Generate a script to install Chrome:
        ```
        result = await generate_intune_remediation_script(
            description="Install Chrome browser to latest version",
            remediation_logic='''
            $installer = "$env:TEMP\\ChromeSetup.exe"
            Invoke-WebRequest -Uri "https://dl.google.com/chrome/install/latest/chrome_installer.exe" -OutFile $installer
            Start-Process -FilePath $installer -Args "/silent /install" -Wait
            Remove-Item $installer -Force
            Complete-Remediation -Success $true -Message "Chrome installation completed successfully"
            ''',
            output_path="remediate_chrome.ps1"
        )
        ```
        
    Tips:
        - Always use Complete-Remediation function to set proper exit codes
        - Test your remediation_logic in a safe environment first
        - Consider creating a system restore point for major changes
        - Use Write-IntuneLog for detailed logging and troubleshooting
        - Ensure no user interaction is required (scripts run silently)
    """
    params = {
        "SYNOPSIS": f"Intune Remediation Script - {description}",        "DESCRIPTION": description,
        "DATE": datetime.now().strftime('%Y-%m-%d'),
        "REMEDIATION_LOGIC": remediation_logic
    }
    
    if output_path:
        output_path = ensure_directory(output_path)
    
    return await generate_script_from_template("intune_remediation", params, output_path, timeout)

@mcp.tool()
async def generate_intune_script_pair(
    description: str,
    detection_logic: str,
    remediation_logic: str,
    output_dir: Optional[str] = None,
    timeout: Optional[int] = 60
) -> Dict[str, str]:
    """Generate a complete pair of Microsoft Intune detection and remediation scripts.
    
    This is the RECOMMENDED tool for Intune compliance as it creates both required scripts:
    - Detection script: Checks current system state and determines compliance
    - Remediation script: Fixes non-compliant conditions with proper safeguards
    
    Both scripts follow Microsoft Intune best practices:
    - Proper exit codes (Detection: 0=compliant, 1=non-compliant, 2=error; Remediation: 0=success, 1=failure, 2=error)
    - Event log integration for centralized monitoring
    - System restore points before changes (remediation only)
    - Comprehensive error handling and logging
    - No user interaction (silent execution required)
    
    Microsoft References:
    - Intune Remediation Scripts Overview: https://docs.microsoft.com/en-us/mem/intune/fundamentals/remediations
    - Script Deployment Best Practices: https://docs.microsoft.com/en-us/mem/intune/fundamentals/remediations-script-samples
    - PowerShell Requirements: https://docs.microsoft.com/en-us/mem/intune/apps/intune-management-extension
    - Exit Code Standards: https://docs.microsoft.com/en-us/mem/intune/apps/troubleshoot-mam-app-deployment
    - Monitoring and Reporting: https://docs.microsoft.com/en-us/mem/intune/fundamentals/remediations-monitor
    
    Args:
        description: Clear description of what the scripts should detect and remediate (e.g., 'Ensure Chrome browser is installed with latest version')
        detection_logic: PowerShell code that performs the compliance check. Use 'Complete-Detection -Compliant $true/$false -Message "status"' to indicate result
        remediation_logic: PowerShell code that fixes non-compliant conditions. Use 'Complete-Remediation -Success $true/$false -Message "result"' to indicate completion
        output_dir: Optional directory to save both scripts. If not provided, returns script content in response
        timeout: Command timeout in seconds (1-300, default 60)
        
    Returns:
        Dictionary containing both scripts: {"detection_script": "content/path", "remediation_script": "content/path"}
        
    Example:
        Generate scripts to manage Chrome browser installation:
        ```
        result = await generate_intune_script_pair(
            description="Ensure Chrome browser is installed with version 100.0.0.0 or higher",
            detection_logic='''
            try {
                $app = Get-ItemProperty "HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\App Paths\\chrome.exe" -ErrorAction Stop
                $version = (Get-Item $app.'(Default)').VersionInfo.FileVersion
                $compliant = [version]$version -ge [version]"100.0.0.0"
                Complete-Detection -Compliant $compliant -Message "Chrome version: $version (Required: 100.0.0.0+)"
            } catch {
                Complete-Detection -Compliant $false -Message "Chrome not found or inaccessible"
            }
            ''',
            remediation_logic='''
            try {
                $installer = "$env:TEMP\\ChromeSetup.exe"
                Write-IntuneLog "Downloading Chrome installer..."
                Invoke-WebRequest -Uri "https://dl.google.com/chrome/install/latest/chrome_installer.exe" -OutFile $installer -UseBasicParsing
                Write-IntuneLog "Installing Chrome silently..."
                Start-Process -FilePath $installer -Args "/silent /install" -Wait
                Remove-Item $installer -Force
                Complete-Remediation -Success $true -Message "Chrome installation completed successfully"
            } catch {
                Complete-Remediation -Success $false -Message "Chrome installation failed: $($_.Exception.Message)"
            }
            ''',
            output_dir="chrome_intune_scripts"
        )
        ```
        
    Tips:
        - Always test both scripts in a controlled environment first
        - Use descriptive logging messages for easier troubleshooting
        - Consider the impact of remediation actions (e.g., system restarts, user disruption)
        - Use Write-IntuneLog for detailed progress tracking
        - Ensure detection logic is fast and efficient (runs frequently)
        - Make remediation logic idempotent (safe to run multiple times)
    """
    if output_dir:
        # Create output directory in current working directory
        abs_output_dir = ensure_directory(output_dir)
        
        # Create full paths for scripts
        detect_path = os.path.join(abs_output_dir, "detect.ps1")
        remedy_path = os.path.join(abs_output_dir, "remedy.ps1")
        
        # Create parent directory if it doesn't exist
        os.makedirs(abs_output_dir, exist_ok=True)
        
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

async def execute_powershell(code: str, timeout: Optional[int] = 60, ctx: Optional[Context] = None) -> str:
    """Execute PowerShell commands securely.
    
    Args:
        code: PowerShell code to execute
        timeout: Command timeout in seconds (1-300, default 60)
        ctx: MCP context for logging and progress reporting
    
    Returns:
        Command output as string
    """
    # Validate timeout
    if not isinstance(timeout, int) or timeout < 1 or timeout > 300:
        raise ValueError("timeout must be between 1 and 300 seconds")
        
    # Validate code
    if not validate_powershell_code(code):
        raise ValueError("PowerShell code contains potentially dangerous commands")

    if ctx:
        await ctx.info("Validating PowerShell code...")

    # Create and run process
    if ctx:
        await ctx.info("Starting PowerShell process...")
    
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
        if ctx:
            await ctx.info("Executing command...")
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        process.kill()
        if ctx:
            await ctx.error(f"Command timed out after {timeout} seconds")
        raise TimeoutError(f"Command timed out after {timeout} seconds")

    if process.returncode != 0:
        error_msg = stderr.decode() if stderr else "Command failed with no error output"
        if ctx:
            await ctx.error(f"PowerShell command failed: {error_msg}")
        raise RuntimeError(error_msg)
    
    result = stdout.decode() if stdout else ""
    if ctx:
        await ctx.info(f"Command completed successfully, returned {len(result)} characters")
        
    return result

@mcp.tool()
async def run_powershell_with_progress(
    code: str, 
    timeout: Optional[int] = 60, 
    ctx: Optional[Context] = None
) -> str:
    """Execute PowerShell commands with detailed progress reporting.
    
    Args:
        code: PowerShell code to execute
        timeout: Command timeout in seconds (1-300, default 60)
        ctx: MCP context for logging and progress reporting
    
    Returns:
        Command output as string with execution details
    """
    if not ctx:
        # If no context provided, fall back to basic execution
        return await execute_powershell(code, timeout)
    
    start_time = datetime.now()
    
    try:
        await ctx.info("🔍 Validating PowerShell code...")
        
        # Validate timeout
        if not isinstance(timeout, int) or timeout < 1 or timeout > 300:
            await ctx.error("❌ Invalid timeout value")
            raise ValueError("timeout must be between 1 and 300 seconds")
            
        # Validate code
        if not validate_powershell_code(code):
            await ctx.error("❌ PowerShell code contains potentially dangerous commands")
            raise ValueError("PowerShell code contains potentially dangerous commands")

        await ctx.info("✅ Code validation passed")
        await ctx.info("🚀 Starting PowerShell execution...")
        
        # Report progress at start
        await ctx.report_progress(0, 4, "Initializing PowerShell process")

        # Create and run process
        process = await asyncio.create_subprocess_exec(
            "powershell",
            "-NoProfile",
            "-NonInteractive", 
            "-Command",
            code,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        await ctx.report_progress(1, 4, "Process created, executing command")
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            await ctx.report_progress(3, 4, "Command execution completed")
        except asyncio.TimeoutError:
            process.kill()
            await ctx.error(f"⏰ Command timed out after {timeout} seconds")
            raise TimeoutError(f"Command timed out after {timeout} seconds")

        if process.returncode != 0:
            error_msg = stderr.decode() if stderr else "Command failed with no error output"
            await ctx.error(f"❌ PowerShell command failed: {error_msg}")
            raise RuntimeError(error_msg)
        
        result = stdout.decode() if stdout else ""
        
        # Calculate execution time
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        await ctx.report_progress(4, 4, "Processing results")
        await ctx.info(f"✅ Command completed successfully in {execution_time:.2f} seconds")
        await ctx.info(f"📊 Output size: {len(result)} characters")
        
        # Add execution metadata to result
        metadata = {
            "execution_time_seconds": execution_time,
            "output_length": len(result),
            "exit_code": process.returncode,
            "timestamp": end_time.isoformat()
        }
        
        if result.strip():
            return f"--- PowerShell Output ---\n{result}\n--- Execution Metadata ---\n{json.dumps(metadata, indent=2)}"
        else:
            return f"--- No Output Produced ---\n--- Execution Metadata ---\n{json.dumps(metadata, indent=2)}"
            
    except Exception as e:
        await ctx.error(f"❌ Execution failed: {str(e)}")
        raise

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

# Resource definitions for exposing templates and system info
@mcp.resource("template://{template_name}")
def get_powershell_template(template_name: str) -> str:
    """Get a PowerShell script template by name."""
    template_path = os.path.join(TEMPLATES_DIR, f"{template_name}.ps1")
    if not os.path.exists(template_path):
        raise ValueError(f"Template '{template_name}' not found")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

@mcp.resource("templates://list")
def list_templates() -> str:
    """List all available PowerShell templates."""
    if not os.path.exists(TEMPLATES_DIR):
        return json.dumps({"templates": [], "message": "Templates directory not found"})
    
    templates = []
    for file in os.listdir(TEMPLATES_DIR):
        if file.endswith('.ps1'):
            template_name = file[:-4]  # Remove .ps1 extension
            template_path = os.path.join(TEMPLATES_DIR, file)
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    first_lines = f.readlines()[:10]  # Read first 10 lines for description
                    description = ""
                    for line in first_lines:
                        if line.strip().startswith('.SYNOPSIS'):
                            # Find next non-comment line for description
                            for desc_line in first_lines[first_lines.index(line)+1:]:
                                if desc_line.strip() and not desc_line.strip().startswith('#') and not desc_line.strip().startswith('.'):
                                    description = desc_line.strip()
                                    break
                            break
                    
                    templates.append({
                        "name": template_name,
                        "description": description or f"PowerShell template: {template_name}",
                        "path": f"template://{template_name}"
                    })
            except Exception as e:
                templates.append({
                    "name": template_name,
                    "description": f"Template file (error reading: {str(e)})",
                    "path": f"template://{template_name}"
                })
    
    return json.dumps({"templates": templates}, indent=2)

@mcp.resource("system://info")
def get_system_info_resource() -> str:
    """Get basic system information as a resource."""
    import platform
    
    try:
        import psutil
        system_info = {
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "node": platform.node()
            },
            "memory": {
                "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
                "percent_used": psutil.virtual_memory().percent
            },
            "disk": {
                "total_gb": round(psutil.disk_usage('/').total / (1024**3), 2) if os.name != 'nt' else round(psutil.disk_usage('C:\\').total / (1024**3), 2),
                "free_gb": round(psutil.disk_usage('/').free / (1024**3), 2) if os.name != 'nt' else round(psutil.disk_usage('C:\\').free / (1024**3), 2),
            },
            "cpu": {
                "cores": psutil.cpu_count(),
                "percent": psutil.cpu_percent(interval=1)
            },
            "timestamp": datetime.now().isoformat()
        }
        return json.dumps(system_info, indent=2)
    except ImportError:
        # Fallback if psutil is not available
        system_info = {
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "node": platform.node()
            },
            "timestamp": datetime.now().isoformat(),
            "note": "Install psutil for detailed system metrics"
        }
        return json.dumps(system_info, indent=2)
        
# Prompt definitions for PowerShell script generation guidance
@mcp.prompt()
def powershell_best_practices(script_purpose: str) -> str:
    """Generate a prompt for PowerShell script best practices."""
    return f"""
Please help me create a PowerShell script for: {script_purpose}

Please ensure the script follows these best practices:

1. **Error Handling**: Include proper try-catch blocks and error handling
2. **Parameter Validation**: Use proper parameter validation and help text
3. **Logging**: Include informative Write-Host or Write-Output statements
4. **Security**: Avoid dangerous commands and validate inputs
5. **Documentation**: Include proper comment-based help with .SYNOPSIS, .DESCRIPTION, .PARAMETER, and .EXAMPLE
6. **Performance**: Use efficient PowerShell cmdlets and avoid unnecessary loops
7. **Compatibility**: Consider Windows PowerShell vs PowerShell Core compatibility

Template structure:
```powershell
<#
.SYNOPSIS
    Brief description

.DESCRIPTION
    Detailed description

.PARAMETER ParameterName
    Description of parameter

.EXAMPLE
    Example usage

.NOTES
    Additional notes
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$RequiredParam
)

try {{
    # Main script logic here
    Write-Host "Starting {script_purpose}..."
    
    # Your implementation
    
    Write-Host "Completed successfully"
}}
catch {{
    Write-Error "Error occurred: $($_.Exception.Message)"
    exit 1
}}
```

Please provide a complete PowerShell script that implements the requested functionality while following these guidelines.
"""

@mcp.prompt()
def troubleshoot_powershell_error(error_message: str, script_context: str = "") -> str:
    """Generate a prompt for troubleshooting PowerShell errors."""
    context_section = f"\n\nScript context:\n{script_context}" if script_context else ""
    
    return f"""
I'm encountering a PowerShell error and need help troubleshooting it.

Error message:
{error_message}{context_section}

Please help me:

1. **Identify the root cause** of this error
2. **Provide specific solutions** to fix the issue
3. **Suggest preventive measures** to avoid similar errors in the future
4. **Recommend best practices** for the type of operation that's failing

Please provide:
- Clear explanation of what's causing the error
- Step-by-step solution with corrected PowerShell code
- Alternative approaches if applicable
- Testing steps to verify the fix works

If you need more information to provide a complete solution, please ask specific questions about:
- PowerShell version being used
- Operating system and version
- Security context (admin privileges, execution policy)
- Input data or parameters being used
- Expected vs actual behavior
"""


if __name__ == "__main__":
    log_tools()
    mcp.run()
