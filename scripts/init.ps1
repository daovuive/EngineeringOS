param(
    [Parameter(Position = 0)]
    [string]$Command = "help"
)

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ScriptsDir = Join-Path $ScriptRoot "scripts"

function Get-Platform {

    if ($IsWindows) { return "windows" }
    if ($IsLinux)   { return "linux" }
    if ($IsMacOS)   { return "macos" }

    # Fallback cho Windows PowerShell 5.1
    if ($env:OS -eq "Windows_NT") {
        return "windows"
    }

    return "unknown"
}

function Invoke-Init {

    $platform = Get-Platform

    switch ($platform) {

        "windows" {

            $script = Join-Path $ScriptsDir "init.windows.ps1"

            if (!(Test-Path $script)) {
                throw "Cannot find $script"
            }

            & $script
        }

        "linux" {

            $script = Join-Path $ScriptsDir "init.linux.sh"

            if (!(Test-Path $script)) {
                throw "Cannot find $script"
            }

            bash $script
        }

        "macos" {

            $script = Join-Path $ScriptsDir "init.linux.sh"

            if (!(Test-Path $script)) {
                throw "Cannot find $script"
            }

            bash $script
        }

        default {

            throw "Unsupported operating system."

        }

    }

}

switch ($Command.ToLower()) {

    "init" {

        Invoke-Init

    }

    "help" {

        Write-Host ""
        Write-Host "Engineering OS CLI"
        Write-Host ""
        Write-Host "Commands:"
        Write-Host "  init"

    }

    default {

        Write-Host "Unknown command: $Command"

    }

}