<#
.SYNOPSIS
    {{SYNOPSIS}}
.DESCRIPTION
    BigFix relevance script to check {{DESCRIPTION}}
.NOTES
    Author: PowerShell MCP Server
    Date: {{DATE}}
    BigFix Relevance Logic:
        True - Computer is relevant and needs action
        False - Computer is not relevant (compliant)
    
    Reference: IBM BigFix Documentation
    - Relevance Language: https://help.hcltechsw.com/bigfix/11.0/relevance/Relevance/c_relevance_language.html
    - Action Scripts: https://help.hcltechsw.com/bigfix/11.0/platform/Platform/Console/c_creating_action_scripts.html
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
        $LogEntry = "[$Timestamp] [$Level] PowerShell Relevance: $Message"
        
        # Write to BigFix client log if available
        if (Test-Path (Split-Path $LogPath)) {
            Add-Content -Path $LogPath -Value $LogEntry -ErrorAction SilentlyContinue
        }
        
        # Also write to Application Event Log
        $EventSource = "BigFixRelevance"
        if (-not [System.Diagnostics.EventLog]::SourceExists($EventSource)) {
            [System.Diagnostics.EventLog]::CreateEventSource($EventSource, "Application")
        }
        
        $EventType = switch ($Level) {
            "Error" { "Error" }
            "Warning" { "Warning" }
            default { "Information" }
        }
        
        Write-EventLog -LogName Application -Source $EventSource -EventId 2000 `
            -EntryType $EventType -Message $Message
    }
    catch {
        # If logging fails, write to standard output
        Write-Host "[$Level] $Message"
    }
}

# Function to handle relevance completion
function Complete-Relevance {
    param (
        [Parameter(Mandatory=$true)]
        [bool]$Relevant,
        
        [Parameter(Mandatory=$false)]
        [string]$Message = ""
    )
    
    if ($Message) {
        Write-BigFixLog -Message $Message -Level $(if ($Relevant) { "Warning" } else { "Information" })
    }
    
    # BigFix expects specific output format
    if ($Relevant) {
        Write-Output "TRUE"
        Write-BigFixLog -Message "Computer is RELEVANT - Action required"
    } else {
        Write-Output "FALSE"
        Write-BigFixLog -Message "Computer is NOT RELEVANT - Compliant"
    }
    
    exit $(if ($Relevant) { 1 } else { 0 })
}

try {
    Write-BigFixLog -Message "Starting relevance check for {{DESCRIPTION}}"
    
    {{RELEVANCE_LOGIC}}
    
    # Example relevance pattern:
    # $softwareInstalled = Get-WmiObject -Class Win32_Product | Where-Object { $_.Name -like "*Chrome*" }
    # $relevant = $softwareInstalled -eq $null
    # Complete-Relevance -Relevant $relevant -Message "Chrome installation status: $(if ($relevant) { 'Missing' } else { 'Installed' })"
}
catch {
    $ScriptError = $true
    Write-BigFixLog -Level Error -Message "Error during relevance check: $($_.Exception.Message)`nStack Trace: $($_.ScriptStackTrace)"
    Write-Output "FALSE"  # Default to not relevant on error to prevent unwanted actions
    exit 2
}
finally {
    if (-not $ScriptError) {
        Write-BigFixLog -Message "Relevance check completed successfully"
    }
}
