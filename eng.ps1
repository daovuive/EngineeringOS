<#
Engineering OS CLI

Entry point of Engineering OS.

Responsibilities:
- Parse command line
- Dispatch commands
- Display help/version

Business logic must be implemented inside scripts/.
#>

param(
    [Parameter(Position = 0)]
    [string]$Command = "help",

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Arguments
)

$ErrorActionPreference = "Stop"

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

$Version = "1.0.0"

# -------------------------------------------------------------
# Banner
# -------------------------------------------------------------

function Show-Banner {

    Write-Host ""
    Write-Host "==========================================="
    Write-Host "           Engineering OS"
    Write-Host "==========================================="
    Write-Host "Version : $Version"
    Write-Host ""

}

# -------------------------------------------------------------
# Invoke Script
# -------------------------------------------------------------

function Invoke-Command {

    param(
        [string]$Script
    )

    $scriptPath = Join-Path $ScriptRoot "scripts\$Script"

    if (!(Test-Path $scriptPath)) {

        throw "Command not implemented: $Script"

    }

    & $scriptPath @Arguments

}

# -------------------------------------------------------------
# Help
# -------------------------------------------------------------

function Show-Help {

    Show-Banner

    Write-Host "Usage"
    Write-Host ""
    Write-Host "    ./eng.ps1 <command>"
    Write-Host ""

    Write-Host "Commands"
    Write-Host ""
    Write-Host "    init"
    Write-Host "        Initialize project."
    Write-Host ""

    Write-Host "    validate"
    Write-Host "        Validate project."
    Write-Host ""

    Write-Host "    sync"
    Write-Host "        Synchronize project."
    Write-Host ""

    Write-Host "    config"
    Write-Host "        Manage configuration."
    Write-Host ""

    Write-Host "    doctor"
    Write-Host "        Check environment."
    Write-Host ""

    Write-Host "    version"
    Write-Host "        Show version."
    Write-Host ""

    Write-Host "    help"
    Write-Host "        Show help."
    Write-Host ""

}

# -------------------------------------------------------------
# Main
# -------------------------------------------------------------

switch ($Command.ToLower()) {

    "init" {

        Invoke-Command "init.ps1"

    }

    "validate" {

        Invoke-Command "validate.ps1"

    }

    "sync" {

        Invoke-Command "sync.ps1"

    }

    "doctor" {

        Invoke-Command "doctor.ps1"

    }

    "config" {

        Invoke-Command "config.ps1"

    }

    "version" {

        Show-Banner

    }

    "help" {

        Show-Help

    }

    default {

        Write-Host ""
        Write-Host "Unknown command: $Command"
        Write-Host ""
        Show-Help

    }

}