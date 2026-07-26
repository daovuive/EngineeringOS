<#
=====================================================
 Engineering OS CLI
 Version : 1.1
=====================================================
#>

param(
    [Parameter(Position = 0)]
    [string]$Command = "help"
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Scripts = Join-Path $Root "scripts"

function Banner {

    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "        Engineering OS CLI v1.1"
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Help {

    Banner

    Write-Host "Usage"
    Write-Host "-----"
    Write-Host "  .\eng.ps1 init"
    Write-Host "  .\eng.ps1 doctor"
    Write-Host "  .\eng.ps1 setup"
    Write-Host "  .\eng.ps1 run"
    Write-Host "  .\eng.ps1 clean"
    Write-Host "  .\eng.ps1 update"
    Write-Host "  .\eng.ps1 help"
    Write-Host ""

}

function Invoke-EngineeringScript {

    param([string]$Name)

    if (!(Test-Path $Scripts)) {
        Write-Host "scripts folder not found." -ForegroundColor Red
        exit 1
    }

    $script = Join-Path $Scripts "$Name.ps1"

    if (!(Test-Path $script)) {

        Write-Host ""
        Write-Host "Command '$Name' not found." -ForegroundColor Red
        Write-Host ""

        Help

        exit 1
    }

    try {

        & $script

    }
    catch {

        Write-Host ""
        Write-Host "==========================================" -ForegroundColor Red
        Write-Host "Script Failed"
        Write-Host "==========================================" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Yellow
        Write-Host ""

        exit 1

    }

}

switch ($Command.ToLower()) {

    "init"   { Invoke-EngineeringScript "init" }

    "doctor" { Invoke-EngineeringScript "doctor" }

    "setup"  { Invoke-EngineeringScript "setup" }

    "run"    { Invoke-EngineeringScript "run" }

    "clean"  { Invoke-EngineeringScript "clean" }

    "update" { Invoke-EngineeringScript "update" }

    "help"   { Help }

    default {

        Write-Host ""
        Write-Host "Unknown command : $Command" -ForegroundColor Red
        Help

    }

}