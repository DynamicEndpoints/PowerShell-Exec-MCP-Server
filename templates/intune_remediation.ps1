<#
.SYNOPSIS
    {{SYNOPSIS}}
.DESCRIPTION
    Intune remediation script to fix {{DESCRIPTION}}
.NOTES
    Author: PowerShell MCP Server
    Date: {{DATE}}
    Exit Codes:
        0 - Remediation Success
        1 - Remediation Failed
        2 - Script Error
#>

# Error handling
$ErrorActionPreference = "Stop"
$ScriptError = $false

# Function to write to event log
function Write-IntuneLog {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$false)]
        [ValidateSet("Information", "Warning", "Error")]
        [string]$Level = "Information"
    )
    
    try {
        $EventSource = "IntuneRemediation"
        
        if (-not [System.Diagnostics.EventLog]::SourceExists($EventSource)) {
            [System.Diagnostics.EventLog]::CreateEventSource($EventSource, "Application")
        }
        
        Write-EventLog -LogName Application -Source $EventSource -EventId 1001 `
            -EntryType $Level -Message $Message
    }
    catch {
        # If event log writing fails, write to standard output
        Write-Host "[$Level] $Message"
    }
}

# Function to create system restore point
function New-RemediationRestorePoint {
    param (
        [string]$Description = "Intune Remediation"
    )
    
    try {
        # Enable System Restore if not already enabled
        Enable-ComputerRestore -Drive $env:SystemDrive
        
        # Create restore point
        Checkpoint-Computer -Description $Description -RestorePointType "MODIFY_SETTINGS"
        Write-IntuneLog -Message "Created system restore point: $Description"
    }
    catch {
        Write-IntuneLog -Level Warning -Message "Failed to create system restore point: $($_.Exception.Message)"
    }
}

# Function to handle script completion
function Complete-Remediation {
    param (
        [Parameter(Mandatory=$true)]
        [bool]$Success,
        
        [Parameter(Mandatory=$false)]
        [string]$Message = ""
    )
    
    if ($Message) {
        Write-IntuneLog -Message $Message -Level $(if ($Success) { "Information" } else { "Warning" })
    }
    
    exit $(if ($Success) { 0 } else { 1 })
}

try {
    Write-IntuneLog -Message "Starting remediation for {{DESCRIPTION}}"
    
    # Create system restore point before making changes
    New-RemediationRestorePoint -Description "Pre-{{DESCRIPTION}}-Remediation"
    
    {{REMEDIATION_LOGIC}}
    
    # Example remediation pattern:
    # New-Item -Path "C:\Program Files\App" -ItemType Directory -Force
    # Copy-Item -Path "\\server\share\app.exe" -Destination "C:\Program Files\App\app.exe" -Force
    # Complete-Remediation -Success $true -Message "Successfully installed application"
}
catch {
    $ScriptError = $true
    Write-IntuneLog -Level Error -Message "Error during remediation: $($_.Exception.Message)`nStack Trace: $($_.ScriptStackTrace)"
    exit 2
}
finally {
    if (-not $ScriptError) {
        Write-IntuneLog -Message "Remediation completed successfully"
    }
}
