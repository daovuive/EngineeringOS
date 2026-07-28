<#
Engineering OS

Project Validation

Responsibilities

- Validate configuration files
- Validate folder structure
- Validate file structure
- Validate templates

No modification is performed.
#>

param(
    [string]$StructureConfig = "configs/project-structure.json",
    [string]$TemplateConfig = "configs/templates.json",
    [string]$SchemaFile = "configs/project-structure.schema.json"
)

$ErrorActionPreference = "Stop"

# ------------------------------------------------------------
# Utilities
# ------------------------------------------------------------

function Load-Json {

    param([string]$Path)

    if (!(Test-Path $Path)) {
        throw "Configuration file not found: $Path"
    }

    return Get-Content $Path -Raw | ConvertFrom-Json

}

# ------------------------------------------------------------
# Validate Configuration Files
# ------------------------------------------------------------

Write-Host ""
Write-Host "======================================="
Write-Host " Engineering OS Validation"
Write-Host "======================================="
Write-Host ""

Test-Path $StructureConfig | Out-Null
if (!(Test-Path $StructureConfig)) {
    throw "Missing: $StructureConfig"
}

Test-Path $TemplateConfig | Out-Null
if (!(Test-Path $TemplateConfig)) {
    throw "Missing: $TemplateConfig"
}

Write-Host "[ OK ] $StructureConfig"
Write-Host "[ OK ] $TemplateConfig"

# ------------------------------------------------------------
# Validate JSON Schema
# ------------------------------------------------------------

if (Test-Path $SchemaFile) {

    try {

        Get-Content $StructureConfig -Raw |
            Test-Json `
                -SchemaFile $SchemaFile `
            | Out-Null

        Write-Host "[ OK ] project-structure.schema.json"

    }
    catch {

        Write-Host "[FAIL] Invalid project structure."

        throw

    }

}
else {

    Write-Host "[WARN] Schema file not found."

}

# ------------------------------------------------------------
# Load Configuration
# ------------------------------------------------------------

$structure = Load-Json $StructureConfig
$templates = Load-Json $TemplateConfig

Write-Host ""

# ------------------------------------------------------------
# Validate Folders
# ------------------------------------------------------------

$missingFolders = 0

foreach ($folder in $structure.folders) {

    if (Test-Path $folder.path) {

        Write-Host "[ OK ] Folder : $($folder.path)"

    }
    else {

        Write-Host "[MISS] Folder : $($folder.path)"
        $missingFolders++

    }

}

Write-Host ""

# ------------------------------------------------------------
# Validate Files
# ------------------------------------------------------------

$missingFiles = 0

foreach ($file in $structure.files) {

    if (Test-Path $file.path) {

        Write-Host "[ OK ] File   : $($file.path)"

    }
    else {

        Write-Host "[MISS] File   : $($file.path)"
        $missingFiles++

    }

}

Write-Host ""

# ------------------------------------------------------------
# Validate Templates
# ------------------------------------------------------------

$templateRoot = $templates.templateDirectory

$missingTemplates = 0

foreach ($template in $templates.templates) {

    if ($null -eq $template.source) {
        continue
    }

    $templateFile = Join-Path `
        $templateRoot `
        $template.source

    if (Test-Path $templateFile) {

        Write-Host "[ OK ] Template : $($template.source)"

    }
    else {

        Write-Host "[MISS] Template : $($template.source)"
        $missingTemplates++

    }

}

Write-Host ""
Write-Host "======================================="
Write-Host ""

$totalErrors =
    $missingFolders +
    $missingFiles +
    $missingTemplates

if ($totalErrors -eq 0) {

    Write-Host "Validation completed successfully."

}
else {

    Write-Host "Validation failed."
    Write-Host ""
    Write-Host "Missing folders   : $missingFolders"
    Write-Host "Missing files     : $missingFiles"
    Write-Host "Missing templates : $missingTemplates"
    Write-Host ""

    exit 1

}