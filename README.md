# PowerShell Exec MCP Server

A secure Model Context Protocol (MCP) server that provides controlled PowerShell command execution capabilities through MCP tools. This server includes security features to prevent dangerous commands and provides timeouts for command execution.

## Features

- Secure PowerShell command execution
- JSON-formatted output for structured data
- System information retrieval
- Service management and monitoring
- Process monitoring and analysis
- Event log access
- PowerShell script generation
- Template-based script generation
- Dynamic script generation
- Microsoft Intune detection and remediation script generation
- IBM BigFix relevance and action script generation
- Command timeout support
- Blocking of dangerous commands
- Non-interactive and profile-less execution
- Async support
- Type hints and input validation

## Project Structure

```
mcp-powershell-exec/
├── mcp_powershell_exec/         # Main package directory
│   ├── __init__.py             # Package initialization
│   ├── __main__.py            # Entry point
│   ├── server.py              # Server implementation
│   ├── templates/             # PowerShell script templates
│   │   ├── basic_script.ps1   # Basic script template
│   │   ├── system_inventory.ps1 # System inventory template
│   │   ├── intune_detection.ps1 # Intune detection script template
│   │   ├── intune_remediation.ps1 # Intune remediation script template
│   │   ├── bigfix_relevance.ps1 # BigFix relevance script template
│   │   └── bigfix_action.ps1  # BigFix action script template
│   └── py.typed               # Type hints marker
├── pyproject.toml             # Project metadata and dependencies
├── setup.py                   # Package installation
└── README.md                  # Documentation
```

## Installation

1. Ensure you have Python 3.7+ installed
2. Install the package:
```bash
pip install .
```

Or install in development mode:
```bash
pip install -e .
```

## Usage

### Running the Server

You can run the server in several ways:

1. Using the MCP CLI:
```bash
mcp run mcp_powershell_exec
```

2. Using Python module:
```bash
python -m mcp_powershell_exec
```

3. Using the console script:
```bash
mcp-powershell-exec
```

For development and testing:
```bash
mcp dev mcp_powershell_exec
```

### Installing in Claude Desktop

To install the server in Claude Desktop:
```bash
mcp install mcp_powershell_exec
```

## Available Tools

### run_powershell

The base tool for executing PowerShell commands securely with timeout support.

Parameters:
- `code` (required): PowerShell code to execute
- `timeout` (optional): Command timeout in seconds (1-300, default 60)

Example:
```python
result = await run_powershell(
    code="Get-Process | Select-Object Name, Id, CPU",
    timeout=30
)
```

### get_system_info

Retrieve system information using Get-ComputerInfo cmdlet.

Parameters:
- `properties` (optional): List of ComputerInfo properties to retrieve
- `timeout` (optional): Command timeout in seconds (1-300, default 60)

Example:
```python
result = await get_system_info(
    properties=["OsName", "OsVersion", "OsArchitecture"]
)
```

### get_running_services

Get information about Windows services.

Parameters:
- `name` (optional): Filter services by name (supports wildcards)
- `status` (optional): Filter by status (Running, Stopped, etc.)
- `timeout` (optional): Command timeout in seconds (1-300, default 60)

Example:
```python
result = await get_running_services(
    name="*sql*",
    status="Running"
)
```

### get_processes

Monitor running processes with filtering and sorting capabilities.

Parameters:
- `name` (optional): Filter processes by name (supports wildcards)
- `top` (optional): Limit to top N processes
- `sort_by` (optional): Property to sort by (e.g., CPU, WorkingSet)
- `timeout` (optional): Command timeout in seconds (1-300, default 60)

Example:
```python
result = await get_processes(
    top=5,
    sort_by="CPU"
)
```

### get_event_logs

Access Windows event logs with filtering capabilities.

Parameters:
- `logname` (required): Name of the event log (System, Application, Security, etc.)
- `newest` (optional): Number of most recent events to retrieve (default 10)
- `level` (optional): Filter by event level (1: Critical, 2: Error, 3: Warning, 4: Information)
- `timeout` (optional): Command timeout in seconds (1-300, default 60)

Example:
```python
result = await get_event_logs(
    logname="System",
    newest=5,
    level=2  # Error events only
)
```

### generate_script_from_template

Generate PowerShell scripts using predefined templates.

Parameters:
- `template_name` (required): Name of the template to use (without .ps1 extension)
- `parameters` (required): Dictionary of parameters to replace in the template
- `output_path` (optional): Where to save the generated script
- `timeout` (optional): Command timeout in seconds (1-300, default 60)

Example:
```python
result = await generate_script_from_template(
    template_name="basic_script",
    parameters={
        "SYNOPSIS": "My Test Script",
        "DESCRIPTION": "A test script generated from template",
        "PARAM1_DESCRIPTION": "First parameter",
        "PARAM2_DESCRIPTION": "Second parameter",
        "PARAM1_MANDATORY": "true",
        "PARAM2_MANDATORY": "false",
        "PARAM1_DEFAULT": "",
        "PARAM2_DEFAULT": "default_value",
        "MAIN_CODE": "Write-Host 'Hello World!'"
    },
    output_path="test_script.ps1"
)
```

### generate_custom_script

Generate custom PowerShell scripts based on description.

Parameters:
- `description` (required): Natural language description of what the script should do
- `script_type` (required): Type of script to generate (file_ops, service_mgmt, etc.)
- `parameters` (optional): List of parameters the script should accept
- `include_logging` (optional): Whether to include logging functions (default: true)
- `include_error_handling` (optional): Whether to include error handling (default: true)
- `output_path` (optional): Where to save the generated script
- `timeout` (optional): Command timeout in seconds (1-300, default 60)

Example:
```python
result = await generate_custom_script(
    description="Script to monitor CPU usage and log high utilization",
    script_type="monitoring",
    parameters=[
        {
            "name": "ThresholdPercent",
            "type": "int",
            "mandatory": "true",
            "default": "90"
        },
        {
            "name": "LogPath",
            "type": "string",
            "mandatory": "false",
            "default": "cpu_usage.log"
        }
    ],
    output_path="monitor_cpu.ps1"
)
```

### generate_intune_detection_script

Generate Intune detection scripts with proper exit codes and logging.

Parameters:
- `description` (required): What the script should detect
- `detection_logic` (required): PowerShell code that performs the detection
- `output_path` (optional): Where to save the script
- `timeout` (optional): Command timeout in seconds (1-300, default 60)

Example:
```python
result = await generate_intune_detection_script(
    description="Check if Chrome is installed with correct version",
    detection_logic="""
    $app = Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\App Paths\\chrome.exe
    $version = (Get-Item $app.Path).VersionInfo.FileVersion
    $compliant = [version]$version -ge [version]"100.0.0.0"
    Complete-Detection -Compliant $compliant -Message "Chrome version: $version"
    """,
    output_path="detect_chrome.ps1"
)
```

### generate_intune_remediation_script

Generate Intune remediation scripts with system restore points and error handling.

Parameters:
- `description` (required): What the script should remediate
- `remediation_logic` (required): PowerShell code that performs the remediation
- `output_path` (optional): Where to save the script
- `timeout` (optional): Command timeout in seconds (1-300, default 60)

Example:
```python
result = await generate_intune_remediation_script(
    description="Install or update Chrome browser",
    remediation_logic="""
    $installer = "C:\\Windows\\Temp\\ChromeSetup.exe"
    Invoke-WebRequest -Uri "https://dl.google.com/chrome/install/latest/chrome_installer.exe" -OutFile $installer
    Start-Process -FilePath $installer -Args "/silent /install" -Wait
    Remove-Item $installer
    Complete-Remediation -Success $true -Message "Chrome installation completed"
    """,
    output_path="remedy_chrome.ps1"
)
```

### generate_intune_script_pair

Generate both detection and remediation scripts as a matched pair.

Parameters:
- `description` (required): What the scripts should detect and remediate
- `detection_logic` (required): PowerShell code that performs the detection
- `remediation_logic` (required): PowerShell code that performs the remediation
- `output_dir` (optional): Directory to save the scripts
- `timeout` (optional): Command timeout in seconds (1-300, default 60)

Example Usage:

1. Software Installation Check:
```python
result = await generate_intune_script_pair(
    description="Manage Chrome browser installation and version",
    detection_logic="""
    $app = Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\App Paths\\chrome.exe
    $version = (Get-Item $app.Path).VersionInfo.FileVersion
    $compliant = [version]$version -ge [version]"100.0.0.0"
    Complete-Detection -Compliant $compliant -Message "Chrome version: $version"
    """,
    remediation_logic="""
    $installer = "C:\\Windows\\Temp\\ChromeSetup.exe"
    Invoke-WebRequest -Uri "https://dl.google.com/chrome/install/latest/chrome_installer.exe" -OutFile $installer
    Start-Process -FilePath $installer -Args "/silent /install" -Wait
    Remove-Item $installer
    Complete-Remediation -Success $true -Message "Chrome installation completed"
    """,
    output_dir="chrome_scripts"
)
```

2. BitLocker Encryption:
```python
result = await generate_intune_script_pair(
    description="Check and enable BitLocker encryption on system drive",
    detection_logic="""
    $systemDrive = $env:SystemDrive
    $bitlockerVolume = Get-BitLockerVolume -MountPoint $systemDrive
    $compliant = $bitlockerVolume.ProtectionStatus -eq 'On'
    Complete-Detection -Compliant $compliant -Message "BitLocker status: $($bitlockerVolume.ProtectionStatus)"
    """,
    remediation_logic="""
    $systemDrive = $env:SystemDrive
    Enable-BitLocker -MountPoint $systemDrive -TpmProtector -UsedSpaceOnly
    Backup-BitLockerKeyProtector -MountPoint $systemDrive -KeyProtectorId $bitlockerVolume.KeyProtector[0].KeyProtectorId
    Complete-Remediation -Success $true -Message "BitLocker enabled with TPM protection"
    """,
    output_dir="bitlocker_scripts"
)
```

3. Windows Update Configuration:
```python
result = await generate_intune_script_pair(
    description="Check and configure Windows Update settings",
    detection_logic="""
    $wu = New-Object -ComObject Microsoft.Update.AutoUpdate
    $settings = $wu.Settings
    $compliant = ($settings.NotificationLevel -eq 4) -and ($settings.NoAutoRebootWithLoggedOnUsers -eq $true)
    Complete-Detection -Compliant $compliant -Message "Windows Update settings status"
    """,
    remediation_logic="""
    $wu = New-Object -ComObject Microsoft.Update.AutoUpdate
    $settings = $wu.Settings
    $settings.NotificationLevel = 4
    $settings.NoAutoRebootWithLoggedOnUsers = $true
    $settings.Save()
    Complete-Remediation -Success $true -Message "Windows Update settings configured"
    """,
    output_dir="windows_update_scripts"
)
```

4. Security Settings:
```python
result = await generate_intune_script_pair(
    description="Check and configure basic Windows security settings",
    detection_logic="""
    $firewall = Get-NetFirewallProfile
    $uac = (Get-ItemProperty HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System).EnableLUA
    $screenSaver = (Get-ItemProperty 'HKCU:\\Control Panel\\Desktop').ScreenSaveActive
    $compliant = ($firewall.Enabled -contains $true) -and ($uac -eq 1) -and ($screenSaver -eq 1)
    Complete-Detection -Compliant $compliant -Message "Security settings status"
    """,
    remediation_logic="""
    Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
    Set-ItemProperty -Path HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System -Name EnableLUA -Value 1
    Set-ItemProperty -Path 'HKCU:\\Control Panel\\Desktop' -Name ScreenSaveActive -Value 1
    Complete-Remediation -Success $true -Message "Security settings configured"
    """,
    output_dir="security_scripts"
)
```

## BigFix Script Generation Tools

### generate_bigfix_relevance_script

Generate BigFix relevance scripts to determine if computers need action.

Parameters:
- `description` (required): What the script should check
- `relevance_logic` (required): PowerShell code that determines relevance
- `output_path` (optional): Where to save the script
- `timeout` (optional): Command timeout in seconds (1-300, default 60)

Example:
```python
result = await generate_bigfix_relevance_script(
    description="Check if Chrome needs updating to version 100.0.0.0",
    relevance_logic="""
    try {
        $app = Get-ItemProperty "HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\App Paths\\chrome.exe" -ErrorAction Stop
        $version = (Get-Item $app.'(Default)').VersionInfo.FileVersion
        $needsUpdate = [version]$version -lt [version]"100.0.0.0"
        Complete-Relevance -Relevant $needsUpdate -Message "Chrome version: $version (Target: 100.0.0.0+)"
    } catch {
        Complete-Relevance -Relevant $true -Message "Chrome not found - installation needed"
    }
    """,
    output_path="chrome_relevance.ps1"
)
```

### generate_bigfix_action_script

Generate BigFix action scripts to perform remediation or configuration changes.

Parameters:
- `description` (required): What the script should accomplish
- `action_logic` (required): PowerShell code that performs the action
- `output_path` (optional): Where to save the script
- `timeout` (optional): Command timeout in seconds (1-300, default 60)

Example:
```python
result = await generate_bigfix_action_script(
    description="Install Chrome browser to latest version",
    action_logic="""
    try {
        $installer = "$env:TEMP\\ChromeSetup.exe"
        Write-BigFixLog "Downloading Chrome installer..."
        Invoke-WebRequest -Uri "https://dl.google.com/chrome/install/latest/chrome_installer.exe" -OutFile $installer -UseBasicParsing
        Write-BigFixLog "Installing Chrome silently..."
        Start-Process -FilePath $installer -Args "/silent /install" -Wait
        Remove-Item $installer -Force
        Complete-Action -Result "Success" -Message "Chrome installation completed successfully"
    } catch {
        Complete-Action -Result "RetryableFailure" -Message "Chrome installation failed: $($_.Exception.Message)"
    }
    """,
    output_path="chrome_action.ps1"
)
```

### generate_bigfix_script_pair

Generate both relevance and action scripts as a matched pair for BigFix fixlet deployment.

Parameters:
- `description` (required): What the scripts should accomplish
- `relevance_logic` (required): PowerShell code that determines relevance
- `action_logic` (required): PowerShell code that performs the action
- `output_dir` (optional): Directory to save the scripts
- `timeout` (optional): Command timeout in seconds (1-300, default 60)

Example Usage:

1. Chrome Browser Management:
```python
result = await generate_bigfix_script_pair(
    description="Manage Chrome browser installation with version 100.0.0.0 or higher",
    relevance_logic="""
    try {
        $app = Get-ItemProperty "HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\App Paths\\chrome.exe" -ErrorAction Stop
        $version = (Get-Item $app.'(Default)').VersionInfo.FileVersion
        $needsAction = [version]$version -lt [version]"100.0.0.0"
        Complete-Relevance -Relevant $needsAction -Message "Chrome version: $version (Target: 100.0.0.0+)"
    } catch {
        Complete-Relevance -Relevant $true -Message "Chrome not found - installation needed"
    }
    """,
    action_logic="""
    try {
        $installer = "$env:TEMP\\ChromeSetup.exe"
        Write-BigFixLog "Downloading Chrome installer..."
        Invoke-WebRequest -Uri "https://dl.google.com/chrome/install/latest/chrome_installer.exe" -OutFile $installer -UseBasicParsing
        Write-BigFixLog "Installing Chrome silently..."
        Start-Process -FilePath $installer -Args "/silent /install" -Wait
        Remove-Item $installer -Force
        Complete-Action -Result "Success" -Message "Chrome installation completed successfully"
    } catch {
        Complete-Action -Result "RetryableFailure" -Message "Chrome installation failed: $($_.Exception.Message)"
    }
    """,
    output_dir="chrome_bigfix_scripts"
)
```

2. Windows Update Configuration:
```python
result = await generate_bigfix_script_pair(
    description="Ensure Windows Update service is running and configured properly",
    relevance_logic="""
    $service = Get-Service -Name "wuauserv" -ErrorAction SilentlyContinue
    $needsAction = ($service.Status -ne "Running") -or ($service.StartType -ne "Automatic")
    Complete-Relevance -Relevant $needsAction -Message "Windows Update service status: $($service.Status), StartType: $($service.StartType)"
    """,
    action_logic="""
    try {
        Set-Service -Name "wuauserv" -StartupType Automatic
        Start-Service -Name "wuauserv"
        Complete-Action -Result "Success" -Message "Windows Update service configured and started"
    } catch {
        Complete-Action -Result "RetryableFailure" -Message "Failed to configure Windows Update service: $($_.Exception.Message)"
    }
    """,
    output_dir="windows_update_bigfix_scripts"
)
```

3. Security Settings Configuration:
```python
result = await generate_bigfix_script_pair(
    description="Ensure basic Windows security settings are properly configured",
    relevance_logic="""
    $firewall = Get-NetFirewallProfile
    $uac = (Get-ItemProperty HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System).EnableLUA
    $firewallOk = ($firewall | Where-Object { $_.Enabled -eq $false }).Count -eq 0
    $needsAction = (-not $firewallOk) -or ($uac -ne 1)
    Complete-Relevance -Relevant $needsAction -Message "Security settings check - Firewall OK: $firewallOk, UAC Enabled: $($uac -eq 1)"
    """,
    action_logic="""
    try {
        Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
        Set-ItemProperty -Path HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System -Name EnableLUA -Value 1
        Complete-Action -Result "Success" -Message "Security settings configured successfully"
    } catch {
        Complete-Action -Result "RetryableFailure" -Message "Failed to configure security settings: $($_.Exception.Message)"
    }
    """,
    output_dir="security_bigfix_scripts"
)
```

## Security Features

The server implements several security measures:

1. Blocks dangerous commands like:
   - Recursive deletions
   - Drive formatting
   - System shutdown/restart
   - Service manipulation
   - User account manipulation
   - Dynamic code execution

2. Command timeout enforcement
3. Non-interactive mode to prevent hangs
4. No profile loading to ensure clean execution environment
5. JSON output formatting for consistent data structures
6. Input validation for all tool parameters

## Development

The project uses modern Python packaging tools and includes full type hints support. To set up a development environment:

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install development dependencies:
```bash
pip install -e .
```

## Contributing

Contributions are welcome! Please ensure any changes maintain the security standards of the server.

## License

MIT License
