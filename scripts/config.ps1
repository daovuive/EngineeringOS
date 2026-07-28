param(
    [string]$StructureConfig = "configs/project-structure.json",
    [string]$TemplateConfig = "configs/templates.json"
)

$ErrorActionPreference = "Stop"

function Load-Json {
    param([string]$Path)

    if (!(Test-Path $Path)) {
        throw "Configuration file not found: $Path"
    }

    Get-Content $Path -Raw | ConvertFrom-Json
}

function Ensure-Directory {
    param([string]$Path)

    if (!(Test-Path $Path)) {

        New-Item `
            -ItemType Directory `
            -Force `
            -Path $Path | Out-Null

        Write-Host "[CREATE] Folder : $Path"

    }

}

function Ensure-ParentDirectory {
    param([string]$File)

    $parent = Split-Path $File -Parent

    if (![string]::IsNullOrWhiteSpace($parent)) {
        Ensure-Directory $parent
    }

}

function Find-Template {
    param(
        $Templates,
        [string]$TemplateId
    )

    foreach ($item in $Templates.templates) {

        if ($item.id -eq $TemplateId) {
            return $item
        }

    }

    return $null
}

$structure = Load-Json $StructureConfig
$templateConfig = Load-Json $TemplateConfig

$templateRoot = $templateConfig.templateDirectory

Write-Host ""
Write-Host "======================================="
Write-Host " Engineering OS Synchronization"
Write-Host "======================================="
Write-Host ""

foreach ($folder in $structure.folders) {

    Ensure-Directory $folder.path

}

foreach ($file in $structure.files) {

    if (Test-Path $file.path) {
        continue
    }

    Ensure-ParentDirectory $file.path

    $template = Find-Template `
        -Templates $templateConfig `
        -TemplateId $file.template

    if ($null -eq $template) {
        throw "Unknown template: $($file.template)"
    }

    if ($null -eq $template.source) {

        New-Item `
            -ItemType File `
            -Force `
            -Path $file.path | Out-Null

    }
    else {

        $source = Join-Path `
            $templateRoot `
            $template.source

        Copy-Item `
            $source `
            $file.path

    }

    Write-Host "[CREATE] File   : $($file.path)"

}

Write-Host ""
Write-Host "Synchronization completed."