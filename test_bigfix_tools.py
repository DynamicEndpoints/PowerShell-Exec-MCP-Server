#!/usr/bin/env python3
"""
Test script for the new BigFix script generation tools
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from server import generate_bigfix_relevance_script, generate_bigfix_action_script, generate_bigfix_script_pair

async def test_bigfix_tools():
    """Test the new BigFix script generation tools"""
    print("Testing BigFix script generation tools...")
    
    # Test BigFix relevance script generation
    print("\n1. Testing BigFix relevance script generation...")
    relevance_result = await generate_bigfix_relevance_script(
        description="Test if Chrome browser needs updating",
        relevance_logic='''
        try {
            $app = Get-ItemProperty "HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\App Paths\\chrome.exe" -ErrorAction Stop
            $version = (Get-Item $app.'(Default)').VersionInfo.FileVersion
            $needsUpdate = [version]$version -lt [version]"100.0.0.0"
            Complete-Relevance -Relevant $needsUpdate -Message "Chrome version: $version"
        } catch {
            Complete-Relevance -Relevant $true -Message "Chrome not found"
        }
        '''
    )
    print(f"✓ Relevance script generated successfully ({len(relevance_result)} characters)")
    
    # Test BigFix action script generation
    print("\n2. Testing BigFix action script generation...")
    action_result = await generate_bigfix_action_script(
        description="Install Chrome browser",
        action_logic='''
        try {
            $installer = "$env:TEMP\\ChromeSetup.exe"
            Write-BigFixLog "Downloading Chrome installer..."
            Invoke-WebRequest -Uri "https://dl.google.com/chrome/install/latest/chrome_installer.exe" -OutFile $installer
            Start-Process -FilePath $installer -Args "/silent /install" -Wait
            Remove-Item $installer -Force
            Complete-Action -Result "Success" -Message "Chrome installed successfully"
        } catch {
            Complete-Action -Result "RetryableFailure" -Message "Installation failed: $($_.Exception.Message)"
        }
        '''
    )
    print(f"✓ Action script generated successfully ({len(action_result)} characters)")
    
    # Test BigFix script pair generation
    print("\n3. Testing BigFix script pair generation...")
    pair_result = await generate_bigfix_script_pair(
        description="Manage Chrome browser installation",
        relevance_logic='''
        try {
            $app = Get-ItemProperty "HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\App Paths\\chrome.exe" -ErrorAction Stop
            $version = (Get-Item $app.'(Default)').VersionInfo.FileVersion
            $needsUpdate = [version]$version -lt [version]"100.0.0.0"
            Complete-Relevance -Relevant $needsUpdate -Message "Chrome version: $version"
        } catch {
            Complete-Relevance -Relevant $true -Message "Chrome not found"
        }
        ''',
        action_logic='''
        try {
            $installer = "$env:TEMP\\ChromeSetup.exe"
            Write-BigFixLog "Downloading Chrome installer..."
            Invoke-WebRequest -Uri "https://dl.google.com/chrome/install/latest/chrome_installer.exe" -OutFile $installer
            Start-Process -FilePath $installer -Args "/silent /install" -Wait
            Remove-Item $installer -Force
            Complete-Action -Result "Success" -Message "Chrome installed successfully"
        } catch {
            Complete-Action -Result "RetryableFailure" -Message "Installation failed: $($_.Exception.Message)"
        }
        '''
    )
    print(f"✓ Script pair generated successfully:")
    print(f"  - Relevance script: {len(pair_result['relevance_script'])} characters")
    print(f"  - Action script: {len(pair_result['action_script'])} characters")
    
    print("\n🎉 All BigFix script generation tools are working correctly!")
    return True

if __name__ == "__main__":
    asyncio.run(test_bigfix_tools())
