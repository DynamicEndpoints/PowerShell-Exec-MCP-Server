<#
.SYNOPSIS
    {{SYNOPSIS}}
.DESCRIPTION
    BigFix action script to fix {{DESCRIPTION}}
.NOTES
    Author: PowerShell MCP Server
    Date: {{DATE}}
    BigFix Action Exit Codes:
        0 - Action completed successfully
        1 - Action failed - retry
        2 - Action failed - don't retry
    
    Reference: IBM BigFix Documentation
    - Action Scripts: https://help.hcltechsw.com/bigfix/11.0/platform/Platform/Console/c_creating_action_scripts.html
    - Exit Codes: https://help.hcltechsw.com/bigfix/11.0/platform/Platform/Console/c_action_script_exit_codes.html
#>

# Error handling
$ErrorActionPreference = "Stop"
$ScriptError = $false

# Function to write to BigFix client log
function Write-BigFixLog {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$false)]
        [ValidateSet("Information", "Warning", "Error")]
        [string]$Level = "Information"
    )
    
    try {
        $LogPath = "$env:ProgramFiles(x86)\BigFix Enterprise\BES Client\BESClientLog"
        $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $LogEntry = "[$Timestamp] [$Level] PowerShell Action: $Message"
        
        # Write to BigFix client log if available
        if (Test-Path (Split-Path $LogPath)) {
            Add-Content -Path $LogPath -Value $LogEntry -ErrorAction SilentlyContinue
        }
        
        # Also write to Application Event Log
        $EventSource = "BigFixAction"
        if (-not [System.Diagnostics.EventLog]::SourceExists($EventSource)) {
            [System.Diagnostics.EventLog]::CreateEventSource($EventSource, "Application")
        }
        
        $EventType = switch ($Level) {
            "Error" { "Error" }
            "Warning" { "Warning" }
            default { "Information" }
        }
        
        Write-EventLog -LogName Application -Source $EventSource -EventId 2001 `
            -EntryType $EventType -Message $Message
    }
    catch {
        # If logging fails, write to standard output
        Write-Host "[$Level] $Message"
    }
}

# Function to create system restore point
function New-ActionRestorePoint {
    param (
        [string]$Description = "BigFix Action"
    )
    
    try {
        # Enable System Restore if not already enabled
        Enable-ComputerRestore -Drive $env:SystemDrive
        
        # Create restore point
        Checkpoint-Computer -Description $Description -RestorePointType "MODIFY_SETTINGS"
        Write-BigFixLog -Message "Created system restore point: $Description"
    }
    catch {
        Write-BigFixLog -Level Warning -Message "Failed to create system restore point: $($_.Exception.Message)"
    }
}

# Function to handle action completion
function Complete-Action {
    param (
        [Parameter(Mandatory=$true)]
        [ValidateSet("Success", "RetryableFailure", "NonRetryableFailure")]
        [string]$Result,
        
        [Parameter(Mandatory=$false)]
        [string]$Message = ""
    )
    
    if ($Message) {
        $LogLevel = switch ($Result) {
            "Success" { "Information" }
            "RetryableFailure" { "Warning" }
            "NonRetryableFailure" { "Error" }
        }
        Write-BigFixLog -Message $Message -Level $LogLevel
    }
    
    $ExitCode = switch ($Result) {
        "Success" { 0 }
        "RetryableFailure" { 1 }
        "NonRetryableFailure" { 2 }
    }
    
    Write-BigFixLog -Message "Action completed with result: $Result (Exit Code: $ExitCode)"
    exit $ExitCode
}

try {
    Write-BigFixLog -Message "Starting BigFix action for {{DESCRIPTION}}"
    
    # Create system restore point before making changes
    New-ActionRestorePoint -Description "Pre-{{DESCRIPTION}}-Action"
    
    {{ACTION_LOGIC}}
    
    # Example action pattern:
    # $installer = "C:\Windows\Temp\app-installer.exe"
    # Invoke-WebRequest -Uri "https://example.com/installer.exe" -OutFile $installer
    # Start-Process -FilePath $installer -Args "/silent" -Wait
    # Remove-Item $installer -Force
    # Complete-Action -Result "Success" -Message "Application installed successfully"
}
catch {
    $ScriptError = $true
    Write-BigFixLog -Level Error -Message "Error during action execution: $($_.Exception.Message)`nStack Trace: $($_.ScriptStackTrace)"
    Complete-Action -Result "RetryableFailure" -Message "Action failed due to error: $($_.Exception.Message)"
}
finally {
    if (-not $ScriptError) {
        Write-BigFixLog -Message "Action execution completed successfully"
    }
}
