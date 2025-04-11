<#
.SYNOPSIS
    {{SYNOPSIS}}
.DESCRIPTION
    Intune detection script to check {{DESCRIPTION}}
.NOTES
    Author: PowerShell MCP Server
    Date: {{DATE}}
    Exit Codes:
        0 - Compliant/Success
        1 - Non-compliant/Failure
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
        $EventSource = "IntuneDetection"
        
        if (-not [System.Diagnostics.EventLog]::SourceExists($EventSource)) {
            [System.Diagnostics.EventLog]::CreateEventSource($EventSource, "Application")
        }
        
        Write-EventLog -LogName Application -Source $EventSource -EventId 1000 `
            -EntryType $Level -Message $Message
    }
    catch {
        # If event log writing fails, write to standard output
        Write-Host "[$Level] $Message"
    }
}

# Function to handle script completion
function Complete-Detection {
    param (
        [Parameter(Mandatory=$true)]
        [bool]$Compliant,
        
        [Parameter(Mandatory=$false)]
        [string]$Message = ""
    )
    
    if ($Message) {
        Write-IntuneLog -Message $Message -Level $(if ($Compliant) { "Information" } else { "Warning" })
    }
    
    exit $(if ($Compliant) { 0 } else { 1 })
}

try {
    Write-IntuneLog -Message "Starting detection check for {{DESCRIPTION}}"
    
    {{DETECTION_LOGIC}}
    
    # Example detection pattern:
    # $result = Test-Path "C:\Program Files\App\app.exe"
    # Complete-Detection -Compliant $result -Message "Application installation status: $result"
}
catch {
    $ScriptError = $true
    Write-IntuneLog -Level Error -Message "Error during detection: $($_.Exception.Message)`nStack Trace: $($_.ScriptStackTrace)"
    exit 2
}
finally {
    if (-not $ScriptError) {
        Write-IntuneLog -Message "Detection check completed successfully"
    }
}
