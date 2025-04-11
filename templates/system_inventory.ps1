<#
.SYNOPSIS
    System Inventory Script
.DESCRIPTION
    Collects detailed system information and exports it to a file
.PARAMETER OutputFormat
    The format to export data (CSV, JSON, HTML)
.PARAMETER OutputPath
    The path where the output file will be saved
.PARAMETER IncludeHardware
    Include hardware information in the report
.PARAMETER IncludeSoftware
    Include installed software in the report
.PARAMETER IncludeServices
    Include services information in the report
.PARAMETER IncludeNetworking
    Include networking information in the report
.EXAMPLE
    .\system_inventory.ps1 -OutputFormat JSON -OutputPath "C:\Reports\inventory.json" -IncludeHardware -IncludeSoftware
.NOTES
    Author: PowerShell MCP Server
    Date: {{DATE}}
#>

param (
    [Parameter(Mandatory=$false)]
    [ValidateSet("CSV", "JSON", "HTML")]
    [string]$OutputFormat = "JSON",
    
    [Parameter(Mandatory=$false)]
    [string]$OutputPath = ".\system_inventory_$(Get-Date -Format 'yyyyMMdd_HHmmss').$($OutputFormat.ToLower())",
    
    [Parameter(Mandatory=$false)]
    [switch]$IncludeHardware = $true,
    
    [Parameter(Mandatory=$false)]
    [switch]$IncludeSoftware = $true,
    
    [Parameter(Mandatory=$false)]
    [switch]$IncludeServices = $true,
    
    [Parameter(Mandatory=$false)]
    [switch]$IncludeNetworking = $true
)

# Function to write log messages
function Write-Log {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$false)]
        [ValidateSet("INFO", "WARNING", "ERROR")]
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] [$Level] $Message"
}

# Function to handle errors
function Handle-Error {
    param (
        [Parameter(Mandatory=$true)]
        [System.Management.Automation.ErrorRecord]$ErrorRecord
    )
    
    Write-Log -Level ERROR -Message "Error occurred: $($ErrorRecord.Exception.Message)"
    Write-Log -Level ERROR -Message "Error details: $($ErrorRecord | Out-String)"
}

# Main inventory collection function
function Get-SystemInventory {
    $inventory = @{
        ComputerName = $env:COMPUTERNAME
        CollectionDate = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        OperatingSystem = Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, BuildNumber, OSArchitecture
    }
    
    # Hardware information
    if ($IncludeHardware) {
        Write-Log "Collecting hardware information..."
        try {
            $inventory.Hardware = @{
                Processor = Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed
                Memory = Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum | Select-Object @{Name="TotalGB";Expression={[math]::Round($_.Sum / 1GB, 2)}}
                DiskDrives = Get-CimInstance Win32_DiskDrive | Select-Object Model, Size, MediaType
                BiosInfo = Get-CimInstance Win32_BIOS | Select-Object Manufacturer, Name, SerialNumber, Version
            }
        }
        catch {
            Handle-Error -ErrorRecord $_
        }
    }
    
    # Software information
    if ($IncludeSoftware) {
        Write-Log "Collecting software information..."
        try {
            $inventory.Software = @{
                InstalledApplications = Get-ItemProperty HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* | 
                                        Where-Object { $_.DisplayName } | 
                                        Select-Object DisplayName, DisplayVersion, Publisher, InstallDate |
                                        Sort-Object DisplayName
            }
        }
        catch {
            Handle-Error -ErrorRecord $_
        }
    }
    
    # Services information
    if ($IncludeServices) {
        Write-Log "Collecting services information..."
        try {
            $inventory.Services = @{
                RunningServices = Get-Service | Where-Object { $_.Status -eq "Running" } | 
                                  Select-Object Name, DisplayName, Status, StartType |
                                  Sort-Object DisplayName
            }
        }
        catch {
            Handle-Error -ErrorRecord $_
        }
    }
    
    # Networking information
    if ($IncludeNetworking) {
        Write-Log "Collecting networking information..."
        try {
            $inventory.Networking = @{
                NetworkAdapters = Get-NetAdapter | Select-Object Name, InterfaceDescription, Status, LinkSpeed, MacAddress
                IPConfiguration = Get-NetIPConfiguration | Select-Object InterfaceAlias, IPv4Address, IPv6Address, DNSServer
            }
        }
        catch {
            Handle-Error -ErrorRecord $_
        }
    }
    
    return $inventory
}

# Main execution
try {
    Write-Log "Starting system inventory collection..."
    
    $inventory = Get-SystemInventory
    
    # Export the data in the specified format
    Write-Log "Exporting data to $OutputPath in $OutputFormat format..."
    
    switch ($OutputFormat) {
        "CSV" {
            $inventory | ConvertTo-Csv -NoTypeInformation | Out-File -FilePath $OutputPath
        }
        "JSON" {
            $inventory | ConvertTo-Json -Depth 10 | Out-File -FilePath $OutputPath
        }
        "HTML" {
            # Create HTML content
            $htmlContent = @()
            $htmlContent += "<!DOCTYPE html>"
            $htmlContent += "<html>"
            $htmlContent += "<head>"
            $htmlContent += "    <title>System Inventory Report</title>"
            $htmlContent += "    <style>"
            $htmlContent += "        body { font-family: Arial, sans-serif; margin: 20px; }"
            $htmlContent += "        h1, h2, h3 { color: #0066cc; }"
            $htmlContent += "        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }"
            $htmlContent += "        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }"
            $htmlContent += "        th { background-color: #f2f2f2; }"
            $htmlContent += "        tr:nth-child(even) { background-color: #f9f9f9; }"
            $htmlContent += "    </style>"
            $htmlContent += "</head>"
            $htmlContent += "<body>"
            $htmlContent += "    <h1>System Inventory Report</h1>"
            $htmlContent += "    <p>Computer Name: $($inventory.ComputerName)</p>"
            $htmlContent += "    <p>Collection Date: $($inventory.CollectionDate)</p>"
            
            # Operating System
            $htmlContent += "    <h2>Operating System</h2>"
            $htmlContent += "    <table><tr><th>Property</th><th>Value</th></tr>"
            $htmlContent += "    <tr><td>OS Name</td><td>$($inventory.OperatingSystem.Caption)</td></tr>"
            $htmlContent += "    <tr><td>Version</td><td>$($inventory.OperatingSystem.Version)</td></tr>"
            $htmlContent += "    <tr><td>Build Number</td><td>$($inventory.OperatingSystem.BuildNumber)</td></tr>"
            $htmlContent += "    <tr><td>Architecture</td><td>$($inventory.OperatingSystem.OSArchitecture)</td></tr>"
            $htmlContent += "    </table>"
            
            # Hardware
            if ($IncludeHardware) {
                $htmlContent += "    <h2>Hardware</h2>"
                
                $htmlContent += "    <h3>Processor</h3>"
                $htmlContent += "    <table><tr><th>Property</th><th>Value</th></tr>"
                $htmlContent += "    <tr><td>Name</td><td>$($inventory.Hardware.Processor.Name)</td></tr>"
                $htmlContent += "    <tr><td>Cores</td><td>$($inventory.Hardware.Processor.NumberOfCores)</td></tr>"
                $htmlContent += "    <tr><td>Logical Processors</td><td>$($inventory.Hardware.Processor.NumberOfLogicalProcessors)</td></tr>"
                $htmlContent += "    <tr><td>Max Clock Speed</td><td>$($inventory.Hardware.Processor.MaxClockSpeed) MHz</td></tr>"
                $htmlContent += "    </table>"
                
                $htmlContent += "    <h3>Memory</h3>"
                $htmlContent += "    <table><tr><th>Property</th><th>Value</th></tr>"
                $htmlContent += "    <tr><td>Total Memory</td><td>$($inventory.Hardware.Memory.TotalGB) GB</td></tr>"
                $htmlContent += "    </table>"
            }
            
            # Add more sections for Software, Services, and Networking as needed
            
            $htmlContent += "</body>"
            $htmlContent += "</html>"
            
            $htmlContent | Out-File -FilePath $OutputPath
        }
    }
    
    Write-Log "System inventory completed successfully. Output saved to: $OutputPath"
}
catch {
    Handle-Error -ErrorRecord $_
    exit 1
}
