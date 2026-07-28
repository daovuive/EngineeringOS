$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "======================================="
Write-Host " Engineering OS Doctor"
Write-Host "======================================="
Write-Host ""

$failed = 0

function Test-Command {

    param(
        [string]$Name
    )

    $cmd = Get-Command $Name -ErrorAction SilentlyContinue

    if ($null -eq $cmd) {

        Write-Host "[FAIL] $Name"
        $script:failed++

    }
    else {

        Write-Host "[ OK ] $Name"

    }

}

function Test-File {

    param(
        [string]$Path
    )

    if (Test-Path $Path) {

        Write-Host "[ OK ] $Path"

    }
    else {

        Write-Host "[FAIL] $Path"
        $script:failed++

    }

}

Write-Host "System"
Write-Host "------"

Test-Command "pwsh"
Test-Command "git"

Write-Host ""

Write-Host "Configuration"
Write-Host "-------------"

Test-File "configs/project-structure.json"
Test-File "configs/templates.json"
Test-File "configs/settings.json"
Test-File "configs/ai-runtime.json"

Write-Host ""

Write-Host "Templates"
Write-Host "---------"

Test-File "templates/README.md"
Test-File "templates/ADR.md"
Test-File "templates/LICENSE.txt"
Test-File "templates/gitignore.txt"

Write-Host ""

Write-Host "Project"
Write-Host "-------"

Test-File "README.md"
Test-File "eng.ps1"

Write-Host ""

Write-Host "Optional"

$ollama = Get-Command "ollama" -ErrorAction SilentlyContinue

if ($null -eq $ollama) {

    Write-Host "[WARN] Ollama not installed"

}
else {

    Write-Host "[ OK ] Ollama"

}

Write-Host ""

if ($failed -eq 0) {

    Write-Host "Doctor completed successfully."

}
else {

    Write-Host "Doctor found $failed problem(s)."

    exit 1

}