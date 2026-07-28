<#
Engineering OS

Project Initialization

Responsibilities

- Read configuration
- Create folder structure
- Create files from templates

Business rules belong elsewhere.
#>

param(
    [string]$StructureConfig = "configs/project-structure.json",
    [string]$TemplateConfig = "configs/templates.json"
)

$ErrorActionPreference = "Stop"

# ------------------------------------------------------------
# Utilities
# ------------------------------------------------------------

function Load-Json {

    param(
        [string]$Path
    )

    if (!(Test-Path $Path)) {
        throw "Configuration file not found: $Path"
    }

    return Get-Content $Path -Raw | ConvertFrom-Json

}

function Ensure-Directory {

    param(
        [string]$Path
    )

    if (!(Test-Path $Path)) {

        New-Item `
            -ItemType Directory `
            -Force `
            -Path $Path | Out-Null

        Write-Host "[CREATE] Folder : $Path"

    }
    else {

        Write-Host "[ OK ]    Folder : $Path"

    }

}

function Ensure-ParentDirectory {

    param(
        [string]$FilePath
    )

    $parent = Split-Path $FilePath -Parent

    if (![string]::IsNullOrWhiteSpace($parent)) {

        Ensure-Directory $parent

    }

}

function Find-Template {

    param(
        $Templates,
        [string]$TemplateId
    )

    foreach($item in $Templates.templates){

        if($item.id -eq $TemplateId){

            return $item

        }

    }

    return $null

}

# ------------------------------------------------------------
# Load Configuration
# ------------------------------------------------------------

$structure = Load-Json $StructureConfig
$templateConfig = Load-Json $TemplateConfig

$templateRoot = $templateConfig.templateDirectory

Write-Host ""
Write-Host "======================================="
Write-Host " Engineering OS Initialization"
Write-Host "======================================="
Write-Host ""

# ------------------------------------------------------------
# Create Folders
# ------------------------------------------------------------

foreach($folder in $structure.folders){

    Ensure-Directory $folder.path

}

Write-Host ""

# ------------------------------------------------------------
# Create Files
# ------------------------------------------------------------

foreach($file in $structure.files){

    if(Test-Path $file.path){

        Write-Host "[ OK ]    File   : $($file.path)"
        continue

    }

    Ensure-ParentDirectory $file.path

    $template = Find-Template `
                    -Templates $templateConfig `
                    -TemplateId $file.template

    if($null -eq $template){

        throw "Unknown template: $($file.template)"

    }

    if($template.source){

        $templateFile = Join-Path `
                            $templateRoot `
                            $template.source

        if(!(Test-Path $templateFile)){

            throw "Template not found: $templateFile"

        }

        Copy-Item `
            $templateFile `
            $file.path

    }
    else{

        New-Item `
            -ItemType File `
            -Force `
            -Path $file.path | Out-Null

    }

    Write-Host "[CREATE] File   : $($file.path)"

}

Write-Host ""
Write-Host "Initialization completed successfully."
Write-Host ""